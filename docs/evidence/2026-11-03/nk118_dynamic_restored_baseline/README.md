# NK118 — Audit dynamic sau khôi phục NK116

Bản ghi: `recordings/dynamic_20261103_134837_827628782`, baseline, kết thúc102.501s.
Controller SHA74c6b9f35c896d05a707b95255ef2f69ba136b132c8e91c14b45b84becc13908 khớp nguồn hiện tại.
Không có stop_analysis.json; đọc goal/config/status trước rồi tổng hợp world và diagnostic của duy nhất bản này.

- Goal t3.825: (-5.0185041428,-2.9926850796).
- 2051world frames;1992frames có contact (bao gồm nền). Không có cặp robot–người/robot–robot hay robot–vật khác ngoài ground_plane trong dữ liệu contact.
- Leader robot3 cách goal nhỏ nhất0.002803964m tại90.251s; cuối0.092360347m.
- Cuối robot1 cách goal0.717119341m, robot2 cách2.617135593m. Đây là khoảng cách tới goal leader, không phải sai số slot follower.
- Cả3 có checked_escape_command. Counts diagnostic bị lấy mẫu theo cửa sổ dừng, không dùng làm tỷ lệ uptime/thành công.
- Coordinator independent_goal đã hoạt động. Cuối robot2(index1) holding: no checked join; robot1(index0) joining measured leader trail.
- Từ mẫu93.8 đến cuối moving_safety_active=true. Ở102.2s leader normal nhưng reference_first là pose hiện tại và command xấp xỉ0. publish_reference ưu tiên hold cả đội khi moving safety active; local xe có nguy cơ vẫn tự né. Không coi đây là thiếu dữ liệu LiDAR cuối phiên (scan/state age~0.1s sim).
- Goal scan active được ghi85.2–85.5s và90.4–90.9s; không mẫu goal_scan_done=true. Chưa xác định riêng nguyên nhân mỗi lần ngắt từ diagnostic hiện có.
- Camera/social có dữ liệu; viewing_tv được ghi12.826–83.406s (mốc xuất hiện đầu/cuối, không khẳng định liên tục). Cuối chỉ possible_legs; chưa audit nguyên nhân TV mất.
- avoidance_use_camera=false: tránh vật động dựa LiDAR, không đồng nghĩa camera/social bị tắt.
- Có watchdog_wall_freshness, stale reference, sensor expired và beam empty; chưa quy CPU/RTF riêng lẻ.

Kết luận: không ghi nhận contact trong lượt này, leader đã tới rất sát goal. Chưa hoàn tất quan sát và hội tụ đội; không đủ tuyên bố ổn mọi tình huống hay benchmark tốt hơn. Chỉ đọc bản người dùng, không chạy test/build/Gazebo, không sửa thuật toán.
