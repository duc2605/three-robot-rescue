# NK110 — Ưu tiên né về vị trí đầu phiên

03/11/2026. Lượt người dùng092310 tới97.701s đúng mã NK109 trước sửa;
manifest backup NK110 khớp hash controller bản ghi. Physics contact leader
với walking32.37–34.848s, returning93.995–95.968s. Snapshot32.4/94s đều
emergency=true, chưa chọn được candidate, escape_compute_budget_exhausted;
các trial đã xét chủ yếu bị escape.moving loại (aggregate88/103 tại tick).
Không kết luận chỉ tăng budget hoặc về origin sẽ chắc chắn hết contact.

NK110 nhớ pose map mới đầu tiên riêng mỗi xe; không phải hardcode ground
truth hoặc lấy lại goal. Khi yield, thử local target tối đa0.72m về origin
trước các proposal khác ở cả stage. Trong cùng social rank/terminal safety,
xếp ưu tiên tiến gần origin trước rear/cost. Nếu home target có sẵn thì
không chạy shortcut hướng goal trước search; hết threat, normal tracking
vẫn nhận goal chính. Home path chỉ là rollout cục bộ, không phải D* toàn
cục tự đưa về nhà qua mọi ngõ; bị chặn thì vẫn dùng hướng khác.

Capture không đổi theo new goal hoặc pose mới; simulation clock reset thì
xóa để ghi lại. Origin có thể là ước lượng map đầu tiên nhận được, không
bảo đảm đúng tâm spawn nếu node được khởi động muộn. Không đổi map/LiDAR/
moving/corridor/peer/gia tốc/freshness và social-first/emergency NK109.
Trace có home/home_target/selected_proposal/selected_home_rank; từng trial
có proposal=home/refuge/astar/direction. Nhãn side vẫn theo yaw xe, home
không đồng nghĩa rear. Chưa chạy test/Gazebo, chưa xác nhận hết va chạm.
