# Danh mục thư mục và file — NK097

## 1. Nguồn hiện hành và cách đọc

Xem [README mục6: thuật toán và nguồn gốc](../README.md#6-thuật-toán-thực-sự-có-trong-dự-án-và-nguồn-gốc)
và [mục7: cây từng file nguồn](../README.md#7-cây-thư-mục-từ-workspace-tới-từng-file-nguồn).
Cây nguồn chú thích293file phân phối, gồm source/test/config/asset/tài liệu.
Tên node/launch/file không được dùng thay định nghĩa thuật toán. Model người,
trọng số mạng và source code có provenance khác nhau.

## 2. Cây minh chứng lịch sử

Danh mục NK097 và bổ sung NK098–099, 837file. Chú thích theo vai trò/định dạng;
không diễn giải mỗi log/ảnh thành kết quả đạt. Script trong đây là bản hỗ trợ
audit hoặc bản sao theo thời điểm; sửa chúng không tự sửa controller đang chạy.
Ba trích đoạn raw NK092 giữ cục bộ và bị gitignore nên có thể không hiện khi
clone GitHub. Những file khác cũng có thể được bổ sung/xóa theo quyết định
lưu dữ liệu; đối chiếu đường dẫn thật trước khi dùng làm bằng chứng.

<details>
<summary>Mở toàn bộ thư mục con và file minh chứng</summary>

```text
docs/evidence/  # Minh chứng lịch sử; không import/build làm nguồn runtime.
├── 2026-10-27/  # Nhóm theo ngày thử.
│   ├── posture_empty_bed.png  # Ảnh/đồ thị minh chứng lịch sử.
│   ├── posture_validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── posture_with_person.png  # Ảnh/đồ thị minh chứng lịch sử.
│   ├── runtime_after.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── runtime_before.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   └── scenario_motion_validation.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
├── 2026-10-28/  # Nhóm theo ngày thử.
│   ├── astar_camera_priority/  # Nhóm minh chứng astar_camera_priority; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── regression_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── ros_smoke.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── ros_smoke.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── safety_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   └── validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── collision_investigation/  # Nhóm minh chứng collision_investigation; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   └── timeline_comparison.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── collision_retest/  # Nhóm minh chứng collision_retest; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── audit.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── interpretation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── latest_goal_observed.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── poses_after_event.pbtxt  # Cấu hình/log graph dạng protobuf text của lần thử.
│   │   ├── regression_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── runtime.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   └── safety_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   ├── dynamic_restart/  # Nhóm minh chứng dynamic_restart; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   └── startup_audit.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── follower_collision/  # Nhóm minh chứng follower_collision; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── geometry_validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── poses.pbtxt  # Cấu hình/log graph dạng protobuf text của lần thử.
│   │   ├── regression_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── replay_state.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── runtime.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   └── safety_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   ├── followers_live/  # Nhóm minh chứng followers_live; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── audit.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   └── interpretation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── leader_hold/  # Nhóm minh chứng leader_hold; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── interpretation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── maps.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── reference_audit.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── shadow_tracks.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   └── team_audit.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── leader_live_version/  # Nhóm minh chứng leader_live_version; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── interpretation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   └── read_only_audit.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── leader_rejection_analysis/  # Nhóm minh chứng leader_rejection_analysis; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── check_shadow.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── live_audit.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── normal_replay.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── second_shadow.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   └── summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── leader_uncertainty_recovery/  # Nhóm minh chứng leader_uncertainty_recovery; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── check_ros_smoke.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── regression_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── ros_smoke.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── ros_smoke.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   └── safety_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   ├── manual_run_audit/  # Nhóm minh chứng manual_run_audit; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── diagnostic_excerpt.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── user_map_diagnosis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── user_physical_map.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── user_run_audit.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   └── user_social_map.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── moving_obstacle_fix/  # Nhóm minh chứng moving_obstacle_fix; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── regression_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── ros_smoke.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── ros_smoke.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── safety_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   └── validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── persistent_viewing/  # Nhóm minh chứng persistent_viewing; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── check_ros_tick.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── regression_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── ros_tick_smoke.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── ros_tick_smoke.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   └── social_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   ├── rtf_profile/  # Nhóm minh chứng rtf_profile; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── diagnosis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── rtf_cpu_profile.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── rtf_gazebo_stack.txt  # Văn bản đầu ra/ghi chú lịch sử.
│   │   ├── rtf_gazebo_stats.txt  # Văn bản đầu ra/ghi chú lịch sử.
│   │   └── source_comparison.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── status_recheck/  # Nhóm minh chứng status_recheck; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   └── audit.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── tv_memory_loss/  # Nhóm minh chứng tv_memory_loss; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── interpretation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   └── status_timeline.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   ├── cleanup_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   ├── cleanup_validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── github_build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   ├── github_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   ├── rename_build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   ├── rename_checks.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   └── rename_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
├── 2026-11-01/  # Nhóm theo ngày thử.
│   ├── actor_visibility/  # Nhóm minh chứng actor_visibility; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── after/  # Nhóm minh chứng after; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   │   ├── comparison.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   │   ├── first.png  # Ảnh/đồ thị minh chứng lịch sử.
│   │   │   ├── first_state.pbtxt  # Cấu hình/log graph dạng protobuf text của lần thử.
│   │   │   ├── second.png  # Ảnh/đồ thị minh chứng lịch sử.
│   │   │   └── second_state.pbtxt  # Cấu hình/log graph dạng protobuf text của lần thử.
│   │   ├── 2026-11-01T12:50:55.499954617.png  # Ảnh/đồ thị minh chứng lịch sử.
│   │   ├── 2026-11-01T12:51:18.494471907.png  # Ảnh/đồ thị minh chứng lịch sử.
│   │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── capture_after.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── ctest.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── python_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── runtime_after_fix.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── state_first.pbtxt  # Cấu hình/log graph dạng protobuf text của lần thử.
│   │   ├── state_second.pbtxt  # Cấu hình/log graph dạng protobuf text của lần thử.
│   │   └── test_build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   ├── audit_10min_115903/  # Nhóm minh chứng audit_10min_115903; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── analysis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── analyze_audit.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── events.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   ├── gazebo_pose_during_slowdown.pbtxt  # Cấu hình/log graph dạng protobuf text của lần thử.
│   │   ├── gazebo_stats_during_slowdown.pbtxt  # Cấu hình/log graph dạng protobuf text của lần thử.
│   │   ├── monitor_read_only.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── near_goal_completion_reproduction.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── progress.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── ros_log_excerpt.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── runtime_log_during_audit.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── runtime_plot.png  # Ảnh/đồ thị minh chứng lịch sử.
│   │   ├── snapshots.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   ├── summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   └── user_observation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── avoidance_regression_before/  # Nhóm minh chứng avoidance_regression_before; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── cpu_10s.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── events.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   ├── progress.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── ros_log_excerpt.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── snapshots.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   └── summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── avoidance_rework/  # Nhóm minh chứng avoidance_rework; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── runtime_after/  # Nhóm minh chứng runtime_after; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   │   ├── events.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   │   ├── progress.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   │   ├── ros_log_excerpt.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   │   ├── snapshots.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   │   └── summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── runtime_after_goal/  # Nhóm minh chứng runtime_after_goal; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   │   ├── analysis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   │   ├── events.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   │   ├── progress.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   │   ├── ros_log_excerpt.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   │   ├── snapshots.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   │   └── summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── runtime_braking/  # Nhóm minh chứng runtime_braking; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   │   ├── analysis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   │   ├── events.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   │   ├── progress.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   │   ├── ros_log_excerpt.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   │   ├── snapshots.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   │   └── summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── runtime_compact_stream/  # Nhóm minh chứng runtime_compact_stream; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   │   ├── analysis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   │   ├── events.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   │   ├── progress.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   │   ├── ros_log_excerpt.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   │   ├── snapshots.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   │   └── summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── runtime_final/  # Nhóm minh chứng runtime_final; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   │   ├── events.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   │   ├── progress.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   │   ├── ros_log_excerpt.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   │   ├── snapshots.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   │   └── summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── runtime_verified/  # Nhóm minh chứng runtime_verified; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   │   ├── analysis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   │   ├── events.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   │   ├── progress.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   │   ├── ros_log_excerpt.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   │   ├── snapshots.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   │   └── summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── before_runtime_limit.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── benchmark_escape.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── blocked_route_after.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   ├── blocked_route_before.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   ├── braking_2d_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── braking_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── build_final.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── compact_stream_probe.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── connector_compatibility.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── coordinator.prof  # Profile thời gian chạy để phân tích chi phí tính.
│   │   ├── coordinator_profile.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── coordinator_profile.txt  # Văn bản đầu ra/ghi chú lịch sử.
│   │   ├── coordinator_resumed.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── coordinator_stack.txt  # Văn bản đầu ra/ghi chú lịch sử.
│   │   ├── cpu_after_10s.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── cpu_before_compact_10s.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── cpu_verified_10s.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── ctest.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── escape_benchmark.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── final_saved_goal.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── follower.prof  # Profile thời gian chạy để phân tích chi phí tính.
│   │   ├── follower_profile.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── follower_profile.txt  # Văn bản đầu ra/ghi chú lịch sử.
│   │   ├── follower_resumed.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── follower_stack.txt  # Văn bản đầu ra/ghi chú lịch sử.
│   │   ├── goal_restore.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── local_escape_before.py  # Script/test hỗ trợ audit lịch sử — Bounded space-time A* for a temporary rear/left/right yielding waypoint.; không tự thực thi khi launch.
│   │   ├── margin_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── monitor_braking.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── new_regression_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── peer_recovery_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── probe_blocked_route.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── probe_compact_stream.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── profile_nodes_resumed.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── regression.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── regression_final.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── restore_goal.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── runtime_before_braking_revision.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── runtime_before_final_stream.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── runtime_before_peer_final.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── runtime_before_restart.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── runtime_before_stream.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── runtime_comparison.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── runtime_final_launch.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── safety_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── saved_goal_note.txt  # Văn bản đầu ra/ghi chú lịch sử.
│   │   └── static_world_smoke.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   ├── camera_diagnostics/  # Nhóm minh chứng camera_diagnostics; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── core_unchanged.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── live_summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── session.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   └── validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── collision_audit/  # Nhóm minh chứng collision_audit; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── attach_result.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── build_final.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── physics_validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── profile_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── regression.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── robot1_contact.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── robot1_contact.sdf  # Bản world/model được lưu làm bằng chứng, không phải world runtime mặc định.
│   │   ├── robot2_contact.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── robot2_contact.sdf  # Bản world/model được lưu làm bằng chứng, không phải world runtime mặc định.
│   │   ├── robot3_contact.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── robot3_contact.sdf  # Bản world/model được lưu làm bằng chứng, không phải world runtime mặc định.
│   │   ├── robot3_near_miss.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── robot3_near_miss.sdf  # Bản world/model được lưu làm bằng chứng, không phải world runtime mặc định.
│   │   ├── validate_installed_wire.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── validate_physics.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── validate_wire.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── wire_bridge.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── wire_events.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   ├── wire_events_verified.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   ├── wire_installed_bridge.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── wire_installed_physics.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── wire_installed_recorder.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── wire_physics.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── wire_recorder.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── wire_validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   └── wire_validation_verified.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── collision_live_audit_143718/  # Nhóm minh chứng collision_live_audit_143718; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── followup/  # Nhóm minh chứng followup; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   │   ├── events.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   │   ├── progress.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   │   ├── ros_log_excerpt.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   │   ├── snapshots.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   │   └── summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── analysis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── contacts_after_audit.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   ├── contacts_before_audit.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   ├── events.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   ├── followup_monitor.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── launch_after_audit.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── launch_before_audit.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── monitor.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── ros_log_excerpt.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   └── snapshots.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   ├── cooperative_escape/  # Nhóm minh chứng cooperative_escape; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── direction_comparison.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── guidance_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── regression.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── regression_before_fixture_fix.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   └── targeted.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   ├── dynamic_start/  # Nhóm minh chứng dynamic_start; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── audit.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── launch_summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   └── startup_status.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   ├── early_reaction/  # Nhóm minh chứng early_reaction; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── check_ingress.py  # Script/test hỗ trợ audit lịch sử — Isolated ROS test: production MPC ingress receives while its control group waits.; không tự thực thi khi launch.
│   │   ├── ingress.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── ingress_validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── new_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── regression.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   └── targeted.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   ├── escape_margin_fix/  # Nhóm minh chứng escape_margin_fix; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── predicate_ablation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   └── regression.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   ├── ground_truth_replay/  # Nhóm minh chứng ground_truth_replay; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── fixture_run/  # Nhóm minh chứng fixture_run; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   │   ├── gazebo.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   │   ├── replay.html  # Trang/ảnh biểu diễn replay hoặc audit lưu tại thời điểm thử.
│   │   │   ├── scene.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   │   ├── session.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   │   ├── validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   │   └── world_frames.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   ├── baseline_integrity.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── browser.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── browser_validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── browser_verified.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── fixture.sdf  # Bản world/model được lưu làm bằng chứng, không phải world runtime mặc định.
│   │   ├── gazebo_validation.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── http_validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── python_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── regression.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── regression_final.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── scene.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── server.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── session.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── validate_browser.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── viewer.png  # Ảnh/đồ thị minh chứng lịch sử.
│   │   └── world_frames.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   ├── latest_replay_audit/  # Nhóm minh chứng latest_replay_audit; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── analysis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── analyze.py  # Script/test hỗ trợ audit lịch sử — Offline measured pose/contact audit; run from project root.; không tự thực thi khi launch.
│   │   ├── scene.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── selected_frames.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   └── trajectories.png  # Ảnh/đồ thị minh chứng lịch sử.
│   ├── leader_audit_current/  # Nhóm minh chứng leader_audit_current; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── analysis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── events.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   ├── monitor.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── progress.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── ros_log_excerpt.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── snapshots.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   └── summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── leader_audit_encounter/  # Nhóm minh chứng leader_audit_encounter; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── analysis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── analyze.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── context.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── events.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   ├── monitor.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── progress.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── ros_log_excerpt.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── snapshots.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   ├── state.pbtxt  # Cấu hình/log graph dạng protobuf text của lần thử.
│   │   ├── state_summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   └── summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── leader_contact_recheck/  # Nhóm minh chứng leader_contact_recheck; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── contacts.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   ├── events.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   ├── launch.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── monitor.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── progress.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── ros_log_excerpt.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── snapshots.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   └── summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── lidar_only_trial/  # Nhóm minh chứng lidar_only_trial; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── runtime_180s/  # Nhóm minh chứng runtime_180s; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   │   ├── analysis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   │   ├── events.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   │   ├── progress.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   │   ├── ros_log_excerpt.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   │   ├── runtime_log_during_audit.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   │   ├── runtime_plot.png  # Ảnh/đồ thị minh chứng lịch sử.
│   │   │   ├── snapshots.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   │   └── summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── before_camera_off.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── before_poses.pbtxt  # Cấu hình/log graph dạng protobuf text của lần thử.
│   │   ├── before_stats.pbtxt  # Cấu hình/log graph dạng protobuf text của lần thử.
│   │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── goal_reapply.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── graph_check.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── launch_args.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── profile_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── regression_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── sensor_description.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── startup_failed_domain31.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   └── three_robot_trial_summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── map_inbox_fix/  # Nhóm minh chứng map_inbox_fix; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── build_apply.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── build_final.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── contacts_snapshot.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   ├── launch_snapshot.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── mpc_restart.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── mpc_restart_final.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── observe.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── observe_final.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── robot1_distributed_mpc.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── robot1_distributed_mpc_final.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── robot2_distributed_mpc.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── robot2_distributed_mpc_final.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── robot3_distributed_mpc.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── robot3_distributed_mpc_final.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── runtime_after.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── runtime_before_summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── runtime_inbox_only.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── runtime_summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   └── tests_final.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   ├── new_session_182452/  # Nhóm minh chứng new_session_182452; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── previous_collision_events.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   └── previous_manual_lidar_only.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   ├── nk034_restore/  # Nhóm minh chứng nk034_restore; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── backup_validation.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── build_docs.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── build_final.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── dynamic_launch_args.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── launch_validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── paper1_launch_args.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── paper2_launch_args.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── reconstruction.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── regression.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── restoration_manifest.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── source_edit_evidence.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── static_launch_args.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   └── stopped_session.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── pedestrians_no_yield/  # Nhóm minh chứng pedestrians_no_yield; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── ctest.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── plugin_test.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── regression.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── runtime_comparison.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── runtime_startup.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── runtime_state.pbtxt  # Cấu hình/log graph dạng protobuf text của lần thử.
│   │   └── scenario_policy.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── people_visibility/  # Nhóm minh chứng people_visibility; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── comparison.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── state_first.pbtxt  # Cấu hình/log graph dạng protobuf text của lần thử.
│   │   └── state_second.pbtxt  # Cấu hình/log graph dạng protobuf text của lần thử.
│   ├── physical_contacts/  # Nhóm minh chứng physical_contacts; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── browser_validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── browser_verified.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── fixture.sdf  # Bản world/model được lưu làm bằng chứng, không phải world runtime mặc định.
│   │   ├── gazebo.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── replay.html  # Trang/ảnh biểu diễn replay hoặc audit lưu tại thời điểm thử.
│   │   ├── scene.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── validate_browser.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── viewer.png  # Ảnh/đồ thị minh chứng lịch sử.
│   │   └── world_frames.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   ├── realistic_people/  # Nhóm minh chứng realistic_people; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── ctest.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── gazebo_walking.png  # Ảnh/đồ thị minh chứng lịch sử.
│   │   ├── plugin_ecm_test.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── plugin_test_build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── regression_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── runtime_final_startup.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── runtime_initial_walk.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── state.pbtxt  # Cấu hình/log graph dạng protobuf text của lần thử.
│   │   ├── state_summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   └── verification.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── right_escape_audit/  # Nhóm minh chứng right_escape_audit; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── analysis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── analyze.py  # Script/test hỗ trợ audit lịch sử — Read recorded inputs around rightward body commands overlapping follower yield.; không tự thực thi khi launch.
│   │   ├── body_frame_comparison.png  # Ảnh/đồ thị minh chứng lịch sử.
│   │   ├── final_summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── selected_events.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   ├── selected_scans.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   └── stopped_session.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   ├── stable_handoff/  # Nhóm minh chứng stable_handoff; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── analysis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── applied.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── capture_goal.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── contacts_snapshot.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
│   │   ├── new_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── observe.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   ├── regression.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── retained_goal.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── robot1_distributed_mpc.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── robot2_distributed_mpc.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── robot3_distributed_mpc.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── runtime.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   │   ├── targeted.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   ├── targeted_final.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   │   └── three_robot_dstar_mpc.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│   ├── stop_go_audit/  # Nhóm minh chứng stop_go_audit; trạng thái kỹ thuật xem README/summary của nhóm.
│   │   ├── observe.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│   │   └── runtime.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│   └── walk_heading/  # Nhóm minh chứng walk_heading; trạng thái kỹ thuật xem README/summary của nhóm.
│       ├── rendered/  # Nhóm minh chứng rendered; trạng thái kỹ thuật xem README/summary của nhóm.
│       │   ├── close_view.png  # Ảnh/đồ thị minh chứng lịch sử.
│       │   ├── first.png  # Ảnh/đồ thị minh chứng lịch sử.
│       │   ├── first_state.pbtxt  # Cấu hình/log graph dạng protobuf text của lần thử.
│       │   ├── second.png  # Ảnh/đồ thị minh chứng lịch sử.
│       │   └── second_state.pbtxt  # Cấu hình/log graph dạng protobuf text của lần thử.
│       ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│       ├── capture.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
│       ├── comparison.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
│       ├── cpp_build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│       ├── ctest.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│       ├── plugin_heading.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│       ├── regression.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
│       └── runtime_after_heading_fix.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
└── 2026-11-02/  # Nhóm theo ngày thử.
    ├── goal_markers/  # Nhóm minh chứng goal_markers; trạng thái kỹ thuật xem README/summary của nhóm.
    │   ├── browser_validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── browser_verified.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── goals.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   ├── http_validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── replay.html  # Trang/ảnh biểu diễn replay hoặc audit lưu tại thời điểm thử.
    │   ├── ros_marker_smoke.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── ros_marker_smoke.py  # Script/test hỗ trợ audit lịch sử — Isolated coordinator callbacks; no executor, Gazebo, or real command output.; không tự thực thi khi launch.
    │   ├── ros_marker_validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── scene.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── validate_browser.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
    │   ├── viewer.png  # Ảnh/đồ thị minh chứng lịch sử.
    │   └── world_frames.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    ├── lidar_2m_01_audit/  # Nhóm minh chứng lidar_2m_01_audit; trạng thái kỹ thuật xem README/summary của nhóm.
    │   ├── README.md  # Hướng dẫn/kết luận và giới hạn của nhóm bằng chứng.
    │   ├── analysis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── analyze.py  # Script/test hỗ trợ audit lịch sử — Read a bounded snapshot of the user's replay; never publish commands.; không tự thực thi khi launch.
    │   ├── checkpoints.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── contact_trajectories.png  # Ảnh/đồ thị minh chứng lịch sử.
    │   └── contact_windows.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    ├── lidar_2m_avoidance/  # Nhóm minh chứng lidar_2m_avoidance; trạng thái kỹ thuật xem README/summary của nhóm.
    │   ├── final_replay/  # Nhóm minh chứng final_replay; trạng thái kỹ thuật xem README/summary của nhóm.
    │   │   ├── diagnostics_config.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   ├── goals.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   │   ├── scene.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   └── world_frames.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── analyze_runs.py  # Script/test hỗ trợ audit lịch sử — Preserve measured outcomes of every trial, including failed intermediate versions.; không tự thực thi khi launch.
    │   ├── backups.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── before_buffered_retry_launch.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── before_buffered_retry_live.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── before_buffered_retry_samples.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── before_fusion_launch.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── before_fusion_live.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── before_fusion_samples.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── before_motion_persistence_launch.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── before_motion_persistence_live.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── before_motion_persistence_samples.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── before_pose_alignment_launch.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── before_pose_alignment_live.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── before_pose_alignment_samples.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── before_speed_fix_launch.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── before_speed_fix_live.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── before_speed_fix_samples.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── before_turn_guard_launch.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── before_turn_guard_live.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── before_turn_guard_samples.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── check_defaults.py  # Script/test hỗ trợ audit lịch sử — No spinning/commands: inspect constructed controller sensor subscriptions.; không tự thực thi khi launch.
    │   ├── corner_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── defaults.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── defaults.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── final_harness.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── final_launch.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── final_source_matches.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── final_trajectories.png  # Ảnh/đồ thị minh chứng lịch sử.
    │   ├── launch_args.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── live.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── physics_contact_ledger.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   ├── pilot_launch.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── pilot_live.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── pilot_samples.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── regression.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── samples.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── sensor_config.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── startup_failed_launch.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── startup_failed_live.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── startup_failed_motion_launch.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── startup_failed_motion_live.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── startup_failed_motion_samples.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── startup_failed_samples.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── turn_checkpoints.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── validate_live.py  # Script/test hỗ trợ audit lịch sử — Bounded isolated ROS/Gazebo run; preserve source and runtime record separately.; không tự thực thi khi launch.
    │   └── validation_summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    ├── nk073_motion_escape/  # Nhóm minh chứng nk073_motion_escape; trạng thái kỹ thuật xem README/summary của nhóm.
    │   ├── trial01_replay/  # Nhóm minh chứng trial01_replay; trạng thái kỹ thuật xem README/summary của nhóm.
    │   │   ├── diagnostics_config.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   ├── goals.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   │   ├── scene.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   ├── stop_robot1.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   │   ├── stop_robot2.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   │   ├── stop_robot3.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   │   └── world_frames.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── trial02_replay/  # Nhóm minh chứng trial02_replay; trạng thái kỹ thuật xem README/summary của nhóm.
    │   │   ├── diagnostics_config.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   ├── goals.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   │   ├── scene.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   ├── stop_robot1.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   │   ├── stop_robot2.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   │   ├── stop_robot3.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   │   └── world_frames.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── trial03_replay/  # Nhóm minh chứng trial03_replay; trạng thái kỹ thuật xem README/summary của nhóm.
    │   │   ├── diagnostics_config.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   ├── goals.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   │   ├── scene.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   ├── stop_robot1.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   │   ├── stop_robot2.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   │   ├── stop_robot3.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   │   └── world_frames.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── trial04_replay/  # Nhóm minh chứng trial04_replay; trạng thái kỹ thuật xem README/summary của nhóm.
    │   │   ├── diagnostics_config.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   ├── goals.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   │   ├── scene.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   ├── stop_robot1.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   │   ├── stop_robot2.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   │   ├── stop_robot3.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   │   └── world_frames.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── trial05_replay/  # Nhóm minh chứng trial05_replay; trạng thái kỹ thuật xem README/summary của nhóm.
    │   │   ├── diagnostics_config.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   ├── goals.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   │   ├── scene.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   ├── stop_robot1.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   │   ├── stop_robot2.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   │   ├── stop_robot3.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   │   └── world_frames.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── trial06_replay/  # Nhóm minh chứng trial06_replay; trạng thái kỹ thuật xem README/summary của nhóm.
    │   │   ├── diagnostics_config.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   ├── goals.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   │   ├── scene.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   ├── stop_robot1.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   │   ├── stop_robot2.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   │   ├── stop_robot3.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   │   └── world_frames.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── README.md  # Hướng dẫn/kết luận và giới hạn của nhóm bằng chứng.
    │   ├── acceptance.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── backups.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── check_defaults.py  # Script/test hỗ trợ audit lịch sử — No spinning/commands: inspect constructed controller sensor subscriptions.; không tự thực thi khi launch.
    │   ├── defaults.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── defaults.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── drive_probe.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── escape_regressions.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── failed_cruise_heading.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── failed_floor_trial.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── failed_refuge_commit.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── failed_refuge_wait.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── failed_stop_only.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── final_harness.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── final_launch.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── final_source_matches.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── final_trajectories.png  # Ảnh/đồ thị minh chứng lịch sử.
    │   ├── live.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── map_gate_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── measured_regressions.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── pause_turn_tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── probe_drive.py  # Script/test hỗ trợ audit lịch sử; không tự thực thi khi launch.
    │   ├── prototype_source_provenance.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── regression.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── regression_before_map_gate.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── samples.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── summarize.py  # Script/test hỗ trợ audit lịch sử — Preserve negative iterations and final test without publishing ROS data.; không tự thực thi khi launch.
    │   ├── trial01_blocked_refuge.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── trial01_harness_error.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── trial01_launch.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── trial01_sources.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── trial02_harness.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── trial02_launch.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── trial02_live.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── trial02_samples.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── trial03_harness.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── trial03_launch.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── trial03_live.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── trial03_samples.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── trial04_harness.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── trial04_launch.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── trial04_live.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── trial04_samples.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── trial05_harness.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── trial05_launch.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── trial05_live.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── trial05_samples.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── validate_live.py  # Script/test hỗ trợ audit lịch sử — Bounded isolated ROS/Gazebo run; preserve source and runtime record separately.; không tự thực thi khi launch.
    │   └── validation_summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    ├── nk075_leader_timeout/  # Nhóm minh chứng nk075_leader_timeout; trạng thái kỹ thuật xem README/summary của nhóm.
    │   ├── analysis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── decisions.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   └── frame.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    ├── nk076_resume_goal/  # Nhóm minh chứng nk076_resume_goal; trạng thái kỹ thuật xem README/summary của nhóm.
    │   ├── README.md  # Hướng dẫn/kết luận và giới hạn của nhóm bằng chứng.
    │   ├── analysis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── analyze.py  # Script/test hỗ trợ audit lịch sử — Summarize recorded poses/decisions/contacts without launching simulation.; không tự thực thi khi launch.
    │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── diagnostics_config.json.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── goals.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── initial_refactor_failure.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── launch.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── live.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── navigation_excerpt.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── regression.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── samples.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── scene.json.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── source_scope.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── targeted.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── validate_once.py  # Script/test hỗ trợ audit lịch sử — Bounded isolated ROS/Gazebo run; preserve source and runtime record separately.; không tự thực thi khi launch.
    │   ├── validation.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   └── world_frames.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    ├── nk077_recording_picker/  # Nhóm minh chứng nk077_recording_picker; trạng thái kỹ thuật xem README/summary của nhóm.
    │   ├── README.md  # Hướng dẫn/kết luận và giới hạn của nhóm bằng chứng.
    │   ├── browser.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── browser_checks.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── browser_validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── offline.html  # Trang/ảnh biểu diễn replay hoặc audit lưu tại thời điểm thử.
    │   ├── picker.png  # Ảnh/đồ thị minh chứng lịch sử.
    │   ├── source_hashes.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   └── validate_browser.py  # Script/test hỗ trợ audit lịch sử — Firefox verifies live/offline overlays using synthetic poses + ROS fixtures.; không tự thực thi khi launch.
    ├── nk078_social_camera_120s/  # Nhóm minh chứng nk078_social_camera_120s; trạng thái kỹ thuật xem README/summary của nhóm.
    │   ├── launch_parameters/  # Nhóm minh chứng launch_parameters; trạng thái kỹ thuật xem README/summary của nhóm.
    │   │   ├── human_activity_analysis.yaml  # Cấu hình được lưu để đối chiếu lần thử.
    │   │   ├── leader_person_detector.yaml  # Cấu hình được lưu để đối chiếu lần thử.
    │   │   ├── robot1_distributed_mpc.yaml  # Cấu hình được lưu để đối chiếu lần thử.
    │   │   ├── robot2_distributed_mpc.yaml  # Cấu hình được lưu để đối chiếu lần thử.
    │   │   ├── robot3_distributed_mpc.yaml  # Cấu hình được lưu để đối chiếu lần thử.
    │   │   ├── social_navigation.yaml  # Cấu hình được lưu để đối chiếu lần thử.
    │   │   └── three_robot_dstar_mpc.yaml  # Cấu hình được lưu để đối chiếu lần thử.
    │   ├── README.md  # Hướng dẫn/kết luận và giới hạn của nhóm bằng chứng.
    │   ├── analysis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── analyze.py  # Script/test hỗ trợ audit lịch sử — Summarize recorded poses/decisions/contacts without launching simulation.; không tự thực thi khi launch.
    │   ├── completion.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── contact_diagnostics.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── detection_003.556.jpg  # Ảnh chụp/camera minh chứng lịch sử.
    │   ├── detection_023.587.jpg  # Ảnh chụp/camera minh chứng lịch sử.
    │   ├── detection_044.146.jpg  # Ảnh chụp/camera minh chứng lịch sử.
    │   ├── detection_064.501.jpg  # Ảnh chụp/camera minh chứng lịch sử.
    │   ├── detection_084.704.jpg  # Ảnh chụp/camera minh chứng lịch sử.
    │   ├── detection_105.213.jpg  # Ảnh chụp/camera minh chứng lịch sử.
    │   ├── diagnostics_config.json.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── goals.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── launch.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── navigation_excerpt.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── navigation_status.json.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── provenance.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── scene.json.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── social_events.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   ├── social_events.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── validate_once.py  # Script/test hỗ trợ audit lịch sử — Bounded isolated ROS/Gazebo run; preserve source and runtime record separately.; không tự thực thi khi launch.
    │   ├── validation.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   └── world_frames.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    ├── nk079_camera_social_replay/  # Nhóm minh chứng nk079_camera_social_replay; trạng thái kỹ thuật xem README/summary của nhóm.
    │   ├── ros_fixture/  # Nhóm minh chứng ros_fixture; trạng thái kỹ thuật xem README/summary của nhóm.
    │   │   ├── navigation.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   │   ├── navigation_status.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   ├── perception.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   │   └── perception_status.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── README.md  # Hướng dẫn/kết luận và giới hạn của nhóm bằng chứng.
    │   ├── browser.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── browser_checks.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── browser_validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── contact_camera.png  # Ảnh/đồ thị minh chứng lịch sử.
    │   ├── nk078_import_provenance.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── replay.html.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── ros_checks.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── ros_validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── source_hashes.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── tv_overlay.png  # Ảnh/đồ thị minh chứng lịch sử.
    │   ├── validate_browser.py  # Script/test hỗ trợ audit lịch sử — Firefox verifies live/offline overlays using synthetic poses + ROS fixtures.; không tự thực thi khi launch.
    │   └── validate_ros.py  # Script/test hỗ trợ audit lịch sử — Read-only recorder smoke using controlled messages, never Gazebo/commands.; không tự thực thi khi launch.
    ├── nk080_nk078_cause_audit/  # Nhóm minh chứng nk080_nk078_cause_audit; trạng thái kỹ thuật xem README/summary của nhóm.
    │   ├── README.md  # Hướng dẫn/kết luận và giới hạn của nhóm bằng chứng.
    │   ├── analysis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   └── analyze.py  # Script/test hỗ trợ audit lịch sử — Offline correlation only: GT evaluates tracks, never feeds navigation.; không tự thực thi khi launch.
    ├── nk081_motion_uncertainty/  # Nhóm minh chứng nk081_motion_uncertainty; trạng thái kỹ thuật xem README/summary của nhóm.
    │   ├── tested_source/  # Nhóm minh chứng tested_source; trạng thái kỹ thuật xem README/summary của nhóm.
    │   │   ├── dstar_mpc_controller.py  # Script/test hỗ trợ audit lịch sử — D* Lite, adaptive leader-first triangle/column references and distributed MPC.; không tự thực thi khi launch.
    │   │   └── moving_obstacles.py  # Script/test hỗ trợ audit lịch sử — Short, bounded motion estimates from measured map-frame points only.; không tự thực thi khi launch.
    │   ├── README.md  # Hướng dẫn/kết luận và giới hạn của nhóm bằng chứng.
    │   ├── analysis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── analyze.py  # Script/test hỗ trợ audit lịch sử — Summarize recorded poses/decisions/contacts without launching simulation.; không tự thực thi khi launch.
    │   ├── checkpoints.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── detection_002.584.jpg  # Ảnh chụp/camera minh chứng lịch sử.
    │   ├── detection_022.985.jpg  # Ảnh chụp/camera minh chứng lịch sử.
    │   ├── detection_043.196.jpg  # Ảnh chụp/camera minh chứng lịch sử.
    │   ├── detection_063.661.jpg  # Ảnh chụp/camera minh chứng lịch sử.
    │   ├── detection_084.019.jpg  # Ảnh chụp/camera minh chứng lịch sử.
    │   ├── detection_104.022.jpg  # Ảnh chụp/camera minh chứng lịch sử.
    │   ├── diagnostics_config.json.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── final_build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── final_regression.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── goals.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── launch.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── live.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── navigation.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── navigation_status.json.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── perception.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── perception_status.json.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── pre_cleanup.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── provenance.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── samples.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── scene.json.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── social_events.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   ├── social_events.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── source_scope.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── trial_build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── trial_regression.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── validate_once.py  # Script/test hỗ trợ audit lịch sử — Bounded isolated ROS/Gazebo run; preserve source and runtime record separately.; không tự thực thi khi launch.
    │   ├── validation.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   └── world_frames.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    ├── nk082_social_escape_priority/  # Nhóm minh chứng nk082_social_escape_priority; trạng thái kỹ thuật xem README/summary của nhóm.
    │   ├── README.md  # Hướng dẫn/kết luận và giới hạn của nhóm bằng chứng.
    │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   └── tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    ├── nk083_social_escape_120s/  # Nhóm minh chứng nk083_social_escape_120s; trạng thái kỹ thuật xem README/summary của nhóm.
    │   ├── README.md  # Hướng dẫn/kết luận và giới hạn của nhóm bằng chứng.
    │   ├── analysis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── analyze.py  # Script/test hỗ trợ audit lịch sử — Summarize recorded poses/decisions/contacts without launching simulation.; không tự thực thi khi launch.
    │   ├── detection_003.610.jpg  # Ảnh chụp/camera minh chứng lịch sử.
    │   ├── detection_023.911.jpg  # Ảnh chụp/camera minh chứng lịch sử.
    │   ├── detection_044.149.jpg  # Ảnh chụp/camera minh chứng lịch sử.
    │   ├── detection_064.426.jpg  # Ảnh chụp/camera minh chứng lịch sử.
    │   ├── detection_084.500.jpg  # Ảnh chụp/camera minh chứng lịch sử.
    │   ├── detection_104.541.jpg  # Ảnh chụp/camera minh chứng lịch sử.
    │   ├── diagnostics_config.json.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── goals.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── launch.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── live.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── navigation.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── perception.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── pre_cleanup.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── samples.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── scene.json.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    │   ├── social_events.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   ├── source_hashes.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── validate_once.py  # Script/test hỗ trợ audit lịch sử — Bounded isolated ROS/Gazebo run; preserve source and runtime record separately.; không tự thực thi khi launch.
    │   ├── validation.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   └── world_frames.jsonl.gz  # Dữ liệu lịch sử nén gzip; không phải model điều hướng.
    ├── nk084_rear_escape_preference/  # Nhóm minh chứng nk084_rear_escape_preference; trạng thái kỹ thuật xem README/summary của nhóm.
    │   ├── README.md  # Hướng dẫn/kết luận và giới hạn của nhóm bằng chứng.
    │   └── tests.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    ├── nk087_ten_comparison_methods/  # Nhóm minh chứng nk087_ten_comparison_methods; trạng thái kỹ thuật xem README/summary của nhóm.
    │   ├── README.md  # Hướng dẫn/kết luận và giới hạn của nhóm bằng chứng.
    │   ├── check_static.py  # Script/test hỗ trợ audit lịch sử — Validate changed source syntax/paths only; never import or execute ROS/policies.; không tự thực thi khi launch.
    │   ├── method_catalog.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── provenance.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   └── static_checks.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    ├── nk088_inline_recording/  # Nhóm minh chứng nk088_inline_recording; trạng thái kỹ thuật xem README/summary của nhóm.
    │   ├── README.md  # Hướng dẫn/kết luận và giới hạn của nhóm bằng chứng.
    │   └── static_checks.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    ├── nk089_backup_build_cleanup/  # Nhóm minh chứng nk089_backup_build_cleanup; trạng thái kỹ thuật xem README/summary của nhóm.
    │   ├── README.md  # Hướng dẫn/kết luận và giới hạn của nhóm bằng chứng.
    │   └── cleanup.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    ├── nk090_goal_blocked_after_escape/  # Nhóm minh chứng nk090_goal_blocked_after_escape; trạng thái kỹ thuật xem README/summary của nhóm.
    │   ├── README.md  # Hướng dẫn/kết luận và giới hạn của nhóm bằng chứng.
    │   ├── analysis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── backup_retention.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── diagnostics_config.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── goal_clearance_warnings.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── goals.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   ├── latest_decisions.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   └── social_regions.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    ├── nk092_robot1_contact_tv/  # Nhóm minh chứng nk092_robot1_contact_tv; trạng thái kỹ thuật xem README/summary của nhóm.
    │   ├── README.md  # Hướng dẫn/kết luận và giới hạn của nhóm bằng chứng.
    │   ├── contact.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── diagnostics_config.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── goals.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   ├── robot1_22_29.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   └── social.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    ├── nk094_tv_region_expiry/  # Nhóm minh chứng nk094_tv_region_expiry; trạng thái kỹ thuật xem README/summary của nhóm.
    │   ├── README.md  # Hướng dẫn/kết luận và giới hạn của nhóm bằng chứng.
    │   ├── final_loss_status.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   └── tv_count_changes.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    ├── nk095_contact_free_checkpoint/  # Nhóm minh chứng nk095_contact_free_checkpoint; trạng thái kỹ thuật xem README/summary của nhóm.
    │   ├── README.md  # Hướng dẫn/kết luận và giới hạn của nhóm bằng chứng.
    │   └── summary.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    ├── replay_lidar_astar/  # Nhóm minh chứng replay_lidar_astar; trạng thái kỹ thuật xem README/summary của nhóm.
    │   ├── dense_fixture/  # Nhóm minh chứng dense_fixture; trạng thái kỹ thuật xem README/summary của nhóm.
    │   │   ├── navigation.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   │   ├── navigation_status.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   ├── scene.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   ├── session.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   └── world_frames.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   ├── fixture/  # Nhóm minh chứng fixture; trạng thái kỹ thuật xem README/summary của nhóm.
    │   │   ├── navigation.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   │   ├── navigation_status.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   ├── scene.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   ├── session.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   └── world_frames.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   ├── fixture_all_robots/  # Nhóm minh chứng fixture_all_robots; trạng thái kỹ thuật xem README/summary của nhóm.
    │   │   ├── navigation.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   │   ├── navigation_status.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   ├── scene.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   ├── session.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   │   └── world_frames.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   ├── launch_smoke/  # Nhóm minh chứng launch_smoke; trạng thái kỹ thuật xem README/summary của nhóm.
    │   │   ├── navigation.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   │   └── navigation_status.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── README.md  # Hướng dẫn/kết luận và giới hạn của nhóm bằng chứng.
    │   ├── all_robots.png  # Ảnh/đồ thị minh chứng lịch sử.
    │   ├── browser.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── browser_checks.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── browser_validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── canvas_export.png  # Ảnh/đồ thị minh chứng lịch sử.
    │   ├── http.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── launch_validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── regression.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── replay.html  # Trang/ảnh biểu diễn replay hoặc audit lưu tại thời điểm thử.
    │   ├── ros_validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── source_hashes.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── validate_browser.py  # Script/test hỗ trợ audit lịch sử — Firefox verifies live/offline overlays using synthetic poses + ROS fixtures.; không tự thực thi khi launch.
    │   ├── validate_launch.py  # Script/test hỗ trợ audit lịch sử — Run only the installed optional observer for two seconds, never Gazebo.; không tự thực thi khi launch.
    │   ├── validate_ros.py  # Script/test hỗ trợ audit lịch sử — Controlled ROS publishers; no Gazebo and no navigation command is issued.; không tự thực thi khi launch.
    │   └── viewer.png  # Ảnh/đồ thị minh chứng lịch sử.
    ├── stop_diagnostics/  # Nhóm minh chứng stop_diagnostics; trạng thái kỹ thuật xem README/summary của nhóm.
    │   ├── ros_smoke/  # Nhóm minh chứng ros_smoke; trạng thái kỹ thuật xem README/summary của nhóm.
    │   │   ├── stop_coordinator.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   │   └── stop_robot3.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   ├── ros_smoke_final/  # Nhóm minh chứng ros_smoke_final; trạng thái kỹ thuật xem README/summary của nhóm.
    │   │   ├── stop_coordinator.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   │   └── stop_robot3.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
    │   ├── build.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── launcher_validation.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── regression.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── ros_smoke.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── ros_smoke.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   ├── ros_smoke.py  # Script/test hỗ trợ audit lịch sử — Real ROS initialization/timers in isolated domain; no Gazebo or sensor input.; không tự thực thi khi launch.
    │   ├── ros_smoke_analysis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
    │   ├── targeted.log  # Log đầu ra của phiên/lệnh lịch sử; không phải mã runtime.
    │   └── validate_launcher.py  # Script/test hỗ trợ audit lịch sử — Verify wrapper activation with only final ROS executable stubbed.; không tự thực thi khi launch.
    └── stop_diagnostics_audit/  # Nhóm minh chứng stop_diagnostics_audit; trạng thái kỹ thuật xem README/summary của nhóm.
        ├── analysis.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
        ├── analyze.py  # Script/test hỗ trợ audit lịch sử — Audit the saved opt-in session; no ROS/Gazebo or navigation changes.; không tự thực thi khi launch.
        ├── contact_frames.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
        ├── diagnostics_config.json  # Dữ liệu/tổng hợp audit dạng JSON; đọc trường bên trong để biết kết luận.
        └── selected_diagnostics.jsonl  # Chuỗi mẫu theo timestamp, bằng chứng chẩn đoán/replay lịch sử.
```

</details>

## 3. Thư mục chỉ có trên máy và tài nguyên không còn trong nguồn

README mục7.1 mô tả build/install/log/recordings/backups và file con điển
hình; đây là dữ liệu sinh ra, không được coi là danh mục mã thuật toán.
Cấu hình riêng `.git/.codex/.agents` không mở rộng tới nội dung tài khoản.

Danh mục `models/` hiện có body_pose/head_pose/person_detector/person_standing/
person_talking. LICENSES.md có ghi lịch sử person_walking nhưng thư mục đó
không có trong cây nguồn đọc tại NK097; không khẳng định asset đó đang được
nạp chỉ dựa vào tài liệu lịch sử. Nếu cần sửa walking animation phải kiểm
tra world/model thực tế. Mục này ghi nhận hiện trạng, không tự tải/thay asset.

## 4. Duy trì danh mục

Đây là tài liệu snapshot, không trình quét nền. Khi thêm file cần bổ sung
chức năng vào README/danh mục và cập nhật nhật ký. Phần báo cáo chỉ thay khi
có thay đổi kỹ thuật/bằng chứng; biên tập tài liệu không tạo phiên bản thuật toán.


## 5. Bổ sung NK098 — video replay

- `scripts/replay_media.py`: dữ liệu video/manifest, chuẩn bị MP4 camera và
  kiểm tra byte range/đường dẫn phiên.
- `scripts/record_replay_media.py`: supervisor launch, quay hai cửa sổ X11,
  clock wall–sim và kết thúc encoder khi launch dừng.
- `scripts/tests/test_replay_media.py`: Range, cách ly file, source/epoch,
  frame thưa và chọn cửa sổ. Đã viết, chưa chạy pytest.
- `docs/evidence/2026-11-03/nk098_replay_video/README.md`: phạm vi thay đổi,
  phụ thuộc và giới hạn kiểm chứng.
- `docs/evidence/2026-11-03/nk098_replay_video/checks.json`: kiểm tra tĩnh
  thực sự đã chạy, không số liệu RTF/contact.


## 6. Bổ sung NK099 — quét nhanh quanh goal

Không thêm file nguồn: social_observation.py thêm FastGoalSweep và hàm
rotation_reference_rate; coordinator/tracking/launch nối quick scan.
Regression trong test_goal_scan_rotation.py mở rộng, chưa chạy. Evidence:
`docs/evidence/2026-11-03/nk099_fast_goal_scan/README.md` và `checks.json`.
Camera coverage là ảnh processed ở hướng đo, không là bằng chứng nhãn xã hội.


## Bổ sung hiện hành NK120 — Paper độc lập

Danh mục lịch sử bên trên không có nghĩa prototype cũ còn được chạy.
`social_navigation_planner/social_navigation_planner/paper_experiment_node.py`
nhận ROS và xuất lệnh cả3xe. Thư mục con `paper_models/` gồm:
`__init__.py` khai báo package; `catalog.py` DOI/trạng thái;
`kinematic.py` V/PurePursuit/VO và outer impedance;
`deform.py` bản chuyển đổi DEFORM;
`environment.py` A* waypoint, clustering/association LiDAR và veto chung.
`social_navigation_planner/test/test_independent_papers.py` chứa regression mới,
chưa chạy. `docs/evidence/2026-11-03/nk120_independent_papers/README.md`
lưu nguồn/giới hạn; `static_checks.json` ghi SHA bảo toàn baseline và AST.
Các README Paper3–12 được viết lại theo trạng thái, chỉ3/4/7 có lệnh chạy.


## Bổ sung hiện hành NK121 — thay nguồn Paper5/6/7

- `social_navigation_planner/social_navigation_planner/paper_models/upstream_sources.py`: tên, URL, commit và loại nguồn của ba mục mới.
- `paper_models/ho_mpc.py`: cầu nối tới HO-MPC/HierarchicalQP tác giả ở cache ngoài repo, cấu hình3omni/horizon4 và task hierarchy.
- `paper_models/drivetrains.py`: HybridA* SE(2), PurePursuit và luật follower omni đổi hệ tọa độ/đội3xe.
- `paper_models/robile.py`: slot quay theo leader, vectorPID và yawP; chuyển từ PyBullet sang Twist Gazebo.
- `scripts/prepare_ho_mpc.py`: người dùng tự tải/kiểm hai commit upstream vào `~/.cache/three-robot-rescue/paper5`, không build/pip/chạy thuật toán.
- `social_navigation_sim/launch/paper5_ho_mpc.launch.py`, `paper6_different_drivetrains.launch.py`, `paper7_robile_formation.launch.py`: wrapper tên mới. Các tên cũ đã xóa tại NK123.
- `README_PAPER5_HO_MPC.md`, `README_PAPER6_DIFFERENT_DRIVETRAINS.md`, `README_PAPER7_ROBILE_FORMATION.md`: đủ lệnh chuẩn bị/build/chạy/ghi/viewer; nguồn và giới hạn.
- `social_navigation_planner/test/test_paper_replacements.py`: regression luật PID/frame và HybridA*; `test_ho_mpc_optional.py`: kiểm solver thật nếu đủ dependency (thiếu thìSKIP). Chưa chạy.
- `docs/evidence/2026-11-04/nk121_papers08_10/`: trạng thái/bằng chứng tĩnh và bảo toàn nguồn baseline.

Các bản ghi cũ mang số8/9/10 giữ nhãn nguồn của chính chúng; không diễn giải
chúng như kết quả của các repository mới trongNK121.


## Dọn nguồn NK122

Paper5/6/11/12 và module legacy method03/04/09/10 đã xóa theo yêu cầu.
Catalog/runner chỉ còn các paper1/2/3/4/5/6/7/8; số giữ nguyên.
Danh sách28file đã xóa: `docs/evidence/2026-11-04/nk122_remove_skipped/deleted_files.json`.
Lịch sử evidence ở danh mục này vẫn được giữ, không phải file runtime.


## Số/tên hiện hành NK123

HO-MPC=Paper5, DifferentDrivetrains=Paper6, Robile=Paper7, DEFORM=Paper8.
Các alias và prototype trùng backstepping/sliding/observer đã xóa.
Script chuẩn bị `scripts/prepare_ho_mpc.py`; test `test_ho_mpc_optional.py`.
Root README và cây nguồn phía trên dùng tên mới; các mô tả NK/evidence
lịch sử giữ theo thời điểm. Danh sách đổi/xóa ở
`docs/evidence/2026-11-04/nk123_names/changes.json`.


## Lưu trữ hiện hành NK124

Hướng dẫn chạy tập trung ở README gốc; docs chứa tài liệu chuyên đề và minh chứng.
Backups hiện giữ3mốc: đầu01/11, NK094/NK095 và nguồn hiện tại trước dọn
04/11. Đã xóa10snapshot trung gian theo yêu cầu; xem backups/README.md và
`docs/evidence/2026-11-04/nk124_backup_cleanup/retention.json`.
Docs/evidence và recordings không bị xóa trong tác vụ này.


## Docs còn giữ sau NK126

Chỉ còn7file hướng dẫn.md tại gốc docs: FILE_CAN_DOC_VA_LENH_CHAY,
DANH_MUC_THU_MUC_VA_FILE, PHAT_LAI_MO_PHONG, CHAN_DOAN_DUNG_XE,
CHAN_DOAN_PHIEN_CHAY, COLLISION_AUDIT, BACKUP_VA_KHOI_PHUC.
Sáu tài liệu chuyên đề/kịch bản cũ đã xóa theo yêu cầu; danh sách tại
`docs/evidence/2026-11-04/nk126_docs_cleanup.json`. Minh chứng và JSON lịch
sử vẫn giữ. Các nội dung cũ trong nhật ký phải đọc theo mốc đã ghi.

NK127 đã xóa mục lục README_PAPERS_03_12.md bị trùng. Tra cứu paper ở README.md mục3 và8READMEriêng; hạ tầng chung ở mục6.5. Không có README thay thế.


## Lưu trữ mới nhất NK128

Theo yêu cầu mới chỉ còn backup `20261104_111229_242934_nk128_keep_current_only`;
6snapshot cũ, gồm mốc đầu/NK094, đã xóa. Thư mục build/ đã xóa, cần build
lại trước khi chạy. Các ghi chú giữ3mốc NK124 ở trên là lịch sử. install,
log, evidence và recordings không xóa trong lần này.
