# Mô phỏng ba robot omni với vùng xã hội

## Build và chạy

Chạy từ thư mục gốc repository (`~/three-robot-rescue`), trên máy đã có
ROS 2 Humble / Gazebo Fortress và các phụ thuộc của dự án:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
recording_dir="recordings/dynamic_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh dynamic --diagnose-stop "$recording_dir"
# Sau khi dừng mô phỏng bằng Ctrl+C, xem bản vừa ghi:
python3 scripts/view_replay.py --session "$recording_dir"
```

Chọn **2D Goal Pose** trong RViz; `Ctrl+C` ở terminal chạy để dừng.
Camera/vùng xã hội và chế độ ghi lỗi: xem [hướng dẫn gốc](../README.md).
Các lệnh do người dùng tự chạy; AI chỉ tự chạy mô phỏng khi được yêu cầu rõ.


**Hiện hành:** mã tiếp tục cải tiến tới NK-084; xem bàn giao đầu
[nhật ký](../README_NHAT_KY_DU_AN.md). NK-034 là mốc lịch sử khôi phục. Trước mỗi cải tiến phải tạo
[backup](../docs/BACKUP_VA_KHOI_PHUC.md).

Package được duy trì cho ROS 2 Humble / Gazebo Fortress, dùng robot
`3w_v2_multi` và mesh `meshes/3w_v2`. Các demo một robot, Nav2/SLAM và mẫu
robot khác của bản gốc đã được gỡ khỏi phạm vi dự án ngày 28/10/2026.

## Hướng dẫn đang dùng

- [Build và chọn backend](../README.md).
- [D* Lite + MPC, cảm biến và đội hình](README_DSTAR_MPC.md).
- [Cảnh tĩnh social_static](README_SOCIAL_STATIC.md).
- [Cảnh động social_dynamic](README_SOCIAL_DYNAMIC.md).
- [Paper1](../README_PAPER1_GWO_WOA.md), [Paper2](../README_PAPER2_APF_MPC.md) và
  [10 prototype ba tầng mới — Paper3–12](../README_PAPERS_03_12.md).
- [Báo cáo tiến độ](../README_BAO_CAO_TIEN_DO.md).

## Cấu trúc

| Thư mục | Chức năng |
|---|---|
| `launch/` | Hai chế độ xã hội, hai paper và hai launch nền; helper đồ họa |
| `scripts/` | Perception, tracking, vùng xã hội, quan sát chủ động và generator |
| `src/` | Kinematics robot và plugin chuyển động người |
| `worlds/`, `map/`, `config/` | Hai cảnh tĩnh/động, map vật lý, bridge và cấu hình |
| `urdf/3w_v2_multi/`, `meshes/3w_v2/` | Robot, camera RGB-D và LiDAR |
| `models/` | Model người và trọng số perception cần cho pipeline |
| `test/` | Hồi quy perception, vùng TV, lịch động và LiDAR |

Các generator dùng chung `scripts/scene_geometry.py` và
`scripts/map_geometry.py`. Chỉ chạy generator khi chủ động cập nhật asset;
launch nạp world/map có sẵn. Model/manifest kịch bản không phải kết quả
nhận diện cảm biến. Pose robot vẫn lấy từ Gazebo.
