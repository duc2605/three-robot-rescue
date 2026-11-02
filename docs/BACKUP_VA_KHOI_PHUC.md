# Sao lưu trước khi cải tiến

Theo yêu cầu từ NK-060, tạo snapshot trước thay đổi đầu tiên của mỗi tác vụ:

```bash
python3 scripts/create_backup.py --reason truoc_ten_cai_tien
```

Kết quả trong `backups/<ngay_gio_Viet_Nam>_<ly_do>/` gồm `source.tar.gz`,
`manifest.json` (SHA-256 từng file và archive), `git-status.txt`. Có cả file
chưa commit, nguồn, model/mesh, cấu hình, test và tài liệu. Không gồm `.git`,
credentials/cấu hình riêng, build/install/log/cache hoặc các backup khác.
Symlink được giữ dưới dạng link; dữ liệu đích bên ngoài không được chép vào.
Không xóa backup cũ; thư mục này không được colcon build hoặc push mặc định.

Kiểm tra lại trước khi sử dụng:

```bash
python3 scripts/create_backup.py --verify backups/TEN_THU_MUC
```

Lệnh verify chỉ đọc archive, không ghi đè dự án. Khi khôi phục, tạo một
backup mới của trạng thái hiện tại, giải nén bản cần phục hồi vào một thư
mục riêng, đối chiếu manifest và danh sách file rồi mới thay nguồn. Build
lại từ nguồn đã phục hồi; giữ lịch sử hai README thay vì ghi đè nhật ký.
Không chạy lẫn node/ thư viện Gazebo của hai phiên bản.

Quy trình được thực hiện bởi người/AI sửa dự án theo AGENTS.md. Đây không
phải dịch vụ tự theo dõi và sao lưu mọi thao tác editor ở nền.
