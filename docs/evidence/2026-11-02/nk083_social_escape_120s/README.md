# Kiểm thử NK-082 — 120 giây với camera/vùng xã hội

### NK-083 — 02/11/2026 — Một lượt120s kiểm tra NK-082 có camera/xã hội

Người dùng yêu cầu chạy thử rồi tiếp tục. Đã chạy đúng1 lượt server-only,
ROS domain69, goal(1.0815577507,−2.00203228), camera/person/head/body/social
map/observation/auto-observe bật, LiDAR2m. Không đổi thuật toán trong tác vụ.
Đã dừng sau120s sim. Không chạy lần2 và không push.

Kết quả không đạt: trong cửa sổ0.001–120.001s, contact physics ghi nhận
patrol_person–robot2 từ85.445 tới97.334, robot2–robot3 từ88.111 tới89.318,
robot2–tv_console từ88.218 tới90.460. Đây là mốc đầu/cuối theo cặp, không
khẳng định tiếp xúc liên tục trong toàn khoảng. Robot1 không contact ngoài
nền ghi nhận. Leader từng vào bán kính15cm goal ở20.351s, rời xa hơn50cm
ở23.101s, chưa trở lại15cm; cuối cách0.963m. Robot2 cuối ở(−4.383,−3.160).
Có195 mẫu marker viewing_tv từ14.067 tới76.434s; không chứng minh nhận diện
đúng toàn bộ hoặc vùng liên tục tồn tại. Không coi hết contact leader–người
là thành công chung vì vẫn có contact giữa xe và lỗi trở về goal.

Nguồn NK082 cùng hash lưu source_hashes.json; params thực tế/live và dữ liệu
nén tại `docs/evidence/2026-11-02/nk083_social_escape_120s/`. Chưa audit riêng
quỹ đạo xuyên planning keepout hoặc định lượng tác động carve; chưa thể quy
chuỗi contact cho ưu tiên vùng xã hội, camera hay một nhánh cụ thể. Decision
có nhánh timeout, all-rollouts-rejected, overspeed và freshness; cần đối
chiếu timeline trước khi kết luận nhân quả. Một lượt không là benchmark.

Backup trước tạo harness/tài liệu:
`backups/20261102_161727_010342_nk083_social_escape_validation/`; script đã
xác minh archive đọc được/SHA-256 nguồn/manifest. Phạm vi nguồn, assets,
cấu hình, test, tài liệu, không log/build/credentials. Không chạy lại unit
test vì không đổi controller; kết quả40 test NK082 không chứng minh vật lý.

Xem: `python3 scripts/view_replay.py --session recordings/nk083_social_escape_120s_once`.


Số liệu: [analysis.json](analysis.json); cấu hình xác minh: [live.json](live.json).
Raw có thể chứa đuôi đóng phiên sau120.001s; phần đó không tính đánh giá.
