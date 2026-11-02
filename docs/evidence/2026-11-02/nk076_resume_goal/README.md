# NK-076 — Tiếp tục về goal sau né

Yêu cầu: giữ phần né đang tốt của bản ghi người dùng, sửa phần quay về
goal nếu cần; chỉ chạy **một lượt mô phỏng** để kiểm, không lặp Gazebo.

Bản gốc recordings/lidar_vung_01:0.001–165.201s không có contact ngoài
nền được engine ghi nhận. Điều này phù hợp quan sát người dùng, nhưng
không là chứng minh mọi tình huống an toàn. NK-075 xác định timeout ở
normal tracking sau né, không chứng minh escape chưa thoát được.

Sửa riêng fallback normal MPC: trước dùng beam12 ngay; sau thử width1,
ngõ cụt thì3/12 trong deadline100ms cũ. Chỉ phát full horizon đã kiểm,
giữ cost/acceleration/map/rawLiDAR/moving/peer/freshness. Không phát
quỹ đạo dở để kịp giờ. Đánh đổi: chấp nhận quỹ đạo hợp lệ ở beam hẹp
trước, không bảo đảm bằng chi phí nghiệm beam12 đủ thời gian.

[source_scope.json](source_scope.json) so AST với backup xác nhận
escape planner, checked tracking rollout, stationary scan filter và peer
sweep helper không đổi. Normal tracking phát telemetry clear marker
thoát né để replay không bám điểm cũ.

[regression.log](regression.log):248 test qua,2 warning SciPy,3 ament
lint file không chạy.4 test mới: hoàn tất horizon trong work budget hữu
hạn, không trả partial khi deadline, không bỏ collision check và tiếp
tục reference sau pause. [targeted.log](targeted.log):15 test liên quan
qua sau sửa. [initial_refactor_failure.log](initial_refactor_failure.log)
lưu lỗi tên biến khi tách helper, đã sửa trước khi chạy Gazebo.
[build.log](build.log):2 package qua.

validate_once.py chỉ khởi động một lượt server-only, cameraoff/LiDAR2m,
cùng goal(1.0815577507,−2.0020322800), domain64/partition riêng. Không đổi
goal để qua test. Mốc gửi khi ready≥3.031s; thời điểm thực xem live.json.
Không coi điều kiện headless này là benchmark RTF/A-B với phiên GUI.
analyze.py chỉ đọc bản ghi offline, không khởi động mô phỏng.

Kết quả cuối xem [analysis.json](analysis.json), live.json và samples.json.
Dữ liệu replay gốc ở recordings/nk076_resume_goal_once (không đưa GitHub
mặc định). Chưa có benchmark lặp hoặc đảm bảo không tái mắc kẹt ở mọi
vị trí; không thay ngưỡng né để đạt goal.


Kết quả chốt **một lượt**:0.001–75.051s sim, không contact
ngoài nền ghi nhận. Leader đến gần goal lúc12.151s, sau đó rời vùng.5m
lúc24.051s khi né, tracking phục hồi sau né và trở lại cách goal
<.15m ở58.501s; cuối lượt vẫn ở goal. Cả3 safety status cuối normal.
Không có mpc_compute_budget_exhausted trong các decision leader của lượt
này; vẫn có1 escape budget timeout và1 beam empty, không che các stop đó.
Lượt dừng chủ động sau khi thấy về goal; không chạy lần thứ hai. Thời gian
wall gồm startup185.96s; không dùng làm so sánh RTF.

Giữ world_frames/goals/config/scene nén gzip, navigation_excerpt giữ tất
cả decision và raw scans58–70s để kiểm đoạn trở về. Các sample/decision
counts không phải số thử độc lập. Chưa kiểm chu kỳ sau75s hoặc nhiều goal,
và chưa khẳng định3xe luôn hồi phục đội hình ở mọi ngõ cụt.
