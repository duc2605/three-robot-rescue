# Three Robot Rescue — D* Lite + MPC và điều hướng xã hội

Mỗi phần dưới đây có bộ lệnh độc lập: **vào thư mục → build → source → chạy**.
Chỉ sao chép phần cần dùng. Máy cần ROS 2 Humble, Gazebo Fortress, colcon
và các phụ thuộc khai báo trong hai package; các lệnh giả định dự án ở
`~/three-robot-rescue`, thay đường dẫn nếu bạn clone ở nơi khác.

Chỉ mở một phiên mô phỏng mỗi lượt. Trong RViz chọn **2D Goal Pose** để
đặt đích; `Ctrl+C` ở terminal chạy để dừng trước khi chọn chế độ khác.
Các lệnh để người dùng tự chạy; AI chỉ thực thi khi được yêu cầu rõ.
Mỗi bộ lệnh mô phỏng bên dưới **đã bao gồm ghi bản chạy**. Tên thư mục
có chế độ và thời gian, không dùng lại bản cũ. Sau khi dừng bằng Ctrl+C,
chạy dòng viewer ngay trong cùng bộ lệnh để xem lại. Muốn xem trong lúc
đang chạy, sao chép lệnh viewer có đường dẫn đầy đủ mà terminal in ra sang
terminal thứ hai. Thư mục chỉ xuất hiện trên máy thực sự chạy mô phỏng.

## 1. Chạy dự án động — D* Lite + ba MPC

### 1.1. Có camera và nhận diện vùng xã hội

Dùng khi kiểm tra né người đồng thời với vùng xem TV/nhóm người.

```bash
cd ~/three-robot-rescue
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export ROS_DOMAIN_ID=31
recording_dir="recordings/dynamic_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh dynamic --diagnose-stop "$recording_dir" \
  leader_camera:=true person_detection:=true head_pose_enabled:=true body_pose_enabled:=true social_avoidance:=true social_observation:=true social_auto_observe:=true
# Sau khi dừng mô phỏng bằng Ctrl+C, xem bản vừa ghi:
python3 scripts/view_replay.py --session "$recording_dir"
```

Khi leader còn cách **goal đã chọn không quá20cm**, xe tự thử quay đủ một
vòng để camera quan sát quanh goal. Một vòng hoàn tất cho mỗi goal; nếu
có người tới hoặc camera mất dữ liệu mới, xe ưu tiên an toàn và thử lại sau.
Đổi goal bắt đầu lượt quan sát mới. Chế độ này cần camera và
`social_observation:=true` như lệnh trên. Kết quả nhận diện vẫn phụ thuộc
camera; quay không tự tạo vùng xã hội. Bản NK093 chưa kiểm chứng Gazebo.

### 1.2. Chỉ thử né vật động bằng LiDAR 2m

Camera và nhận diện vùng xã hội tắt theo profile động mặc định; vẫn ghi
bản chạy với LiDAR/pose/contact. Bộ lệnh độc lập:

```bash
cd ~/three-robot-rescue
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export ROS_DOMAIN_ID=31
recording_dir="recordings/dynamic_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh dynamic --diagnose-stop "$recording_dir"
# Sau khi dừng mô phỏng bằng Ctrl+C, xem bản vừa ghi:
python3 scripts/view_replay.py --session "$recording_dir"
```

## 2. Chạy dự án tĩnh — D* Lite + ba MPC

Cảnh tĩnh có nhóm người và vùng xem TV. Camera/nhận diện xã hội được bật
rõ trong lệnh để không phụ thuộc lựa chọn ở lượt chạy trước.

```bash
cd ~/three-robot-rescue
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export ROS_DOMAIN_ID=31
recording_dir="recordings/static_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh static --diagnose-stop "$recording_dir" \
  leader_camera:=true person_detection:=true head_pose_enabled:=true body_pose_enabled:=true social_avoidance:=true social_observation:=true social_auto_observe:=true
# Sau khi dừng mô phỏng bằng Ctrl+C, xem bản vừa ghi:
python3 scripts/view_replay.py --session "$recording_dir"
```

## 3. Chạy các bài báo đối chiếu

### 3.1. Paper1 — GWO–WOA + DWA

Mặc định chạy cảnh tĩnh. Muốn chạy cảnh động, thêm `social_scene:=dynamic`
vào cuối lệnh launch trước khi chạy.

