# Paper8 — bản chuyển đổi độc lập trên omni (NK120)

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
recording_dir="recordings/paper8_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh paper8 --diagnose-stop "$recording_dir" social_scene:=dynamic
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
recording_dir="recordings/paper8_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh paper8 --diagnose-stop "$recording_dir" social_scene:=static
# Ctrl+C để dừng, rồi xem đúng lượt vừa chạy:
python3 scripts/view_replay.py --session "$recording_dir"
```

## 3. Thuật toán, nguồn và phần chuyển đổi

[Nguồn DOI](https://doi.org/10.1109/LRA.2025.3552998)

Nguồn: Li, Xu, Shi, Li (2025), *DEFORM: Adaptive Formation Reconfiguration of Multi-Robot Systems in Confined Environments*. [PDF từ repository tác giả](https://github.com/NeSC-IV/DEFORM/blob/main/RA_L_DEFORM.pdf).

- Eq2/4: tinh chỉnh waypoint bằng chi phí khoảng cách vật cản và sai lệch tham chiếu.
- Eq3: đo bề rộng hành lang; bản này rời rạc5cm và một lượt tinh chỉnh, **không tái lập đầy đủ vòng lặp hội tụ Algorithm1**.
- Eq5: Hungarian gán robot vào slot, robot nhận slotđầu trở thành leader tạm; hysteresis0.08 và chu kỳ1s là bổ sung tích hợp.
- Eq6: tham chiếu consensus từ pose peer, offset và slot ảo trên đồ thị đầy đủ.
- Eq7–8: vận tốc tham chiếu, tối ưu SLSQP12bước×0.1s, mô hình unicycle, chi phíQ/R và ràng buộc map/peer/vật động. Solver không hội tụ thì dừng, không chuyển sang baseline.
- **Chuyển đổi:**3xe, thư việnV/cột thay4xe; horizon12 thay40; SLSQP thayCasADi/IPOPT; không cho slack âm để giữ clearance vật lý. Xe omni nhận vận tốc dọc thân theo mô hình unicycle. Cả ba bài toán giải trong một node bằng snapshot, **không phải benchmark phân tán qua mạng**. Giới hạn1s kiểm sau tính không phải solver thời gian thực có ngắt.
- Mã: `paper_models/deform.py`. Chưa kiểm chứng bề rộng/handoff leader/khả năng hội tụ trong Gazebo.

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
