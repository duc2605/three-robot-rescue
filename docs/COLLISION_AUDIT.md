# Đo tiếp xúc vật lý trong Gazebo

Bộ đo đọc `ContactSensorData` do physics Gazebo sinh ra. Nó không suy va
chạm từ khoảng cách tâm, marker xã hội hay kết quả camera; không phát lệnh
điều khiển và không làm người nhường robot.

Collision hình học đã có trước bản này. Bản mới bổ sung bộ ghi tiếp xúc,
không thay kích thước người/robot hoặc luật tránh đường.

## Dùng khi chạy mô phỏng

Các launch xã hội tĩnh/động tự bật bộ đo trong chế độ simulation, kể cả
`lidar_only_dynamic.launch.py`. Khởi động theo hướng dẫn hiện hành sau khi
chủ động kết thúc phiên cũ. Không cần bật camera để đo contact.

- `/collision_audit/events`: JSON trong `std_msgs/String`; sự kiện
  `contact_begin`, `contact_update`, `contact_end`, `contact_reset`.
- `/collision_audit/status`: session/epoch, pause, số collision được theo dõi,
  độ đầy đủ cấu hình và đã quan sát bước physics hay chưa.
- `/collision_audit/markers`: điểm chạm màu đỏ và nhãn cặp model; display
  **Physics Contacts** có sẵn trong cấu hình RViz cho lượt chạy mới.
- `log/collision_events.jsonl`: ghi append các bắt đầu/kết thúc/reset, status
  khi đổi trạng thái và update đầu tiên nếu recorder tham gia giữa contact.
  Đường dẫn mặc định theo thư mục chạy; script chạy dự án đã `cd` về repo.

```bash
ros2 topic echo /collision_audit/events
ros2 topic echo /collision_audit/status
# Khi chạy script với ROS_DOMAIN_ID=32, dùng cùng domain ở terminal đọc.
tail -f log/collision_events.jsonl
```

Có thể đổi nơi ghi bằng launch argument `collision_log:=/duong/dan/events.jsonl`.
Log gồm thời gian thực UTC, thời gian mô phỏng, session/epoch, tên hai model,
collision cụ thể, tối đa 8 điểm tiếp xúc, thời gian bắt đầu/kết thúc và số
mẫu physics có tiếp xúc. `physics_samples` không phải số lần va chạm độc lập.
Các update liên tiếp không tăng số sự kiện bắt đầu. Điểm chạm không còn sẽ
được xóa khỏi marker. Reset không nối nhầm contact giữa hai epoch.

Khi mới nạp lúc pause, `physics_sample_received=false`: chưa được xem là
đã kiểm chứng không va chạm. `coverage_complete=false` báo thiếu model/
collision cấu hình, không phải trạng thái an toàn.

## Phạm vi và giới hạn

Tất cả collision proxy của người được theo dõi nên contact với thân,
camera, bánh/roller của robot có thể được ghi. Thân/camera/bánh chính của
robot cũng được theo dõi để báo robot–robot hoặc đồ đạc; roller riêng không
được bật contact data để tránh luồng roller–sàn lớn. Vì vậy không coi đây
là đo đầy đủ mọi contact robot–robot chỉ qua roller. Tiếp xúc sàn thường
và self-contact cùng model được bỏ khỏi sự kiện va chạm.

Actor có hoạt ảnh là phần hiển thị, contact dùng collision proxy. Va quệt
nhìn thấy giữa mesh/áo/tay và robot có thể khác contact của proxy. Không
đổi proxy hay dùng khoảng cách để tạo contact giả. Backend hiện cung cấp
điểm chạm; chưa đo lực va chạm hoặc độ xuyên bằng pipeline này.

Số bắt đầu đếm theo cặp model vật lý, không phải số người độc nhất: viewer
đổi proxy khi chuyển giai đoạn có thể tạo cặp mới. Hai contact có khoảng
ngắt physics thật được ghi thành hai đợt; không tự gộp để làm đẹp số liệu.
Thêm đo contact có chi phí truy vấn physics; chưa có benchmark overhead.

## Kiểm chứng

[Fixture nguồn](../social_navigation_sim/test/contact_fixtures/contact.sdf)
cho người tiến vào robot rồi rời đi trong world riêng, không dùng camera
hoặc controller né. Đã chạy physics cho robot1/2/3: mỗi ca có begin và end;
ca đi lệch 1 m không có contact. Fixture dùng thân robot đơn giản, không
thay thế replay toàn bộ URDF/leader hoặc benchmark tránh va chạm.

[Physics validation](evidence/2026-11-01/collision_audit/physics_validation.json),
[kiểm tra bridge/JSONL/marker](evidence/2026-11-01/collision_audit/wire_validation_verified.json).
Mọi thử nghiệm này ở partition riêng; không resume phiên chính.