```bash
cd ~/three-robot-rescue
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export ROS_DOMAIN_ID=31
recording_dir="recordings/paper1_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh paper1 --diagnose-stop "$recording_dir"
# Sau khi dừng mô phỏng bằng Ctrl+C, xem bản vừa ghi:
python3 scripts/view_replay.py --session "$recording_dir"
```

### 3.2. Paper2 — APF–MPC

Cần SciPy trong Python hệ thống; nếu thiếu, cài bằng
`sudo apt install python3-scipy`. Mặc định cảnh tĩnh, thêm
`social_scene:=dynamic` vào cuối lệnh launch nếu muốn cảnh động.

```bash
cd ~/three-robot-rescue
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export ROS_DOMAIN_ID=31
recording_dir="recordings/paper2_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh paper2 --diagnose-stop "$recording_dir"
# Sau khi dừng mô phỏng bằng Ctrl+C, xem bản vừa ghi:
python3 scripts/view_replay.py --session "$recording_dir"
```

Chi tiết: [Paper1](README_PAPER1_GWO_WOA.md), [Paper2](README_PAPER2_APF_MPC.md).
Các triển khai là bản thích nghi; chưa có benchmark chứng minh tốt hơn baseline.

### 3.3–3.12. Mười phương pháp mới từ danh sách chia sẻ

Paper1/2 cũ giữ nguyên. Method01–10 mới tương ứng paper3–12 trong dự án.
Mỗi mục sau có bộ lệnh độc lập; camera/vùng xã hội bật, quan sát tự quay
mặc định tắt. Đây là prototype ba tầng, chưa tái lập bài báo đã kiểm chứng.

### 3.3. Paper3 — pure_pursuit_vo

Method `01` trong danh sách chia sẻ; [ba tầng và giới hạn](README_PAPER3_PURE_PURSUIT_VO.md).

```bash
cd ~/three-robot-rescue
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export ROS_DOMAIN_ID=31
recording_dir="recordings/paper3_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh paper3 --diagnose-stop "$recording_dir" \
  social_scene:=static
# Sau khi dừng mô phỏng bằng Ctrl+C, xem bản vừa ghi:
python3 scripts/view_replay.py --session "$recording_dir"
```

Thêm `social_scene:=dynamic` vào cuối lệnh launch để dùng môi trường động.

### 3.4. Paper4 — impedance

Method `02` trong danh sách chia sẻ; [ba tầng và giới hạn](README_PAPER4_IMPEDANCE.md).

```bash
cd ~/three-robot-rescue
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export ROS_DOMAIN_ID=31
recording_dir="recordings/paper4_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh paper4 --diagnose-stop "$recording_dir" \
  social_scene:=static
# Sau khi dừng mô phỏng bằng Ctrl+C, xem bản vừa ghi:
python3 scripts/view_replay.py --session "$recording_dir"
```

Thêm `social_scene:=dynamic` vào cuối lệnh launch để dùng môi trường động.

### 3.5. Paper5 — receding_mpc

Method `03` trong danh sách chia sẻ; [ba tầng và giới hạn](README_PAPER5_RECEDING_MPC.md).

```bash
cd ~/three-robot-rescue
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export ROS_DOMAIN_ID=31
recording_dir="recordings/paper5_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh paper5 --diagnose-stop "$recording_dir" \
  social_scene:=static
# Sau khi dừng mô phỏng bằng Ctrl+C, xem bản vừa ghi:
python3 scripts/view_replay.py --session "$recording_dir"
```

Thêm `social_scene:=dynamic` vào cuối lệnh launch để dùng môi trường động.

### 3.6. Paper6 — ctc_virtual

Method `04` trong danh sách chia sẻ; [ba tầng và giới hạn](README_PAPER6_CTC_VIRTUAL.md).

```bash
cd ~/three-robot-rescue
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export ROS_DOMAIN_ID=31
recording_dir="recordings/paper6_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh paper6 --diagnose-stop "$recording_dir" \
  social_scene:=static
# Sau khi dừng mô phỏng bằng Ctrl+C, xem bản vừa ghi:
python3 scripts/view_replay.py --session "$recording_dir"
```

Thêm `social_scene:=dynamic` vào cuối lệnh launch để dùng môi trường động.

