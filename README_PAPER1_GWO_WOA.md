# Bài 1 — GWO–WOA + DWA + leader–follower, v1

Tài liệu gốc: **A Hybrid Path Planning and Formation Control Strategy of
Multi-Robots in a Dynamic Environment**, JACIII 26(3), 342–354, 2022.
DOI: https://doi.org/10.20965/jaciii.2022.p0342
PDF: https://www.fujipress.jp/main/wp-content/uploads/13-Fujipress_JACIII-26-3-8.pdf

Đây là bản triển khai độc lập, có điều chỉnh để tích hợp, không phải mã nguồn
của tác giả hoặc bản tái lập đã được xác nhận tương đương kết quả bài báo.
Gói chỉ triển khai **bài 1**, không bao gồm sáu bài còn lại.

## Đã thay gì?

| Chức năng | Chế độ PAPER1_V1 |
|---|---|
| Lập đường | GWO–WOA một chiều trong hệ tọa độ start–goal; tent initialization, ba cá thể tốt nhất, cập nhật spiral và random prey; spline tự nhiên |
| Leader | DWA lấy mẫu vận tốc tiến/quay, giới hạn gia tốc, dự đoán và kiểm tra đoạn phanh |
| Đội hình | Hai vị trí ảo sau leader 0.70 m, lệch trái/phải 0.50 m |
| Follower | Sai số theo Eq. (3), luật bám Eq. (32) của bài; giới hạn vận tốc và lọc an toàn DWA |
| Camera | Giữ node RGB-D nhận người, hướng đầu/thân, mục tiêu màu/TV và bản đồ xã hội của dự án |
| LiDAR | Giữ ba scan; đầu mút còn mới và vị trí robot được kiểm tra ở mỗi lượt điều khiển |
| D* Lite / MPC | Không tham gia lập đường/điều khiển trong chế độ paper1; không có A*/D* fallback |

File/topic có chữ `dstar` hoặc `mpc` còn được dùng làm tên tương thích RViz và
luồng đo pose/TF. Điều đó không có nghĩa chế độ paper1 đang dùng thuật toán đó.
Chỉ node coordinator của backend paper1 phát cmd_vel cho ba robot; ba node MPC
cũ bị tắt bởi điều kiện launch. Không chạy đồng thời hai lượt launch.

## Những điều chỉnh phải biết khi báo cáo

1. Robot omni chạy theo mô hình v, omega của bài (vy=0); chưa khai thác trượt
   ngang. Không khẳng định giữ được mọi tính chất của bài trên mô hình omni.
2. Trở ngại trong bài là các hình tròn. Ở đây dùng occupancy grid camera/social
   và scan đo được; kiểm tra footprint tròn quét liên tục giữa các mẫu.
3. Spline dùng natural cubic; cài thêm cá thể khởi tạo gần đường thẳng, giữ elite,
   giới hạn ngân sách tìm kiếm 2 giây/lần và thử seed kế tiếp nếu chưa tìm thấy.
   Số cá thể/vòng lặp giảm cho thử tương tác. **GWO_SEARCH_FAILED không chứng minh
   không tồn tại đường**. Dạng tìm kiếm 1D không diễn tả được mọi đường cần đi lùi
   theo trục start–goal, ví dụ một số bẫy chữ U.
4. Eq. (32) giữ nguyên công thức, nhưng bị giới hạn lệnh theo khả năng robot.
   DWA được thêm làm lọc an toàn cho follower khi lệnh Eq32 không hợp lệ. Khi
   leader dừng, dùng DWA phục hồi vị trí follower; Eq32 riêng không sửa được
   sai lệch ngang ở v_ref=0. Leader giảm tốc nếu follower lệch quá 0.5 m.
5. DWA có thêm hạng tiến gần đích để giảm xoay tại chỗ; trọng số, lookahead,
   horizon và gia tốc là cấu hình tích hợp, chưa được hiệu chuẩn theo bài.
   Cửa sổ vận tốc dùng lệnh trước làm xấp xỉ trạng thái vận tốc; cần đo sai lệch
   lệnh/đo thực khi đánh giá khả năng phanh trong Gazebo.
6. LiDAR giữ các điểm đo mới như vật cản đứng yên trong horizon ngắn. Chưa có
   dự báo vận tốc người hoặc bảo đảm tránh mọi người di chuyển ngoài góc nhìn.
7. Tạm tắt **tự quay quan sát** để không chạy bộ điều phối nhiệm vụ riêng của
   bản MPC. Camera và vùng xã hội vẫn cập nhật khi xe di chuyển; không xóa
   vùng cấm để ép xe đi. Chưa có cơ chế đổi tam giác sang hàng dọc.
8. Pose nhóm được lấy từ Gazebo như bản nền; đây chưa phải bài thử định vị thực.

