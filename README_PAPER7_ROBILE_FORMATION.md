# Paper7 — Robile Multi-Robot Formation (NK121)

## 1. Build và chạy cảnh động, có ghi — mặc định

Dừng lượt cũ bằng Ctrl+C trước khi mở lượt mới.

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
recording_dir="recordings/paper7_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh paper7 --diagnose-stop "$recording_dir" social_scene:=dynamic
# Chọn 2D Goal Pose trong RViz. Sau Ctrl+C, xem đúng lượt vừa chạy:
python3 scripts/view_replay.py --session "$recording_dir"
```

## 2. Build và chạy cảnh tĩnh, có ghi

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
recording_dir="recordings/paper7_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh paper7 --diagnose-stop "$recording_dir" social_scene:=static
# Chọn 2D Goal Pose trong RViz. Sau Ctrl+C, xem đúng lượt vừa chạy:
python3 scripts/view_replay.py --session "$recording_dir"
```

## 3. Nguồn, ba phần thuật toán và chuyển đổi

Nguồn: [SuneshSundarasami/Robile-Multi-Robot-Formation-Simulation-Environment-Using-Pybullet-And-ROS2](https://github.com/SuneshSundarasami/Robile-Multi-Robot-Formation-Simulation-Environment-Using-Pybullet-And-ROS2), commit `1af1a4c802621e4d8a22791e28daf3728271eb08`. Đây là repository mô phỏng; chưa xác minh bài báo/DOI. **Paper7 là số chế độ trong dự án**.

- **Điều khiển:** xuất vận tốc omni world `[vx,vy,w]`, đổi sang hệ thân tại node ROS. Không port cơ cấu lái/bánh Robile hoặc PyBullet actuator.
- **Bám đội hình:** slot tương đối quay theo yaw leader: `p_des=pL+R(thetaL)offset`. Giữ hai slot đầuV`[-1,±1]m` từ ví dụ4follower, giảm còn2follower.
- PID theo **vector sai số vị trí**, không chỉ khoảng cách vô hướng: `v=e+0.1∫e dt+0.1 de/dt`, tích phân giới hạn±10, yawP gain1 theo leader.
- Đổi `dt=1/240`cứng của nguồn thành dt thực của callback, bỏ xung đạo hàm mẫu đầu; giới hạn tốc độ0.28m/s. Các thay đổi này phải được nêu khi báo cáo kết quả so sánh.
- **Bám quỹ đạo leader:** nguồn minh họa lệnh chuyển động cố định; ở đây bổ sung goal/setpoint tracking tối đa0.2m/s và A*waypoint chung để người dùng chọn đích như các chế độ khác. Đây là phần tích hợp, không phải kết quả planner từ repo Robile.

Mã mới tự viết `paper_models/robile.py`, dùng cùng Gazebo/world/socialmap và pose robot hiện có, không chép URDF/PyBullet models sang đây. Lớp veto vật lý/xã hội/LiDAR là bổ sung chung, không thuộc bộ PID gốc. Tích phân có cap nhưng chưa có anti-windup theo lệnh sau veto; cần kiểm tra giữdừng/bật lại. Chưa kiểm chứng hiệu năng, đội hình hoặc va chạm.

## Kiểm chứng và bản ghi

Đã viết code, regression và kiểm tra cấu trúc; **chưa build/pytest/Gazebo** trong tác vụ. Người dùng tự chạy theo khối lệnh phía trên. Bản ghi vẫn có camera/vùng xã hội, nguồn upstream/commit và reason của từngxe trong `navigation.jsonl` → `decision.search`. Xem `diagnostics_config.json` để xác định module/nguồn đã nạp.

D*+MPC gốc và Paper1/2 giữ thuật toán hiện có. Các chế độ so sánh dùng node độc lập; map xã hội/camera và lớp veto chung có thể giữ xe. Phanh không chứng minh người không tiếp tục đi vào robot đang đứng. Không khẳng định phương pháp mới tốt hơn baseline trước benchmark cùng điều kiện.

Cập nhật NK185 dùng lớp cảm biến, phân loại LiDAR, giới hạn vận tốc,
an toàn và camera quan sát chung cho các paper. Thông số và giới hạn kiểm
chứng xem mục “Hành vi chung” trong README gốc. Chính sách điều khiển và
đội hình của bài được mô tả ở các mục trên. Chưa chạy thử NK185.
