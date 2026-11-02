# NK-080 — Chuỗi nguyên nhân va chạm NK-078

Audit offline, không sửa navigation, không chạy mô phỏng. [analysis.json](analysis.json)
và analyze.py tái hiện đối chiếu từ frames/diagnostics NK-078 đã giữ nén.
Ground truth chỉ dùng đánh giá offline; track gần patrol được ghép theo
vị trí tại stamp, không coi LiDAR đã có semantic identity.

## Đã xác nhận

1. Người tuần tra đứng ở(1.6,−2) khoảng81.5–82.5s rồi đi−X≈.404m/s.
   Robot3 t83.0 dùng track stamp82.9 có velocity≈(−.140,−.003), trong
   khi GT quanh đúngstamp≈(−.404,0). Các nguồn độc lập trong diagnostic
   cũng đánh giá thấp lúc này; không chỉ vấn đề thiếu dữ liệu một xe.
2. T83.0 robot3 ở≈(.623,−1.800), selected goal(.620,−2.640), command
   chủ yếu−Y, qua tuyến người y=−2. T83.1 selected goal đổi thành
   (.527,−1.261), nhưng command vẫn−Y do giới hạn gia tốc. T83.2 timeout,
   từ83.3 all_rollouts_rejected, cuối cùng contact84.180. Goal ghi ở
   tick rejected là goal lần thành công trước, không quyết định mới.
3. Robot2 t84.0 và85.1 có track gần patrol velocity0 trong khi GT≈.404m/s,
   reason moving_obstacle_pause_hold. collision_risk trả None khi speed
   <.05; yield branch giữ chờ thay vì né khi không còn threats. Việc
   radius tăng lên.83m không biến velocity0 thành dự báo đang tiến tới.
   Lúc85.6 velocity lại≈.411m/s, toàn bộ candidate bị moving checks loại;
   contact85.647. Không có history/track ID đầy đủ để quy zero velocity
   riêng cho fit, association hay fusion; cần audit sâu phần đó.
4. Trước contact scan/state≈.1–.2s sim, compute mẫu26.4ms robot3 và13.4ms
   robot2; rejection thống kê moving, không phải map/social hay peer.
   Không đủ căn cứ quy lỗi trực tiếp cho camera chậm hoặc vùng TV chặn
   toàn bộ lối né. Camera không trực tiếp tạo moving tracks ở profile này.
5. Robot3 command0 từ83.2 nhưng root từ83.201 đến84.151 còn dịch≈.0594m.
   Cmd0 không chứng minh đứng yên ngay. Chưa có wheel/effort/all publisher
   trace để kết luận actuator, ma sát, trễ DDS hoặc riêng inertia.

## Kết luận có giới hạn

Chuỗi phù hợp dữ liệu: restart/đổi hướng người→ước lượng vận tốc bị thấp/
chập chờn→lối né dựa forecast không đủ bảo thủ, có đoạn cắt qua luồng
người→đổi phía muộn trong khi xe chưa thể đảo vận tốc→không có full
rollout được chấp nhận→phát dừng giữa hành lang người→contact.

Không chứng minh tại83.3s vẫn tồn tại một lối vật lý an toàn khả thi;
all_rollouts_rejected không đồng nghĩa toàn không gian không có đường.
A* chỉ proposal, MPC kiểm full horizon; không nên ép chạy theo A* hoặc
bỏ collision check khi rejected. Chưa có120s baseline cameraoff cùng
điều kiện, nên không coi bật camera là nguyên nhân duy nhất của khác biệt.

Vùng viewing_tv chỉ14.033–18.235s và không lying detection là giới hạn
kiểm chứng của NK-078; chưa phân biệt mất track với người thay hành vi/
ra khỏi FOV, không tự gọi đây là lỗi memory đã xác định.

Ưu tiên đề xuất (chưa triển khai): đánh dấu vận tốc uncertain khi mới
đi lại/mất fit, không coi đó là standing chắc chắn; kiểm thời gian cắt
corridor với biên bất định; quyết định pause phải xét khả năng người vẫn
đi tới; đo/calibrate braking/actuator và kiểm rollout thực thi. Giữ mọi
hard check, không tăng tốc/giảm radius hoặc bỏ full-horizon để ép xe né.
