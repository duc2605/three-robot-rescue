# NK111 — Home priority đã thử, leader vẫn bị người đuổi kịp

03/11/2026. Bản094020 tới33.601s, hash đúng NK110. ContactSensorData xác
nhận leader/walking31.763–33.601s (tới hết bản ghi), hai follower chưa có
contact ngoài nền.613/673world frames có contact data. Đầu/cuối không
khẳng định tiếp xúc liên tục. Goal còn cách gần nhất0.389m tại23.151s;
không có bằng chứng tới goal/scan xong trong lượt ngắn này.

## Home priority không bị bỏ qua

Leader home=(3.5,-2.2), target mỗi tick hướng đó. Trace23.3s home bị
escape.lidar loại;25.6s escape.peer;31/31.7s escape.moving;32s
escape.corridor. Mục đích ưu tiên là chọn trong phương án hợp lệ, không
được bỏ gates để ép về. Việc home là vị trí cũ không xác nhận đường hiện
tại trống. Không đủ quy một gate luôn quá bảo thủ hoặc luôn đúng từ trace này.

## Chuỗi lỗi gần contact

24–26s leader đi lên gần x1.6 theo+Y, vẫn ở hành lang người sắp đổi hướng.
28s quay lại mpc_tracking_command,29s mpc_beam_empty_step_1/moving chặn.
Người ground truth ở(1.6,-2.5)28–29s rồi đi+Y;29s nearest LiDAR track có
velocity0 và radius0.83;30s fit lại gần+Y0.217m/s,31s+Y0.366m/s.
collision_risk trảNone cho speed<0.05; nguy cơ còn được latch0.5s nhưng
không bảo đảm giữ quyết định né qua dừng/đổi hướng. 28s track còn thiên+X,
đúng là dự báo vận tốc hiện tại chưa thấy bước rẽ+Y trong tương lai.
Không dùng authored timeline để thay perception.

30–32s repeatedly no candidate ở cả social/physical, moving/corridor loại
và hết budget.31.7s lệnh0, pose(1.5577,-1.1619), LiDAR/pose mới~0.1s sim.
31.763s contact đầu.33s lại có escape nhưng tiếp xúc đã bắt đầu; thêm
priority không tạo được đường thoát sau khi đã mất khoảng trống.
Điều phối vẫn refs9 ở33.5s, không phải crash marker hay mất goal/reference.

## Điểm yếu cụ thể trong mô hình chuyển động

escape_initial_velocity chỉ dùng velocity đo khi last_command linear<0.03
và tốc độ đo>0.04; các trường hợp khác trả last_command (bao gồm yawrate).
Ví dụ31s initial body=(0.0227,-0.2791,0), measured world=(-0.0701,0.1602,
-0.5109). Hai hệ tọa độ khác nhau, không so component trực tiếp; nhưng
initial angular0 khác yawrate đo-0.511, tốc độ linear0.280 khác tốc độ đo
0.175.23.3s tốc độ command trước khoảng0.278 khác đo0.130. Sai lệch này
cho thấy rollout không luôn khởi tạo từ trạng thái vận tốc thực, cần xử
lý cùng chấp hành/feedback thay vì chỉ thêm thứ tự ưu tiên. Chưa tách được
mức đóng góp riêng của sai mô hình, nhiễu pose và động lực học bánh xe.

## Hướng tiếp theo, chưa triển khai

Dùng vận tốc đo mới (đổi frame đúng) làm trạng thái rollout, kiểm gia tốc/
phanh từ trạng thái thật; giữ/lập lại escape qua đoạn fit0/đổi hướng với
bất định có giới hạn. Chỉ nhả né về goal khi đã ra khỏi hành lang và có
hysteresis/đủ bằng chứng; tránh di chuyển lại vào đường người sắp tới.
Giữ kiểm vật lý/peer/social, không chỉ giảm radius hay tăng budget.
Ưu tiên home vẫn hữu ích nếu đường hợp lệ, chưa là phương án chữa hết.
Chỉ audit, chưa sửa source, không test/build/chạy lại/GitHub.
