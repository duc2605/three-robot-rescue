# NK-090 — Vì sao không trở về goal sau né — 02/11/2026

## Phiên được đọc

`recordings/dynamic_20261102_173439_286642343`, baseline, goal do người dùng
chọn `(1.0355337858, -1.9560085535)`, epoch0. Phạm vi kết luận đến106.245s.
Hash controller ghi trong diagnostics_config khớp nguồn hiện hành. Không
mở/dừng mô phỏng, không đổi goal/code và không chạy test/build.

## Nguyên nhân trực tiếp xác định được

Coordinator log lặp `Goal lacks obstacle clearance; choose a free goal.`.
Trong `plan()` kiểm goal diễn ra trước tạo D* route; thất bại thì return.
Khi không còn convoy/structure/maneuver, publish_reference gửi mảng rỗng.
Sau né, reference không được phục hồi vì điều kiện goal vẫn bị loại.

Tại106.245s: coordinator `observation_active=false`,
`moving_safety_active=false`, `replan_required=true`, `reference_rows=0`.
Cả3 controller giữ lệnh0 vì reference rỗng/cũ. Robot3 tại106.235s có tuổi
state0.037s, scan0.035s nhưng reference1.734s, reason watchdog_wall_freshness.
Do đó cảnh báo freshness cuối này không chứng minh LiDAR/camera xử lý chậm;
đường tham chiếu thiếu từ phía coordinator. Leader còn cách goal2.047m.

## Lớp chặn goal

Bản đồ vật lý hiện hành cho khoảng cách từ goal tới ô occupied gần nhất
khoảng1.052m. Đường viền viewing_tv ở90–100s cách goal0.146m; contour
color_attention ở105–106s cách0.137m. Nhỏ hơn biên planning0.18m, phù hợp
việc vùng xã hội cộng khoảng hở làm goal bị loại dù nhìn trên RViz có vẻ
nằm ngoài viền. Đầu ra cuối có color_regions1 và tv_regions0, không nhầm
nhãn TV với contour color_attention ở cuối phiên.

Chưa ghi raster planning map/keepout sau carve; không khẳng định chính xác
ô nào bị chặn hay loại trừ đóng góp bổ sung của dynamic layer. Cảnh báo
reject goal và chuỗi empty-reference → hold được xác nhận bằng log.
Không chứng minh nhận diện xã hội đúng về ngữ nghĩa.

## Hướng sửa cần cân nhắc — chưa triển khai

Tách trạng thái goal bị lớp xã hội chặn tạm khỏi goal nằm trong vật cản
vật lý; giữ nguyên goal người dùng và báo rõ nguyên nhân. Chọn vị trí chờ/
tiếp cận an toàn ngoài vùng rồi lập lại đường khi lớp chặn hết; không tự
xóa keepout hoặc bỏ biên an toàn chỉ để đi tới goal. Cần kiểm riêng mask/
persistence để biết vùng có thực sự hết hoạt động chưa. Đây là sửa phục
hồi đường sau né, không kết luận phải đổi thuật toán né đang có.

## Minh chứng và backup

- [analysis.json](analysis.json): số liệu và giới hạn.
- [latest_decisions.json](latest_decisions.json): mẫu cuối coordinator/3xe.
- [goal_clearance_warnings.log](goal_clearance_warnings.log): cảnh báo planner.
- [social_regions.json](social_regions.json): contour quanh mốc90–106s.
- Goal và hash cấu hình gốc được sao chép trong thư mục này.

Backup trước cập nhật tài liệu:
`backups/20261102_175016_860682_nk090_audit_goal_blocked_after_escape/`;
script đã xác minh archive đọc được, SHA-256 nguồn và manifest. Theo yêu
cầu chỉ giữ2 bản đầu/cuối, giữ bản đầu01/11 và bản cuối mới này, xóa bản
cuối NK089 sau khi bản mới xác minh xong. Không xóa recordings/log runtime.
Không push.
