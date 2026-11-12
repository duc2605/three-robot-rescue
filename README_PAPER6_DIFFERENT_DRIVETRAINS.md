# Paper6 — Formation Control with Different Drivetrains (NK121)

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
recording_dir="recordings/paper6_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh paper6 --diagnose-stop "$recording_dir" social_scene:=dynamic
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
recording_dir="recordings/paper6_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh paper6 --diagnose-stop "$recording_dir" social_scene:=static
# Chọn 2D Goal Pose trong RViz. Sau Ctrl+C, xem đúng lượt vừa chạy:
python3 scripts/view_replay.py --session "$recording_dir"
```

## 3. Nguồn, ba phần thuật toán và chuyển đổi

Nguồn: [Fangtnw/Formation-Control-of-the-Mobile-Robot-with-Different-Drivetrains](https://github.com/Fangtnw/Formation-Control-of-the-Mobile-Robot-with-Different-Drivetrains), commit `5b3912443cdae2aff31897816c2641fc0d7fb593`. README tự mô tả là đồ án bậc cử nhân ROS2 Humble cho2robot phối hợp vận chuyển. Chưa xác minh bài báo/DOI; **Paper6 là số chế độ dự án**, không phải tuyên bố đây là bài báo đã phản biện.

- **Điều khiển:** động học mecanum/omni, luật feedforward chuyển động cứng và feedback sai số trong hệ thân follower, gain vị trí1/.2 và yaw1 theo nhánh mecanum nguồn.
- **Bám đội hình:** mở rộng2xe thành leader+2follower ở slotV0.7m×0.5m. Vận tốc slot tính `vL + wL×R(thetaL)offset`; đã đổi dấu/hệ tọa độ để phù hợp xe cùng hướng, khác cấu hình pallet đối diện trong nguồn.
- **Bám quỹ đạo:** Hybrid A* trong SE(2) dùng primitive xe đạp thuận/lùi, sau đó Pure Pursuit. Mã tự triển khai theo cấu trúc nguồn; chưa port Reeds–Shepp analytic expansion, chi phí đổi lái cực lớn hoặc footprint chữ nhật dài chở pallet.
- Hybrid grid16cm/15°, primitive32cm kiểm mỗi4cm; wheelbase0.5m, lái±20°; tối đa8000expansion/0.3s wall, sai số XY kết thúc12cm. Hết budget trả thiếu đường và giữ, không âm thầm chuyển sang A*baseline.
- Leader giới hạn0.2m/s, follower0.28m/s. Quay yaw follower khi sai số vị trí<20cm. Cả3vẫn có veto vật lý/xã hội/LiDAR chung.

**Đầu vào định vị chuyển đổi:** dùng pose robot hiện có để tính tương đối. Không dùng ArUco ở follower và không được gọi kết quả này là nhận diện ArUco. Camera leader tiếp tục nhận diện xã hội. Mecanum4bánh được đổi sang Twist cho omni3bánh, không chạy motor/wheel hardware code của tác giả.

Mã: `paper_models/drivetrains.py`. Chưa build/test/Gazebo, chưa xác nhận robot qua được mọi hành lang hoặc giữV trong chuyển hướng. Hybrid A* giới hạn hình học leader; không lập kế hoạch cho toàn pallet/đội cùng một thân cứng.

## Kiểm chứng và bản ghi

Đã viết code, regression và kiểm tra cấu trúc; **chưa build/pytest/Gazebo** trong tác vụ. Người dùng tự chạy theo khối lệnh phía trên. Bản ghi vẫn có camera/vùng xã hội, nguồn upstream/commit và reason của từngxe trong `navigation.jsonl` → `decision.search`. Xem `diagnostics_config.json` để xác định module/nguồn đã nạp.

D*+MPC gốc và Paper1/2 giữ thuật toán hiện có. Các chế độ so sánh dùng node độc lập; map xã hội/camera và lớp veto chung có thể giữ xe. Phanh không chứng minh người không tiếp tục đi vào robot đang đứng. Không khẳng định phương pháp mới tốt hơn baseline trước benchmark cùng điều kiện.

Cập nhật NK185 dùng lớp cảm biến, phân loại LiDAR, giới hạn vận tốc,
an toàn và camera quan sát chung cho các paper. Thông số và giới hạn kiểm
chứng xem mục “Hành vi chung” trong README gốc. Chính sách điều khiển và
đội hình của bài được mô tả ở các mục trên. Chưa chạy thử NK185.
