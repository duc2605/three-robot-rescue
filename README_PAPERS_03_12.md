# 10 phương pháp ba tầng — Paper03 tới Paper12

## Build và chọn phương pháp

Hai paper cũ giữ số1–2. Mười phương pháp trong liên kết dùng method01–10,
tương ứng paper03–12 của repository; bảng sau chỉ rõ ánh xạ.

Ví dụ chọn method01 (paper03), cảnh động, có camera/xã hội:

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
  social_scene:=dynamic
# Sau khi dừng mô phỏng bằng Ctrl+C, xem bản vừa ghi:
python3 scripts/view_replay.py --session "$recording_dir"
```

Hoặc dùng launch chọn method rõ ràng, mặc định cảnh tĩnh:

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

Mỗi README riêng bên dưới có đủ lệnh build/chạy/test; ghi bản chạy đã
được ghép ngay vào từng lệnh chạy, không có bước ghi riêng. Chỉ mở
một phương pháp mỗi lượt; không chạy baseline cùng lúc.

| Paper dự án | Method liên kết | Phương pháp | Launch | Tài liệu |
|---|---|---|---|---|
| 3 | 01 | pure_pursuit_vo | `paper3_pure_pursuit_vo.launch.py` | [Hướng dẫn](README_PAPER3_PURE_PURSUIT_VO.md) |
| 4 | 02 | impedance | `paper4_impedance.launch.py` | [Hướng dẫn](README_PAPER4_IMPEDANCE.md) |
| 5 | 03 | receding_mpc | `paper5_receding_mpc.launch.py` | [Hướng dẫn](README_PAPER5_RECEDING_MPC.md) |
| 6 | 04 | ctc_virtual | `paper6_ctc_virtual.launch.py` | [Hướng dẫn](README_PAPER6_CTC_VIRTUAL.md) |
| 7 | 05 | deform | `paper7_deform.launch.py` | [Hướng dẫn](README_PAPER7_DEFORM.md) |
| 8 | 06 | backstepping | `paper8_backstepping.launch.py` | [Hướng dẫn](README_PAPER8_BACKSTEPPING.md) |
| 9 | 07 | sliding_mode | `paper9_sliding_mode.launch.py` | [Hướng dẫn](README_PAPER9_SLIDING_MODE.md) |
| 10 | 08 | observer | `paper10_observer.launch.py` | [Hướng dẫn](README_PAPER10_OBSERVER.md) |
| 11 | 09 | dwa | `paper11_dwa.launch.py` | [Hướng dẫn](README_PAPER11_DWA.md) |
| 12 | 10 | consensus_polygon | `paper12_consensus_polygon.launch.py` | [Hướng dẫn](README_PAPER12_CONSENSUS_POLYGON.md) |

## Kiến trúc và phạm vi

Mười bộ có ba module thực thi formation/trajectory/control, kết hợp pipeline
riêng. Normal tracking dùng pipeline của phương pháp đang chọn; bị loại
thì giữ dừng, không âm thầm quay sang beam tracking MPC baseline. Emergency
escape và kiểm tra map/LiDAR/peer/moving/freshness/gia tốc vẫn dùng chung.
D* Lite/coordinator và camera/social map dùng lại hạ tầng hiện tại.
Wrapper nhận leader robot khác và adapter đổi chỉ số về leader2 nội bộ.
Ba node điều khiển mới thay ba distributed MPC baseline, không khởi động
hai bộ publisher cạnh tranh; paper1/2 giữ cách hoạt động cũ.

Đây là **10 prototype ba tầng lấy từ [hội thoại được cung cấp](https://chatgpt.com/share/6ae85d47-5250-83ec-80a5-0b07b13a65e6)**,
không phải 10 bản tái lập bài báo đã xác nhận. CTC/vision/slip/car-like và
DEFORM có giới hạn cụ thể trong từng README. DEFORM gốc có repository tại
[NeSC-IV/DEFORM](https://github.com/NeSC-IV/DEFORM); mã ở đây không phải port
repository đó. Thông tin thư mục/tên phương pháp không thay thế trích dẫn
bài báo đầy đủ; nhiều DOI/phương trình chưa xác minh.

## Kiểm chứng thực tế

Chỉ kiểm cấu trúc AST, import nội bộ tĩnh, shell syntax và liên kết tài liệu.
Đã viết test numerical/adapter nhưng **chưa chạy**, chưa build và chưa thử
ROS/Gazebo theo quy ước người dùng tự chạy. Không chuyển số60 test của hội
thoại thành số test dự án. Không khẳng định né tốt hơn baseline/hai paper cũ.
Xem [minh chứng phạm vi tích hợp](docs/evidence/2026-11-02/nk087_ten_comparison_methods/README.md).

## Chú giải file

`comparison_methods/registry.py` ánh xạ method; mỗi thư mục `method_*` có
bốn module; `common.py` giữ math/memory chung. Adapter
`comparison_controller.py` ghép với hạ tầng. Helper launch
`_comparison_backend.py` tránh sao chép cấu hình; 10 wrapper đặt tên paper03–12.
`run_comparison.sh` tự ghi từng lượt, hỗ trợ `--diagnose-stop NEW_DIRECTORY` để đặt tên, ghi hash đúng
module của phương pháp đang chọn, dùng viewer hiện có.
