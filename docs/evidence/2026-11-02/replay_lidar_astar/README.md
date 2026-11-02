# NK-074 — Lớp phủ LiDAR và điểm né, 02/11/2026

Đây là minh chứng chức năng ghi/phát lại, không phải benchmark né hoặc
một lượt Gazebo mới. `dense_fixture/`, `fixture/`, `fixture_all_robots/`
sử dụng **pose tổng hợp**, scan/Path/decision qua ROS kiểm soát. Ảnh PNG và
replay.html có nhãn kiểm thử tổng hợp; không coi là đo người thật/Gazebo.

- [regression.log](regression.log):244 test qua,2 warning SciPy;3 file ament
  lint không chạy.10 test mới ở scripts/tests/test_replay_sensors.py gồm
  ghi có giới hạn, stamp/reset, TF thiếu, A*/MPC/xóa, export/launch opt-in,
  tương đương command/rollout khi bật telemetry và lỗi publisher.
- [build.log](build.log): build2 package qua.
- [ros_validation.json](ros_validation.json), validate_ros.py: cả3 xe,
  TF alias thực, capture/receipt khác nhau, A*/MPC khác, epoch reset.
  Không spin controller để phát command; không khởi động Gazebo.
- [launch_validation.json](launch_validation.json), validate_launch.py:
  installed optional observer khởi động/dừng sạch, chỉ observer.
- [browser_validation.json](browser_validation.json), [browser_checks.log](browser_checks.log),
  validate_browser.py: Firefox kiểm trong bán kính nhưng bị che, finite
  return gần người, pose capture khi quay, entry .1–.2s; thiếu mẫu không
  bịa entry; không hiện tương lai/cũ/reset/TF thiếu. HTTP partial/incremental,
  export PNG/HTML và legacy không scan qua.
- [viewer.png](viewer.png), [all_robots.png](all_robots.png),
  [canvas_export.png](canvas_export.png): vòng theo range_max, ◇A* và ×MPC
  riêng; snapshot tổng hợp. [source_hashes.json](source_hashes.json) chỉ
  hash nguồn liên quan lúc kiểm.

Lệnh hồi quy từ root, sau source /opt/ros/humble/setup.bash:

```bash
PYTHONPATH="$PWD/social_navigation_planner:$PYTHONPATH" /usr/bin/python3 -m pytest scripts/tests social_navigation_sim/test social_navigation_planner/test --ignore=social_navigation_planner/test/test_copyright.py --ignore=social_navigation_planner/test/test_flake8.py --ignore=social_navigation_planner/test/test_pep257.py -q -p no:cacheprovider
python3 docs/evidence/2026-11-02/replay_lidar_astar/validate_browser.py
```

Các fixture ROS/launch từ chối ghi đè thư mục đã tồn tại. Muốn chạy lại
phải chọn đường dẫn fixture mới trong harness, giữ nguyên minh chứng cũ.
Browser harness dùng Firefox/Marionette, cổng2834/8774 và profile tạm.
Không cần chạy Gazebo cho kiểm thử này.

Giới hạn: đối chiếu tia gần footprint người không chứng minh semantic
perception hoặc controller chấp nhận track. Chưa benchmark overhead RTF,
chưa kiểm toàn kịch bản Gazebo mới; lỗi né NK-073 vẫn mở. Chạy thường
không ghi. Xem [runbook](../../../PHAT_LAI_MO_PHONG.md).
