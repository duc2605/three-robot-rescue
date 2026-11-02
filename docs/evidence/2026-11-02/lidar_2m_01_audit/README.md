# Audit lidar_2m_01 — 02/11/2026 — NK-072

Đã đọc snapshot4943 frame,0.001–247.101s sim. Goal chọn lúc8.69s:
(1.0355338,−1.9790207). Năm module navigation trong diagnostics_config
khớp SHA-256 nguồn hiện tại NK-071. Camera dùng cho né=false; mẫu scan
range_max2m. Đây là kiểm tra bản ghi người dùng, không chạy mô phỏng mới,
không đổi thuật toán hoặc dừng phiên người dùng.

## Contact thật

Physics engine có8 cặp/9 đợt contact ngoài ground_plane. Ghép đợt khi
cùng cặp/epoch và khoảng trống≤.1s; first_t/last_t nằm trong cửa sổ record.
Đợt cuối còn contact tại cuối snapshot, không coi đó là lúc đã tách ra.

| Cặp | Khoảng thời gian sim (s) |
|---|---|
| robot2 – TV walking |32.117–32.638|
| robot3 leader – patrol |84.382–86.557|
| robot1 – TV returning |93.338–95.664|
| robot1 – TV walking |139.050–140.701|
| robot1 – robot3 |147.650–147.658|
| robot1 – patrol |191.601–192.004|
| robot3 – patrol |192.409–192.773|
| robot3 – TV returning |200.536–201.809|
| robot3 – TV walking |245.110–247.101 (chưa thấy kết thúc)|

Đúng là cả3 có phát lệnh checked_escape_command (robot1:408,robot2:325,
robot3:490 mẫu đã lưu). Không được coi số lệnh này là số lần né thành công.
Không có contact của một lượt90s trước không chứng minh lượt này an toàn;
điều kiện và goal khác nhẹ, lượt này dài hơn. Không suy RTF từ hai lượt.

## Những vấn đề có bằng chứng

1. **Ước lượng/hợp nhất vận tốc có thể sai trước khi chọn điểm.** T30.0,
   robot2 chọn track gần(1.603,−2.171),v≈(+.017,−.428)m/s. Người thật đi
   +Y≈.35m/s, LiDAR1/3 lần lượt≈(+.012,+.312)/(−.041,+.325). Code
   select_lidar_tracks ưu tiên local và loại mọi remote gần<.45m, không
   xét bất đồng vận tốc/chất lượng. Do đó phép dự đoán dùng local ngược
   chiều; lúc30.0 xe vào moving_obstacle_pause_hold. T30.5/31.0 cả64
   candidate bị escape.moving loại;31.5 mới có lệnh thoát+X,32.117 chạm.
   Đây không phải kết luận sensor không quét được người: đã có track ở
   các nguồn. Không có full raw rays để tái chạy association toàn bộ.
2. **Đổi hướng né và không ra khỏi hành lang người đủ sớm.** Leader ở
   t80 command world≈(+.008,+.050),82≈(+.041,−.167),83≈(−.254,+.084),
   84≈(−.133,−.176). Patrol rẽ sang−X; leader có đoạn lùi−X cùng chiều,
   vẫn gần y=−2.0, đến84.5 mọi rollout bị loại rồi contact84.382–86.557.
   T82.9 tốc độ patrol local mới≈.10m/s trong khi sau rẽ thật≈.40m/s;
   dự báo vận tốc hằng không bao phủ ngay việc tăng tốc/rẽ.
3. **A* goal không đồng nghĩa command bám tới điểm đó.** plan_escape thử
   6 điểm cách.56/.72m theo trái/phải/sau thân xe, connector trả điểm hợp
   lệ đầu tiên; A* bị giới hạn160 expansion/15ms. Nó không xếp hạng toàn
   bộ nơi trú theo nhiều khả năng đổi hướng. MPC thử cả heading A* và16
   hướng; target_cost trọng số.2, lateral/clearance/crossing cạnh tranh.
   Plan có thể đổi sau.4s, không có cam kết phía né qua cả encounter.
   Label A* proposal chỉ là đề xuất; cần dùng command world/pose thật
   để xác định xe đi phía nào. Không kết luận riêng mọi goal A* là sai.
4. **Mô hình dừng/đồng đội không khớp chuyển động thật.**147.0–147.6,
   7 mẫu command robot1 đều0 nhưng root XY đi≈.270m; contact robot3 lúc
   147.650. publish_stop dự đoán ngay mọi pose tương lai đứng tại own_pose.
   Peer safety theo prediction này có thể lạc quan khi xe chưa dừng thực.
   Đây là bằng chứng sai lệch command/pose; chưa biết nguyên nhân trôi
   do actuator/physics hoặc lệnh khác vì thiếu wheel velocity/effort và
   kiểm tất cả publisher cmd_vel. Không tự quy cho quán tính đã xác nhận.

Ở các checkpoint contact đầu, scan/state capture age khoảng.1s; mẫu
escape thường quanh budget60ms wall, không thấy tính toán nhiều giây ở
các mẫu này. Không thể quy toàn bộ lỗi hiện tại cho camera/RTF/nhận diện
muộn; camera không tham gia và còn lỗi dự báo, hướng né, thực thi dừng.

## Hướng cải tiến được đề xuất, chưa triển khai trong audit

- Trước hết giữ range2m, sửa chất lượng association và fusion: không để
  một track local mâu thuẫn vận tốc chặn dữ liệu đồng thuận từ đồng đội;
  giữ uncertainty/hypotheses khi chưa biết hướng, không chọn bừa vận tốc.
- Chọn điểm theo hành lang chuyển động và thời gian xe thực sự đến được;
  ưu tiên đủ khoảng cách ngang, tránh lùi cùng chiều vật nhanh hơn. Giữ
  phía né ổn định khi còn an toàn, cho đổi ngay khi xuất hiện nguy cơ mới;
  kiểm đoạn đi, điểm dừng và cửa sổ vật có thể rẽ/tăng tốc.
- Dùng vận tốc robot đo từ pose/odom và khoảng phanh khi đánh giá peer/
  stop, đo response thực để sửa controller/physics nếu cần. Lệnh0 chưa
  phải bằng chứng xe dừng; không phát stationary prediction quá sớm.
- Tái hiện riêng các mốc32/84/93/147s trong test hồi quy rồi thử nhiều
  chu kỳ≥247s, cả GUI và server; giữ backup NK-071 trước cải tiến tiếp.

## Minh chứng và chạy lại phân tích

- `analysis.json`: contact9đợt, hash snapshot/source, counters, drift.
- `checkpoints.json`: dữ liệu thật chọn lọc cho các mốc nêu trên.
- `contact_windows.jsonl.gz`: frame thô ở các cửa sổ liên quan.
- `contact_trajectories.png`: tọa độ world; mũi tên từ root pose, chữ là
  sim-time; dấu đỏ là vị trí root tại lần contact đầu của cặp trong panel,
  không phải tọa độ điểm tiếp xúc trên bề mặt hay nhãn perception.

Từ root repository: `python3 docs/evidence/2026-11-02/lidar_2m_01_audit/analyze.py`.
Script chỉ đọc input, không publish ROS, viết lại minh chứng từ snapshot
input lúc chạy. Nếu record tiếp tục tăng, kết quả chạy sau có thể khác;
analysis.json hiện tại giữ hash của complete prefix đã phân tích.