### 3.7. Paper7 — deform

Method `05` trong danh sách chia sẻ; [ba tầng và giới hạn](README_PAPER7_DEFORM.md).

```bash
cd ~/three-robot-rescue
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export ROS_DOMAIN_ID=31
recording_dir="recordings/paper7_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh paper7 --diagnose-stop "$recording_dir" \
  social_scene:=static
# Sau khi dừng mô phỏng bằng Ctrl+C, xem bản vừa ghi:
python3 scripts/view_replay.py --session "$recording_dir"
```

Thêm `social_scene:=dynamic` vào cuối lệnh launch để dùng môi trường động.

### 3.8. Paper8 — backstepping

Method `06` trong danh sách chia sẻ; [ba tầng và giới hạn](README_PAPER8_BACKSTEPPING.md).

```bash
cd ~/three-robot-rescue
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export ROS_DOMAIN_ID=31
recording_dir="recordings/paper8_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh paper8 --diagnose-stop "$recording_dir" \
  social_scene:=static
# Sau khi dừng mô phỏng bằng Ctrl+C, xem bản vừa ghi:
python3 scripts/view_replay.py --session "$recording_dir"
```

Thêm `social_scene:=dynamic` vào cuối lệnh launch để dùng môi trường động.

### 3.9. Paper9 — sliding_mode

Method `07` trong danh sách chia sẻ; [ba tầng và giới hạn](README_PAPER9_SLIDING_MODE.md).

```bash
cd ~/three-robot-rescue
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export ROS_DOMAIN_ID=31
recording_dir="recordings/paper9_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh paper9 --diagnose-stop "$recording_dir" \
  social_scene:=static
# Sau khi dừng mô phỏng bằng Ctrl+C, xem bản vừa ghi:
python3 scripts/view_replay.py --session "$recording_dir"
```

Thêm `social_scene:=dynamic` vào cuối lệnh launch để dùng môi trường động.

### 3.10. Paper10 — observer

Method `08` trong danh sách chia sẻ; [ba tầng và giới hạn](README_PAPER10_OBSERVER.md).

```bash
cd ~/three-robot-rescue
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export ROS_DOMAIN_ID=31
recording_dir="recordings/paper10_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh paper10 --diagnose-stop "$recording_dir" \
  social_scene:=static
# Sau khi dừng mô phỏng bằng Ctrl+C, xem bản vừa ghi:
python3 scripts/view_replay.py --session "$recording_dir"
```

Thêm `social_scene:=dynamic` vào cuối lệnh launch để dùng môi trường động.

### 3.11. Paper11 — dwa

Method `09` trong danh sách chia sẻ; [ba tầng và giới hạn](README_PAPER11_DWA.md).

```bash
cd ~/three-robot-rescue
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export ROS_DOMAIN_ID=31
recording_dir="recordings/paper11_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh paper11 --diagnose-stop "$recording_dir" \
  social_scene:=static
# Sau khi dừng mô phỏng bằng Ctrl+C, xem bản vừa ghi:
python3 scripts/view_replay.py --session "$recording_dir"
```

Thêm `social_scene:=dynamic` vào cuối lệnh launch để dùng môi trường động.

### 3.12. Paper12 — consensus_polygon

Method `10` trong danh sách chia sẻ; [ba tầng và giới hạn](README_PAPER12_CONSENSUS_POLYGON.md).

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

Thêm `social_scene:=dynamic` vào cuối lệnh launch để dùng môi trường động.

## 4. Test — không mở Gazebo

### 4.1. Test nhanh phần chọn điểm né và an toàn vật động

Chạy bộ test liên quan các sửa gần nhất. Máy cần pytest trong Python hệ thống
(`sudo apt install python3-pytest` nếu chưa có). Bộ lệnh đầy đủ:

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
  social_navigation_planner/test/test_rear_escape_preference.py \
  social_navigation_planner/test/test_social_escape_priority.py \
  social_navigation_planner/test/test_motion_uncertainty_corridor.py \
  social_navigation_planner/test/test_moving_obstacle_safety.py \
  -q -p no:cacheprovider
