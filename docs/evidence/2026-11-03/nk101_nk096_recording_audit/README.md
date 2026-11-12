# Audit bản chạy NK096 — NK101, 03/11/2026

Bản người dùng: `recordings/dynamic_20261103_073340_299331702`, tới111.601s.
Hash controller trong diagnostics_config khớp manifest trước NK097 và NK098:
`1fb2e988224f66be389dbe11bf4784da1d15957c60a47220c31e1fe414fa8aef`.
Đây là NK096, chưa có FastGoalSweep NK099. Không tự chạy mô phỏng mới.

## Kết quả

Goal XY `(0.943486, -1.979021)`. Leader đạt khoảng cách tâm1.015mm lúc
67.451s. Có14 diagnostic events checked_goal_return_command từ24.1–80.8s;
nhánh phục hồi thực sự chạy, nhưng không chứng minh cả đội hoàn tất.

ContactSensorData xác nhận robot1/tv_viewer_b từ89.561–99.914s;
robot3/tv_viewer_a_returning từ101.737–104.366s và robot3/tv_viewer_a
106.745–111.601s. Robot2 không có contact ngoài nền được ghi.
Mốc đầu/cuối không khẳng định tiếp xúc liên tục; số entries không phải số
lần va độc lập. Contact stream có dữ liệu2175/2233world frames.

## Lệnh quanh lỗi

- Robot1 lúc89.5s: checked_escape_command, A* proposal=left, lệnh thân xe
  `[-0.03695,0.25692,0]`, scan age wall0.548s, state0.555s; contact đầu89.561s.
  Lúc95s escape_compute_budget_exhausted, bị loại bởi lidar36/peer10/moving35.
  Chưa xác định duy nhất sai footprint, dự báo hay độ trễ làm rollout được
  chấp nhận nhưng physics vẫn tiếp xúc. Left là nhãn đề xuất, không suy ra
  trái/phải trên ảnh từ riêng vận tốc thân xe.
- Leader101.7s: escape_all_rollouts_rejected, lệnh0, escape.map272;
  pose `(-1.0246,-3.2931)`. Người returning tiếp xúc sau37ms sim.
  Đây là bằng chứng nhánh dừng vì không tìm được escape qua map; chưa đủ
  tách vật nào/lớp map nào chặn từng ứng viên.
- Leader106.699s: watchdog_wall_freshness, scan age wall2.335s, refs0.
  Lúc110.5s missing_or_stale_reference. Cuối111.531s vẫn watchdog, leader
  khoảng `(-1.0304,-3.2853)`, cách goal khoảng2.37m. Trễ wall không phải
  thời gian suy luận CPU; không dùng nó khẳng định camera là thủ phạm.
- Goal scan bật19.7–20.0,65.5–66.7,70.6–72.9,75.7–75.9s; chưa lần nào done.
  Chưa có bằng chứng chi tiết lý do ngắt từng vòng, không gán cho NK099.

## Kết luận và giới hạn

NK096 đã tới XY goal trong một lượt, sau né chưa trở lại cuối lượt và có
contact robot1/leader. Chưa chạy ổn toàn hệ thống. Không so trực tiếp với
NK095 để quy hồi quy vì goal/lịch tương tác khác. Chưa sửa thuật toán,
chưa test/build/Gazebo mới, chưa đo RTF hoặc audit đầy đủ nhận diện TV.
Tổng hợp lưu tại [summary.json](summary.json); JSONL gốc được giữ cục bộ.
