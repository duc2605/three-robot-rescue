# NK092 — Audit robot1 và vùng TV, 02/11/2026

Nguồn: recordings/dynamic_20261102_180718_643579943, đọc đến khoảng44.8s.
Controller hash khớp nguồn NK091. Không chạy/dừng mô phỏng, không sửa thuật toán.

Contact Gazebo robot1–tv_viewer_a_walking: first26.834,last28.738s
(khoảng đầu/cuối, không khẳng định liên tục). Trước contact robot đã né:
23s checked_escape_command, 23.5 moving_obstacle_pause_hold,
24s escape_compute_budget_exhausted (~62ms wall),24.5 lại có lệnh né,
25/26/26.8s escape_all_rollouts_rejected, escape.moving=140, cmd0.
T24.9 track LiDAR có vận tốc~0.43m/s, TTC~0.325s; không phải hoàn toàn
không phát hiện. T26.8 controller~21ms, scan_age_sim~0.1s. Dừng khi mọi
rollout bị loại không ngăn người đi tiếp vào robot. Chưa xác định từng
track/nhánh kiểm tra nào làm mất tất cả đường; không kết luận do social
hay peer duy nhất. Nhiều track LiDAR cùng người có thể đóng góp nhưng
chưa xác minh association. Không coi RTF thấp là nguyên nhân duy nhất.

TV: tv_tracks/raw_tracks1 từ5.619s; tv_regions1 từ13.061 đến trước16.247s,
sau đó0 tới cuối phần đọc. Marker viewing_tv thực sự có, không lỗi chỉ
ẩn hiển thị. T16.247 remembered_people9→8, remembered_viewers5→4;
TV track vẫn1. Search báo aborted: camera inference is stale ở cả13.061
và16.247: có bất ổn inference/quan sát, nhưng không đủ chứng minh nó trực
tiếp xóa vùng. social_costmap.tick loại vùng theo contradicted/TTL và
color_attention.contradicted xét người invalidated, đổi heading>40deg,
chuyển nhóm hội thoại, target retired. Bản ghi thiếu candidate/debug
nguyên nhân xóa nên chưa phân biệt gate cụ thể. Không được giữ vùng vĩnh
viễn nếu người đã đứng dậy, cũng không nên mất toàn bộ vì một track rớt.

Goal=(1.035533905,-2.048056126). Goal gần TV không tự chứng minh viewing_tv.
Hướng sửa tiếp: tránh giữ dừng kéo dài khi người tiếp tục đến; xác minh
track trùng/giả thuyết chuyển động và tiến triển escape; bổ sung lý do
xóa vùng và track viewer trước khi chỉnh memory. Chưa triển khai.