## Cài đặt

Dừng mô phỏng cũ bằng Ctrl+C, rồi:

```bash
cd ~/three-robot-rescue
source /opt/ros/humble/setup.bash
sudo apt install -y python3-numpy ros-humble-gz-ros2-control ros-humble-ros2-controllers
CMAKE_BUILD_PARALLEL_LEVEL=1 colcon build --symlink-install \
  --packages-select social_navigation_planner social_navigation_sim --executor sequential
source install/setup.bash
export ROS_DOMAIN_ID=31
export QT_QPA_PLATFORM=xcb
ros2 launch social_navigation_sim paper1_gwo_woa.launch.py
```

Mã paper đã tích hợp trong repository; build trực tiếp, không cần installer cũ.

Trong RViz chọn 2D Goal Pose. Lần đầu chọn đích gần, ở phía trước robot3 và
ngoài mọi vùng cấm. Nếu bị vùng xã hội chặn, trạng thái báo rõ và xe dừng.

## Theo dõi

Terminal khác:

```bash
source /opt/ros/humble/setup.bash
source ~/three-robot-rescue/install/setup.bash
export ROS_DOMAIN_ID=31
ros2 topic echo /paper1/status
```

- `backend: PAPER1_V1` xác nhận backend.
- `PLANNING_GWO_WOA`: đang tối ưu nền; ba robot dừng.
- `WAIT_RETRY_GWO_WOA`: chưa có đường hợp lệ, chờ thử lại.
- `WAIT_FRESH_LIDAR`, `WAIT_MAP_OR_FRESH_POSES`: thiếu dữ liệu đủ mới, dừng.
- `TRACKING`: DWA cho leader, Eq32 hoặc DWA safety filter cho follower.
- `GOAL_BLOCKED_IN_CURRENT_MAP`: đích bị bản đồ hiện tại chặn.
- `GOAL_REACHED`: leader trong 0.12 m, hai follower trong 0.18 m.
- `NO_SAFE_COMMAND` trong trạng thái điều khiển: không có lệnh ứng viên an toàn.

`formation_error_m` theo thứ tự robot1, robot2, robot3. Hai follower là sai số
so với vị trí ảo; phần tử leader là khoảng cách đến goal, không phải sai số
bám ngang đường. `travelled_m` là quãng đường đo từ pose sau khi đặt goal;
`goal_elapsed_sim_s`, `goal_reached_sim_s` dùng thời gian mô phỏng.
Đây chưa phải bộ benchmark đầy đủ (chưa có thống kê va chạm/RTF/RMSE theo lô).

## Trở lại bản nền

Ctrl+C lượt paper1, rồi chạy launch cũ:

```bash
ros2 launch social_navigation_sim social_navigation.launch.py \
  navigation_backend:=baseline social_scene:=static leader_robot:=robot3 \
  person_input_size:=416 person_confidence:=0.25
```

Không cần gỡ file paper1 để chạy bản nền. Nếu muốn khôi phục file hoàn toàn,
dùng đường dẫn BACKUP mà installer in ra:

```bash
python3 ~/Downloads/paper1-gwo-woa-v1/install.py ~/three-robot-rescue \
  --restore /duong/dan/BACKUP
```

Sau khôi phục build lại hai package. Restore từ chối nếu bạn đã sửa file sau
khi cài nhằm tránh làm mất công việc mới.

## Kiểm thử đã làm

11 test số chạy bằng unittest: spline, đường trống, vòng vật cản, bản đồ bị
chia cắt, goal bị chặn, hội tụ Eq32 trên tham chiếu đi thẳng, vị trí ảo quay
theo leader, va chạm hai robot giữa mẫu, cửa sổ DWA/phanh, LiDAR/peer loại
lệnh Eq32 và DWA đi tới goal. Có kiểm tra cú pháp Python và diff whitespace.

Thử tích hợp động học offline ba robot đi thẳng: 106 bước x 0.1 s, leader cách
đích 0.1186 m, hai follower lệch khoảng 0.0062 m. Đây là mô hình lý tưởng,
không có trượt bánh, trễ cảm biến, vật cản hoặc tải Gazebo; **không dùng làm
kết quả thực nghiệm của bài báo**. Eq32 ở v_ref=0.1 m/s hội tụ ngang chậm;
test hội tụ chạy 300 giây mô phỏng, không phải cam kết hội tụ nhanh.

Chưa chạy colcon/ROS/Gazebo ở môi trường tạo gói vì không có ROS cài sẵn.
Phiên chạy trên máy người dùng là bước kiểm chứng tích hợp tiếp theo.

Chạy lại test số:

```bash
cd ~/three-robot-rescue
PYTHONPATH=social_navigation_planner python3 -m unittest discover \
  -s social_navigation_planner/test -p test_paper1_gwo_woa.py -v
```
