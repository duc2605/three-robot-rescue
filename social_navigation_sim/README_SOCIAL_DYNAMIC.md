# Môi trường động — chạy và kiểm tra

## Chạy

Build trước theo [README gốc](../README.md), sau đó chạy từ thư mục gốc:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=31
recording_dir="recordings/dynamic_$(date +%Y%m%d_%H%M%S_%N)"
bash scripts/run_simulation.sh dynamic --diagnose-stop "$recording_dir"
# Sau khi dừng mô phỏng bằng Ctrl+C, xem bản vừa ghi:
python3 scripts/view_replay.py --session "$recording_dir"
```

Hoặc `bash scripts/run_dynamic.sh` để chạy profile LiDAR2m, tự ghi mỗi lượt vào thư mục mới; xem
[hướng dẫn](../docs/CHAN_DOAN_PHIEN_CHAY.md). Chọn 2D Goal Pose trong RViz. Chỉ mở một phiên.
Từ NK-071, profile động mặc định dùng LiDAR2m/10Hz, tắt camera/perception/
quan sát và social map từ camera để kiểm né vật động. Đây là sửa mới từ
baseline khôi phục, khác profile LiDAR-only thử nghiệm cũ đã loại ở NK-060.
Xem [thiết kế và giới hạn](../docs/LIDAR_2M_AVOIDANCE.md).


Nguồn hiện hành tới NK-084; xem bàn giao đầu nhật ký. NK-034 là mốc
lịch sử tái dựng. NK-083 đã ghi nhận contact; NK-084 chưa thử Gazebo.


## Ba tình huống

- Người nằm tại giường: tư thế nằm trong kịch bản không chứng minh đang ngủ.
- Người xem TV: xem12 giây mô phỏng, chuyển tư thế rồi đi bình nước với
  tốc độ .35m/s, dừng theo lịch và quay lại. Chu kỳ mặc định khoảng106.7s.
- Người tuần tra: đi theo tuyến định sẵn với tốc độ .4m/s, chu kỳ khoảng107.2s.

Tuyến chuyển động dùng tốc độ từng đoạn và quay tại góc theo
`scenario_motion.py`/`social_scenario_motion.cpp`. Hoạt ảnh bước chân và
cơ chế cải tiến hành vi sau NK-034 không nằm trong bản khôi phục.
Lịch/pose kịch bản chỉ dùng mô phỏng và đánh giá, không cấp cho navigation
như kết quả camera. Bản đồ vật lý chứa giường/TV/ghế/bình nước; tránh giường
không chứng minh nhận diện người nằm.

## Cảm biến và điều khiển

D* Lite cấp tuyến cho leader, coordinator tạo đội hình, ba MPC kiểm lệnh
riêng. Nhánh né dùng vận tốc đo và A* trái/phải/sau, không dùng lịch người.
Nguồn cũ chưa có provisional2 mẫu, cooperative hint, inbox đa luồng, clock
compact hoặc deadline milliseconds của các thử nghiệm sau này.

Bản ghi hiện tại có contact physics như minh chứng NK-083; đối chiếu
contact theo đúng phiên. Không dùng chồng lấn hình học thay cho contact.

## Sinh lại cảnh

```bash
python3 social_navigation_sim/scripts/generate_social_dynamic_world.py
```

Trước khi thay generator, world, thuật toán hoặc tài liệu, tạo backup theo
[quy trình](../docs/BACKUP_VA_KHOI_PHUC.md). Các mốc cũ vẫn được giữ trong
[nhật ký](../README_NHAT_KY_DU_AN.md); không phải Git release/tag.


## File cần đọc khi kiểm tra lỗi

Dùng bảng [file tối thiểu theo tác vụ](../docs/FILE_CAN_DOC_VA_LENH_CHAY.md).
Mô tả baseline NK-034 ở trên là lịch sử; hiện đã có các sửa NK-071–084 và
contact physics trong bản ghi NK-083. Nguồn/trạng thái kiểm chứng mới nhất
ở đầu nhật ký. Người dùng tự chạy các lệnh; AI không tự chạy mô phỏng.
