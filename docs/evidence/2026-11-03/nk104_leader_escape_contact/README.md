# NK104 — Leader né rồi bị người đuổi kịp

03/11/2026; bản `dynamic_20261103_082433_955413378`, tới35.851s.
Hash controller khớp NK103 hiện hành. Không mở/dừng mô phỏng hoặc sửa luật né.

## Kết quả vật lý và luồng dữ liệu

ContactSensorData ghi robot3/tv_viewer_a_walking33.078–35.582s;
robot1/robot2 chưa ghi contact ngoài nền.658/718world frames có dữ liệu
contact.881 entries không phải881lần va hay khẳng định tiếp xúc liên tục.
Điều phối còn reference_rows9 tại35.6s; goal scan bị moving safety hủy,
last_result là cancelled: yielding to an approaching moving obstacle.
Không lặp lại bằng chứng chết điều phối giữa phiên như NK102. Không đủ
chứng minh toàn vòng quét hoàn tất hoặc marker fix đã an toàn mọi trường hợp.

## Vì sao va chạm

Xe có phát hiện và né từ trước: tại24–26s đã checked_escape_command.
Sau khi người đổi hướng tiến theo +Y, leader vẫn ở gần x1.6, cùng hành
lang với người. Ground truth30.001→33.001s: người (1.6,-2.22556)→
(1.6,-1.16681), tốc độ khoảng0.353m/s; leader (1.61278,-0.95154)→
(1.55992,-0.68717), dịch +Y khoảng0.088m/s, chưa tách ngang đáng kể.
Đây là tốc độ thực đo đoạn đó, không phải tốc độ lệnh tối đa0.28m/s.

Lệnh né30/31/32s đều selected_escape_terminal_safe=false;31s chỉ dự báo
0.6s,30/32s3s. Nguồn cho phép nhận candidate khi terminal_safe hoặc
not stop_at_goal; cruise có cuối không an toàn vẫn được chấm điểm (phạt2).
Điều này hỗ trợ thoát tình huống chật nhưng không bảo đảm tìm được bước
né kế tiếp. Candidate được kiểm theo track vận tốc hiện tại; không phải
bảo đảm an toàn toàn kịch bản khi người đổi hướng/track đổi theo scan.

32.5s hết budget tìm escape, loại moving154/corridor16, lệnh0.
33s hết budget, loại corridor40/moving72;33.1s moving223;33.5s mọi
rollout bị moving272 loại. Contact đầu33.078s: người tiếp tục tiến khi xe
đã mất đường né hợp lệ. Không có bằng chứng map là nút chặn chính lúc này.

33s LiDAR vẫn accepted, điểm gần phía trước0.309m; có track gần vận tốc
+Y khoảng0.31–0.52m/s tùy sample. Đây không phải không quét được người.
Wall age scan khoảng0.5–1.6s và watchdog xuất hiện một số đoạn là yếu tố
cần cải thiện tính liên tục; không dùng wall age làm thời gian inference,
không đủ kết luận camera/CPU là nguyên nhân duy nhất. Escape search lúc
bị chặn dùng khoảng63ms so budget60ms; nhiều ứng viên bị moving/corridor
loại. Không bảo đảm chỉ tăng budget sẽ có đường an toàn.

## Hướng xử lý, chưa triển khai

Ưu tiên đưa xe ra ngoài hành lang dự báo của người, chỉ ưu tiên phía sau
khi phía đó giúp thoát hành lang. Cruise cuối chưa an toàn cần điều kiện
còn đường thoát tiếp/đang tăng khoảng hở; tránh lùi cùng hướng với người
nhanh hơn. Kiểm thêm vì sao rollout đã chấp nhận không tạo đủ tiến triển
thực và vì sao bị corridor loại khi cần thoát sát; chưa hạ điều kiện an toàn.
Không khẳng định đây là nguyên nhân duy nhất hoặc NK103 gây hồi quy:
NK103 chỉ sửa marker, luật né được giữ nguyên. Chưa sửa thuật toán/chạy lại.
