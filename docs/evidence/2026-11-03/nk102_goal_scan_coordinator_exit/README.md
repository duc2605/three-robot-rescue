# NK102 — Audit lỗi thoát điều phối khi quét goal

03/11/2026. Bản ghi `dynamic_20261103_081423_551496763` tới39.101s;
controller hash khớp nguồn NK099 hiện hành. Không chạy mô phỏng mới.

## Bằng chứng và chuỗi lỗi

- Leader sát XY goal14.4mm lúc19.151s. Điều phối ghi bắt đầu observation
  lúc wall1793668550.4658 rồi process15203 exit1 lúc1793668550.8836,
  tương ứng khoảng19.2s sim. Không phải chỉ đứng để quét xong rồi đi tiếp.
- Log còn tại `~/.ros/log/2026-11-03-08-14-24-043329-duc-Vivobook-ASUSLaptop-X1502ZA-X1502ZA-15193/launch.log`
  và `~/.ros/log/python3_15203_1793668465016.log`. Đã lưu các mốc chính trong
  summary.json, không dựa duy nhất vào log tạm để giữ kết luận.
- `publish_markers` controller dòng1949 vẫn đọc observation.index/targets
  theo ObservationSweep. FastGoalSweep không có hai thuộc tính này;
  control_tick gọi publish_markers sau maybe_start_goal_scan. Lỗi tương
  thích chắc chắn tồn tại trong nguồn. Thời điểm thoát khớp nhánh này;
  traceback không nằm trong log còn giữ nên chưa xác nhận nguyên văn
  exception/runtime stack. Đây là nguyên nhân thoát có bằng chứng mạnh.
- Local MPC nhận pose đội từ /formation/robot_states do điều phối phát.
  Khi tiến trình chết, state_time ngừng ở khoảng19.143s; watchdog giữ0,
  refs0. scan_callback từ chối scan mới nếu pose cũ quá0.3s sim.
- Lúc30.9s robot2 vẫn nhận scan2m, điểm gần phía trước0.276m,
  nhưng accepted=false, reason=missing_or_stale_pose. State cũ11.751s sim
  (64.199s wall); không phải mất phần cứng LiDAR, không lấy age làm CPU time.
- Physics xác nhận robot2/tv_viewer_a_walking30.959–31.964s;
  robot1/leader chưa ghi contact ngoài nền.742/783world frames có contact
  stream.145 entries không phải145 lần va độc lập hay tiếp xúc liên tục.
- Không có checked_escape_command trong diagnostic streams3xe lượt này;
  không đánh giá chất lượng chọn điểm né từ ca mất pose/điều phối này.

## Hướng sửa, chưa triển khai

Cho marker hỗ trợ riêng FastGoalSweep (góc quay/sector), tránh phụ thuộc
index/targets của sweep cũ. Sau đó cần xem một lượt mới để xác nhận điều
phối sống qua goal scan và escape nhận pose mới. Về kiến trúc, local pose
độc lập điều phối giúp giảm phụ thuộc chung, nhưng là thay đổi riêng cần
cân nhắc; không dùng pose cũ để bỏ qua kiểm tra an toàn.

Chỉ audit và cập nhật tài liệu; chưa sửa code/build/test/Gazebo/push.
