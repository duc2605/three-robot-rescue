# NK099 — Quick goal social sweep

03/11/2026. FastGoalSweep thay full sweep chậm tại goal20cm; quay liên tục
1rad/s trong giới hạn, lý thuyết6.3s/vòng, không phải thời gian đã đo.
Cần vòng yaw đo và8sector có processed-frame capture với pose history.
Missing views được nhìn bù có deadline; không bịa nhãn/pose người từ scene.
Moving safety preempts; mọi MPC map/peer/sensor check giữ. Sau rời goal35cm
quay lại sẽ rearm. Không sửa TTL mất vùng TV.

Tệp sửa: dstar_mpc_controller.py, social_observation.py,2launch, test goal scan.
Thêm feedforward góc cho reference đứng tại chỗ; reference dịch chuyển giữ
luật cũ. Viết4regression mới, không chạy pytest/Gazebo/build. Chỉ AST và
local docs/diff. Chưa đo thời gian/RTF/contact, chưa xác nhận perception
quanh goal đủ ổn định. Xem checks.json.

Backup: backups/20261103_075031_384260_nk099_fast_goal_social_sweep.
Archive/SHA nguồn/manifest đã kiểm thành công, không xóa checkpoint NK095.
