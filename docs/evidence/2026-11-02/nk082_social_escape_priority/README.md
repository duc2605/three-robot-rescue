# NK-082 — Ưu tiên né ngoài vùng xã hội

### NK-082 — 02/11/2026 — Ưu tiên né ngoài vùng xã hội

Theo yêu cầu người dùng, sửa `dstar_mpc_controller.py`: A* tìm trên planning
map trước (8ms trong tổng ngân sách A*15ms); không tìm thấy thì thử lối vật
lý trong ngân sách còn lại. MPC xếp quỹ đạo đã qua hard checks theo ưu tiên:
không xuyên planning keepout → endpoint ngoài vùng → ít bước xuyên vùng →
điểm né cũ. Xe đang trong vùng có thể thoát; không cấm tuyệt đối lối khẩn cấp.
Không thay ngưỡng vật lý/LiDAR/peer hay bỏ kiểm tra vận tốc/horizon NK-081.

Backup trước sửa: `backups/20261102_161459_438064_nk082_social_escape_priority/`;
script xác minh archive/SHA-256 nguồn và manifest thành công; phạm vi nguồn,
assets, cấu hình, test, tài liệu; không gồm build/log/credentials.

40 test qua gồm test mất fit/corridor/moving safety và 4 test mới
`test_social_escape_priority.py`. Lần thu thập test đầu lỗi tên class import,
đã sửa và chạy thành công. Không chạy Gazebo mới, không benchmark hiệu năng;
không tuyên bố hết va chạm. Kết quả NK-081 vẫn là bản thử không đạt.

Giới hạn: ưu tiên trong các ứng viên kiểm tra được dưới ngân sách thời gian,
không chứng minh hết mọi đường ngoài vùng. Dùng planning map hiện hành (sau
carve escape), không phải toàn bộ contour marker. Chưa có cơ chế chuyên biệt
đưa xe ra khỏi vùng sau khi threat hết ngoài normal tracking về goal.
Không commit/push. Minh chứng: `docs/evidence/2026-11-02/nk082_social_escape_priority/`.


Test log: [tests.log](tests.log). Không chạy mô phỏng mới.
