# NK094 — Vùng TV mất trong bản mới, 02/11/2026

Nguồn recordings/dynamic_20261102_182843_287553000, đọc perception đến130.404s.
Vùng đầu27.035s; mất28.657 rồi xuất hiện29.058. Những lần mất toàn bộ tiếp:
40.647→41.018,49.633→50.049. Cuối cùng2vùng→1 tại77.834,→0 tại80.612,
không tạo lại đến130.404. TV track vẫn1 ở cả hai mốc cuối. Đây là marker
nguồn bị gỡ, không chỉ giao diện replay ẩn.

Nguồn social_costmap.py defaults tv_view_memory75s; tick lọc cả vùng sinh
mới và cache với now-zone.stamp<75. color_attention.regions đặt stamp bằng
min(target.stamp,person.stamp,person.direction_stamp). prune xóa hướng nhìn
khi quá75s. Vì vậy cập nhật frame mới hoặc nhìn thấy người/màn hình riêng
không làm mới toàn bộ bằng chứng xem TV. Hết hạn của thành phần cũ nhất
làm vùng biến mất dù TV track vẫn được giữ.

Mốc cuối phù hợp expiry75s; không có stamp/gate từng zone trong bản ghi,
KHÔNG khẳng định đã xác minh chính xác timestamp hoặc nhánh xóa. Nhánh
contradicted còn có thể gỡ sớm khi chuyển động/đổi hướng/ghép track.
Các lần chớp tắt ngắn27–50s không thể quy hết cho TTL. Hướng nhớ giảm6→4
quanh79–80s hỗ trợ vấn đề duy trì viewer. Camera77.5–81s có9frame capture
age0.004–0.244s; coordinator frame age~0.23–0.80s trong74–81s, không thể
quy toàn bộ mất vùng cuối cho camera ngừng gửi. Search nhận từ chối do
moving safety quanh79–81s, chưa tái thu được bằng chứng đủ để dựng vùng.

Đề xuất: tách nhớ màn hình tĩnh với xác nhận hoạt động, trạng thái chưa
được quan sát lại và lý do xóa theo viewer; không tăng TTL vô hạn, không
lấy ground truth thay camera. Chưa sửa code/khởi động mô phỏng/test.
