# NK108 — Escape đi vào vùng TV đã nhận diện

03/11/2026. Bản người dùng090103 tới47.751s, hash đúng NK107 hiện hành.
Không mở/dừng/chạy lại mô phỏng, không sửa thuật toán.

## Sự kiện

Navigation31.516s (stamp31.5) leader checked_escape_command, goal né
(0.026208,-1.340838), stops=true, terminal_safe=true. Tâm leader đi vào
polygon xã hội id2 tại31.551s, tọa độ(0.710013,-1.362103); vùng label
viewing_tv: temporally confirmed viewer + RGB-D measured TV segment,
buffer0.40m. Đây là marker từ camera-social, không phải vòng LiDAR2m hay
chỉ ground-truth scenario marker. Goal né cũng nằm trong polygon này.
Tâm leader còn trong vùng tới cuối bản ghi. Không ghi contact robot ngoài
nền trong lượt47.751s; không coi đó là chứng minh né ổn/giữ vùng xã hội.

## Vì sao code cho phép

Escape kiểm cứng theo physical_grid, ray tĩnh, moving sweeps, corridor,
peers và freshness. A* thử planning-map trước rồi physical fallback;
rollout sampling vẫn được tạo theo physical checks. escape_social_rank
chỉ xếp hạng sau khi đã gom các candidate trong budget, không phải điều
kiện loại ứng viên. social_costmap fused[mask]=100, nhưng bản ghi không có
snapshot binary planning map từng candidate nên không xác nhận từng ô
đúng lúc chấm điểm. Không đủ kết luận duy nhất map chưa cập nhật hay mọi
ứng viên ngoài vùng đã bị loại. Ưu tiên rank chỉ có tác dụng với candidate
thực sự được tìm thấy, không bảo đảm đã tìm hết hướng trước khi fallback.
Terminal_safe là kiểm dừng vật lý/approach corridor, không bao gồm social.
A* proposal=rear là nhãn kế hoạch đề xuất; rollout cuối có thể là reactive
fallback hoặc hướng khác, không được dùng nhãn này chứng minh xe lùi.

NK105 giảm tình huống lùi cùng dòng người nhanh hơn bằng xét hướng ngang
sớm, rear đưa lên đầu nếu abs(sin(rear-flow))>=0.5. Candidate trong cùng
social rank được ưu tiên terminal_safe rồi rear rồi cost. Cả rear và social
là ưu tiên có điều kiện, không phải lệnh bắt buộc. Refuge cũ được xét sớm;
budget60ms và dừng sau horizon dài có candidate cũng hạn chế tập so sánh.
Đoạn này checked_escape_command, không phải recovery mới NK107.

## Hướng sau xe trong ảnh

Ví dụ31.501s pose leader(0.721798,-1.355609), yaw2.634084rad. Điểm đúng sau
0.6m là(1.246173,-1.647210), nằm ngoài bbox TV phía phải nhưng chỉ cách tâm
walking_person(1.6,-1.697059)0.357m. Đây là ảnh chụp hình học, chưa là
rollout theo thời gian hoặc chứng minh chính điểm người dùng vẽ không an
toàn. Không có log rejected checks theo từng hướng, nên không khẳng định
hướng lùi đã bị loại chính xác vì corridor/moving/peer hay hết budget.

## Hướng cải thiện, chưa triển khai

Tìm quỹ đạo đủ horizon ở ngoài social zone (sau xe trước nếu thực sự thoát
hành lang) thành một lượt tìm riêng trong budget trước khi cho fallback
physical. Nếu đã ở trong vùng, ưu tiên giảm xâm nhập/đi ra. Chỉ fallback
đi vào vùng khi tình huống thoát hiểm thực sự cần, ghi lý do rõ; không bỏ
kiểm người/peer để ép lùi. Cần ghi candidate heading/goal, social rank,
rejected gate và timeout để giải thích chính xác vì sao không chọn rear.
Không chứng minh rear an toàn từ ảnh tĩnh hoặc nâng ưu tiên rear vô điều kiện.
