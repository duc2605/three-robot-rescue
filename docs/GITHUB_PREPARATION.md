# Bản nguồn chuẩn bị đưa lên GitHub

Hai package hiện hành là `social_navigation_planner` và
`social_navigation_sim`. Chạy lệnh từ thư mục gốc repository.

## Kiểm tra và đóng gói

```bash
python3 scripts/prepare_github.py
python3 scripts/prepare_github.py --output /tmp/three-robot-rescue-github.zip
```

ZIP chỉ chứa hai package, `docs/`, `scripts/`, README/quy trình/giấy phép
và `.gitignore`. Không chứa `.git`, output build, log, cache, cài đặt editor
hoặc thư mục tài khoản/agent. ZIP là bản nguồn; cần build trước khi chạy ROS.
Trọng số và model đang dùng được giữ vì pipeline cần chúng.

Script kiểm tra tên package, cú pháp Python, kích thước file dưới 100 MiB
và một số mẫu private key/AWS/GitHub token; đây không phải kiểm toán bí mật
đầy đủ. Xem [giấy phép từng phần](../LICENSES.md) trước khi cấp phép tái sử dụng.

## Chuẩn bị commit trong repository hiện tại

Snapshot cũ từng theo dõi `build/`, `install/`, `log/` và cấu hình cá nhân.
`.gitignore` không tự xóa những file đã theo dõi. Đợt làm sạch đã xóa chúng
khỏi cây làm việc; cần ghi nhận cả các đường dẫn bị xóa trong commit:

```bash
git status --short
git add -A
git diff --cached --stat
git diff --cached --name-only
```

Kiểm tra danh sách trước khi commit/push. Tránh chỉ thêm hai thư mục nguồn
mà bỏ các deletion của snapshot cũ. Sau này build lại sẽ tạo output cục bộ,
nhưng output đó được ignore sau khi commit xóa bản snapshot đã theo dõi.

Đích đồng bộ là `https://github.com/duc2605/three-robot-rescue.git`, nhánh
`main`. Cập nhật bằng commit nối tiếp lịch sử remote, không force-push.
Commit làm sạch không xóa các blob cũ khỏi lịch sử. Nếu khởi tạo repository
mới hoàn toàn, có thể lấy bản ZIP nguồn thay vì sao chép `.git` cũ.

`.agents`, `.codex`, `.aws` có thể còn xuất hiện trên máy vì do môi trường
quản lý ở chế độ chỉ đọc. Chúng đã được ignore và không nằm trong ZIP nguồn.
