# NK106 — Sau né không quay về: phục hồi clearance chặn cả đội

03/11/2026. Bản `dynamic_20261103_083547_393965840` tới129.301s;
controller hash d1e87e125978677200825c468af79e611ba9acf23d196325c7ad02c08c61e6e1
khớp NK105 hiện hành. Không mở/dừng mô phỏng hay sửa nguồn.

## Xe có trở về goal trong lượt này

Goal giữ nguyên (1.058547,-1.956009). Leader sát tâm goal1.048mm tại
70.301s, rồi né ra lần nữa. Cuối sample129s còn cách1.479m.
Checked goal return có3events24.5/24.6/28.7s; không coi số event là tỷ lệ
hoặc số lần thực hiện vật lý độc lập. Không phải không bao giờ trở về.

## Nút chặn chính đoạn đứng lâu

96.8s→ít nhất126s coordinator_no_route_or_maneuver, moving_safety=false,
reference_rows0, replan_required=true. Goal vẫn original_goal, không có
approach_goal. Đây là khoảng đã hết moving safety nhưng vẫn không có tuyến.

Log điều phối lặp cảnh báo robot2 planning/lidar clearance0.136m dưới
footprint0.15m; physical/lidar cũng0.136m. Tại110s local robot2 ghi
physical_clearance0.135606m. Chưa xác định vật/lớp cụ thể tạo điểm gần nhất.
Nguồn plan() kiểm toàn3xe; chỉ cần1xe is_free_world=false sẽ gọi
start_clearance_recovery và return. Recovery lại return false ngay khi
initial_clearance<robot_radius, không dựng bước thoát. Không có convoy/
structure/maneuver thì publish_reference xuất rỗng cho cả đội. Lần lặp
sau vẫn gặp đúng clearance, tạo tình trạng chờ không tự phục hồi.

Local leader110s vẫn state/scan age~0.098s sim, LiDAR accepted, nhưng
refs0, reference age80.5s wall. watchdog/missing_or_stale_reference là
hệ quả thiếu đường, không chứng minh LiDAR/pose bị mất như NK102. Coordinator
sống tới lúc người dùng dừng, exit cleanly; không phải lỗi marker tái diễn.
Cuối128s moving safety bật lại, vẫn còn thêm vấn đề né/overspeed cần xét
riêng; không gọi toàn phần cuối là hết vật động.

## Các hạn chế khác ghi nhận

Physics có leader/tv_viewer_b95.638–95.847s; không contact ngoài nền cho
2follower.2545/2587world frames có contact data. Lượt mới chưa hết va chạm,
không dùng nó tuyên bố NK105 tốt hơn ca khác. Goal scan cũng chưa done;
last_result abort camera inference stale, đo quay15.75deg/0sector.
Lỗi camera quét chưa hoàn tất khác với nút chặn clearance đoạn96.8–126s.

## Hướng tiếp theo, chưa triển khai

Cần nhánh phục hồi clearance tăng dần khi xe đã sát vật cản, kiểm toàn
rollout và các xe còn lại; không ép is_free hoặc hạ bán kính để lọt qua.
Khi follower đang phục hồi, tránh làm mọi xe mất reference không có kế
hoạch; có thể cấp hold/recovery/leader route độc lập chỉ nếu kiểm peer/map
và vật động cho phép. Chưa triển khai, chưa chạy thử. Bằng chứng gốc log:
~/.ros/log/python3_20051_1793669748816.log; các kết luận chính giữ tại đây
và summary.json để không phụ thuộc duy nhất log cục bộ.
