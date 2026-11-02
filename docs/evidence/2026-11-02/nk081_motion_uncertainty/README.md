# NK-081 — Sửa dự báo vật động và kiểm tra lối né — 02/11/2026

**Trạng thái: chưa xác nhận sửa hết va chạm.** Mã cuối đã build và qua kiểm thử số học; bản ghi Gazebo là bản thử trước khi thu hẹp thay đổi, không phải mã cuối.

## Thay đổi mã cuối

- `moving_obstacles.py`: khi fit vận tốc xuống dưới 0.05 m/s, giữ thêm giả thuyết bằng vận tốc thực sự đo gần nhất tối đa 0.8 giây nếu track còn mới và chưa có bằng chứng đứng yên. Không tăng vận tốc đo bằng giá trị giả định. Nominal track và hạn dùng vẫn giữ; fusion giữ thông tin này mà không tính là thêm phiếu từ cảm biến.
- `dstar_mpc_controller.py`: kiểm tra giả thuyết bổ sung; A* và rollout né loại đường cắt phía trước luồng vật đang tới, cho phép xem xét đi phía sau. Đây là kiểm tra hình học dựa trên vận tốc ước lượng, chưa phải bảo đảm tránh mọi quỹ đạo người.
- Khi command bằng 0 nhưng pose cho thấy xe vẫn trôi, rollout bắt đầu từ vận tốc đo. Nếu vận tốc đo vượt giới hạn lệnh thì phanh, không xuất lệnh né vượt giới hạn.
- Giữ kiểm tra map, LiDAR, xe khác, freshness, gia tốc và toàn horizon; không cấp ground truth cho controller. Không đổi goal, world, lịch người hay defaults camera/xã hội. Normal tracking NK-076 được giữ.

## Một lượt Gazebo đã thực hiện — bản thử không đạt

Camera/person/head/body/social map/observation/auto-observe bật, LiDAR 2 m, server-only. Goal `(1.0815577507, -2.0020322800)`. Đánh giá 0.001–120.001 giây mô phỏng; raw tiếp tục tới 125.601 trong lúc đóng phiên, phần đuôi không tính kết quả.

Physics ghi nhận robot3–tv_viewer_a_walking tiếp xúc **32.117–34.595 s**. Robot1/2 không có contact ngoài nền ghi nhận trong cửa sổ này. Leader cuối cách goal **4.222 m**, chưa tới goal. Không coi việc không lặp lại contact patrol ở 84–88 s là đã sửa được tình huống NK-078 vì quỹ đạo xe đã khác.

Bản thử ban đầu thêm vận tốc giả định khi người mới đi lại, có mẫu nominal khoảng 0.30–0.33 m/s nhưng giả thuyết khoảng 0.68 m/s, nhiều nhánh né bị loại/timeouts và xe vòng xa. Sau lượt này đã sao lưu checkpoint rồi **bỏ cơ chế tăng vận tốc giả định**, chỉ giữ vận tốc đo gần nhất khi mất fit. Chưa tách được tác động nhân quả riêng từng thay đổi. Mã cuối chưa chạy Gazebo; không chạy lần hai theo giới hạn người dùng.

## Kiểm chứng và nguồn gốc

- Mã cuối: **260 test qua**, 2 cảnh báo SciPy clipping; không chạy ba bài ament copyright/flake8/pep257. Xem `final_regression.log`.
- Build planner và sim thành công: `final_build.log`; module install khớp SHA-256 nguồn cuối.
- Thêm 8 test trong `social_navigation_planner/test/test_motion_uncertainty_corridor.py`: không phóng đại tốc độ, mất fit/expiry/đứng yên, fusion, cắt hành lang, trôi sau command0, giới hạn vận tốc.
- `tested_source/`, `source_scope.json`, `trial_regression.log` lưu bản đã thử; `provenance.json` phân biệt hash bản thử và bản cuối. Bản thử có 258 test qua nhưng vẫn thất bại vật lý; test số học không chứng minh né ổn.
- `analysis.json`, raw `.jsonl.gz`, `pre_cleanup.json`, `live.json`, `samples.json` và `checkpoints.jsonl.gz` giữ bằng chứng. Các contact frame có thể lặp cùng sự kiện, không được tính thành số va chạm độc lập.
- Backup trước sửa: `backups/20261102_153811_755576_nk081_motion_uncertainty_corridor_escape/`.
- Backup trước thu hẹp: `backups/20261102_155547_550541_nk081_checkpoint_prior_trial_before_narrowing/`.
  Cả hai đã được script kiểm archive đọc được, SHA-256 nguồn và manifest khi tạo; gồm nguồn/assets/cấu hình/test/tài liệu, không gồm log/build/credentials.

## Xem lượt thử

Tại thư mục gốc dự án:

```bash
python3 scripts/view_replay.py --session recordings/nk081_social_motion_120s_once
```

Bản ghi này thể hiện bản thử không đạt, có ảnh camera/vùng xã hội; không thể dùng nó để kết luận mã cuối đã được thử. Phiên đã dừng. Không commit/push. Bước tiếp theo là người dùng kiểm tra mã cuối ở phiên mới; chưa có benchmark lặp hoặc chứng minh phục hồi đội hình/goal trong mọi tình huống.
