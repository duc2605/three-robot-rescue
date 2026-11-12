# Paper5 — Hierarchical Optimization MPC (NK121)

## 1. Build và chạy cảnh động, có ghi — mặc định

Dừng lượt cũ bằng Ctrl+C trước khi mở lượt mới.

```bash
cd ~/three-robot-rescue
sudo apt install -y git python3-venv python3-pip python3-numpy python3-scipy ffmpeg x11-utils
export SOCIAL_HO_MPC_ROOT="$HOME/.cache/three-robot-rescue/paper5"
python3 scripts/prepare_ho_mpc.py --directory "$SOCIAL_HO_MPC_ROOT"
python3 -m venv --system-site-packages "$SOCIAL_HO_MPC_ROOT/venv"
"$SOCIAL_HO_MPC_ROOT/venv/bin/python" -m pip install \
  'numpy<2' 'casadi>=3.6,<4' 'qpsolvers>=4,<5' quadprog matplotlib
paper5_site="$("$SOCIAL_HO_MPC_ROOT/venv/bin/python" -c 'import sysconfig; print(sysconfig.get_path("purelib"))')"
export PYTHONPATH="$paper5_site:${PYTHONPATH:-}"
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export ROS_DOMAIN_ID=31
recording_dir="recordings/paper5_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh paper5 --diagnose-stop "$recording_dir" social_scene:=dynamic
# Chọn 2D Goal Pose trong RViz. Sau Ctrl+C, xem đúng lượt vừa chạy:
python3 scripts/view_replay.py --session "$recording_dir"
```

## 2. Build và chạy cảnh tĩnh, có ghi

```bash
cd ~/three-robot-rescue
sudo apt install -y git python3-venv python3-pip python3-numpy python3-scipy ffmpeg x11-utils
export SOCIAL_HO_MPC_ROOT="$HOME/.cache/three-robot-rescue/paper5"
python3 scripts/prepare_ho_mpc.py --directory "$SOCIAL_HO_MPC_ROOT"
python3 -m venv --system-site-packages "$SOCIAL_HO_MPC_ROOT/venv"
"$SOCIAL_HO_MPC_ROOT/venv/bin/python" -m pip install \
  'numpy<2' 'casadi>=3.6,<4' 'qpsolvers>=4,<5' quadprog matplotlib
paper5_site="$("$SOCIAL_HO_MPC_ROOT/venv/bin/python" -c 'import sysconfig; print(sysconfig.get_path("purelib"))')"
export PYTHONPATH="$paper5_site:${PYTHONPATH:-}"
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export ROS_DOMAIN_ID=31
recording_dir="recordings/paper5_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh paper5 --diagnose-stop "$recording_dir" social_scene:=static
# Chọn 2D Goal Pose trong RViz. Sau Ctrl+C, xem đúng lượt vừa chạy:
python3 scripts/view_replay.py --session "$recording_dir"
```

## 3. Nguồn, ba phần thuật toán và chuyển đổi

