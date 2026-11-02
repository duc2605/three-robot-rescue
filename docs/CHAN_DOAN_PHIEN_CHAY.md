# Chạy mô phỏng và giữ bản ghi mỗi lượt

Từ yêu cầu NK-088, bộ lệnh chạy trong README đã tích hợp lưu bản chạy.
Wrapper tạo thư mục mới trong `recordings/`, không dùng lại `log/sessions`
hoặc observer/supervisor NK-061 đã gỡ. Đây là thao tác khi chạy script,
không phải dịch vụ nền giám sát mọi tiến trình ROS.

Mỗi mục động/tĩnh/paper trong [README gốc](../README.md) có đủ build,
source, tạo tên thư mục mới, chạy có ghi và xem lại sau Ctrl+C. Ví dụ sau
build dùng `bash scripts/run_simulation.sh dynamic`; tĩnh dùng `static`,
paper dùng `paper1` tới `paper12`. Các script động/comparison cũng tự ghi
khi không chỉ định đường dẫn. Terminal in đường dẫn và lệnh viewer đầy đủ.

Ghi mặc định gồm pose/contact vật lý, nguồn LiDAR/điểm né và perception khi
camera/nhận diện được bật; bộ nhớ ghi có giới hạn theo tài liệu recorder.
Không tự bật camera nếu profile tắt. Controller diagnostics tùy backend có
thể thiếu một số stream; không có event không tự chứng minh không va chạm.
Muốn đặt tên bản chạy, thêm `--diagnose-stop recordings/TEN_MOI` ngay sau
chế độ; không dùng thư mục đã tồn tại.

Dừng bằng Ctrl+C để đóng ghi. Sau đó dùng lệnh viewer in ra; xem thêm
[phát lại](PHAT_LAI_MO_PHONG.md) và [chẩn đoán](CHAN_DOAN_DUNG_XE.md).
Nếu chạy thẳng `ros2 launch` ngoài wrapper, không mặc nhiên có bản ghi.
Không thay thuật toán điều hướng hoặc khởi động mô phỏng khi chỉ đọc tài liệu.
