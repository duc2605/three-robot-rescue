# NK116 — Khôi phục nền NK094, thêm tiến goal không chờ đội hình

03/11/2026. Người dùng yêu cầu restore thuật toán, giữ giao diện bản ghi.
Nguồn baseline snapshot NK095/c8af894 là code của lượt audit NK094.
Backup hiện trạng trước thay đổi:20261103_130052_564246_nk116_restore_nk094_independent_goal.

## Đã kiểm tĩnh

Verify SHA archive2snapshot và manifest; stage riêng11file allowlist trước
khi copy. Không extract đè .git/docs/assets. Controller có thay coordinator
mới nhưng class DistributedRobotMPC và DStarLiteGrid AST khớp baseline;
local_escape/moving_obstacles/social_observation nguyên SHA.7file replay/
video/runner/recorder/media tests nguyên SHA so trước task. Chi tiết ở
[checks.json](checks.json). Không gọi kết quả này là runtime pass.

## Hành vi bổ sung

IndependentGoalProgress chỉ coordinator: leader có tuyến map/peers riêng
khi sau né hoặc ráp formation bị chặn, followers tự nối measured trail.
Động tác follower không phải điều kiện leader được cấp tham chiếu. Vẫn
kiểm segment map/peer cùng thời điểm, không đi xuyên xe giữ. Moving safety
vẫn dùng local NK094, không mang các gate/radius mới sauNK094 vào.
Normal formation cũ vẫn dùng nếu chưa cần fallback. Diagnostics có
 goal_progress_mode/follower_join_status; UI/MP4 không đổi.

## Giới hạn và lệnh kiểm cho người dùng

Chưa pytest/build/Gazebo/RTF.6tests mới gồm5pure-policy và1coordinator ROS
message fixture. Test commands đầy đủ ở README4.1; chạy động có camera/ghi
ở README1.1. Không nhận là coordinator mới có kết quả no-contact của
baseline. Nếu follower không có join, vẫn giữ; leader thật sự blocked
vẫn không thể đi. Load video hiện tại khác mốc cũ có thể ảnh hưởng timing.
