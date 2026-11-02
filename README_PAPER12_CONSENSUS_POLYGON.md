# Paper 12 — consensus_polygon (comparison 10)

## 1. Build và chạy môi trường tĩnh

Các lệnh để người dùng tự chạy trên máy có ROS 2 Humble/Gazebo Fortress.
Dừng phiên cũ bằng Ctrl+C trước khi mở phiên mới; chọn 2D Goal Pose trong RViz.

```bash
cd ~/three-robot-rescue
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export ROS_DOMAIN_ID=31
recording_dir="recordings/paper12_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh paper12 --diagnose-stop "$recording_dir" \
  social_scene:=static
# Sau khi dừng mô phỏng bằng Ctrl+C, xem bản vừa ghi:
python3 scripts/view_replay.py --session "$recording_dir"
```

## 2. Build và chạy môi trường động

```bash
cd ~/three-robot-rescue
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export ROS_DOMAIN_ID=31
recording_dir="recordings/paper12_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh paper12 --diagnose-stop "$recording_dir" \
  social_scene:=dynamic
# Sau khi dừng mô phỏng bằng Ctrl+C, xem bản vừa ghi:
python3 scripts/view_replay.py --session "$recording_dir"
```

Mỗi bộ lệnh chạy phía trên đã bật ghi bản chạy vào thư mục mới.
Camera và vùng xã hội bật trong wrapper. Quan sát chủ động tự quay mặc định
tắt cho các chế độ đối chiếu, có thể bật `social_observation:=true social_auto_observe:=true`.
Để tắt camera/xã hội, thêm `leader_camera:=false person_detection:=false
head_pose_enabled:=false body_pose_enabled:=false social_avoidance:=false` vào cuối lệnh.

## 3. Test và kiểm tra ba tầng

Bộ test đã viết, **chưa được chạy trong tác vụ tích hợp**. Toàn bộ lệnh:

```bash
cd ~/three-robot-rescue
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export ROS_DOMAIN_ID=31
PYTHONPATH="$PWD/social_navigation_planner:$PYTHONPATH" /usr/bin/python3 -m pytest \
  social_navigation_planner/test/test_comparison_methods.py \
  social_navigation_planner/test/test_comparison_adapter.py \
  -q -p no:cacheprovider
```

Trong terminal khác khi mô phỏng đang chạy, kiểm tra phương pháp và các đầu ra:

```bash
cd ~/three-robot-rescue
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=31
ros2 topic echo /comparison/robot3/status --once
ros2 topic info /robot3/cmd_vel
```

`stages` gồm `formation_target`, `trajectory_twist`, `control_twist` khi
tracking được tính. Nếu shared safety/escape đang giữ quyền điều khiển,
stages có thể rỗng; xem `reason` và `command_body`. Mỗi xe chỉ được có một
publisher cmd_vel từ bộ điều khiển đang chọn. Tên node vẫn chứa distributed_mpc
để tương thích chẩn đoán, không chứng minh thuật toán đang là baseline.

## 4. Ba thuật toán và phạm vi triển khai

| Tầng | Nội dung |
|---|---|
| Điều khiển robot | Improved State Transformation controller |
| Bám quỹ đạo | Consensus-based directed-graph tracking |
| Đội hình | Directed Distributed Regular Polygon Formation |

Thứ tự thực thi theo phụ thuộc dữ liệu: **formation → trajectory → control**,
sau đó giới hạn gia tốc và kiểm tra quỹ đạo an toàn. D* Lite/coordinator
vẫn cấp tham chiếu chung; nguồn camera/LiDAR/map và nhánh né khẩn cấp
NK-084 dùng chung. Vì vậy đây là thử kiến trúc lai, không so sánh thuần
thuật toán né của bài báo. Không dùng kết quả này để tuyên bố tái lập bài gốc.

**Giới hạn riêng:** Consensus tam giác/offset tham chiếu trên ba xe; chưa tái lập bộ điều khiển đồ thị có hướng của bài gốc.

Nguồn triển khai: bản generator ba tầng trong [cuộc trao đổi người dùng cung cấp](https://chatgpt.com/share/6ae85d47-5250-83ec-80a5-0b07b13a65e6).
Trích các chuỗi module bằng AST literal, không thực thi generator/shell từ
trang chia sẻ. Không tải được artifact sandbox từ phiên khác; đây là tích
hợp mã xuất hiện trong hội thoại, không phải giải nén ZIP gốc.
Tên tác giả/DOI/phương trình từng bài chưa được đối chiếu đầy đủ; không gán
kết quả Gazebo cũ hoặc số test của phiên chia sẻ thành kết quả của dự án này.

**Kiểm chứng tác vụ này:** kiểm tra cú pháp tĩnh và đường dẫn; chưa build,
chưa chạy pytest, chưa ROS/Gazebo. Baseline NK-083 vẫn có lỗi contact,
nhánh an toàn chung không là bảo đảm không va chạm.

## 5. File chính

- `social_navigation_planner/social_navigation_planner/comparison_methods/method_10_consensus_polygon/formation.py`.
- Cùng thư mục: `trajectory.py`, `control.py`, `pipeline.py`.
- `social_navigation_planner/social_navigation_planner/comparison_controller.py`: ROS/safety adapter.
- `social_navigation_sim/launch/paper12_consensus_polygon.launch.py`: launch riêng.
- `scripts/run_comparison.sh`: chạy động và tự ghi từng lượt.

Tổng hợp: [10 phương pháp](README_PAPERS_03_12.md).
