# Paper3 — bản chuyển đổi độc lập trên omni (NK120)

## 1. Chạy môi trường động, có ghi bản chạy

Dừng phiên cũ bằng Ctrl+C trước khi mở. Chọn 2D Goal Pose trong RViz.

```bash
cd ~/three-robot-rescue
sudo apt install -y python3-numpy python3-scipy ffmpeg x11-utils
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export ROS_DOMAIN_ID=31
recording_dir="recordings/paper3_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh paper3 --diagnose-stop "$recording_dir" social_scene:=dynamic
# Ctrl+C để dừng, rồi xem đúng lượt vừa chạy:
python3 scripts/view_replay.py --session "$recording_dir"
```

## 2. Chạy môi trường tĩnh, có ghi bản chạy

```bash
cd ~/three-robot-rescue
sudo apt install -y python3-numpy python3-scipy ffmpeg x11-utils
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export ROS_DOMAIN_ID=31
recording_dir="recordings/paper3_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh paper3 --diagnose-stop "$recording_dir" social_scene:=static
# Ctrl+C để dừng, rồi xem đúng lượt vừa chạy:
python3 scripts/view_replay.py --session "$recording_dir"
```

## 3. Thuật toán, nguồn và phần chuyển đổi

[Nguồn DOI](https://doi.org/10.12962/jaree.v9i1.433)

Nguồn: Putra, Agustinah, Sahal (2025), *Leader-Follower Formation and Obstacle Avoidance for Nonholonomic Mobile Robots Using Velocity Obstacles*.

- Đội hình V: đích follower lấy trực tiếp từ pose leader đo được, `pL + R(thetaL)[−0.7, ±0.5]`, tương ứng Eq5–6. Không lấy offset từ coordinator baseline.
- Pure Pursuit: góc mục tiêu dùng `atan2`, `w=2v sin(alpha)/Ld` (Eq3–4); chuẩn hóa góc, quay tại chỗ nếu mục tiêu ở phía sau.
- VO: kiểm tia vận tốc tương đối cắt đĩa Minkowski (Eq12). Bản chuyển đổi dùng horizon3s, 24hướng×3mức tốc độ; chọn nghiệm gần vận tốc mong muốn và tiến mục tiêu.
- **Chuyển đổi:** đầu ra VO được phép chạy ngang bằng bánh omni. Đây không còn là ràng buộc nonholonomic nguyên bản. Giới hạn0.28m/s,1.2rad/s, kích thướcV và tiêu chí chọn ứng viên là cấu hình thực nghiệm của dự án, không phải sao chép tham số kết quả tác giả.
- Mã: `paper_models/kinematic.py`: `v_targets`, `pursuit`, `vo_collision`, `vo_command`.

## Hạ tầng chung và giới hạn đối chiếu

`paper_experiment_node.py` là node độc lập, không kế thừa D*+MPC của người dùng. Launch tắt coordinator và ba MPC baseline **chỉ trong chế độ paper**. Baseline, Paper1 và Paper2 giữ nguyên thuật toán.

Chung scene/camera/nhận diện và map vùng xã hội; LiDAR tối đa2m, vận tốc vật thể ước lượng từ cụm điểm qua thời gian. Chỉ pose robot dùng Gazebo để định vị, không dùng lịch/pose người ground truth cho điều khiển. Ước lượng cụm đơn giản có thể nhầm association/che khuất, không tương đương tracker đã benchmark.

A* thông thường trong `paper_models/environment.py` chỉ cấp waypoint cho leader, là **hạ tầng thực nghiệm thêm vào**, không phải luật né A* baseline và không gán là công thức bài báo. Các luật paper tự tạo formation/command. Lớp veto kiểm map vật lý, map xã hội, swept LiDAR và peer trong0.4s; nếu vi phạm thì phanh, **không tìm hộ đường né bằng baseline**. Phanh không bảo đảm người không đi vào robot đang đứng. Nếu xe đang nằm trong vùng xã hội mới xuất hiện, veto có thể giữ xe; đây là giới hạn, không phải kết quả bài báo.

Từ NK185, camera/xã hội và quan sát chủ động bật mặc định qua PaperBehavior, dùng ObservationSweep với phản hồi hướng đo và kiểm an toàn chung. Node ghi `stamp`, lý do, lệnh trước/sau veto và target vào `escape_decision.search`; `goal` né đểnull vì đây không phải đíchA*né. Viewer giữ nguyên; goal người dùng vẫn do recorder goal ghi riêng. `terminal_safe=false` nghĩa chưa chứng minh an toàn dừng dài hạn.

**Trạng thái:** đã viết mã chuyển đổi và kiểm cấu trúc; chưa build/pytest/Gazebo. Không phải tái lập nguyên vẹn hay bằng chứng tốt hơn D*+MPC. Khi so sánh phải báo cả phần chuyển đổi, số lần veto và điều kiện mô phỏng; không gán kết quả hệ kết hợp hoàn toàn cho tác giả.

Cập nhật NK185 dùng lớp cảm biến, phân loại LiDAR, giới hạn vận tốc,
an toàn và camera quan sát chung cho các paper. Thông số và giới hạn kiểm
chứng xem mục “Hành vi chung” trong README gốc. Chính sách điều khiển và
đội hình của bài được mô tả ở các mục trên. Chưa chạy thử NK185.
