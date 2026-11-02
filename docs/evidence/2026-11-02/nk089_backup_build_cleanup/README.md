# NK-089 — Dọn backup và đầu ra build — 02/11/2026

Theo yêu cầu người dùng, đã xóa47 thư mục backup trung gian (gồm một bản
không có manifest), giữ đúng hai snapshot:

- `backups/20261101_185410_before_nk034_restore/` — đầu tiên.
- `backups/20261102_173137_174092_nk089_final_before_backup_build_cleanup/` — nguồn hiện tại trước dọn.

Bản đầu đã đối chiếu SHA-256 archive và585 file với manifest thành công.
Bản cuối được script create_backup xác minh archive đọc được, hash nguồn
và manifest khi tạo. Không giải nén/khôi phục hoặc ghi đè nguồn. Các đường
backup trung gian trong nhật ký cũ nay là tham chiếu lịch sử đã được người
dùng cho phép xóa; không sửa lịch sử để che việc này.

Đã xóa `build/`, `install/` và66 mục log build. Giữ nguyên bản ghi trong
`recordings/`, log chẩn đoán, docs/evidence, mã nguồn và Git history/refs.
Cần build lại theo README trước lần chạy kế tiếp; chưa tự build/test/mở
mô phỏng. Không push. Kết quả chi tiết: [cleanup.json](cleanup.json).

Tác vụ dọn dữ liệu vận hành, báo cáo kỹ thuật giữ nguyên.
