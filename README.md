# Three Robot Rescue — D* Lite + MPC và điều hướng xã hội

Repository: [duc2605/three-robot-rescue](https://github.com/duc2605/three-robot-rescue).

Mô phỏng ba robot omni trên ROS 2 Humble / Gazebo Fortress. Repository hiện
có hai package nguồn, ba backend và hai môi trường được duy trì.

```text
three-robot-rescue/
├── social_navigation_planner/  # D* Lite/MPC và hai backend paper
├── social_navigation_sim/      # Robot, perception, hai cảnh Gazebo
├── scripts/                    # Kiểm tra và đóng gói bản nguồn
├── docs/                       # Minh chứng, manifest và hướng dẫn GitHub
└── README*.md                  # Hướng dẫn, nhật ký và báo cáo
```

Hai package đã đổi tên từ `astar_planner` và `ros2_omni_robot_sim`.
Build/install cũ không đi kèm bản nguồn; cần build lại bằng tên mới bên dưới.

## Tài liệu

- [Nhật ký trao đổi và chỉnh sửa](README_NHAT_KY_DU_AN.md).
- [Báo cáo tiến độ gửi giảng viên](README_BAO_CAO_TIEN_DO.md).
- [Quy trình cập nhật hai tài liệu](AGENTS.md).
- [Chuẩn bị đưa lên GitHub](docs/GITHUB_PREPARATION.md) và [giấy phép](LICENSES.md).
- [D* Lite, MPC và đội hình](social_navigation_sim/README_DSTAR_MPC.md).
- [Môi trường tĩnh](social_navigation_sim/README_SOCIAL_STATIC.md) và
  [môi trường động](social_navigation_sim/README_SOCIAL_DYNAMIC.md).
- [Paper1](README_PAPER1_GWO_WOA.md) và [Paper2](README_PAPER2_APF_MPC.md): triển khai thích
  nghi đã có kiểm thử; chưa có benchmark kết luận tốt hơn baseline.

## Thành phần được giữ

| Thành phần | Nội dung |
|---|---|
| `social_navigation_planner` | D* Lite + ba MPC, đội hình, hai backend paper, test hồi quy |
| `social_navigation_sim` | Ba robot `3w_v2_multi`, cảm biến, perception, vùng xã hội, Gazebo và RViz |
| Tĩnh | `social_static`: nhóm trò chuyện, người đứng và người xem TV |
| Động | `social_dynamic`: thêm người nằm, rời TV đi bình nước và tuần tra |

Các scene cũ `maze1`, `maze2`, `my_maze`, `social_rescue`/`rooms`, demo một
robot và package A*/PID cũ đã được gỡ ngày 28/10/2026. Hình học `my_maze`
chỉ còn làm fixture cho test hồi quy, không được cài làm môi trường chạy.
Danh mục: [manifest tinh gọn](docs/cleanup_2026-10-28.json).

## Build

Chạy từ thư mục repository, trên máy đã có phụ thuộc ROS/Gazebo:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export ROS_DOMAIN_ID=31
```

`BUILD_TESTING=OFF` bỏ bước tìm ament lint khi build trên máy hiện tại;
không thay thế việc chạy regression test Python.

## Chạy

Chọn một lệnh cho mỗi lượt mô phỏng:

```bash
# Thuật toán của dự án, môi trường tĩnh
ros2 launch social_navigation_sim social_static.launch.py

# Thuật toán của dự án, môi trường động
ros2 launch social_navigation_sim social_dynamic.launch.py

# Hai backend paper; mặc định môi trường tĩnh
ros2 launch social_navigation_sim paper1_gwo_woa.launch.py
ros2 launch social_navigation_sim paper2_apf_mpc.launch.py
```

Paper1/Paper2 hỗ trợ môi trường động bằng `social_scene:=dynamic`.
`social_navigation.launch.py` là launch dùng chung, nhận
`social_scene:=static|dynamic` và `navigation_backend:=baseline|paper1|paper2`.
`dstar_mpc.launch.py` và `three_robot_sim.launch.py` là các
launch nền còn được giữ; mặc định đã chuyển sang `social_static`.

Tên file được chuẩn hóa ngày 28/10/2026; xem
[bảng tên cũ → mới](docs/rename_2026-10-28.json) và
[đợt đổi tên package](docs/github_cleanup_2026-10-28.json). Executable
console và topic điều khiển giữ nguyên; package ROS dùng tên mới ở trên.

`build/`, `install/`, `log/` và cache là dữ liệu sinh ra, đã thêm vào
`.gitignore`; các đường dẫn đã được Git theo dõi từ snapshot cũ vẫn hiện
trong diff cho đến khi thay đổi được commit. Không chỉnh sửa mã trong đó.
`install/` được tạo lại bởi build và vẫn cần khi chạy ROS.

## Bản nguồn GitHub

```bash
python3 scripts/prepare_github.py
python3 scripts/prepare_github.py --output /tmp/three-robot-rescue-github.zip
```

Chỉ đóng gói nguồn/tài nguyên/tài liệu; không đưa build, install, log,
cấu hình cá nhân hoặc thư mục agent/tài khoản vào ZIP. Sau kiểm chứng,
output build được dọn khỏi cây làm việc.

Giữ thông tin tác giả và giấy phép riêng của model/package; xem `LICENSES.md`.