```

### 4.2. Test hồi quy Python rộng hơn

Gồm scripts, perception/xã hội và planner. Ba test ament lint được loại rõ
trong lệnh; đây không phải kiểm thử Gazebo hoặc benchmark né người.

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
  scripts/tests social_navigation_sim/test social_navigation_planner/test \
  --ignore=social_navigation_planner/test/test_copyright.py \
  --ignore=social_navigation_planner/test/test_flake8.py \
  --ignore=social_navigation_planner/test/test_pep257.py \
  -q -p no:cacheprovider
```

`BUILD_TESTING=OFF` trong các lệnh build chỉ bỏ tìm ament lint khi build;
pytest bên trên vẫn chạy riêng. Test qua không chứng minh hết va chạm.

### 4.3. Test mười phương pháp ba tầng và adapter

Các test này mới được bổ sung, chưa thực thi trong tác vụ tích hợp.

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

## 5. Trạng thái và tài liệu

Điều hướng baseline hiện hành tới **NK-084**: ưu tiên điểm né phía sau theo hướng thân xe,
sau ưu tiên ngoài vùng xã hội; 44 test liên quan đã qua, chưa chạy Gazebo
bản NK-084. Lượt NK-083 kiểm bản NK-082 vẫn có contact và leader chưa quay
về goal. Chưa xác nhận cả ba xe né ổn. Tình trạng mới nhất ở đầu
[nhật ký bàn giao](README_NHAT_KY_DU_AN.md).

- [Báo cáo cải tiến kỹ thuật](README_BAO_CAO_TIEN_DO.md).
- [D* Lite, MPC và đội hình](social_navigation_sim/README_DSTAR_MPC.md).
- [LiDAR 2m và giới hạn](docs/LIDAR_2M_AVOIDANCE.md).
- [Quy trình làm việc](AGENTS.md), [backup/khôi phục](docs/BACKUP_VA_KHOI_PHUC.md).
- [Giấy phép](LICENSES.md), [chuẩn bị GitHub](docs/GITHUB_PREPARATION.md).

Trước mỗi cải tiến, người sửa tạo backup đã kiểm tra:

```bash
python3 scripts/create_backup.py --reason truoc_ten_cai_tien
```

Chỉ commit/push khi người dùng yêu cầu rõ trong tác vụ hiện tại.

Mười phương pháp đối chiếu ba tầng đã tích hợp nguồn ở NK-087;
chưa build/test/Gazebo. Xem [danh mục](README_PAPERS_03_12.md).

## 6. Chú giải thư mục và file cần biết

| Đường dẫn | Vai trò |
|---|---|
| `social_navigation_planner/` | D* Lite, ba MPC, hai paper cũ và mười prototype ba tầng |
| `social_navigation_sim/launch/` | Chọn cảnh, backend, camera, RViz/Gazebo |
| `social_navigation_sim/worlds/`, `map/`, `config/` | Cảnh, bản đồ vật lý và cấu hình cảm biến/bridge |
| `social_navigation_sim/urdf/`, `meshes/`, `models/` | Robot, cảm biến, model người và perception |
| `social_navigation_sim/scripts/` | Perception, vùng xã hội và ghi dữ liệu |
| `scripts/run_simulation.sh` | Chọn cảnh/backend; mỗi lượt ghi vào thư mục mới |
| `scripts/run_comparison.sh` | Chọn method01–10, tự ghi mỗi lượt |
| `scripts/run_dynamic.sh` | Điểm vào chạy động, ghi/chẩn đoán trong từng lượt chạy |
| `scripts/view_replay.py` | Mở giao diện bản ghi |
| `scripts/analyze_stop_diagnostics.py` | Tổng hợp nguyên nhân dừng và contact |
| `recordings/<tên>/` | Dữ liệu một lượt người dùng chủ động ghi |
| `docs/evidence/` | Minh chứng đã lưu để đối chiếu lâu dài |
| `backups/` | Snapshot nguồn trước cải tiến; không đưa lên GitHub mặc định |
| `build/`, `install/`, `log/` | Dữ liệu sinh bởi build/chạy; không phải nguồn để chỉnh sửa |

Hai package hiện tại thay cho tên cũ `astar_planner` và `ros2_omni_robot_sim`.
Bộ file tối thiểu theo từng loại lỗi và cách tránh đọc tràn lan:
[FILE_CAN_DOC_VA_LENH_CHAY.md](docs/FILE_CAN_DOC_VA_LENH_CHAY.md).
