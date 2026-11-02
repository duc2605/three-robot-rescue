# NK-087 — Tích hợp 10 prototype ba tầng — 02/11/2026

## Người dùng tự build/test/chạy

Xem [danh mục và lệnh đầy đủ](../../../../README_PAPERS_03_12.md).
Không build, không chạy pytest/ROS/Gazebo trong tác vụ này. Không commit/push.

## Nguồn và phạm vi

Người dùng cung cấp [cuộc trao đổi chia sẻ](https://chatgpt.com/share/6ae85d47-5250-83ec-80a5-0b07b13a65e6).
Payload công khai chứa generator bản ba tầng, khác bộ compute một hàm ở
phiên đầu. Chỉ trích các literal METHODS/COMMON/F/T/C/PIPE bằng AST;
không chạy generator, installer, shell hay lệnh trong trang. Không tải được
ZIP sandbox của phiên khác; không mô tả nguồn trích là ZIP chính thức.
`provenance.json` lưu hash generator và module lúc trích;
`method_catalog.json` giữ danh mục; `static_checks.json` giữ hash nguồn cuối.

Danh sách method01–10 ánh xạ paper3–12 để tránh trùng hai paper cũ. Mỗi method
có formation/trajectory/control/pipeline; math/memory và adapter dùng chung.
Các module từ nguồn chia sẻ được đổi import common và bổ sung guard đầu vào.

Adapter mới kế thừa dữ liệu và safety/escape NK084, đổi chỉ số leader về
quy ước2 của prototype. Normal tracking gọi pipeline và kiểm toàn horizon;
không quay sang beam tracking baseline khi quỹ đạo bị loại. Chỉ commit
memory bước đầu sau khi lệnh được chấp nhận phát. Hạ tầng D* coordinator,
LiDAR2m/camera/social map/peer/freshness/gia tốc vẫn dùng chung, không là
phép so sánh thuần thuật toán bài báo. Shared escape vẫn có giới hạn NK083.

Launch choices compare01–10 chọn executable comparison thay distributed MPC;
coordinator vẫn D*. Hai paper cũ không đổi thuật toán. Launch/helper/script
được thêm vào các package hiện có, không thêm dependency/model. Recorder
opt-in giữ scene/method và hash đúng module method; không tự ghi mọi lần.

## Kiểm tra đã thực hiện

- Phân tích cú pháp AST các file Python mới và hai launch sửa/setup.
- Đối chiếu đường dẫn import nội bộ,10 method/10 wrapper, choices backend.
- `bash -n` cho hai script và khối lệnh trong README; không thực thi lệnh.
- Kiểm liên kết nội bộ tài liệu và `git diff --check`.
- Đã viết `test_comparison_methods.py` và `test_comparison_adapter.py` để
  người dùng chạy sau build; **chưa chạy**, không báo số test đạt.
- **Chưa build/ROS/Gazebo**, chưa kiểm số publisher thật hoặc hiệu quả né.
  `check_static.py` là kiểm cấu trúc, không thay kiểm chứng runtime.

## Giới hạn

Đây là prototype/xấp xỉ theo bản ba tầng trong hội thoại. CTC chưa điều khiển
mô-men; visual servoing dùng pose proxy; slip/observer xấp xỉ; car-like là
ràng buộc vận tốc trên omni; DEFORM-inspired không là port mã tác giả.
Một mục kết hợp nhiều nghiên cứu. DOI/tác giả/phương trình toàn bộ danh sách
chưa xác minh đầy đủ, không trình bày như tái lập10 bài báo. Không gán kết
quả30/60 test của hội thoại hoặc contact NK078/NK083 thành kết quả bộ mới.

## Backup

`backups/20261102_165433_691056_nk087_ten_three_stage_comparison_backends/`:
script đã kiểm archive đọc được, SHA-256 nguồn và manifest trước sửa.
Phạm vi nguồn/assets/cấu hình/test/tài liệu; không credentials/build/log.

## Bước tiếp theo

Người dùng build rồi chạy test theo README. Khi thử mô phỏng, chỉ mở một
method mỗi lượt, kiểm `/comparison/robot3/status` và số publisher cmd_vel,
ghi vào thư mục mới nếu cần audit. Chưa đề xuất kết luận benchmark.
