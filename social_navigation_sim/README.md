# Mô phỏng ba robot omni với vùng xã hội

Package được duy trì cho ROS 2 Humble / Gazebo Fortress, dùng robot
`3w_v2_multi` và mesh `meshes/3w_v2`. Các demo một robot, Nav2/SLAM và mẫu
robot khác của bản gốc đã được gỡ khỏi phạm vi dự án ngày 28/10/2026.

## Hướng dẫn đang dùng

- [Build và chọn backend](../README.md).
- [D* Lite + MPC, cảm biến và đội hình](README_DSTAR_MPC.md).
- [Cảnh tĩnh social_static](README_SOCIAL_STATIC.md).
- [Cảnh động social_dynamic](README_SOCIAL_DYNAMIC.md).
- [Paper1](../README_PAPER1_GWO_WOA.md) và [Paper2](../README_PAPER2_APF_MPC.md).
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
