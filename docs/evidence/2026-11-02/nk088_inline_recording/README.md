# NK-088 — Ghi mỗi lượt trong bộ lệnh chạy — 02/11/2026

README chính và các hướng dẫn động/tĩnh/paper1–12 đã ghép tạo tên bản ghi,
chạy với --diagnose-stop và viewer vào cùng mục/bộ lệnh. Bỏ mục chạy ghi
riêng. `run_simulation.sh` chọn chế độ và gọi runner đã dùng; runner mặc
định tạo bản ghi mới bằng profile + timestamp + PID nếu không truyền tên.
Scene/backend/hash bao gồm đúng paper cũ hoặc comparison mới. Không ghi
đè thư mục cũ, không tự bật camera ở LiDAR-only. Raw ros2 launch ngoài
wrapper không được tự động ghi; không thêm observer nền/log/sessions.

Đã kiểm tĩnh3 shell script,2 embedded Python,93 khối bash tài liệu,56 ví dụ
có ghi/viewer cùng khối và các link. Xem [static_checks.json](static_checks.json).
**Không build, không chạy test, không ROS/Gazebo**, chưa đo overhead/RTF
hoặc runtime ghi/đóng file. Không đổi thuật toán điều hướng. Các giới hạn
dung lượng/queue recorder vẫn áp dụng, mức diagnostics khác giữa backend.

Backup trước sửa: `backups/20261102_170953_270249_nk088_record_every_documented_run/`;
archive đọc được/SHA-256 nguồn/manifest đã được script xác minh. Giữ lịch sử
các quyết định opt-in trước đây; nhật ký thêm quyết định NK088 thay thế.
Báo cáo kỹ thuật giữ nguyên vì đây là cập nhật vận hành. Không push.
