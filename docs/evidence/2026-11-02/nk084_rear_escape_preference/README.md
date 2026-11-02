# Ưu tiên điểm né sau xe

### NK-084 — 02/11/2026 — Ưu tiên vùng trống phía sau xe khi né

Người dùng yêu cầu chọn điểm né đằng sau xe. Quy ước phía sau theo yaw
thân xe hiện tại, nón±45 độ và lùi hơn8cm; không theo hướng nhìn camera
hay hướng chuyển động người. A* xét connector sau trước, cộng penalty
cho endpoint ngoài nón sau. MPC xét hướng lùi chính xác sớm và ưu tiên
endpoint phía sau có holding_safe, sau ưu tiên vùng xã hội NK082, trước
điểm tiện lợi cũ. Nếu sau bị chắn/người tới/xe khác hoặc không an toàn để
dừng thì vẫn xét hai bên. Không bỏ kiểm tra vật lý/LiDAR/peer/corridor/
full horizon/gia tốc. Không đảm bảo mọi tick tìm được đường sau.

Sửa `dstar_mpc_controller.py`, `local_escape.py`; thêm
`test_rear_escape_preference.py`. Backup đã kiểm archive/SHA-256/manifest:
`backups/20261102_163208_394000_nk084_rear_escape_preference/`, gồm nguồn,
assets/cấu hình/test/tài liệu; loại log/build/credentials. 44 test qua,
gồm hướng thân xe, sau trống, sau bị chặn và sau không an toàn để dừng.
Không chạy Gazebo mới; chưa chứng minh giảm contact NK083. Không push.
Minh chứng: `docs/evidence/2026-11-02/nk084_rear_escape_preference/`.