Nguồn: De Benedittis, Garabini, Pallottino (2025), *Managing Conflicting Tasks in Heterogeneous Multi-Robot Systems Through Hierarchical Optimization*, IEEE RA-L. [DOI10.1109/LRA.2025.3559843](https://doi.org/10.1109/LRA.2025.3559843), [trang tác giả](https://ddebenedittis.github.io/managing_conflicting_tasks_website/), [repository](https://github.com/ddebenedittis/hierarchical_optimization_mpc).

Commit cố định `4f4f0898d555c3864b7bc025e5099860c83f6cb9`; solver phụ thuộc `hierarchical_qp` commit `2139fa438300ac0fa14ad514f18a175319a93bab`. Script chuẩn bị chỉ tải/kiểm revision, không build/pip/chạy mã upstream. Cache ở ngoài workspace để không đưa cây nguồn upstream vào backup/GitHub. Chưa có khai báo license tổng thể rõ ràng của upstream, không vendor mã tác giả vào repo này.

- **Điều khiển:** gọi trực tiếp `HOMPCMultiRobot(hierarchical=True)` và `HierarchicalQP`/quadprog của tác giả. Không dùng một tổng có trọng số thay cho ưu tiên phân cấp.
- **Bám đội hình:** ràng buộc tuyến tính hóa khoảng cách bình phương giữa từng cặp robot. Khoảng cách tham chiếu lấy từ hìnhV0.7m×0.5m, không phụ thuộc độ dài waypoint.
- **Bám quỹ đạo:** tác vụ vị trí leader theo waypoint; đây là cấu hình thí nghiệm thay cho tác vụ vận tốc tâm đội hình trong ví dụ5omni của bài.
- Thứ tự: dynamics của solver → giới hạn đầu vào → tránh peer/vật thể LiDAR dự báo → vị trí leader → khoảng cách đội hình → giảm đầu vào. Cấu hình này ưu tiên leader hơn formation, vì vậy đội hình có thể biến dạng khi xung đột.
- Mô hình omni của tác giả là `[x,y]`, đầu vào world `[vx,vy]`; góc yaw được bám bằng luậtP ngoài MPC rồi node đổi về Twist từng xe. Horizon4×0.1s,3xe. Giới hạn từng trục0.28/√2m/s để chuẩn vận tốc không quá0.28m/s.
- Ràng buộc tránh vật động tuyến tính hóa dùng cluster LiDAR và dự báo vận tốc không đổi. Map xã hội/vật lý còn được kiểm bằng lớp veto chung sau giải. Không chứng minh an toàn khi tuyến tính hóa sai hoặc người đổi hướng.

Mã: `paper_models/ho_mpc.py`; định danh nguồn `upstream_sources.py`; chuẩn bị `scripts/prepare_ho_mpc.py`. Thiếu cache/dependency hoặc sai revision thì báo lỗi trước khi mở mô phỏng. Chưa xác nhận thời gian solver, hiệu năng hoặc tích hợp ROS. Không claim kết quả5xe của tác giả là kết quả3xe trong Gazebo này.

## Kiểm chứng và bản ghi

Đã viết code, regression và kiểm tra cấu trúc; **chưa build/pytest/Gazebo** trong tác vụ. Người dùng tự chạy theo khối lệnh phía trên. Bản ghi vẫn có camera/vùng xã hội, nguồn upstream/commit và reason của từngxe trong `navigation.jsonl` → `decision.search`. Xem `diagnostics_config.json` để xác định module/nguồn đã nạp.

D*+MPC gốc và Paper1/2 giữ thuật toán hiện có. Các chế độ so sánh dùng node độc lập; map xã hội/camera và lớp veto chung có thể giữ xe. Phanh không chứng minh người không tiếp tục đi vào robot đang đứng. Không khẳng định phương pháp mới tốt hơn baseline trước benchmark cùng điều kiện.

## 4. Test cầu nối solver — người dùng tự chạy

Sau khi làm phần chuẩn bị cache/dependency của khối chạy phía trên (không cần mở mô phỏng):

```bash
cd ~/three-robot-rescue
export SOCIAL_HO_MPC_ROOT="$HOME/.cache/three-robot-rescue/paper5"
paper5_site="$("$SOCIAL_HO_MPC_ROOT/venv/bin/python" -c 'import sysconfig; print(sysconfig.get_path("purelib"))')"
PYTHONPATH="$PWD/social_navigation_planner:$paper5_site:${PYTHONPATH:-}" /usr/bin/python3 -m pytest \
  social_navigation_planner/test/test_ho_mpc_optional.py -q -rs -p no:cacheprovider
```

Thiếu nguồn/dependency thì test báoSKIP; SKIP không phải solver đã qua. Nếu `SOCIAL_HO_MPC_ROOT` khác mặc định, giữ cùng biến trong terminal chạy.

Cập nhật NK185 dùng lớp cảm biến, phân loại LiDAR, giới hạn vận tốc,
an toàn và camera quan sát chung cho các paper. Thông số và giới hạn kiểm
chứng xem mục “Hành vi chung” trong README gốc. Chính sách điều khiển và
đội hình của bài được mô tả ở các mục trên. Chưa chạy thử NK185.
