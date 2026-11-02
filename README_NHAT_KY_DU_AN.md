# Nhật ký và bàn giao kỹ thuật cho AI — Three Robot Rescue

**Cập nhật:** 02/11/2026 — múi giờ Việt Nam (`Asia/Ho_Chi_Minh`).\
**Nguồn hiện hành:** NK-087 thêm 10 prototype đối chiếu ba tầng (paper3–12; chưa build/test/Gazebo), baseline giữ NK084.  NK-084 ưu tiên điểm né phía sau theo yaw xe, sau ưu tiên xã hội; 44 test qua, chưa Gazebo.  NK-082 ưu tiên A*/MPC né ngoài planning keepout (40 test qua; Gazebo NK083 chưa đạt); NK-081 thêm giả thuyết vận tốc đo khi mất fit, kiểm tra cắt luồng người và vận tốc trôi/phanh (260 test qua, chưa Gazebo mã cuối); NK-076 sửa tìm kiếm normal tracking sau né; NK-074 bổ sung lớp phủ LiDAR/A*/MPC cho bản ghi; điều hướng NK-073 — sửa fusion vận tốc, chọn lối né/điểm dừng và dự báo xe đang phanh trên nền LiDAR2m NK-071; phát triển từ bản tái dựng NK-060, không khôi phục thử nghiệm NK-035–058.\
**Phiên hiện hành:** Audit NK092 bản `dynamic_20261102_180718_643579943` có contact robot1–người26.834–28.738s; vùng TV có rồi mất. Nguồn NK093 sửa nhánh né và thêm quay quanh goal20cm; chưa kiểm thử runtime. Lỗi vùng TV giữ nguyên theo yêu cầu. Không tự chạy/dừng/push.\
**Báo cáo gửi giảng viên:** [README_BAO_CAO_TIEN_DO.md](README_BAO_CAO_TIEN_DO.md).

## 0. Bàn giao hiện hành — AI tiếp nhận đọc phần này trước

Phần này phản ánh trạng thái cuối đã xác minh ngày 02/11/2026. Các mục
NK phía sau là lịch sử theo thời điểm: tên file, package, nhận định và số
mục của báo cáo trong các mục cũ có thể khác hiện tại. Khi tiếp tục công
việc, kiểm tra mã nguồn thực tế trước khi dựa vào một nhận định lịch sử.

### Checkpoint NK-095 — trước sửa trở về goal

Bản NK093 trong lượt người dùng tới130.801s không ghi contact ngoài nền
cho3xe; chưa goal/scan hoàn tất, chưa là benchmark. Source hash khớp bản ghi.
Người dùng yêu cầu backup/push trước sửa phục hồi goal. Backup được xác minh:
`backups/20261102_184916_116752_nk095_preserve_contact_free_before_goal_recovery`.
Evidence: docs/evidence/2026-11-02/nk095_contact_free_checkpoint/. Giữ nguyên
nhánh né này làm điểm khôi phục. Không coi đề xuất phục hồi là đã sửa.

### Audit vùng TV NK-094 — chưa sửa perception

Bản mới dynamic_20261102_182843_287553000: TV region chớp tắt27–50s,
cuối2→1 tại77.834,→0 tại80.612, vẫn0 đến130.404. TV track còn; camera
vẫn có frame mới. Nguồn lưu75s theo min timestamp TV/vị trí/hướng viewer;
mốc cuối phù hợp expiry nhưng thiếu gate/stamp từng zone để kết luận duy
nhất. Search bị moving safety từ chối khi cần cập nhật. Chi tiết evidence
nk094_tv_region_expiry; chỉ audit, không sửa code/chạy mô phỏng.
Backup cuối:20261102_184257_206365_nk094_tv_region_expiry_audit.

### Nguồn mới NK-093 — chờ người dùng kiểm thử

Sửa nhánh escape chung3xe: bỏ pause cố định khi mất fit, latch đo0.5s,
chờ refuge khi đã tới, thêm rollout ngắn0.6s trong budget hiện có.
Goal<=20cm tự full scan một lần hoàn tất/goal, retry nếu bị ngắt; camera
và observation phải bật. Quay vẫn qua MPC; chưa chứng minh hết contact.
Giữ nguyên lỗi2 vùng TV theo yêu cầu. Chỉ AST/diff, chưa test/build/Gazebo.
Backup cuối: 20261102_181917_162847_nk093_continuous_escape_goal_scan.

### Audit mới NK-092 — robot1 contact, vùng TV mất

Bản người dùng dynamic_20261102_180718_643579943 có contact robot1–người
26.834–28.738s; đã thấy nguy cơ nhưng lệnh né ngắt rồi mọi rollout bị loại,
robot giữ dừng. Vùng TV có13.061–trước16.247s rồi mất, TV track vẫn còn.
Chưa xác định gate mất viewer cụ thể; chưa sửa nguồn/chưa chạy mô phỏng.
Minh chứng: docs/evidence/2026-11-02/nk092_robot1_contact_tv/README.md.
Backup cuối: 20261102_181512_918371_nk092_audit_robot1_contact_tv.

### Cập nhật nguồn NK-091 — chưa kiểm thử runtime

Đã thêm endpoint tiếp cận khi goal bị chặn và tự replan về goal gốc khi
clear. Giữ biên mặc định3cm, chặn cấu hình nhỏ hơn1cm ngoài bán kính xe.
Không có chế độ tiếp xúc chân người. Test mới chưa chạy; không tự chạy mô
phỏng. Backup cuối: `20261102_180407_004374_nk091_goal_approach_recovery`.
Đọc mục NK091 cuối nhật ký và source plan/control_tick trước cải tiến tiếp.

### Audit không trở về goal — NK-090

- Đọc đúng bản ghi mới của người dùng và log coordinator cùng phiên; không
  dùng lại kết luận NK078/NK083. Hash controller khớp diagnostics_config.
- Root cause trực tiếp: `Goal lacks obstacle clearance` → plan return →
  reference rỗng → controller giữ dừng. T106.245 observation/moving safety
  false nhưng replan_required true,9-row path không phục hồi. Leader cách
  goal2.047m. State/scan mới, reference cũ nên không quy watchdog cho camera.
- Vùng xã hội/biên an toàn phù hợp nguyên nhân goal bị chặn: contour cách
  goal0.137–0.146m <0.18m, map vật lý gần nhất1.052m. Chưa có raster sau
  carve để quy chính xác ô/lớp duy nhất. Không đổi goal; đề xuất chờ ngoài
  vùng và replan khi clear, chưa triển khai. Minh chứng:
  `docs/evidence/2026-11-02/nk090_goal_blocked_after_escape/`.
- Giữ hai backup đầu/cuối: bản đầu01/11 và bản cuối
  `20261102_175016_860682_nk090_audit_goal_blocked_after_escape` mới tạo.
  Bản cuối NK089 đã xóa sau khi bản mới được xác minh, giữ số lượng2.

### Dữ liệu cục bộ sau dọn — NK-089

- Chỉ còn hai backup: `backups/20261101_185410_before_nk034_restore/` và
  `backups/20261102_173137_174092_nk089_final_before_backup_build_cleanup/`.
  47 bản trung gian đã xóa theo yêu cầu, đường dẫn lịch sử cũ có thể không
  còn tồn tại. Giữ lịch sử nhật ký, không diễn giải đường cũ như file còn giữ.
- `build/` và `install/` đã xóa;66 mục log build đã dọn. **Cần build lại**
  theo bộ lệnh trong README trước khi chạy; không tự build trong tác vụ.
  Recordings/log chẩn đoán/evidence/source/Git vẫn giữ. Không có mô phỏng
  chạy lúc kiểm tra; không khởi động/dừng mô phỏng để dọn.
- Quy định tạo backup trước cải tiến tiếp theo vẫn áp dụng; đây là đợt
  dọn được người dùng cho phép, không là cơ chế nền tự xóa backup mới.

### Ghi mọi lượt chạy theo từng bộ lệnh — NK-088

- Quyết định mới: mỗi lần chạy mô phỏng cần lưu; README ghép ghi và viewer
  vào ngay mục động/tĩnh/từng paper, không tách mục chạy ghi riêng.
- Dùng `bash scripts/run_simulation.sh dynamic|static|paper1..paper12`.
  Wrapper gọi runner hiện có; mặc định tạo thư mục có profile/thời gian/PID
  và bật diagnose-stop. Các ví dụ đặt `recording_dir` timestamp ngay trong
  khối build/source/chạy, sau Ctrl+C có lệnh viewer dùng đúng biến đó.
- `run_dynamic.sh`, `run_comparison.sh` cũng tự ghi nếu không truyền tên.
  Có thể chỉ định `--diagnose-stop NEW_DIRECTORY`; không ghi đè bản cũ.
  Scene/backend/method/hash theo profile, gồm paper1/2. Không tự bật camera
  ở profile LiDAR-only. Direct `ros2 launch` ngoài wrapper không tự ghi.
- Đây là thay đổi vận hành, không sửa thuật toán. Chỉ kiểm cú pháp/lệnh/
  link/metadata cấu trúc; chưa chạy runtime. Không mở mô phỏng trong tác vụ.
  Quyết định này thay lựa chọn opt-in ghi trước đây, không khôi phục observer
  NK061/log/sessions hoặc dịch vụ nền. Giữ lịch sử các quyết định cũ.

### Bàn giao 10 prototype ba tầng — NK-087

- Nguồn: hội thoại chia sẻ người dùng yêu cầu; bản cuối có ba tầng thực thi.
  Trích literal module bằng AST, không chạy generator/shell/installer ngoài.
  Không tải ZIP sandbox từ phiên khác; nguồn là code xuất hiện trong hội thoại.
- Method01–10 → paper3–12; paper1/2 cũ giữ số. Registry:
  `social_navigation_planner/social_navigation_planner/comparison_methods/registry.py`.
  Adapter `comparison_controller.py` kế thừa safety/escape NK084, tracking
  chạy pipeline phương pháp, không fallback beam baseline khi bị loại.
- Launch `comparison.launch.py method:=01` hoặc `paper3_...` tới `paper12_...`;
  `run_comparison.sh 01` mặc định cảnh động, camera/xã hội bật, quan sát tự quay
  tắt; có `--diagnose-stop NEW_DIRECTORY`. Ba controller mới thay ba MPC cũ,
  coordinator D* vẫn cấp tham chiếu. Không dùng cùng hai launch trong một phiên.
- Đã viết test, chỉ kiểm tra tĩnh; **chưa build/pytest/ROS/Gazebo**. Người dùng
  tự chạy lệnh độc lập trong README từng paper. Không lấy60 test trong hội
  thoại thành kết quả dự án này. Có giới hạn CTC/vision/slip/car-like/DEFORM.
- Hướng dẫn: `README_PAPERS_03_12.md`; từng `README_PAPER3_...` tới
  `README_PAPER12_...`. Chưa là bản tái lập bài gốc hoặc benchmark cải thiện.

### Quy ước làm việc và đọc file — NK-085/NK-086

- Mặc định đưa lệnh build/chạy/test/viewer/phân tích để người dùng tự chạy;
  AI chỉ tự chạy khi yêu cầu hiện tại nói rõ. Không tự đặt goal/mở mô phỏng.
- Đọc đúng phạm vi: bảng `docs/FILE_CAN_DOC_VA_LENH_CHAY.md`, tổng hợp lỗi
  trước, sau đó đoạn log và nguồn liên quan. Không đọc toàn bộ nhật ký/source.
- README gốc chia riêng động/tĩnh/paper/test/ghi lỗi; mỗi chế độ có đủ
  lệnh cd/build/source/chạy, không yêu cầu ghép từ mục khác. Viewer và
  phân tích bản ghi có đủ lệnh riêng, không cần build. Chú giải ở dưới.
  Cấu trúc lịch sử báo cáo/nhật ký/evidence vẫn giữ. NK084 chưa Gazebo;
  kết quả kiểm chứng kỹ thuật giữ nguyên, tác vụ này chỉ sửa tài liệu.

### Bàn giao sửa né — NK-081

- Mã cuối: `moving_obstacles.py`, `dstar_mpc_controller.py`; thêm test
  `test_motion_uncertainty_corridor.py`. Hint chỉ giữ vận tốc thực đo khi
  mất fit, tối đa0.8s và hết khi đứng yên; không synthetic speed prior.
  A*/rollout kiểm cắt phía trước luồng người; rollout xét xe còn trôi sau
  command0, phanh nếu vận tốc đo vượt giới hạn. Không bỏ hard safety checks.
- 260 test qua/2 warning SciPy, ba ament lint chưa chạy; hai package build
  qua, install khớp nguồn. **Mã cuối chưa kiểm chứng Gazebo.** Bản thử trước
  thu hẹp thất bại; không suy ra camera gây lỗi hay bản cuối né ổn.
- Đúng1 lượt theo giới hạn người dùng, không tự chạy lại. Lệnh xem:
  `python3 scripts/view_replay.py --session recordings/nk081_social_motion_120s_once`.
  Đánh giá đến120.001s, tail đóng phiên tới125.601s không tính.
- [Minh chứng/phân biệt bản thử–bản cuối](docs/evidence/2026-11-02/nk081_motion_uncertainty/README.md).
  Bước tiếp: kiểm chứng mã cuối khi người dùng chạy phiên mới; còn mở lỗi
  contact leader và về goal, không coi kiểm thử số học là đã xử lý xong.

### Audit nguyên nhân NK-078 — NK-080

- Đối chiếu GT chỉ offline: R3 t83 track v≈.14m/s trong khi patrol thật
  ≈.404m/s sau đứng/rẽ. Goal né83.0 đi−Y qua y=−2,83.1 đảo goal nhưng
  command còn−Y do giới hạn gia tốc;83.3 toàn rollout bị moving loại.
- R2 t84.0/85.1 track0 dù patrol≈.404, nhánh pause hold. Gate speed<.05
  bỏ risk, nên uncertainty bị xử lý như không có threat động. Chưa có
  trackID/history để quy riêng fit/association/fusion; không đoán bừa.
- Root leader còn dịch≈5.94cm trong83.201–84.151 dù lệnh0 từ83.2;
  chưa kết luận actuator nguyên nhân duy nhất. Sát contact dữ liệu mới/
  compute≈13–26ms, moving rejection; không quy trực tiếp cho camera hay
  social map. Baseline75s không đủ kết luận camera gây hồi quy84–88s.
- Chỉ audit, không đổi code/chạy sim. Bước tiếp sửa uncertainty/restart,
  corridor timing/giữ hướng và pause safety sau khi được yêu cầu; giữ
  các hard checks. [Minh chứng](docs/evidence/2026-11-02/nk080_nk078_cause_audit/README.md).

### Bàn giao camera/vùng xã hội trong replay — NK-079

- Viewer có camera gốc/nhận diện, lớp vùng xã hội theo timeline, timestamp/
  tuổi/nhãn ảnh thưa và PNG ghép camera. HTTP, folder import và HTML export
  đọc perception.jsonl cùng session/epoch; không lấy ảnh tương lai. Vùng
  lấy đường viền publisher, không phải raster keepout sau carve lối thoát.
- Đã đính kèm đầu ra thật NK-078 vào runtime:
  `python3 scripts/view_replay.py --session recordings/nk078_social_camera_120s_once`.
  Bản ghi cũ chỉ6 JPEG rời rạc, capture timestamp không còn lưu; không
  nội suy video. Vùng14–18s và ảnh84.704s xem được; viewer server mã cũ
  cần restart viewer, không restart Gazebo. Các bản ghi khác thiếu dữ
  liệu vẫn báo thiếu. Sau mỗi test gửi lệnh mở runtime như người dùng yêu cầu.
- Recorder opt-in thêm raw/detection ảnh tối đa2Hz mỗi nguồn theo cả sim/
  wall, JPEG75/max cạnh640 ở thread riêng; perception queue32/cap256MiB,
  status riêng. Social marker/status serialize nhẹ. Không tự bật camera
  hoặc nhận diện, không đổi controller. Chạy thường vẫn không ghi.
- File chính: sim/scripts/replay_sensor_recorder.py + replay_perception.py;
  root scripts/view_replay.py/replay_viewer.html/import_perception_replay.py/
  run_dynamic.sh. Các đường dẫn sim đầy đủ dưới social_navigation_sim.
  23 test scripts qua, ROS fixture/read-only và Firefox bản NK-078 qua,
  sim package build qua. Không chạy Gazebo mới/full planner tests.
  [Minh chứng](docs/evidence/2026-11-02/nk079_camera_social_replay/README.md).
  Chưa benchmark overhead; contact NK-078 giữ nguyên, không coi UI là sửa né.

### Bàn giao kiểm thử camera/vùng xã hội — NK-078

- Người dùng yêu cầu đúng1 lượt120s sim có nhận diện xã hội. Đã chạy
  server-only domain66, camera/person/head/body/social map/observation/
  auto-observe bật; LiDAR2m giữ. Goal cũ(1.0815577507,−2.0020322800).
  Không đổi defaults/source navigation hoặc bật direct camera fusion;
  camera tạo planning map cho D*/3MPC, vật động vẫn né theo LiDAR.
- Frames0.001–120.001s: patrol chạm leader84.180–86.253,robot2
  85.647–87.771. Robot1 không contact ngoài nền ghi nhận. Leader trở
  lại goal sau né, cuối cách≈.000122m. Chưa đạt cả3 né an toàn.
- viewing_tv có11 mẫu14.033–18.235; chưa lying_person/lying candidate.
  Có facing_group/person regions, không coi nhãn này là chứng minh đúng
  hành vi xã hội thật. Giữ ảnh camera và outputs để kiểm.
- Sát contact: command0 vì escape_all_rollouts_rejected (moving);
  scan/state≈.1–.2s sim, compute mẫu≈13–26ms. Chưa quy căn nguyên cho
  camera/CPU hoặc khẳng định không có lối. Cần audit capture scans,
  trajectory estimate, geometry và measured robot velocity ở81–89s.
- Runtime recordings/nk078_social_camera_120s_once; mở bằng viewer.
  [Minh chứng](docs/evidence/2026-11-02/nk078_social_camera_120s/README.md),
  [analysis](docs/evidence/2026-11-02/nk078_social_camera_120s/analysis.json).
  Harness SIGTERM trong cleanup làm mất live/samples cuối; raw120s,
  contact/events/params còn đủ, completion.json ghi rõ nguồn phục hồi.
  Đã bổ sung checkpoint trước cleanup (chỉ compile, không chạy lại).
- Không còn process test. Không chạy lượt thứ hai hoặc sửa algorithm.
  NK-076 chỉ75s, không có baseline cameraoff cùng120s nên không quy
  mức hồi quy cho camera. Không push; nguồn né NK-076 vẫn giữ.

### Bàn giao chọn bản ghi — NK-077

- Viewer có thanh Bản ghi trên máy: liệt kê recordings/ đủ scene+frames,
  refresh/mở và chọn thư mục khác (đọc tại browser, không upload).
  Chuyển server session theo URL riêng từng tab, không trộn offset/stream.
  Folder import dừng poll, là snapshot lúc mở; export HTML cũng có nút.
- Sửa scripts/view_replay.py, scripts/replay_viewer.html và test HTTP
  scripts/tests/test_replay_recording_picker.py. Không đổi navigation.
  Server đang chạy mã cũ cần restart **viewer**, không restart Gazebo.
- 20 test scripts/tests qua; Firefox fixture qua. Không chạy/dừng mô phỏng,
  không build/push; không lặp test Gazebo. Xem
  [runbook](docs/PHAT_LAI_MO_PHONG.md) và
  [minh chứng](docs/evidence/2026-11-02/nk077_recording_picker/README.md).

### Bàn giao sửa quay về goal — NK-076

- Người dùng xác nhận cả3 xe né tốt ở lidar_vung_01, chỉ mắc quay về goal.
  Audit toàn record0.001–165.201s không có contact ngoài nền ghi nhận;
  không dùng kết quả contact NK-073 ở lượt khác để phủ nhận lượt này.
- Giữ nguyên AST nhánh yield/escape, tracking rollout nhanh, scan filter,
  peer sweep; đổi fallback normal MPC từ beam12 ngay sang hoàn tất
  width1 trước, ngõ cụt thử3/12 trong100ms cũ. Mọi sweep/cost/limits và
  freshness giữ. Không gửi partial horizon hoặc bỏ collision checks.
  Beam hẹp có thể kém tối ưu cost hoặc cần mở rộng ở ngõ cụt.
- Normal tracking publish telemetry để xóa marker né đã hết hiệu lực.
  248 test qua,2 warning SciPy,3 lint file không chạy;2package build qua.
  Tác vụ chỉ chạy **một** Gazebo server-only riêng, cùng goal bản ghi,
  cameraoff/2m; xem kết quả chốt ở NK-076 cuối lịch sử và
  [evidence](docs/evidence/2026-11-02/nk076_resume_goal/README.md).
- Ràng buộc mới: khi sửa, chỉ chạy mô phỏng test1 lần trong tác vụ như
  người dùng yêu cầu; không tự lặp các lượt Gazebo. Test số học không là
  lượt Gazebo. Không tự push, trước sửa phải backup.

### Audit phiên người dùng — NK-075

- Phiên recordings/lidar_vung_01, robot3 dừng: cửa sổ106.025–126.025s
  có173 decision mpc_compute_budget_exhausted;12 pause hold,2 checked
  escape,2 escape timeout, mỗi loại1 empty/stale reference. Đây là
  lý do trực tiếp từ controller, chưa profile chi phí từng check/CPU.
- Tracking budget .10s wall; khi fallback beam chưa hoàn tất trước hạn,
  code publish_stop phát Twist0. Frame126.301 leader cách goal≈1.72m,
  chỉ có contact nền trong frame đó. Camera process đang tắt. Chưa kết
  luận nghẽn do camera/không thấy đường hay toàn phiên không contact.
- Nguồn/install controller hash khớp. Không sửa navigation, không đổi
  goal hoặc dừng/restart phiên. Safety topic probe timeout12s, không lấy
  đó làm bằng chứng. Bước tiếp profile checked rollout/beam và số check
  trong cùng tình huống trước khi đổi budget hoặc cache.
  [Số liệu](docs/evidence/2026-11-02/nk075_leader_timeout/analysis.json).

### Bàn giao tính năng phát lại — NK-074

- Đã thêm vùng quét theo range_max thực (hiện2m), raw returns và điểm né
  cả3 xe. ◇ là A* proposal; × là MPC thực chọn; nhãn hướng theo thân xe.
  Người trong bán kính và tia gần footprint người là hai trạng thái riêng;
  đối chiếu GT chỉ phục vụ viewer, không cấp vào navigation.
- Ghi **thủ công phiên mới**: `bash scripts/run_dynamic.sh --record-replay recordings/lidar_vung_01`, hoặc --diagnose-stop để có cả lý do
  dừng. Mở `python3 scripts/view_replay.py --session recordings/lidar_vung_01`.
  Chạy thường không recorder; phiên cũ không có scan thì không hồi điền.
- Recorder riêng `social_navigation_sim/scripts/replay_sensor_recorder.py`
  chỉ subscribe scan/escape_path/escape_decision/TF static, ghi
  navigation.jsonl nền1024 queue/128MiB. navigation_status.json báo drop,
  cap/lỗi và writer finish khi kết thúc. TF alias robot-prefix được resolve
  theo cây thật; thiếu TF không chiếu điểm. Capture/receipt tách riêng,
  epoch reset, TTL ẩn dữ liệu cũ. Giới hạn và hướng dẫn trong
  [runbook](docs/PHAT_LAI_MO_PHONG.md).
- Controller chỉ thêm output telemetry tùy chọn, không đổi policy/cost/
  ngưỡng né. Kiểm thử bounded fixture xác nhận command/rollout tương đương
  khi bật/tắt và không đổi command khi publisher lỗi. Không coi đây là sửa
  contact NK-073. Nguồn chính mới: recorder, launch three_robot_sim,
  scripts/view_replay.py, replay_viewer.html, run_dynamic.sh; test
  scripts/tests/test_replay_sensors.py.
- 244 test qua,2 warning SciPy;3 ament lint không chạy. Build2 package qua.
  ROS kiểm soát cả3 nguồn, installed observer và Firefox qua; **pose kiểm
  thử tổng hợp**, không phải lượt Gazebo mới hoặc benchmark RTF/né.
  [Minh chứng](docs/evidence/2026-11-02/replay_lidar_astar/README.md).
  Không khởi động/dừng mô phỏng người dùng hoặc push trong tác vụ này.
- Bước tiếp: ghi phiên mới để đối chiếu thời điểm người vào vòng, returns,
  A* proposal và MPC chọn ngay trước contact. Chưa có raw wheel/actuator
  toàn phiên; giữ các giới hạn NK-073 bên dưới.

### Bàn giao nguồn mới — NK-073

- **Kết quả chốt chưa đạt hết contact:** pha06 đến247.951s, không contact
  trước193.260s; robot2 không non-ground contact nhưng robot1/leader còn
  6 cặp/8 đợt. Contact cuối245.868–247.951 chưa kết thúc khi dừng record.
  Nguồn không được coi là baseline ổn định. Test process đã dừng.
  [Acceptance](docs/evidence/2026-11-02/nk073_motion_escape/acceptance.json),
  [summary](docs/evidence/2026-11-02/nk073_motion_escape/validation_summary.json).
- Fixed refuge giữ trong map qua các tick, wait flow, global goal giữ;
  stop phải terminal holding-safe, cruise chỉ toàn horizon checked nếu
  chưa có nơi dừng (penalty2), không latch endpoint chưa terminal-safe.
  Recovery floor hiện cap radius.30m là kỹ thuật, không đo true body.
- Bước tiếp phải capture raw3scans+capture-pose+wheel velocities/command/
  robot pose trước193/202/208s. Viewer B physics box.88x.62 offset.18 có
  contact; map chủ động không chứa people/scripts. Không bake GT người
  vào map để cho test qua. Probe pha05 lúc sim chậm thiếu mẫu động nên
  chưa xác định nguồn drift. Phân biệt thiếu sensing/geometry với tracking
  response trước khi thêm heuristics. Giữ cải tiến/backup, không mất
  phần robot2 qua full lượt hoặc nguồn NK-071 đầu tác vụ.
- Đã triển khai fusion velocity theo vote nguồn độc lập, chấm connector
  theo flow/giữ heading, rollout có cả cruise và giảm tốc ở goal. Stop
  prediction và peer checks xét velocity robot đo từ pose cùng capture
  stamp, không coi Twist0 là đứng yên ngay. LiDAR2m/cameraoff và goal gốc
  giữ nguyên. Xem mục NK-073 cuối lịch sử và runbook để biết thông số.
- Map-supported motion gate loại fit centre cách occupied physical map
  <.18m khỏi bước tạo track vận tốc; raw scan_points vẫn giữ. Cả own và
  peer scans dùng gate. Mẫu raw ray/map vẫn kiểm cứng, không cho đi xuyên
  vật đã có trong map. Cần kiểm thêm vật thật di chuyển rất sát tường.
- `robot_motion.py` mới; nguồn khác `moving_obstacles.py`, `local_escape.py`,
  `scan_pose_history.py`, `dstar_mpc_controller.py`, wrapper hash mới.
  Test mới `test_motion_consensus_and_braking.py`. Diagnostic ghi measured
  robot velocities và selected_escape_goal/stops/heading; chỉ xem selected
  target là quyết định mới ở reason checked_escape_command.
- Thêm estimated-velocity update từ2 displacement gần nhất nhất quán,
  không đổi hướng chỉ vì một jump. LiDAR pause_reserve giữ thêm radius
  theo speed đã thấy (tối đa.4m) trong2s khi speed<.12m/s, chỉ nếu track
  trước đó từng có speed≥.15m/s. Không coi vật vừa đi rồi dừng là đứng
  yên chắc chắn. Reserve không ghi thành kích thước vật lý đo được.
- Ưu tiên kiểm lại heading đã chọn trước các hướng còn lại trong budget,
  không replay command. Map/ray/moving/peer/freshness vẫn kiểm mới; nếu
  map vừa chặn hướng đó phải bỏ. Test mô phỏng budget bó hẹp và map đổi
  qua. Lệnh hồi quy đầy đủ xem README trong thư mục minh chứng NK-073.
- 234 test qua,2 warning SciPy,3 lint file không chạy. Bản chỉ-stop từng
  làm hồi quy4 ca, đã sửa để bảo toàn cruise và chạy lại toàn bộ. Hai
  lượt Gazebo trung gian có contact, không gộp thành thành công. Lượt
  chốt mới và provenance ở `docs/evidence/2026-11-02/nk073_motion_escape/`.
- Braking reserve coast.3s/deceleration.4m/s² chưa calibrate actuator;
  chưa chứng minh sửa được nguồn physics gây trôi. Không đưa ground truth
  người vào controller, không sửa timeline người hoặc chuyển goal cho test
  qua. Không tự push; normal run vẫn không recording. Build/chạy như mục
  NK-071 bên dưới; --diagnose-stop phải chọn thư mục mới.

### Bàn giao audit bản trước — NK-072


- Đọc [phân tích](docs/evidence/2026-11-02/lidar_2m_01_audit/README.md),
  [số liệu](docs/evidence/2026-11-02/lidar_2m_01_audit/analysis.json),
  [quỹ đạo contact](docs/evidence/2026-11-02/lidar_2m_01_audit/contact_trajectories.png).
  Physics xác nhận robot2↔TV32.117–32.638,leader↔patrol84.382–86.557,
  robot1↔TV-return93.338–95.664; robot1↔leader147.650–147.658 và các
  lần sau. Đợt cuối leader↔TV245.110 còn contact tại cuối snapshot247.101.
- Cả3 có checked_escape_command, camera tránh=false, scan2m. T30 robot2
  local velocity−Y≈.428m/s ngược người thật+Y≈.35; peer1/3 đo+Y≈.31/.33.
  Fusion local-priority loại remote gần.45m dù velocity bất đồng. T30.5/31
  64 rollout bị moving loại;31.5 mới thoát+X,32.117 đã contact.
- Leader t83 command world−X dọc hành lang patrol rẽ−X, chuyển ngang muộn;
  direction đổi nhiều, constant-velocity model chậm cập nhật sau rẽ. A*
  goal chỉ proposal, MPC có thể chọn16 hướng khác, chưa giữ phía né.
- Robot1 command0 ở7 mẫu147–147.6 nhưng root đi.270m, sau đó chạm leader.
  publish_stop phát stationary prediction ngay. Chưa xác định nguyên nhân
  physics/actuator/lệnh khác; cần đo vận tốc thực và wheel/controller,
  không chỉ tăng buffer/chọn điểm xa. Các mẫu scan/state age≈.1s, không
  đủ lý do quy toàn bộ lỗi cho camera/CPU hay nhận diện muộn.
- Chưa đổi algorithm/start/stop simulation/push. Bước tiếp: backup rồi
  sửa motion fusion có confidence, chọn lối ra khỏi corridor và giữ phía
  né khi an toàn, đồng thời sửa dự báo peer/stop theo vận tốc đo. Tái hiện
  các mốc32/84/93/147s rồi kiểm nhiều chu kỳ. Không roll back cả bộ về
  trạng thái cũ hoặc gọi lượt90s NK-071 là an toàn tổng quát.

### Bàn giao nguồn — NK-071 (kết quả runtime mới hơn xem NK-072 ở trên)

- Theo yêu cầu NK-070 và lượt “tiếp đi”: LiDAR vật lý max2m,360°,10Hz sim,
  240 tia; cả3 controller né vật động theo scan, không cần phân loại người.
  Dynamic mặc định tắt camera/detector/social camera/observation. Static và
  hai paper giữ backend; sensor chung đổi2m nên kết quả paper cũ không là
  benchmark của cấu hình mới. Không đưa ground truth người vào navigation.
- Nguồn chính `social_navigation_planner/social_navigation_planner/`:
  `dstar_mpc_controller.py`, `moving_obstacles.py`, `local_escape.py`, mới
  `scan_pose_history.py`. Sensor ở `social_navigation_sim/urdf/3w_v2_multi/lidar.urdf.xacro`.
  Runbook: [LiDAR2m](docs/LIDAR_2M_AVOIDANCE.md).
- Chiếu scan theo pose capture-time, hàng đợi tối đa4 khi pose đến muộn;
  throttle theo capture thay vì receipt. Gom spatial components/fit cung,
  ưu tiên track local và bổ sung track đồng đội không trùng; giữ vận tốc
  cuối tối đa.4s khi mất ước lượng ngắn. Không gán identity người.
- Recovery cho phép tăng separation từ buffer đã overlap; vẫn kiểm map,
  raw ray, peer và moving sweep. A* tối đa160 expansion/15ms trong escape
  budget60ms wall; normal checked full rollout trước beam100ms. Deadline
  hợp tác, không hard realtime; chỉ phát candidate hoàn chỉnh, kiểm lại
  dữ liệu trước lệnh. Watchdog/reference phối hợp, route/goal được giữ.
- Freshness sim≤.3s; wall liveness thích nghi2–12s khi clock tiến, clock
  dừng>2s quay về2s. Sensor quá tuổi/thiếu coverage vẫn chặn. Camera không
  phải điều kiện để chạy nhánh né. Coordinator giữ reference tại pose đo
  khi xe tự né, rồi replan từ pose thực tế.
- Lượt09 phát hiện leader quay về goal trong lúc patrol tạm dừng/rẽ. Bản
  tiếp bổ sung kích hoạt nearby-approach và giữ dừng1.25s sau nguy cơ cuối
  khi track mất risk ngắn; giữ nguyên goal và không chạy mù trong hold.
- Kết quả chốt:217 test qua,2 warning SciPy; build2package qua. Lượt10
  domain54/partition riêng, server-only90.101s sim không contact ngoài nền.
  Robot1/2/3 có quãng đường XY lấy mẫu≈10.82/10.35/8.20m, không chỉ đứng
  im. Leader gần goal lúc74s rồi né patrol; cuối90s còn cách goal≈1.71m,
  follower đang pause-hold. Chưa xác nhận tái lập đội hình sau né cuối.
  Process test đã dừng; không để Gazebo/launch thuộc test chạy nền.
- Build: `source /opt/ros/humble/setup.bash` rồi
  `colcon build --packages-select social_navigation_planner social_navigation_sim --symlink-install`.
  Chạy thường `bash scripts/run_dynamic.sh` không ghi dữ liệu. Chỉ khi cần:
  `bash scripts/run_dynamic.sh --diagnose-stop recordings/ten_moi`, viewer
  `python3 scripts/view_replay.py --session recordings/ten_moi`.
  Không bật lại observer/log/sessions. Không commit/push trong tác vụ này.
- Kiểm chứng, backup và các lỗi giữa lượt xem NK-071 cuối lịch sử và
  `docs/evidence/2026-11-02/lidar_2m_avoidance/`. Chưa benchmark lặp hoặc
  chứng minh an toàn tổng quát; không so RTF các lượt khác GUI/DDS.

### Bàn giao lịch sử — NK-070 (thông số trước NK-071)


- Ưu tiên hiện tại: cả3 xe né người đi tới ổn trước; chưa quan tâm kết quả
  camera. Người dùng nêu bán kính LiDAR2m. Đã kiểm mã: sensor hiện max10m,
  quét ngang360°/5Hz; MPC lấy ray tới3.5m, vật cản tĩnh gần để rollout2.5m.
  Chưa áp dụng giới hạn2m hoặc tự tắt camera trong lượt giải thích này.
- Mỗi controller đang nhận scan của chính nó và hai xe còn lại, ước lượng
  vật động từ cluster/track; đồng thời nhận /leader/people/poses từ camera
  leader, nhập chung camera_motion + team_lidar_motion để né. LiDAR không
  phân loại chắc chắn người; đó là track hình học vật động. Camera bổ sung
  candidate người nhưng không cần là điều kiện bắt buộc để phát hiện vật
  động bằng LiDAR. Tại các ca contact NK-069, risk từ lidar_1/2/3 trong khi
  camera candidate0; có LiDAR nhưng logic freshness/escape vẫn khóa xe.
- Cần ưu tiên nhánh tránh va chạm LiDAR độc lập kết quả nhận diện/quan sát
  camera ở cải tiến tiếp theo; hiện mới ghi quyết định, chưa đổi thuật toán
  hoặc ngưỡng. Báo cáo tiến độ giữ nguyên vì không có cải tiến/kiểm chứng mới.

### Bàn giao nguyên nhân dừng từ chẩn đoán — NK-069

- Bản mới nhất chan_doan_01:1800 frame,0.001–89.951s sim. Contact physics:
  patrol↔robot2 78.918–83.774; patrol↔robot3 83.269–85.393;
  tv_viewer_a_returning↔robot2 86.305–88.834. Không thấy launch khi kiểm,
  không tự chạy/dừng/restart. Chỉ audit, không sửa controller.
- Leader t83.3 reason escape_requires_fresh_sensors_map_and_peers:
  state age wall2.081s>ngưỡng2s, scan sim.1s/wall1.978s, có2 moving risks.
  T83 scan wall4.074s/state wall2.101s. Không phải chỉ thiếu phát hiện;
  camera candidate0 và observation_active=false ở contact không chứng minh
  camera đang quét giữ xe. Chưa đánh giá CPU camera bằng dữ liệu này.
- Robot2 t78.9 escape_all_rollouts_rejected:64 escape.moving, A* không có
  plan. Theo track/prediction đang dùng, gap đệm ban đầu nhỏ nhất−.1833m,
  yêu cầu≥.03m; swept clearance lấy cả điểm xuất phát nên mọi đường ra
  cũng bị loại. Đây là overlap vùng đệm, không số đo penetration vật lý.
  Probe16 hướng và lập luận min-distance xác minh, không chứng minh môi
  trường có một route vật lý an toàn nào cụ thể.
- Điều phối liên tục coordinator_moving_safety_hold/reference_rows0,
  observation_active=false; goal≈(1.0351,−2.0358). Status moving_obstacle
  khiến rút reference. Khi escape không còn active, watchdog lại cần
  reference mới: chuỗi hold làm gián đoạn bám đường, không được đơn giản
  bỏ an toàn/cho chạy xuyên người.
- T75.3 robot2 tính escape≈3627.9ms wall; khi log command, state wall≈4.20s.
  Lệnh né đổi sang0 sau≈.1251s wall (invalid_or_empty_reference), rồi
  watchdog stop. Source đặt guard_wall từ trước tìm kiếm, nên phép tính
  dài còn làm chính guard bị quá hạn ngay lúc xuất lệnh. Timing gồm
  scheduling/instrument, chưa benchmark quy riêng A*/camera hoặc RTF.
- Files robot1/2/3 gần trần20MiB, kết thúc diagnostic83.101/82.639/83.533s
  trong khi replay tới89.951; phù hợp cap, thiếu ngữ cảnh contact86.305.
  Không quy thiếu log cuối là node crash. Cần ghi gọn hơn ở lần cải tiến.
- Minh chứng/source provenance/numerical probe:
  `docs/evidence/2026-11-02/stop_diagnostics_audit/`. Hash code ghi trong
  session khớp snapshot NK-067 trước marker; không nhầm code đang chạy.
  Backup audit `backups/20261102_003151_391359_audit_stop_diagnostics_root_causes/`
  archive/manifest/SHA-256 qua, loại recordings. Chưa push.
- Hướng sửa được đề xuất, chưa triển khai: tránh khóa toàn bộ escape khi
  điểm đầu ở trong buffer nhưng cho phép tăng separation có kiểm chứng;
  chặn tính toán dài/kiểm lại dữ liệu ngay trước phát lệnh; phối hợp guard/
  reference/watchdog và tách freshness sim/wall hợp lý; giảm log trùng.

### Bàn giao đánh dấu mục tiêu — NK-068

- Coordinator vẽ điểm tím/nhãn GOAL trên topic marker đã có của RViz.
  Mọi goal map có tọa độ finite nhận qua set_goal được ghi `goals.jsonl`
  chỉ khi có SOCIAL_REPLAY_DIRECTORY; không phụ thuộc cửa sổ dừng xe.
  `goal_history.py` lưu tọa độ/sim time/epoch/sequence, giữ mục tiêu qua
  reset clock như logic goal hiện hành; không thay goal hoặc thuật toán.
- Viewer có feed /goals, marker vòng/chữ thập tím, số và thời điểm chọn,
  không hiện goal tương lai khi tua, cập nhật khi đổi đích, xuất HTML/PNG
  và mở file offline có goals.jsonl. Bản ghi cũ không tự suy ra goal thiếu.
- Giữ phiên người dùng đang chạy (launch115277 lúc kiểm tra), không restart
  hoặc publish goal/lệnh vào domain31. Nguồn mới cần phiên chạy mới; nếu
  chan_doan_01 đã có, chọn thư mục mới như chan_doan_02 cho cả launch/viewer.
- Backup đầu thất bại do recordings/chan_doan_01 đang cập nhật. Đã snapshot
  nguồn với recordings bị loại trước khi sửa:
  `backups/20261102_002544_359477_mark_selected_goals_in_replay_source_only/`,
  archive/manifest/SHA-256 nguồn và verify lại645 file qua. Nay backup tool
  loại recordings vĩnh viễn; không đụng dữ liệu đang ghi. Giữ archive
  thất bại002443 (không có manifest), không dùng để khôi phục.
- Kiểm chứng:9 test mục tiêu/export/backup qua; ROS coordinator callback
  riêng domain212 xác nhận set_goal ghi đúng và Marker tọa độ đúng; không
  spin điều khiển/Gazebo. Firefox kiểm thời điểm/thay goal/epoch/tua, HTTP
  feed và screenshot qua, build planner qua. Goal trong fixture browser
  là dữ liệu test tổng hợp, không phải goal người dùng chọn trong phiên.
  Minh chứng: `docs/evidence/2026-11-02/goal_markers/`.

### Bàn giao chẩn đoán dừng xe bật thủ công — NK-067

- Chạy `bash scripts/run_dynamic.sh --diagnose-stop recordings/chan_doan_01`
  với thư mục mới. Bao gồm pose/contact replay và cửa sổ lý do dừng tại
 3 controller/coordinator. Camera bật tại NK-067; nay mặc định tắt ở NK-071, goal do người dùng chọn. Viewer:
  `python3 scripts/view_replay.py --session recordings/chan_doan_01`.
  Đọc lỗi bằng `python3 scripts/analyze_stop_diagnostics.py --session recordings/chan_doan_01`.
- Chạy thường không tạo writer; --record-replay chỉ ghi pose/contact.
  Không khôi phục observer/NK-061/log/sessions, không thêm subscriptions
  sensor. Launcher unset hai biến môi trường nếu không bật tùy chọn.
  diagnostics_config.json ghi nguồn module thực tế+hash và giới hạn.
- Nguồn: `stop_diagnostics.py` mới trong package planner, instrument trong
  `dstar_mpc_controller.py`, wrapper run_dynamic.sh, analyzer và test mới.
  Logic dừng có reason, counters A*/escape/MPC cho map/LiDAR/moving/peer,
  sensor capture/receipt/acceptance, ray filter counts, track velocity/TTC,
  command, state/reference ages, A* side/goal, thời gian tính. Coordinator
  có goal/reference/observation và xe nào gần đứng yên để giữ ngữ cảnh.
- Writer buffer3s wall trước, đợi tình trạng dừng≥.5s wall, giữ suốt hold
  và5s wall sau phục hồi,≤10Hz wall. Trigger thêm pose đội mới không đổi
  dù có command; cần đối chiếu pose Gazebo để xác nhận xe kẹt. Queue256,
  trần20MiB/stream, lỗi IO/drop không được biến thành lệnh điều khiển.
  Không lưu pixel hoặc full raw scan; null là không có số đo.
- Kiểm chứng: build planner qua; full regression180 test qua,2 warning
  SciPy,3 lint file không chạy. Test bật/tắt giữ nguyên command/rollout
  trong tracking cả3 xe và ca escape; writer/cap failure/reset/window và
  analyzer qua. ROS smoke domain211: timer thật controller+coordinator
  ghi đúng lý do thiếu đầu vào; không có Gazebo hoặc sensor thực. Wrapper
  với executable launch stub kiểm default/opt-in/không ghi đè qua.
- Backup trước sửa: `backups/20261102_000006_014767_opt_in_stop_diagnostics/`,
  archive/manifest/SHA-256 xác minh qua; phạm vi source/assets/config/test/
  tài liệu, loại runtime/private/generated. Minh chứng:
  `docs/evidence/2026-11-02/stop_diagnostics/`. Hướng dẫn:
  `docs/CHAN_DOAN_DUNG_XE.md`. Không commit/push hoặc đổi goal/ngưỡng/cost.
- Chưa có lượt Gazebo đầy đủ với mode mới, chưa benchmark overhead/RTF.
  Không thể khôi phục sensor/quyết định thiếu ở thu_ne_01. Bước tiếp theo:
  người dùng tái hiện contact với --diagnose-stop rồi đọc dữ liệu để
  khoanh nhánh hold, dữ liệu cũ, reject constraints hoặc thực thi command.

### Bàn giao audit bản ghi mới nhất — NK-066

- Đã đọc `recordings/thu_ne_01/world_frames.jsonl` gồm1619 frame, epoch0,
  t0.001–80.901s. Không tìm thấy process Gazebo/ROS launch khi kiểm; không
  khởi động hoặc dừng simulation. Không bật lại observer NK-061.
- Physics xác nhận robot3↔tv_viewer_a_walking t29.701–32.268s, chạm base,
  mast/lidar/camera và bánh/roller. Leader gần(1.65,−1.89), người x1.6
  đi +Y≈.35m/s. Leader gần đứng yên trước chạm; net displacement28–33s
  chỉ≈.02075m, không đủ gọi là né thành công. Không quy dịch chuyển do
  controller hay bị physics đẩy vì không có cmd_vel.
- Robot2↔patrol_person t79.626–80.901s, còn contact tại cuối bản ghi;
  robot2 gần(1.404,−2.018), người x1.6 đi−Y≈.40m/s. Net displacement
  78–80.901s≈.00225m. Không thấy contact ngoài nền của robot1 trong phạm
  vi này; không suy ra robot1 an toàn ở mọi lượt.
- Không có goal/cmd_vel/LiDAR/camera trong replay; chưa xác định vì sao
  controller giữ xe hoặc sensor có trễ không. Không dùng pose/contact
  để đo perception. Hướng người trước chạm ở hai ca là phía trái thân xe
  theo heading đo, không phải phải màn hình. Bước tiếp: phân tích nhánh
  hold/escape ở controller với kịch bản này, chưa có ủy quyền sửa trong
  yêu cầu chỉ đọc bản ghi.
- Minh chứng chọn lọc/hash/script/đồ thị ở
  `docs/evidence/2026-11-01/latest_replay_audit/`. Backup trước lưu minh
  chứng/tài liệu `backups/20261101_234926_315176_audit_latest_replay_contacts/`,
  archive/manifest/SHA-256 qua; không sao lưu log/recordings runtime.

### Bàn giao xác nhận tiếp xúc physics — NK-065

- Người dùng yêu cầu viền đỏ phải xác nhận tiếp xúc vật lý. Plugin replay
  nay bật ContactSensorData trên các collision có sẵn của robot1/2/3 khi
  có SOCIAL_REPLAY_DIRECTORY. Physics engine điền dữ liệu, không suy contact
  từ khoảng cách/envelope. Thu từng bước sim, gom vào frame20Hz, không đổi
  geometry/mask/command hay đưa ground truth vào navigation.
- Frame thêm physics_contact_source và contacts: cặp model/collision,
  first_t/last_t trong cửa sổ frame, điểm tiếp xúc đầu tiên, max_depth nếu
  có (không có thì null) và số bước ghi nhận. Contact mặt đất vẫn lưu;
  viewer lọc ground_plane khỏi cảnh báo. Viền đỏ=physics, cam=ước tính.
  Bản ghi cũ thiếu contacts được báo chưa có dữ liệu. Không ghi nhận
  contact không tự chứng minh an toàn; proxy collision người khác mesh.
- Giữ quyết định NK-064: không sessions/observer tự động. Chủ động ghi:
  `bash scripts/run_dynamic.sh --record-replay recordings/thu_ne_01`;
  `python3 scripts/view_replay.py --session recordings/thu_ne_01`.
- Backup: `backups/20261101_233137_788739_physical_contacts_replay/`, source
  archive/manifest/SHA-256 qua. Sửa chỉ replay_recorder.cpp, HTML viewer,
  hướng dẫn và hai README. Bốn module navigation byte-match backup.
- Build qua;5 test replay qua. Fixture headless2500 bước/50 frame ghi
  robot3↔person_contact và robot1↔ground_plane; robot2 cách khối10mm
  không contact. Có tọa độ thực; engine không cung cấp depth nên null.
  Đây là primitive fixture, không phải full URDF/người đi/MPC. Giữ main
  tắt, chưa benchmark overhead/RTF hoặc khẳng định né tốt hơn. Minh chứng:
  `docs/evidence/2026-11-01/physical_contacts/`. Chi tiết xem mục NK-065.

### Bàn giao gỡ chẩn đoán theo phiên — NK-064

- Theo yêu cầu người dùng, đã xóa toàn bộ `log/sessions/` (hai phiên, khoảng
  41MB), symlink `log/current`, latest pointer, lock và supervisor log/PID.
  Đây là xóa dữ liệu runtime được yêu cầu, không có bản sao sessions trong
  backup nguồn. Giữ `docs/evidence/` và các backup cũ.
- Đã gỡ `scripts/run_diagnostic_session.py` và `scripts/session_recorder.py`.
  Không còn observer tự nhận camera/scan hoặc ghi summary/events/telemetry
  mỗi lần chạy. ROS/Gazebo vẫn có log vận hành tiêu chuẩn.
- Chạy: `bash scripts/run_dynamic.sh`; camera bật, domain31 mặc định,
  chọn goal RViz, Ctrl+C dừng ROS launch. `run_dynamic_with_logs.sh` là
  alias tương thích và cũng không ghi session. Các lệnh NK-061–063 dùng
  `log/current` trong phần lịch sử bên dưới không còn áp dụng.
- Giữ viewer/pose recorder NK-063 dưới dạng tùy chọn: chủ động chạy
  `bash scripts/run_dynamic.sh --record-replay recordings/thu_ne_01` với
  thư mục mới; sau đó `python3 scripts/view_replay.py --session recordings/thu_ne_01`.
  Chỉ ghi scene/pose, không có observer chẩn đoán. Chạy thường unset biến
  SOCIAL_REPLAY_DIRECTORY để không vô tình bật recorder do env cũ.
  Viewer nay yêu cầu chỉ rõ `--session`, không mặc định `log/current`.
- Backup trước sửa: `backups/20261101_232836_268483_remove_nk061_session_logging/`;
  archive/manifest/SHA-256 xác minh qua; phạm vi nguồn/assets/config/test/
  tài liệu, không dữ liệu log/private/build/install. Không thay core/world.
- Kiểm chứng: bash syntax qua; thử launcher thay duy nhất executable ros2
  bằng stub, xác nhận default tắt ghi, truyền launch args, metadata opt-in
  và từ chối ghi đè thư mục cũ;5 test replay qua. Không mở/dừng Gazebo,
  không benchmark RTF, không commit/push. Báo cáo kỹ thuật giữ nguyên vì
  đây là gỡ lưu dữ liệu vận hành, không cải tiến thuật toán.

### Bàn giao bộ ghi và trình phát lại — NK-063

- Chạy phiên mới có camera và bản ghi: `bash scripts/run_dynamic_with_logs.sh`.
  Sau khi có session, terminal khác chạy `python3 scripts/view_replay.py`;
  trình duyệt localhost:8765. Chọn goal trong RViz như trước. Viewer cố định
  phiên lúc mở; mở lại khi đổi session. Không tự chạy mô phỏng chính trong
  tác vụ này; các phép thử headless riêng đã kết thúc.
- Plugin `social_navigation_sim/src/replay_recorder.cpp` chỉ đọc ECM sau
  update, ghi mọi model/actor cấp world tại20Hz sim vào `world_frames.jsonl`.
  Wrapper đặt `SOCIAL_REPLAY_DIRECTORY`; không có biến này thì không ghi.
  `scene.json` cố định hình học/nhãn theo phiên; dữ liệu đánh giá không đưa
  vào camera/LiDAR/D*/MPC. Không ghi từng joint hoặc mesh biến dạng.
- Nguồn bổ sung: `scripts/replay_data.py`, `scripts/view_replay.py`,
  `scripts/replay_viewer.html`; tích hợp supervisor, CMake, hai world và
  generator. Hướng dẫn đầy đủ: [PHAT_LAI_MO_PHONG](docs/PHAT_LAI_MO_PHONG.md).
  Viewer có tua/bước/chạy, vệt, heading xanh và vận tốc đo đỏ, nhãn hướng
  theo thân, chọn đối tượng và lưu PNG kèm timestamp. Xuất file độc lập:
  `python3 scripts/view_replay.py --session log/current --export log/current/replay.html`.
- Chồng lấn chỉ là hình học ước tính: robot radius.15m/z0..0.2m, primitive
  SDF và xét chiều cao; không contact physics, không mô tả đủ cột/bánh/mesh,
  có thể bỏ sót giữa mẫu. Root roll/pitch chưa biến đổi đầy đủ polygon.
  Không dùng hình đỏ/không đỏ để kết luận tuyệt đối va chạm. Chi phí ghi
  và RTF chưa benchmark. Không dựng pose người giả cho các session cũ.
- Kiểm chứng: build qua;164 test Python qua,2 warning SciPy,3 file lint
  không chạy. World thật riêng ghi50 đối tượng; fixture thêm3 cylinder
  robot scripted ghi53 đối tượng/90 frame và pose thay đổi. Firefox kiểm
  nhãn phải/trái, overlap/chiều cao, bước/tua/chạy và screenshot qua.
  Đây chưa phải thử né với3 URDF/MPC; chưa có phiên main mới có replay.
- Geometry hai world khớp backup khi bỏ duy nhất plugin recorder;4 module
  điều hướng chính byte-match. Giữ baseline/paper/tĩnh/động hiện có.
  Minh chứng: `docs/evidence/2026-11-01/ground_truth_replay/`.
- Backup trước sửa: `backups/20261101_195516_955149_before_ground_truth_replay/`;
  archive đọc được, SHA-256 nguồn/archive xác minh, có manifest. Phạm vi
  nguồn/assets/cấu hình/test/tài liệu, không build/install/log/private.
  Chưa commit/push. Bước tiếp: người dùng chạy phiên mới, gửi PNG có thời
  điểm hoặc file replay để đối chiếu hướng người/xe với log cảm biến.

### Bàn giao phiên đã dừng và phân tích hướng né — NK-062

- Người dùng yêu cầu dừng, báo leader né phải khi người ở phải và muốn
  xem dữ liệu trước khi chỉ ra chỗ sửa. Đã SIGINT supervisor73993; session
  ended19:30:56, launch/recorder exit0, kiểm process không còn stack.
  Không restart hoặc sửa controller trong tác vụ này.
- Người dùng làm rõ xảy ra khi follower né. Lọc lệnh body vy<−.04 của
  leader đồng thời follower có status yielding còn mới<2s wall: có3đoạn
  19:26:08(robot1),19:27:23(robot2),19:29:29(cả2). Không tự gán đoạn gần
  nhất19:30:12 là sự kiện người dùng nói. Right ở đây là body−y, không
  nhất thiết phải trên màn hình Gazebo.
- Scan robot3 gần lệnh nhất ghi right-sector[−135°,−45°] min≈1.088/1.422/
  1.086m. Cam nearest candidate≈1.343/1.218/.853m ở góc+38.8/+11.7/+28.7°
  (trước-trái theo thân). Còn candidate xa4.427m phía trước-phải ở đoạn2.
  Không biết identity người người dùng thấy, không kết luận cam nhìn đúng
  người đó hay LiDAR point là người.
- Đoạn2 scan capture60.4, sim_estimate command61.299, receipt trước lệnh
  ~4.398s wall. Chỉ chứng minh observer không nhận scan mới, chưa chứng
  minh MPC dùng chính frame đó. No-return ray không chứng minh vùng trống.
- Chờ người dùng chỉ thêm trên hình `docs/evidence/2026-11-01/right_escape_audit/body_frame_comparison.png`.
  Dữ liệu/giới hạn/selected events-scans trong cùng thư mục. Backup trước
  cập nhật tài liệu: `backups/20261101_194101_886130_before_stopped_right_escape_audit/`.

### Bàn giao phiên camera và nơi đọc lỗi — NK-061

- Đã chạy baseline khôi phục, camera RGB-D bật, domain31. Supervisor73993,
  launch74012, recorder74011. Session `log/sessions/20261101_192255_199210/`;
  `log/current` trỏ phiên mới nhất, `log/latest_session.txt` chứa đường dẫn.
  Không tự đặt/khôi phục goal; goal nhận từ RViz được ghi trong events.
- Điểm đọc đầu tiên: `log/current/summary.json` (atomic update1Hz wall),
  tiếp theo `launch.log`, `events.jsonl`, `scans.jsonl`, `telemetry.jsonl`,
  `recorder.log`, `session.json`. Không còn stdout chính ở manual_dynamic.log
  khi chạy qua wrapper mới. Các phiên cũ không bị ghi đè.
- `scripts/run_dynamic_with_logs.sh` nay gọi supervisor; mở cả launch và
  recorder, lock tránh trùng phiên của script, Ctrl+C dừng cả hai và cây
  process còn sót. Để dừng phiên detached hiện tại, gửi SIGINT supervisor
  sau khi xác minh PID/cmdline. Không dừng recorder riêng để giữ logging.
- Recorder chỉ đọc; không publish hoặc thay tham số. Camera chỉ metadata,
  không lưu/giải mã pixel; scans có ranges/capture stamp, commands/reference/
  poses và status có sự kiện. Không subscribe raw clock. Sim/capture age
  ước lượng từ pose header, không thay thế đồng hồ physics/contact.
- Hash4 module core vẫn bằng baseline NK-060. Không thêm thay đổi vào MPC,
  detector hoặc world. Không có contact audit của thử nghiệm mới.
- Live xác nhận RGB/depth + cả3 scan +3pose, JSONL đọc được, recorder không
  báo lỗi. Detector có lúc chờ matched RGB-D; nhận frame không chứng minh
  inference/né người ổn. Chưa đo overhead observer hoặc test Ctrl+C trên
  phiên chính đang dùng; không tuyên bố hết lỗi.
- Backup trước sửa: `backups/20261101_191847_271564_before_camera_session_diagnostics/`.
  Hướng dẫn: `docs/CHAN_DOAN_PHIEN_CHAY.md`; bằng chứng startup ở
  `docs/evidence/2026-11-01/camera_diagnostics/`. Không push.

### Bàn giao hiện hành sau khôi phục — NK-060

**Phần này thay thế trạng thái vận hành/nguồn trong các bàn giao cũ bên dưới.**

- Theo yêu cầu người dùng: phục hồi nguồn của lượt hai follower đã né,
  được ghi nhận tại NK-034. Lượt đó dùng mã NK-032; NK-033 ghi source sửa
  tiếp chưa được nạp vào process. Tái dựng từ Git base5ac6982 và bản vá /
  edit nguồn ngày27–28/10, không giả lập một tag NK-034.
- Baseline controller/moving_obstacles/local_escape/peer_safety byte-match
  candidate tái dựng; source perception/world/config/plugin lịch người
  được phục hồi theo lịch sử. World động sinh lại từ generator cũ. Giữ
  hai paper và hai môi trường, cùng tên package/file hiện hành.
- Paper từng là file untracked không có trong Git base: giữ module/test/
  launch đã có, giữ3 chỗ wiring package/backend để paper còn chạy. Không
  tuyên bố toàn workspace bit-for-bit như một archive gốc tại NK-034.
- Không còn inbox/deadline/cooperative hint, compact clock, hoạt ảnh người
  và contact audit của các thử nghiệm sau NK-034. Profile LiDAR-only mới
  cũng đã đưa khỏi nguồn đang dùng; chạy `social_dynamic.launch.py` như cũ,
  mặc định camera/perception bật. Hai follower từng né ở một lượt, leader
  vẫn có lỗi; chưa replay sau khôi phục để xác nhận thành công mới.
- Backup trước phục hồi:
  `backups/20261101_185410_before_nk034_restore/` (585 file,≈70MB, SHA256 qua).
  Checkpoint bổ sung `backups/20261101_190427_973229_before_apply_recovered_nk034/`.
  Snapshot baseline cuối xem `backups/README.md` (không ghi đè archive cũ).
- **Bắt buộc trước mỗi cải tiến:**
  `python3 scripts/create_backup.py --reason TEN_THAY_DOI`;
  chỉ sửa sau archive/manifest xác minh qua. `--verify DUONG_DAN` kiểm lại
  không giải nén. Quy định ở AGENTS.md, hướng dẫn `docs/BACKUP_VA_KHOI_PHUC.md`.
  Không phải cơ chế nền, không cấp quyền commit/push; backups bị gitignore
  và colcon ignore. Không chép credentials hoặc build/install/log/cache.
- Candidate qua159 test Python,2 warning SciPy,3 file lint không chạy;
  build sạch2 package qua. Launch tĩnh/động/Paper1/Paper2 `--show-args` qua,
 4 executable planner còn đủ. Backup tool kiểm source/binary/symlink,
  loại private/generated và phát hiện archive bị sửa.
- Đã dừng launcher/4 navigation nodes cũ; gửi SIGINT trực tiếp server/GUI
  còn sót, GUI cần SIGTERM. Chưa mở lại Gazebo, chưa gửi goal mới.
- Chạy từ root sau source ROS/install:
  `ros2 launch social_navigation_sim social_dynamic.launch.py`, hoặc
  `bash scripts/run_dynamic_with_logs.sh` (domain31, log/manual_dynamic.log).
  Chi tiết/provenance `docs/RESTORE_NK034.md`,
  `docs/evidence/2026-11-01/nk034_restore/`.

### Bàn giao chuyển trạng thái và kiểm quỹ đạo nhanh — NK-058

- Coordinator không clear route mỗi lần nhận moving safety. Khi né, cấp
  reference đủ27 pose: xe active có target giữ tại pose đo; xe khác tiếp
  tục phần còn lại của reference đã có, hết horizon thì giữ endpoint,
  không ngoại suy hoặc reset timestamp cache. Không còn phát reference
  rỗng toàn đội chỉ vì có một xe đang né. Pose stale vẫn cho reference rỗng.
- Sau hazard_clear/normal, chờ ổn định .4s sim (wall cap2.5s), rồi clear/
  replan một lần từ pose thực. Guard phát hazard_clear riêng; normal chỉ
  sau khi emit tracking đã kiểm. Không đồng nhất hết hazard với xe chạy.
- Finite-budget normal MPC kiểm một tracking rollout đủ8 bước trước khi
  branching; nếu hợp lệ thì phát ngay. Escape dùng candidate đầu tiên đủ
  kiểm khi có deadline. Không phát lại command cũ hoặc dùng rollout dở;
  giữ map/LiDAR/track/peer/braking và kiểm tuổi sensor trước emit.
- 241 test Python qua,2 warning SciPy,3 lint file không chạy; build planner
  qua. Live20s sau nạp: robot1/2/3 đi mẫu≈.074/.321/.175m, leader cuối cách
  goal .039m; không có normal-MPC timeout trong status_changes. Vẫn có
  hold track/budget escape/stale; không xem là hết gián đoạn/contact.
- Giữ nguyên Gazebo/lịch người. Restart riêng coordinator+3 MPC và phát
  lại đúng goal từ endpoint path: `(1.0351457595825195,-2.6798601150512695)`.
  PID mới68536(coordinator),68537/68538/68539(MPC). Cả4 detached, launcher
  gốc không quản lý chúng; khi tắt phiên phải xác minh và dừng cả4 riêng.
- Stdout4 node mới và minh chứng:
  `docs/evidence/2026-11-01/stable_handoff/`. Observer đã kết thúc. Không push.

### Bàn giao chạy–dừng gián đoạn — NK-057

- Mẫu10s chỉ đọc tiếp theo: robot1/2/3 có2/28,6/27,2/31 lệnh khác0.
  Leader thay đổi giữa hold do track/hết budget, scan quá tuổi và có escape.
  Ngay beam1 vẫn có normal MPC hết budget; NK-056 chỉ gỡ đứng im hoàn toàn,
  chưa làm điều khiển liên tục. Không gọi kết quả trước là khôi phục ổn định.
- Code coordinator phát reference rỗng khi bất kỳ moving safety active;
  hết nguy cơ lại replan. Nếu local escape không ra lệnh, cả việc bám đường
  và né có thể cùng dừng. Audit này chưa thu reference đồng bộ để định lượng
  vòng lặp; `normal` chỉ là hết nguy cơ ở guard, không chứng minh cmd khác0.
- Không đổi code/goal/restart trong audit. Minh chứng
  `docs/evidence/2026-11-01/stop_go_audit/runtime.json`.

### Bàn giao phiên chạy và lỗi đứng im — NK-056

- Đã mở phiên mới18:24 ngày01/11, LiDAR-only domain32; ban đầu không còn
  tiến trình cũ, không cần kill phiên khác. Gazebo/RViz và3 MPC chạy, contact
  coverage đủ3 robot/14 proxy. Budget runtime xác nhận60ms/8ms. Không tự gửi goal.
- Người dùng chọn goal rồi báo xe không chạy. Chẩn đoán đầu: inbox mới
  gộp theo topic, làm hai callback `/map` (planning/physical) ghi đè nhau.
  `LatestInputs` nay gộp theo (topic,callback), giữ mỗi consumer nhận mẫu mới.
- Sửa inbox xong lộ lỗi budget: normal beam12 không hoàn thành horizon trong
  60ms nên luôn stop. Finite-budget normal pass dùng beam1 mỗi depth để
  ưu tiên hoàn tất horizon; nhánh không budget vẫn12. Đổi này có thể giảm
  khả năng chọn phương án vòng cục bộ, chưa benchmark chất lượng tối ưu.
- Chỉ restart ba MPC hai lượt áp dụng sửa; giữ nguyên Gazebo/bộ điều phối/
  goal. Goal gần nhất đọc log `(1.03515,-2.67986)`, chỉ ghi nhận, không publish lại.
  MPC mới PID66269/66270/66271; không còn do launcher chính quản lý ba PID
  thay thế này, nếu cần đóng phiên phải dừng chúng riêng sau SIGINT launcher.
- 25 test mục tiêu qua (14 early/input/budget và11 formation MPC), build qua.
  Mẫu10s sau sửa: cả3 có cmd khác0 và dịch chuyển khoảng .184/.161/.094m.
  Leader vẫn có no verified escape/track và budget hết; chưa hết va chạm,
  chưa đảm bảo đến goal. Không gọi đây là benchmark né thành công.
- Minh chứng `docs/evidence/2026-11-01/map_inbox_fix/`; stdout controller mới
  là `robot*_distributed_mpc_final.log`, launch log vẫn `log/manual_lidar_only.log`.

### Bàn giao phản ứng sớm và callback — NK-055

- `moving_obstacles.py`: hai mẫu cách nhau>=.1s, dịch chuyển>=.03m và vận
  tốc hợp lệ tạo provisional motion; ba mẫu vẫn là confirmed. TTC nhận
  vận tốc world đo được của xe, tính vận tốc tương đối. Một mẫu chưa được
  dùng để suy vận tốc; không nới body clearance/TTL.
- MPC dùng MultiThreadedExecutor2 threads, ingress callback group riêng
  chỉ ghi `LatestInputs` (mỗi topic một message). Control/watchdog vẫn cùng
  nhóm mutually-exclusive; state chỉ được cập nhật khi drain, giữ receipt
  wall time thật thay vì tính lại lúc drain. Nhận dữ liệu tách khỏi tính
  đường nhưng chưa có hard real-time/GIL isolation.
- Budget mềm: control60ms, A*8ms, parameter ràng buộc0<search<control<100ms.
  Kiểm deadline giữa candidate/step/search; chỉ quỹ đạo đủ bước được phát.
  Hết ngân sách khi chưa có quỹ đạo đủ thì stop. Ưu tiên kiểm hướng gợi ý,
  đường local và hướng ngang trước để tránh starvation theo compass.
- 234 test Python qua (2 warning SciPy,3 ament lint file không chạy), build
  planner qua. Kiểm ROS domain99 riêng: actual MPC ingress nhận scan khi
  control group bị giữ; probe chờ Event có nhả GIL, không chứng minh CPU-bound
  latency. Chưa replay Gazebo ca va chạm; chưa đo tỷ lệ hết contact hay RTF.
- Bản đang chạy không tự reload. Không đổi goal/restart/pause hoặc push.
  Minh chứng `docs/evidence/2026-11-01/early_reaction/`.

### Bàn giao phối hợp hướng né — NK-054

- Thêm `cooperative_escape.py`: đọc prediction MPC và safety yielding đã
  kiểm tra của đồng đội. Ưu tiên tham khảo robot1→robot2→robot3 để không
  tạo vòng lặp sao chép; leader có thể tham khảo cả hai follower. Đây là
  hướng ưu tiên, không phải khóa hành lang/điều phối lịch thực thi toàn đội.
- Điều kiện nhận: peer trong2.5m, prediction và status mới<.4s sim/<2s wall,
  dự đoán vị trí hiện tại lệch pose đo<=.12m, rollout có dịch chuyển>=.04m.
  Dừng/hold/normal thu hồi gợi ý. Reset clock xóa state phối hợp.
- `local_escape.plan_escape` thêm đích theo hướng world của peer, dịch về
  vị trí xe nhận; rollout thêm hướng và chi phí alignment chỉ giữa ứng viên
  đã an toàn. Không sao chép endpoint/lệnh, không bỏ kiểm map/LiDAR/người/peer.
- Không ép xe bị người đe dọa đứng chờ. Chưa có cam kết/quyền ưu tiên độc
  quyền hay giao thức ACK. Predicted peer motion vẫn được kiểm theo thời gian
  như trước; không coi hướng của peer là bằng chứng hành lang trống.
- Test mới12 ca qua, bao gồm leader dùng hướng follower và từ chối nếu xe
  thứ ba chắn. Hồi quy toàn bộ224 test Python qua (2 warning SciPy,3 file
  ament lint không chạy). Build planner qua. Kiểm tra Gazebo bản mới chưa chạy; phiên
  đang mở không tự nạp code. Minh chứng `docs/evidence/2026-11-01/cooperative_escape/`.

### Bàn giao audit phiên mới — NK-053

- Session contact mới `1793519553895176935`, LiDAR-only domain32. Xác nhận
  robot3 chạm `tv_viewer_a_returning` sim106.239→108.617s, kéo dài2.378s.
  Bản sửa NK-052 chưa giải quyết hết va chạm; log runtime có `rejected` mới.
- Mẫu15s wall sau contact, sim149.24→153.43: leader có11/58 lệnh tịnh tiến,
  có `A*=rear` và reactive fallback; nhiều hold `track:64`, xen stale scan.
  Robot2 cũng có fallback và hold track. Không suy gap âm của estimator
  thành contact physics, không quy nguyên nhân trước contact từ mẫu sau.
- Goal giữ `(1.08156,-2.64636)`; không sửa code/restart/pause. Minh chứng
  `docs/evidence/2026-11-01/leader_contact_recheck/`.

### Bàn giao bản sửa né — NK-052

- Đã sửa `DistributedRobotMPC.escape_map_step_free`: khi tracking đang nằm
  trong đệm map nhưng còn clearance ít nhất robot_radius+0.01 m, chỉ cho
  sweep không giảm clearance và endpoint tăng clearance. Đích dừng phải ra
  khỏi toàn bộ đệm. Nếu đã thiếu khoảng hở thân xe, vẫn từ chối.
- Các nhánh A* và rollout khẩn cấp dùng chung predicate; log hold thêm số
  ứng viên bị loại lần đầu theo map/lidar/track/peer/peer_braking/terminal.
- Hàng đợi cloud ở `scripts/leader_obstacle_scan.py` và scan ở ba MPC dùng
  BEST_EFFORT depth1, không đổi TTL/geometry/số tia. Chưa đo hiệu quả latency/RTF.
- Đính chính giải thích hội thoại: coordinator đã có `moving_safety_callback`
  yêu cầu replan về goal cũ khi safety chuyển normal; không thiếu hoàn toàn
  cơ chế phục hồi sau né. Nó vẫn có thể bị freshness/clearance chặn.
- 212 test Python qua; 2 warning SciPy; 3 ament lint file không chạy. Build
  2 package qua, projector install trùng nguồn. Test tổng hợp cùng tình
  huống sát tường/không reference: predicate cũ fail cả ba vai, mới pass cả ba.
- Chưa replay Gazebo ca NK-051, chưa chứng minh hết va chạm hoặc RTF tăng.
  Không restart phiên đang chạy; process cũ không tự nạp logic mới. Lượt
  launch mới mới dùng bản sửa. Không push. Minh chứng:
  `docs/evidence/2026-11-01/escape_margin_fix/`.

### Bàn giao kiểm tra phiên mới — NK-051

- Người dùng đã mở phiên LiDAR-only domain32; audit chỉ đọc, giữ goal
  `(1.15016,-2.51884)`, không restart/pause hoặc chỉnh điều khiển.
- Physics xác nhận `robot3|tv_viewer_a_walking` chạm thân leader từ sim
  29.751 đến 35.557 s (5.806 s). Coverage đủ 3 robot/14 proxy người.
- Mẫu sau contact: RTF tức thời .2111; đoạn 15 s wall đạt .246.
  Leader cuối mẫu cách goal .0483 m, phát 3/47 lệnh tịnh tiến khác 0;
  robot2 có 10/41, robot1 có 6/51. Không coi số lệnh là tỷ lệ né thành công.
- Leader còn giữ dừng do không tìm được escape an toàn và dữ liệu quá tuổi;
  follower2 có escape. Chưa có lệnh/scan đồng bộ trước contact để quy nguyên nhân.
- Minh chứng: `docs/evidence/2026-11-01/collision_live_audit_143718/analysis.json`,
  contact JSONL và `followup/summary.json`. Bước tiếp: replay có kiểm soát,
  thu trước/sau va chạm; tách lỗi freshness, kiểm rollout và động học thực tế.

### Trạng thái hiện hành — bổ sung tới NK-047

- Có profile `lidar_only_dynamic.launch.py` và `scripts/run_lidar_only_with_logs.sh`:
  tắt RGB-D/DNN/suy luận xã hội, giữ mast và LiDAR đa tầng leader, cả ba MPC.
  `leader_rgbd` độc lập `leader_camera`; mặc định profile động thường vẫn bật RGB-D.
- Phiên thử hiện dùng ROS_DOMAIN_ID=32. Không tự phát goal: goal cuối đọc ở
  thử NK-042 là `(1.0355337858,-2.3932342529)`, chỉ là lịch sử sau restart.
- Theo quyết định NK-047: người đi theo lịch thời gian mô phỏng, **không
  giảm tốc/dừng nhường robot**; robot phải tự né. Giữ acceleration/deceleration
  và quay chậm theo tuyến, dừng theo hoạt động xem TV/bình nước/ngồi ghế. Skeleton walking dùng asset có attribution
  `models/person_walking/`; nguồn plugin `src/social_scenario_motion.cpp`,
  bộ sinh `generate_walking_people.py`, `generate_social_dynamic_world.py`.
  Giữ cảnh tĩnh và backend planner. Không gọi thay đổi người là sửa né leader.
- Test Python mới: `test/test_pedestrian_motion.py`; test C++ chạy plugin thật
  với ECM tổng hợp: `test/test_pedestrian_plugin.cpp`. Cách chạy riêng:
  `cmake -S social_navigation_sim/test/pedestrian -B /tmp/pedestrian-test`,
  `cmake --build /tmp/pedestrian-test`,
  `ctest --test-dir /tmp/pedestrian-test --output-on-failure`.
- Actor chỉ hiển thị; collision model kinematic cùng pose. Nhường người không
  bảo đảm robot không đâm người đang đứng; chưa có né người–người, hoạt ảnh
  đứng/ngồi/uống hoàn chỉnh, hiệu chuẩn sinh cơ học hay benchmark có lặp.
- Với `reactive_yield=false`, marker động dùng mẫu lịch theo sim time,
  khớp plugin không còn chậm/dừng vì robot. Ground truth chỉ dùng để hiển
  thị kịch bản, không cấp cho perception/planner. Các mục NK-043–046 ghi
  cơ chế nhường là lịch sử đã được thay đổi bởi NK-047.
- Minh chứng NK-042: `docs/evidence/2026-11-01/lidar_only_trial/`;
  NK-043: `docs/evidence/2026-11-01/realistic_people/`.
- Vấn đề leader cũ vẫn mở: thiếu fresh scan, reference rỗng gần goal,
  nhiều lần no verified safe escape. Bước tiếp: thử tình huống chạm có kiểm
  soát, ghi contact/clearance và tuổi scan, tách hiệu quả người nhường với
  hiệu quả robot tự né; không suy thành công từ marker/animation.

### Bổ sung bàn giao NK-044/NK-045 — 01/11/2026

- NK-044 audit không sửa controller: leader vẫn có các đợt dừng do track
  chặn MPC bước 1, scan quá tuổi và reference rỗng; có phát lệnh A* né nhưng
  chưa chứng minh né người thành công. Goal lượt cũ `(1.08156,-2.57733)` chỉ
  là lịch sử; không tự phát lại sau restart.
- NK-045 sửa GUI actor: Fortress `Actor::SetTrajectoryPose/SetAnimationTime`
  thay đổi Data() nhưng không tự SetChanged. Plugin phải đánh dấu thay đổi
  TrajectoryPose và AnimationTime để GUI nhận state mới. Trước sửa, pose
  physics/sensor thay đổi nhưng ảnh GUI actor đứng nguyên; không dùng test
  ECM đơn thuần làm bằng chứng animation hiển thị.
- Đã mở lại profile LiDAR-only domain32; không gửi goal. Người đi bộ dùng
  skin áo xanh lá/quần xanh, khác avatar đứng áo trắng trong cảnh. Hai ảnh
  sau sửa xác nhận patrol di chuyển; test C++ có thêm assert change flags.
  1 CTest và 3 Python test mục tiêu qua; không chạy lại toàn bộ 186 test
  vì sửa chỉ ở đồng bộ GUI actor. Chưa xác nhận đủ chu kỳ hoặc hết va chạm.
- Camera và scenario_annotations vẫn tắt trong profile này, nên RViz không
  có marker người từ hai nguồn đó. Marker phản ứng đang dùng dynamic_pose
  có nguy cơ thiếu pose proxy static; cần kiểm riêng nếu bật annotation,
  không suy lỗi render Gazebo chỉ từ RViz.
- Minh chứng: `docs/evidence/2026-11-01/actor_visibility/after/` có hai ảnh,
  pose và comparison; `leader_audit_current/`, `leader_audit_encounter/`
  giữ audit leader. Các script monitor đã kết thúc, không có theo dõi nền.

### Bổ sung bàn giao NK-046 — hướng model đi bộ

- Đã sửa lệch 90°: walking asset hướng +X, không dùng góc +pi/2 của model
  khác. `generate_walking_people.py` đo forward từ hai cặp Foot→ToeBase ở
  rest skeleton và tốc độ từ quãng đường root clip. `loops.json` hiện có
  mesh_forward_yaw≈0,000576 rad, reference_speed≈0,241573 m/s.
- Generator world ghi `animation_forward_yaw`; plugin hiển thị yaw bằng
  yaw quỹ đạo trừ yaw forward của mesh. Không đổi route/goal/controller.
- 187 test Python qua (2 warning SciPy, 3 lint file bỏ qua); 1 CTest qua,
  trong đó 4.730 mẫu dịch chuyển kiểm hướng render khớp vận tốc qua hai
  chu kỳ tuyến trong ECM tổng hợp. Có hai ảnh/state Gazebo sau sửa, đoạn
  thẳng. Chưa đánh giá gait/foot slip hay đầy đủ chu kỳ Gazebo.
- Phiên mới LiDAR-only domain32 đang mở, không tự publish goal. Lỗi leader
  và peer-spacing vẫn độc lập. Minh chứng `docs/evidence/2026-11-01/walk_heading/`.

### Bàn giao điều hướng hiện hành — NK-048

- NK-034 là đính chính quan sát: hai follower né được ở lượt đó, leader còn
  va chạm; không phải Git tag/source snapshot. Giữ kiểm thử hình học follower
  đã ghi, chạy lại với cả hai vai follower; không khôi phục mù toàn bộ code.
- `local_escape.py`: thử sáu đích né thẳng trái/phải/sau bằng cùng predicate
  swept/terminal trước khi mở lattice A*. Budget tính cả kiểm tra trực tiếp.
- MPC có nhánh né cục bộ khi rollout bị track đã xác nhận chặn dù người
  chưa đe dọa robot đứng yên. Giữ nhánh này tối đa 2,5 s khi reference rỗng,
  vẫn kiểm freshness/map/raw scan/body/peer/gia tốc mỗi rollout. Không nới
  footprint/TTL. Khi hold, status có thêm nearest track và nguyên nhân sensor.
- Bổ sung khoảng dự phòng peer theo tuổi pose, coordinator phục hồi khi
  spacing<.48 m, hướng tới .56 m, trước footprint.32 m. Chưa chứng minh hết
  mọi tiếp xúc Gazebo; không coi test kinematic là benchmark collision-free.
- Nguồn pose/clock mới: `src/navigation_state_stream.cpp` trong simulator,
  cài bằng CMake, có trong cả world static/dynamic. `/gazebo/world_poses`
  chỉ mang ba model robot, 20 Hz sim; không còn deserialize cả link stream.
  `/navigation/clock` 100 Hz sim chỉ cho coordinator/MPC qua launch remap.
  `/clock` đầy đủ giữ cho điều khiển bánh xe/physics; LiDAR, step physics
  không đổi. Stamp đặt ở từng Pose lẫn Pose_V; record pose giữ capture stamp.
  Scan chấp nhận tối đa20 ms lệch tương lai do transport, vẫn TTL .3 s.
- Actor animation/trajectory đánh dấu PeriodicChange, stream GUI dynamic
  state30 Hz wall (paused10), giữ bước chân/căn hướng/người không nhường xe.
- Phiên LiDAR-only domain32 được mở đủ ROS theo nhóm tiến trình tách terminal.
  Không tạo service/autostart hay tự theo dõi nền. Chỉ restore goal cuối từ
  log nếu chưa có goal mới; giá trị log có làm tròn, xem `goal_restore.json`.
- 199 test Python qua, 2 warning SciPy, 3 file lint bỏ qua; CTest plugin qua.
  Minh chứng trong `docs/evidence/2026-11-01/avoidance_rework/`: profiler,
  các mẫu CPU/RTF, tái hiện trước/sau, ca follower và test. Xem giới hạn ở
  NK-048 trước khi tuyên bố follower/leader đã tránh hoàn toàn an toàn.

### Trạng thái vận hành — NK-049

Người dùng yêu cầu tạm dừng phiên hiện tại. Gazebo dynamic đã được gửi
pause, giữ vị trí/goal; không tự resume hoặc tiếp tục thử nghiệm. Bản cuối
NK-048 có thêm vận tốc tương đối từ lịch sử pose và dự phòng quãng đường
hãm (giả định deceleration .15 m/s², chưa hiệu chuẩn). Test cuối199 ca qua.
Lượt Gazebo60 s cuối: min tâm lấy mẫu robot2/leader≈.427 m (>footprint.32 m),
RTF toàn mẫu≈.39; chưa có contact sensor/benchmark lặp. Xem
`docs/evidence/2026-11-01/avoidance_rework/runtime_braking/analysis.json`.

### Bàn giao contact hiện hành — NK-050

- Người dùng báo vẫn thấy người đâm leader sau NK-048. Không dùng min
  khoảng cách lấy mẫu .427 m để phủ nhận quan sát này hoặc tuyên bố hết lỗi.
- Thêm `src/collision_audit.cpp`: đọc contact thực từ physics qua component
  ContactSensorData của collision proxy, không đo khoảng cách để tạo sự kiện.
  Cả hai world khai báo human model đầy đủ; không đổi hình học/điều hướng.
- `scripts/collision_monitor.py`, `contact_events.py`: JSONL begin/end/reset,
  update đầu nếu tham gia giữa contact, marker đỏ; không phát command hoặc
  nhãn perception. Launch xã hội tự bật, kể cả camera-off. Xem hướng dẫn
  `docs/COLLISION_AUDIT.md` và `/collision_audit/{events,status,markers}`.
- Current main simulation không còn tiến trình khi kiểm tra nạp trực tiếp;
  dịch vụ add-system timeout, chưa gắn vào phiên cũ. Không biết nguyên nhân
  đóng phiên; không tự mở lại/resume vì yêu cầu pause NK-049 vẫn giữ.
  Bản mới tự bật đo ở lần chạy tiếp theo. Chỉ chạy fixture riêng để kiểm chứng.
- Physics fixture robot1/2/3 có begin/end thật, near-miss không có. Đường
  physics→bridge ROS→JSONL/marker đỏ đã qua trong domain94/partition riêng.
  208 test Python qua (2 warning SciPy, 3 lint file không chạy); chưa đo
  overhead/full-URDF encounter.
- Không có contact sensor ở các lượt NK-048 cũ; dữ liệu mới không hồi suy
  hoặc xóa kết luận lịch sử đó. Bước tiếp theo: chủ động chạy ca người–leader
  với contact mới, đồng bộ scan/state/cmd và video; chỉ resume theo yêu cầu.

### 0.1. Mục tiêu và các quyết định cần giữ

- Duy trì D* Lite + ba MPC với vùng xã hội đã sửa làm backend chính.
- Giữ hai backend Paper1 GWO–WOA/DWA và Paper2 APF–MPC để đối chiếu,
  cùng code/test. Chưa có kết quả chứng minh backend nào tốt hơn.
- Giữ hai môi trường tĩnh `social_static` và động `social_dynamic`.
- Tiếp tục cải tiến vùng xem TV, chuyển hoạt động, người đi bộ/người nằm
  và điều hướng đội hình từ cảm biến. GCFF chỉ được đề xuất, chưa triển khai.
- Chỉ push GitHub khi người dùng yêu cầu rõ trong tác vụ hiện tại; không
  tự push sau mỗi sửa đổi. Người dùng đang tự chạy mô phỏng và để AI đọc
  log/chẩn đoán; không tự dừng hoặc khởi động lại lượt chạy của họ.
- Người dùng yêu cầu giữ goal RViz khi chẩn đoán. Goal mới nhất đọc từ
  log NK-040 lúc kiểm tra khởi động là `(1.24217,-2.67986)`; các goal NK-033
  và trước đó là lịch sử, không được tự phát lại. Người dùng có thể tiếp
  tục đổi goal trong phiên mới; đọc log hiện tại trước mọi chẩn đoán.
  Không lấy goal cũ hoặc chạy helper mặc định để ghi đè đích hiện tại.
- Báo cáo chỉ nêu cải tiến bản sau so với bản trước và bằng chứng. Nhật ký
  giữ cả lịch sử kỹ thuật/vận hành và ngữ cảnh để AI khác tiếp tục.

### 0.2. Cây nguồn và nơi cần sửa

Có hai package: `social_navigation_planner` và `social_navigation_sim`.
Chỉ sửa nguồn; không sửa bản sao trong build/install. Không dùng các tên
package/launch cũ từ tab IDE hoặc từ NK cũ để gọi lệnh.

| Thành phần | File hiện hành cần đọc |
|---|---|
| Coordinator D* Lite, tham chiếu đội hình, ba MPC | [dstar_mpc_controller.py](social_navigation_planner/social_navigation_planner/dstar_mpc_controller.py) |
| Đội hình và tránh kẹt | `moving_formation.py`, `adaptive_leader.py`, `leader_follower.py`, `turnaround.py`, `separation_recovery.py`, `grid_clearance.py`, `peer_safety.py` trong namespace planner |
| Hai backend paper | `paper1_gwo_woa_node/core.py`, `paper2_apf_mpc_node/core.py` trong namespace planner; tên node/core là hai file riêng |
| Chuỗi khởi động | [social_navigation.launch.py](social_navigation_sim/launch/social_navigation.launch.py) → [dstar_mpc.launch.py](social_navigation_sim/launch/dstar_mpc.launch.py) → [three_robot_sim.launch.py](social_navigation_sim/launch/three_robot_sim.launch.py) |
| Profile động | [social_dynamic.launch.py](social_navigation_sim/launch/social_dynamic.launch.py) |
| RGB-D, detector và pose | [leader_person_detector.py](social_navigation_sim/scripts/leader_person_detector.py), `rgbd_pairing.py`, `body_pose_estimation.py`, `head_pose_estimation.py` |
| Tracking, TV và map xã hội | [social_costmap.py](social_navigation_sim/scripts/social_costmap.py), `camera_people_tracking.py`, `color_attention.py`, `colorful_targets.py`, `social_space_inference.py` |
| Người nằm và lượt nhìn | `human_posture.py`, `posture_proposals.py`, `route_inspection.py`, `social_search.py`; `social_observation.py` trong planner |
| Dự báo và nhường người đang tiến tới | [moving_obstacles.py](social_navigation_planner/social_navigation_planner/moving_obstacles.py), `DistributedRobotMPC` trong controller; [hồi quy](social_navigation_planner/test/test_moving_obstacle_safety.py) |
| Đích né tạm A* và ưu tiên hơn camera | [local_escape.py](social_navigation_planner/social_navigation_planner/local_escape.py), `moving_safety_callback` của coordinator; [hồi quy](social_navigation_planner/test/test_escape_and_observation.py) |
| Lịch và hình học mô phỏng | `scripts/generate_social_static_world.py`, `generate_social_dynamic_world.py`, `scenario_motion.py`, `src/social_scenario_motion.cpp` trong simulator |
| Hồi quy | `social_navigation_planner/test/`, `social_navigation_sim/test/`; giữ `test/fixtures/my_maze.pgm` vì test phục hồi cần nó |

Tên rút gọn `paper1_gwo_woa_node/core.py` ở bảng trên nghĩa là
`paper1_gwo_woa_node.py` và `paper1_gwo_woa_core.py`; tương tự với Paper2.
Các helper không có executable riêng vẫn có thể là phụ thuộc đang dùng.

### 0.3. Luồng dữ liệu và giả thiết

Gazebo phát RGB-D/LiDAR; `leader_person_detector.py` chọn capture hợp lệ
rồi chạy detector/pose. `social_costmap.py` nhận quan sát/tracking, tạo
`/social_navigation/map` từ map vật lý và các vùng có bằng chứng. Coordinator
và ba MPC cùng dùng map này khi bật social avoidance. Goal đến từ RViz
`/goal_pose`; mặc định robot3 dẫn đầu. MPC phát `/<robot>/cmd_vel`.

Các topic cần đọc khi kiểm tra: `/leader/people/poses`,
`/leader/people/body_observations`, `/leader/people/tv_screens`,
`/social_navigation/status`, `/social_navigation/attention_debug`,
`/social_navigation/observation_status`, `/dstar_lite/path`,
`/formation/robot_states` và clock/TF. Đối chiếu kiểu message trong node
trước khi viết script đọc; không suy ra trạng thái chỉ từ marker.

Pose robot hiện lấy từ Gazebo, chưa phải hệ định vị robot thực. Lịch người,
manifest và marker `/social_scene/...` là ground truth để đối chiếu, không
phải đầu vào nhãn cho nhận diện. Tránh giường trên map không chứng minh
nhận diện người nằm; nằm bất động không chứng minh ngủ; dừng ở bình nước
không chứng minh nhận diện uống nước. Không lấy nhãn kịch bản thay cảm biến.

### 0.4. Môi trường và lệnh tái hiện

Môi trường đã dùng: ROS 2 Humble, Gazebo Fortress, robot `3w_v2_multi`,
RGB-D/LiDAR. Build/install/log đã được dọn khỏi bản nguồn; cần build lại.
Chạy từ thư mục gốc repository:

```bash
source /opt/ros/humble/setup.bash
colcon build --symlink-install \
  --base-paths social_navigation_planner social_navigation_sim \
  --packages-select social_navigation_planner social_navigation_sim \
  --cmake-args -DBUILD_TESTING=OFF
source install/setup.bash
export ROS_DOMAIN_ID=31

# Chọn một launch mỗi lượt, dừng lượt trước khi chuyển
ros2 launch social_navigation_sim social_static.launch.py
ros2 launch social_navigation_sim social_dynamic.launch.py
ros2 launch social_navigation_sim paper1_gwo_woa.launch.py
ros2 launch social_navigation_sim paper2_apf_mpc.launch.py
```

Paper dùng cảnh động bằng `social_scene:=dynamic`. Launch chung nhận
`social_scene:=static|dynamic`, `navigation_backend:=baseline|paper1|paper2`.
`motion_enabled:=false` dừng robot, không dừng lịch người; pause Gazebo mới
ngừng lịch theo simulation clock. Không chạy các lệnh launch hàng loạt.

Profile động: camera 480×360/6 Hz mô phỏng, DNN tối đa 2 Hz thực/1 thread,
pose 224 px/tối đa 2 crop, scan ngang mỗi 4 capture, ngân sách suy luận 3 s.
Phân biệt đồng hồ thực với đồng hồ mô phỏng khi sửa TTL/cooldown/latency.

Hồi quy không cần khởi động Gazebo:

```bash
source /opt/ros/humble/setup.bash
PYTHONPATH="$PWD/social_navigation_planner:$PYTHONPATH" \
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest \
  social_navigation_sim/test social_navigation_planner/test \
  --ignore=social_navigation_planner/test/test_copyright.py \
  --ignore=social_navigation_planner/test/test_flake8.py \
  --ignore=social_navigation_planner/test/test_pep257.py \
  -q -p no:cacheprovider
```

`BUILD_TESTING=OFF` dùng trên máy thiếu ament lint, không thay cho hồi quy
Python. Bộ test động gọi generator và có thể ghi lại asset động trong
nguồn: kiểm tra diff trước/sau test; không bỏ thay đổi ngoài ý muốn.

### 0.5. Điều gì đã biết chắc và điều gì chưa xong

- NK-041 mới nhất: theo dõi chỉ đọc đủ 600 s thực, 11:59:03–12:09:03
  ngày 01/11. Clock tiến 114,777 s, RTF toàn mẫu ~0,191. Leader có command
  né và 5 transition uncertainty_recovery=True nhưng người dùng vẫn báo
  chưa né; không dùng command hoặc gần goal làm chứng minh tránh được.
  Đo được đoạn gần như không đổi XY 143,326 s, reference rỗng ở 497/596
  snapshot, log yield ready/passed followers lặp 325/323 lần. Scan leader
  từng gián đoạn 17,815 s thực và 122/596 mẫu có capture age >0,3 s mô phỏng.
  Cần xử lý vòng near-goal yield/completion và freshness/RTF, không chỉ
  buffer. Chưa sửa code tại lượt audit này; xem minh chứng NK-041.

- NK-040 — 01/11: đã build lại hai package và mở social_dynamic (baseline
  D* Lite + MPC), Gazebo/RViz, domain31 để người dùng tự thử leader. Clock,
  scan cả ba robot, RGB và pose có dữ liệu; RTF mẫu khởi động ~0,278.
  Có publisher escape_path cả ba, status vùng nhớ mới đã xuất hiện. RViz
  nhận goal `(1.24217,-2.67986)` từ người dùng; log báo D* no route với
  obstacles hiện tại. Không coi khởi động là xác nhận tránh được va chạm.

- NK-039 mới nhất: đã sửa leader kẹt trong uncertainty envelope. Tách body
  model khỏi phần dự phòng; chỉ cho bước thoát tăng khoảng hở khi swept
  body gap >=0,03 m, track đã xác nhận, map/LiDAR/peer/freshness đều hợp lệ.
  Đích phục hồi phải ra ngoài toàn bộ buffer. 179 test qua, gồm 56 safety;
  body gap nhỏ nhất 0,085 m trong ca động học dùng geometry leader và map
  dự án, khoảng cách track 0,563→0,803 m. Node ROS domain94 có lệnh né,
  stale scan dừng; chưa replay Gazebo. Body radius là ước lượng, không phải
  ground truth. Xem [luồng ba phần](docs/LEADER_CAMERA_LIDAR_DIEU_HUONG.md).

- NK-038: shadow chỉ đọc dữ liệu đo hiện tại tái hiện leader bị loại ngay
  bước 1 do track có vùng đệm chồng điểm đứng: initial gap khoảng -0,051/
  -0,115 m. Lượt shadow 1 đếm 68 normal_tracked_obstacle + 12 planning-map;
  lượt 2 đếm 110 + 18. Không phải telemetry nội bộ process live; không đưa
  số đếm này thành benchmark. Chưa sửa ràng buộc, không restart/đổi goal.

- NK-037: cùng phiên cũ, leader đứng nguyên `(0.79196,-2.92672)`;
  92 lệnh/15 s đều 0, RTF ~0,211, sensor vẫn tới. Mẫu tiếp 12 s có 14
  reference không rỗng/14 rỗng, nhưng 42 cmd đều 0; safety no verified
  escape. Điểm đứng vẫn free ở cả map vật lý và social (clearance 0,482/
  0,196 m), nên không được khẳng định thân xe nằm trong ô cấm. Cần chẩn
  đoán rollout guard và nhả reference, không quy cho mất TV hay motor.

- NK-036: đã sửa bộ nhớ viewing trong source. Vùng đã xác nhận được giữ
  trong phiên khi mất quan sát, đánh dấu needs_recheck; không làm mới stamp.
  Bằng chứng người đi/đổi hướng vẫn thu hồi đúng vùng. Smoke node ROS riêng
  giữ 2 vùng/832 ô sau 200 s, còn 1 vùng/576 ô sau một người rời. 168 test
  qua trước chỉnh search cuối; toàn bộ 62 test social qua sau chỉnh cuối.
  Phiên người dùng đang chạy chưa nạp bản này, chưa replay Gazebo.

- NK-035: cùng phiên cũ mất toàn bộ group regions, không chỉ marker.
  Raw TV track → remembered TV track → viewing region lần lượt không còn;
  tham số thực object_memory=60 s, color_object_memory=75 s,
  tv_view_memory=75 s. TTL phù hợp chuỗi mất quan sát nhưng chưa có log
  nhánh xóa polygon cuối để loại trừ invalidation. Trong log lượt này
  tv_regions luôn 0, vùng viewing được tính ở color_regions (tối đa 1),
  không gọi đó là vùng TV chuyên biệt đã xác nhận. Chưa sửa code ở NK-035.

- NK-034: người dùng làm rõ lượt thử sau NK-032 được báo ở NK-033:
  chỉ leader (robot3, có cột camera) bị đâm; hai follower đã né được trong
  lượt đó. Tập trung chẩn đoán leader, không suy số lệnh khác 0 thành
  kết luận cả ba va chạm. Không nhập nhằng với snapshot robot2 NK-032.

- NK-033 đính chính trạng thái NK-032: người dùng đã tự chạy bản đó và
  báo vẫn va chạm. Phiên hiện tại có dữ liệu, RTF mẫu ~0,207, cả ba có
  lệnh né xen giữ dừng; không còn kết luận toàn bộ dữ liệu ngừng tới.
  Đã sửa thêm guard bị xóa bởi publish_stop và người dừng sát bị coi là
  hết nguy cơ; 162 test qua, gồm 46 ca safety, 2 warning SciPy. Chưa restart phiên đang chạy để nạp bản
  sửa này; chưa chứng minh hết va chạm trong Gazebo. Xem NK-033.

- Mới nhất NK-032: đã dừng mô phỏng theo yêu cầu, lưu pose ở 26,483 s
  trong `docs/evidence/2026-10-28/follower_collision/replay_state.json`.
  Người `(1,39263; -2,5)` cách robot2 `(1,67617; -2,75986)` khoảng 0,385 m.
  Sửa sparse LiDAR/chia sẻ scan và collision primitives; build thành công,
  159 test qua (43 safety), 2 warning SciPy, không chạy 3 lint file.
  Chưa khởi động lại Gazebo với bản này; chưa xác nhận hết va chạm/nghẽn.

- Kết quả NK-028: hai package build được, **153 test qua**, hai warning
  SciPy clipping bounds ở Paper2; ba lint file không chạy. Log:
  [build](docs/evidence/2026-10-28/astar_camera_priority/build.log),
  [test](docs/evidence/2026-10-28/astar_camera_priority/regression_tests.log).
  Có 38 ca safety qua, gồm người chậm/nhanh và camera đang quét. Hai node
  ROS thật trong domain 94 riêng xác nhận hủy quét khi MPC báo nguy cơ,
  goal chính giữ nguyên; chưa có replay Gazebo cho bản sửa.
- Bảy launch đã đọc được tham số, sáu tổ hợp scene/backend resolve đúng
  asset; Xacro và 31 tham chiếu tài nguyên hợp lệ. Sau đó đã khởi chạy
  Gazebo/RViz và đủ controller trong lượt chuẩn bị NK-021, nhưng bị yêu cầu
  dừng trước khi gửi goal; chưa có ca tới đích hoặc video lượt chạy hoàn chỉnh.
- TV đã xuất hiện vùng trong Gazebo. Audit từng thấy trùng người/mảnh TV;
  M6 có sửa và hồi quy nhưng chưa có số đo dài hạn về ID switch/vùng tồn dư.
- Nhánh nằm: một ca có người cho 1 ứng viên, cùng giường trống cho 0.
  [Dữ liệu đối chứng](docs/evidence/2026-10-27/posture_validation.json).
  Chưa có bộ dữ liệu nhiều góc hoặc chứng minh robot tự nhìn đúng khi đi qua.
- Ca goal cũ qua giường không xác nhận nhận diện người nằm, không đủ chứng
  minh không va chạm và chưa tới goal trong mẫu cuối. Xem NK-009 trước khi
  dùng ca này làm bằng chứng thành công.
- RTF khoảng 0,16/0,20 ở hai điều kiện khác nhau, vẫn thấp; chưa có A/B
  kiểm soát. RViz từng có lỗi shader indexed map, chưa xác nhận hết lỗi.
- Lượt người dùng tự chạy NK-022: TV có 1–2 vùng, nhưng đoàn đứng gần như
  yên và coordinator báo no route; RTF khoảng 0,089 trong mẫu 25 s thực.
  Hai snapshot map chạy D* mới vẫn có đường; cần phân biệt lớp LiDAR động,
  trạng thái incremental và thời điểm cập nhật trước khi kết luận nguyên nhân.
- Profile NK-023: RTF sau đó giảm xuống khoảng 0,0003–0,0005; Gazebo
  server main thread gần 100% một CPU, D*/MPC chỉ vài %. Nghi phần DART/
  collision của robot nhiều khớp/mesh; chưa xác nhận hotspot vì perf/ptrace
  bị kernel chặn. Không tự gán nguyên nhân cho DNN hoặc giảm cảm biến trước
  khi kiểm chứng phần vật lý. Xem bằng chứng ở `docs/evidence/2026-10-28/rtf_profile/`.
- Kiểm tra mới nhất NK-025: RTF trung bình mẫu 12 s là 0,124, robot đã tới
  vùng phía dưới TV theo hàng dọc; trong mẫu đang `inspect_person` và gần
  như đứng yên, leader còn cách goal khoảng 4,06 m. Chưa xác nhận ổn định
  hoặc hoàn thành đích; không coi RTF phục hồi ở mẫu này là kết quả sửa code.
- Người động chạy kinematic theo lịch, chưa có animation đầy đủ hoặc hành
  vi phản ứng với robot. Chưa có benchmark công bằng ba backend.
- NK-029: process controller khởi động 14:36:55, trước module A* mới;
  graph chưa có escape_path/escape_goal. Trong mẫu 12 s chỉ nhận 60 lệnh
  dừng, không có clock/pose/LiDAR/RGB mới; server Gazebo vẫn sống và dùng
  CPU. Chưa thể dùng phiên này để kết luận bản A* mới đã hoạt động hay
  tránh được người. Phiên này đã kết thúc; xem NK-030 về lượt khởi động mới
  theo yêu cầu người dùng.

### 0.6. Việc AI tiếp theo nên làm

Ưu tiên từ NK-041: khi leader đã cách goal <0,05 m, yield_followers có
thể tạo target leader rất gần; RollingTurnMotion leader_completion đánh
finished ngay, coordinator clear_paths trước publish rows rồi lập yield
lại. Đã tái hiện riêng predicate bằng pose frozen (không phải toàn bộ
live maneuver). Cần kiểm thử/fix theo yêu cầu tiếp theo; giữ khả năng né
khẩn kể cả khi leader đã tới goal. Đồng thời đo projector LiDAR/TF và
phân biệt tuổi sim với receipt age thực; không nới watchdog mù.

Phiên mới NK-040 đã được mở theo yêu cầu 01/11, nên các ghi chú bên dưới
về process cũ chưa nạp NK-039 là lịch sử. Giữ goal người dùng chọn, đọc
`log/manual_dynamic.log` và safety_status khi họ thử. Cảnh báo no route
ở khởi động cần phân biệt với guard không có escape hoặc dữ liệu cũ.

NK-039 đã sửa source theo phân tích NK-038, chưa tự restart. Lần chạy mới
cần đo body_gap/buffer_gap và normal_mpc rejection counters trong
`/robot3/safety_status`, kiểm tra leader thực sự thoát rồi tới goal cũ;
so cùng scene/goal/timing với baseline. Không coi ROS synthetic/kinematic
là chứng minh contact Gazebo đã hết. Giữ nguyên nhánh follower đã qua ca cũ.

NK-036 đã sửa source mất vùng viewing; xem mục bàn giao/test ở dưới.
Khi chạy phiên mới, cần quan sát lại để hình thành vùng ban đầu; bộ nhớ
không lưu qua restart và không thể khôi phục polygon đã mất ở process cũ.
Vùng nhớ là giả thuyết chưa xác minh hoạt động hiện tại; không được coi
nó là frame camera mới hoặc bằng chứng hoàn tất lượt recheck.

Ưu tiên theo đính chính NK-034: lỗi tiếp xúc còn lại ở leader trong lượt
thử NK-033; hai follower đã né theo quan sát người dùng. So sánh dữ liệu
LiDAR leader qua projector đa tầng, thời điểm quan sát camera và ràng buộc
đường thoát với follower trước khi sửa thêm. Đây là hướng kiểm tra, chưa
khẳng định cảm biến hay camera là nguyên nhân. Không đổi nhánh follower
chỉ dựa vào giả định chúng cũng va chạm trong lượt này.

Hiện hành NK-033: người dùng đang tự chạy mô phỏng; giữ goal của họ và
không tự restart. Source mới đã sửa thêm vòng đời guard và close stationary
risk nhưng tiến trình đang chạy chưa nạp. Đọc minh chứng collision_retest,
không dùng kết quả test làm bằng chứng hết va chạm. Cần ghi dữ liệu trước
tiếp xúc trong lượt mới để đánh giá phát hiện muộn/không có đường thoát.

Phiên NK-030 đã dừng tại NK-032 để sửa sau khi người dùng cung cấp ảnh
va chạm. Người dùng muốn thử lại ở phiên mới; giữ snapshot và goal, không
tự đưa pose ground truth vào perception. Các quan sát NK-031 dưới đây
là phiên cũ, không phải bằng chứng bản NK-032 đang chạy.

NK-031: phiên mới đã nạp A* cho cả ba robot nhưng lại nghẽn ở sim ~26,42 s,
RTF ~0,0008; cả ba chỉ nhận lệnh 0 khi không có state/scan/RGB mới.
Coordinator từng báo robot2 clearance 0,126 m < 0,15 m: phép đo này bao gồm
map xã hội và LiDAR động, chưa chứng minh va chạm vật lý. Ưu tiên xác định
nguyên nhân nghẽn và phân biệt chặn xã hội/vật lý trong recovery; không coi
có publisher escape_path là bằng chứng robot đã né thành công.

Ưu tiên từ NK-026–NK-028: người dùng quan sát người trong nhóm TV va vào
leader đúng lúc nghẽn. Đã có bản sửa dự báo/nhường từ camera và LiDAR,
TTC chậm/nhanh, A* tạo đích né tạm và hủy camera sweep ngay khi có nguy cơ.
AI đã khởi động lại theo yêu cầu tại NK-030; chưa gửi goal. Cần kiểm tra
contact/pose/RTF khi người dùng chọn đích và các topic
`/robot3/safety_status`, `/robot3/escape_path`, `/robot3/escape_goal`.
Không coi hồi quy kinematic hoặc ROS domain riêng là replay Gazebo.

Lưu ý quan trọng: các MPC giờ nhận `planning_map_topic` bằng parameter,
không remap `/map` của chúng sang map xã hội. `/map` phải còn là map vật
lý để kiểm tra bước né khẩn; `/social_navigation/map` dùng cho bám đường
bình thường. Trong né va chạm khẩn có thể vượt keepout xã hội để thoát,
nhưng vẫn phải qua kiểm tra map vật lý, LiDAR còn mới và khoảng cách với
mọi người/đồng đội quan sát được. Không được biến nhánh này thành bỏ vật cản.

1. Khi được yêu cầu chạy: tái hiện cảnh động với cùng cấu hình/seed/goal;
   ghi camera coverage, capture RGB-D, vùng nằm/TV, lượt nhìn, đường và lệnh
   robot. Tách tránh vật cản có sẵn khỏi tránh vùng suy ra từ cảm biến.
2. Ưu tiên kiểm tra người nằm khi đường tới goal đi gần giường: robot có
   nhìn thấy đủ khớp/chiều sâu, xác nhận nhiều capture và tạo vùng kịp không.
   Có cả ca giường trống và ca bị che khuất, không dùng tọa độ GT để ép nhận diện.
3. Kiểm tra người rời TV/quay lại: vùng của người rời đi được thu hồi lúc
   nào, người còn ngồi có giữ vùng, ID có bị hợp nhầm và robot có dừng lặp không.
4. Đo cùng điều kiện trước/sau sửa: tỷ lệ tới goal, va chạm/khoảng cách nhỏ
   nhất, thời gian dừng/quay, sai số đội hình, IoU/precision/recall và RTF.
   Số lượt đo phải ghi đúng thực tế; không tự coi test unit là benchmark.
5. Sửa đúng nguyên nhân, thêm hồi quy khi cần, ghi kiểm chứng/giới hạn.
   Nếu có cải tiến chức năng, cập nhật so sánh trong báo cáo; nếu chỉ vận
   hành/đổi tên/GitHub, chỉ ghi nhật ký và phần bàn giao có liên quan.

### 0.7. Git và tài liệu khi bàn giao

Repository đích: `https://github.com/duc2605/three-robot-rescue`, nhánh
`main`; mốc đồng bộ đã xác minh trước đợt biên tập NK-020 là `7731ad4`.
Không mặc định commit này chứa thay đổi mới hơn; kiểm tra HEAD thực tế trước
khi đồng bộ tiếp.

Tại workspace đã kiểm tra ngày 28/10, `.git` còn trỏ tới snapshot cũ
`5ac6982` và remote `ngohoanglong220905/...`; việc push bản nguồn trước đó
thực hiện qua clone tạm. Vì vậy **kiểm tra `git status`, `git remote -v` và
HEAD trước mọi commit/push**, không đẩy nhầm remote hoặc reset mất thay đổi.
Clone `/tmp` và ZIP `/tmp` chỉ là dữ liệu tạm, không phải nguồn chuẩn lâu dài;
AI trên máy khác cần dùng repository đúng và mã nguồn thực tế của nó.

Các yêu cầu và lịch sử cũ giữ nguyên bên dưới. Quy trình cập nhật hiện
hành ở [AGENTS.md](AGENTS.md). Bản báo cáo là so sánh cải tiến kỹ thuật,
không phải changelog công cụ hoặc danh sách việc hành chính.

## 1. Phạm vi và cách đọc

Tài liệu ghi lại các nội dung trao đổi chính, quyết định và thay đổi dự án
có trong lịch sử làm việc hiện có; đây không phải bản chép nguyên văn từng
tin nhắn hoặc từng lần gọi công cụ. Nội dung trước lịch sử hội thoại này chỉ
được ghi khi có README hoặc Git làm căn cứ, không dựng lại các trao đổi chưa có.

Phần nhật ký giữ cả các hướng đã đề xuất nhưng chưa triển khai, các bản sửa
chưa đạt kết quả ở lần đầu và những kết luận đã được kiểm tra lại. Mỗi mục có
ID để các lần cập nhật sau dẫn chiếu hoặc đính chính.

Các mốc M0–M6 là nhãn mô tả tiến trình trong tài liệu, **không phải Git tag hoặc
phiên bản đã phát hành**. Nhiều thay đổi hiện còn trong working tree. Git HEAD
ghi nhận khi lập tài liệu là `5ac6982` (13/10/2026); không gán các sửa mới cho
commit này.

## 2. Nền dự án có trước các trao đổi gần đây

Các căn cứ từ Git:

| Commit | Ngày trong Git | Nội dung tiêu đề commit |
|---|---|---|
| `c74013a` | 04/10/2026 | Mô phỏng ba robot, D* Lite, MPC và đội hình thích nghi |
| `ff15d90` | 04/10/2026 | Snapshot workspace, gồm build/install/log và cấu hình làm việc |
| `5ac6982` | 13/10/2026 | RGB-D social navigation và people-aware planning |

Theo [hướng dẫn MPC/đội hình](social_navigation_sim/README_DSTAR_MPC.md), nền
hệ thống gồm ba robot omni `3w_v2`, mặc định `robot3` dẫn đầu, D* Lite tìm đường
trên occupancy grid và ba node MPC bám tham chiếu chung. Đội hình đổi giữa
tam giác và hàng dọc; có kiểm tra khoảng cách, vật cản và cơ chế phục hồi.

Camera RGB-D, LiDAR, suy luận hướng đầu/thân, nhóm trò chuyện, TV và vùng xã
hội đã có trước các sửa gần đây. README cũ cũng mô tả các lần chỉnh đội hình,
cảm biến và đồ họa; tài liệu này không nhận các phần đó là được tạo mới toàn
bộ trong hội thoại hiện tại.

## 3. Các mốc phát triển

| Mốc | Nội dung | Trạng thái/quan hệ với bản hiện hành |
|---|---|---|
| M0 | D* Lite + ba MPC, đội hình và cảm biến/vùng xã hội nền | Nền được tiếp tục sử dụng |
| M1 | Các nhánh Paper1 và Paper2 để tham khảo/thử thuật toán | Giữ source, không dùng làm backend hiện hành |
| M2 | Sửa hình học vùng người–TV và kiểm tra từng người | Có trong pipeline chung |
| M3 | Sửa xác nhận vùng TV theo quan sát nối tiếp, hướng người ngồi và mặt trước màn hình | Có trong pipeline chung |
| M4 | Thêm `social_dynamic`, người nằm và hai kiểu di chuyển | Chế độ riêng, giữ cảnh tĩnh để đối chiếu |
| M5 | Audit runtime và thử goal đi qua khu vực người nằm | Phát hiện hạn chế; tránh giường chưa chứng minh nhận diện người |
| M6 | Sửa ghép RGB-D, trùng track, cooldown, nhánh tư thế nằm và cấu hình DDS | Mốc chức năng hiện hành; còn cần benchmark đầy đủ |

## 4. Nhật ký chi tiết

### NK-001 — 27/10/2026 — So sánh Paper2 với D* Lite + MPC

**Yêu cầu:** xem thuật toán trong `paper2_social.launch.py` có tối ưu hơn
`dstar_mpc` hay không.

**Kết quả trao đổi:** file launch Paper2 chọn backend APF–MPC cho leader và
enhanced APF cho follower. Bản này dùng SLSQP, mặc định Np=16, Nc=5,
T=0,1 s; không dùng D* Lite tìm đường toàn cục hoặc đổi dạng đội hình.
Baseline có D* Lite, MPC cho từng robot và đội hình tam giác/hàng dọc.

Không có benchmark cùng điều kiện để kết luận Paper2 tốt hơn. Với cảnh có
phòng, tường và khe hẹp, baseline có các cơ chế cần thiết hơn để tìm đường vòng
và đổi đội hình. Đây là đánh giá cấu trúc code, không phải kết quả thống kê.
Giới hạn nhìn trước của Paper2 ở tốc độ 0,18 m/s và 1,6 s dự báo được phân tích
để giải thích vì sao tối ưu cục bộ không bảo đảm đường toàn cục tốt hơn.

**Căn cứ:** [README_PAPER2.md](README_PAPER2_APF_MPC.md),
[paper2_core.py](social_navigation_planner/social_navigation_planner/paper2_apf_mpc_core.py),
[three_robot_dstar_mpc.py](social_navigation_planner/social_navigation_planner/dstar_mpc_controller.py).

### NK-002 — 27/10/2026 — Đề xuất thuật toán vùng xã hội

**Yêu cầu:** một thuật toán xác định vùng xã hội tốt hơn phương pháp hiện tại.

Đã xem quy tắc ghép quan hệ theo cặp, thành phần liên thông và bao lồi. Điểm
yếu được nêu: quan hệ A–B và B–C có thể ghép cả A–B–C dù không có không gian
tương tác chung; nhìn thoáng qua có thể bị hiểu thành trò chuyện; bao lồi có
thể chặn dư diện tích.

Đề xuất GCFF (Graph-Cuts for F-formation), với lọc thời gian và độ bất định,
cho nhóm trò chuyện. **GCFF chỉ được đề xuất, chưa triển khai trong repo.**
Người dùng sau đó xác định ưu tiên là vùng xem TV, nên không chuyển toàn bộ
pipeline sang GCFF.

Tham khảo đã trao đổi: [GCFF, PLOS ONE 2015](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0123783).

### NK-003 — 27/10/2026 — Chốt phạm vi vùng xem TV

**Yêu cầu:** “tôi muốn tối ưu cái vùng xem tivi ấy”.

Phương pháp cũ cho phép hướng lệch tới 60°, yêu cầu người xem có hướng gần
song song và dựng bề ngang màn hình giả định 1,1 m. Đề xuất chuyển sang quan
hệ từng người–màn hình, xác nhận qua thời gian và hợp các vùng nhìn riêng.

Giữ phân biệt hướng đầu/thân với hướng mắt thực sự. Phần mở rộng dựa trên
hình học RGB-D là thiết kế kỹ thuật cho repo, không được gọi là tái lập đầy
đủ một thuật toán nghiên cứu hoặc mô hình gaze đã hiệu chuẩn.

### NK-004 — 27/10/2026 — Sửa code vùng xem TV lần đầu

**Yêu cầu:** “sửa code đi”.

Đã thêm đo đoạn màn hình từ depth trong box TV, topic
`/leader/people/tv_screens`, kiểm tra hướng từng người và polygon riêng cho
từng người–màn hình. Map hợp các polygon để giảm việc lấp khoảng trống giữa
người xem bằng bao lồi cả nhóm. TV chỉ có tâm vẫn dùng bề ngang ước lượng và
ghi rõ nguồn; không gọi đó là kích thước đo được.

Thêm xác nhận qua capture khác nhau, tối thiểu ba quan sát trải dài 0,6 s;
timer lặp hoặc timestamp lặp không tăng bằng chứng. Các kiểm tra đầu gồm
hình học màn hình xiên, hướng người, vùng nhìn, thiếu depth và hồi quy LiDAR.

**Kiểm chứng tại mốc này:** 20 kiểm tra qua; build package thành công. Chưa
đánh giá chuyển động Gazebo tại chính bước sửa đầu. Điều kiện xác nhận này
còn lỗi đối với camera quan sát nối tiếp, được sửa ở NK-006.

### NK-005 — 27/10/2026 — Quay lại dự án D* Lite + MPC

**Yêu cầu:** không chạy các nhánh Paper nữa, chạy dự án D* + MPC với vùng xã
hội đã sửa.

Đã chọn `navigation_backend:=baseline` qua `three_robot_social.launch.py`,
khởi động Gazebo, RViz, bộ điều phối và ba node MPC. Camera/LiDAR và map xã
hội được giữ. Source Paper1/Paper2 còn để tham khảo, không bị xóa.

### NK-006 — 27/10/2026 — Vùng xem TV vẫn chưa được nhận diện

**Phản hồi:** “nhận diện vùng xem tivi vẫn chưa được”.

Đọc tiếp phiên chạy cho thấy có TV và hướng người nhưng `tv_regions` vẫn
bằng 0. Phát hiện và sửa các điểm sau:

- Xác nhận ba mẫu chỉ bắt đầu sau khi thấy TV làm mất lịch sử hướng người
  đã quan sát trước đó. Giữ số mẫu và cửa sổ hướng ổn định từ tracker nguồn.
- Bộ nhớ vùng TV 8 s quá ngắn cho camera cố định quay lần lượt giữa người và
  màn hình. Đổi về 75 s cho bằng chứng nối tiếp, giữ riêng timestamp nguồn;
  quan sát mới về di chuyển/hướng đối lập vẫn phải thu hồi vùng cũ.
- Người ngồi thường thiếu hông hoặc không có mặt chính diện, nên hướng là
  `null`. Bổ sung tín hiệu mũi–mắt–tai RGB-D và kiểm tra hướng vai.
- Lượt quay bị hủy sau 8 giây thực trong khi Gazebo chậm hơn thời gian thực.
  Tách watchdog thực `observation_wall_timeout` mặc định 60 s khỏi deadline
  mô phỏng của lượt quan sát.
- Người phía sau màn hình cũng có thể hướng về tâm TV. Bổ sung mặt trước
  từ hình học màn hình và phía camera đã quan sát bề mặt đó.
- Ưu tiên TV có hình học đo được so với mục tiêu màu gần trùng.

Thêm `/social_navigation/attention_debug` để xem góc lệch, tầm nhìn, tuổi
quan sát, số mẫu hướng, trạng thái xác nhận và hình học màn hình.

**Kiểm chứng:** tại mốc cuối đợt này 29 kiểm tra qua; đã thấy `tv_regions > 0`
và `completed: social evidence acquired` trong Gazebo. Số vùng lúc đó **không
được coi là số người xem duy nhất**: audit sau phát hiện trùng track ở NK-008.

Trong các lần restart có lỗi DDS/shared memory. Đã có lúc chuyển ROS domain
từ 30 sang 31 để tiếp tục kiểm tra; sửa transport riêng cho launch được bổ
sung ở NK-011. Lỗi shader RViz lúc mở vẫn được ghi nhận, chưa xử lý dứt điểm.

### NK-007 — 27/10/2026 — Thêm ba tình huống xã hội động

**Yêu cầu:** thêm người nằm ngủ, người rời TV đi uống nước và người đi bộ
khắp map. Người dùng chọn **triển khai chế độ động riêng và giữ chế độ hiện
tại để đối chiếu**, thay vì chỉ thiết kế thuật toán.

Đã tạo `social_dynamic`, `dynamic_social.launch.py`, generator world/map/
manifest/bridge, plugin C++ `SocialScenarioMotion` và marker kịch bản có cập
nhật vị trí. Các world `people` và `rooms` được giữ.

| Tình huống | Triển khai hiện tại |
|---|---|
| Người nằm | Mesh nằm trên giường, không di chuyển; nhãn ngủ chỉ là mô tả kịch bản |
| Người rời TV | Xem 12 s mô phỏng; đổi tư thế trong 2 s; đi 0,35 m/s tới bình nước; dừng 6 s; trở lại ghế |
| Người đi bộ | Đi theo tuyến tuần tra 0,4 m/s, vòng khoảng 107,2 s mô phỏng |
| Người còn lại tại TV | `tv_viewer_b` tiếp tục ngồi xem |

Chu kỳ rời TV–quay lại khoảng 106,7 s. Chuyển động là kinematic, có thân va
chạm đi cùng mesh; chưa có hoạt ảnh chân bước, tay nâng cốc hoặc ngồi–đứng
hoàn chỉnh. Người theo lịch chưa chủ động nhường robot.

Map tĩnh chỉ thêm đồ đạc như giường/bình nước, không chứa người hoặc tuyến
của họ. Lịch, tên người và marker scenario không được dùng để gán kết quả
nhận diện. Pose robot từ Gazebo là một giả thiết có sẵn của nền mô phỏng.

Thêm ứng viên tư thế nằm từ khớp RGB-D và xử lý thu hồi vùng TV khi camera
đo được người đi khỏi vị trí cũ, kể cả khi ra ngoài bán kính ghép vị trí.

**Kiểm chứng:** 37 kiểm tra Python qua. Một world tạm headless chạy nhanh
112 giây mô phỏng đi qua đầy đủ các giai đoạn; plugin kiểm tra pose mô hình
trong physics khớp lệnh. Bản test nhanh dùng bước 0,01 s và RTF mục tiêu 100,
khác world chính 0,001 s/RTF mục tiêu 1: đây là kiểm tra lịch/pose, không phải
benchmark tránh va chạm của toàn hệ ba robot.

### NK-008 — 27/10/2026 — Audit mô phỏng đang chạy

**Yêu cầu:** “xem trình mô phỏng hiện tại đang có vấn đề gì không”.

Theo dõi log và lấy mẫu topic 22 s, không gửi lệnh điều khiển trong audit.
Các lỗi/hiện tượng được xác định:

| Hiện tượng | Bằng chứng/giới hạn kết luận |
|---|---|
| Chạy chậm | RTF khoảng 0,160; 22 giây thực tương ứng khoảng 3,53 giây mô phỏng |
| RGB–depth không đều | Bộ audit nhận 28 RGB, 20 depth, 20 timestamp trùng; log có `RGB only` |
| Trùng người xem TV | Hai track 16/17 ở gần nhau khoảng 11 cm, cùng vùng người còn ngồi |
| Tách track TV | Nhiều ID tâm/mép của một màn hình |
| D* Lite từng không có đường | Cảnh báo lặp ở giai đoạn trước; sau đó đã có đường 144 điểm và robot di chuyển |
| Shader RViz | Lỗi `active samplers with a different type...` lúc khởi động |

Không kết luận mất chính xác 28% dữ liệu toàn hệ chỉ từ mẫu nhận tại một
subscriber. Không kết luận robot đang kẹt vĩnh viễn khi log sau cho thấy
đã phục hồi đường. Việc nhận diện người nằm chưa được chứng minh ở audit này.

### NK-009 — 27/10/2026 — Theo dõi goal đi qua người nằm

**Yêu cầu:** người dùng đặt goal qua khu vực người nằm và yêu cầu đọc tiếp.

Goal quan sát được xấp xỉ `(-3,01456; 4,91303)`. Robot đi hàng dọc vòng phía
tây giường. Đọc tiếp đến khi cả ba đã đi qua giường; có các khoảng dừng quay
quan sát rồi tiếp tục đi.

- Khoảng hở tới mép giường ước tính nhỏ nhất: robot1 0,061 m, robot2 0,062 m,
  robot3 0,054 m, theo bán kính robot cấu hình 0,15 m.
- Không xuất hiện `lying_person` hoặc nhãn tư thế nằm trong mẫu theo dõi;
  các khung camera lấy ở đoạn sau hướng về nhóm người đứng/trò chuyện.
- Mẫu cuối leader còn cách goal khoảng 3,19 m. Không ghi nhận ca này là đã
  hoàn thành goal chỉ vì các robot đã đi qua giường.

**Kết luận:** đã quan sát hành vi tránh giường vốn có trên map; chưa chứng
minh nhận diện người nằm hoặc giữ khoảng cách xã hội với người đó. Các số
khoảng hở trên không phải phép đo contact hoặc khoảng cách tới thân người.

### NK-010 — 27/10/2026 — Sửa theo các lỗi quan sát được

**Yêu cầu:** “dựa trên những lỗi bạn vừa thấy, hãy sửa lại cho tối ưu hơn”.

Các thay đổi chính của M6:

1. Chọn cặp RGB-D còn mới và khớp frame/kích thước/timestamp trước DNN;
   dùng depth đã ghép suốt lượt suy luận; tránh xử lý lại capture đã dùng.
2. Ghép điểm người theo khoảng cách dự báo có giới hạn, giữ ID qua mất dấu
   ngắn, loại điểm trùng dưới 0,25 m và hợp mảnh bộ nhớ gần trùng dưới 0,28 m.
3. Hợp tâm/mép TV theo đoạn bề mặt đo được và alias ID, giữ timestamp nguồn;
   thu hồi vùng gắn ID đã bỏ. Phân biệt số track đã hợp và số track đầu vào.
4. Cooldown dùng chung cho các kiểu tìm kiếm/kiểm tra; lượt kiểm tra vật cản
   không bị yêu cầu tìm TV thay thế ngay.
5. Cho phép một lượt camera nhìn vật cản hình học lớn sát tuyến sắp đi,
   mặc định bật ở chế độ động. Điểm nhìn lấy từ map và path, không từ nhãn
   người/giường của scenario. Đề xuất nhìn không tự tạo vùng người.
6. Thử ảnh/crop xoay theo tần suất giới hạn; ưu tiên crop nằm ngang, giữ
   kiểm tra khớp ở tọa độ ảnh gốc trước khi dùng depth.
7. Vì YOLO-tiny vẫn bỏ sót người nằm trong ảnh rõ, bổ sung đề xuất bề mặt
   thấp từ RGB-D, rồi xác minh khớp thân/hông/chân và hình học 3D. Thiếu mũi
   có thể dùng hai vai tin cậy cùng chân xa phù hợp; không gán ngủ.
8. Tránh hai lượt detector toàn ảnh xoay dư khi đã có crop hình học; giảm tải
   profile động xuống camera 6 Hz, tối đa hai crop thường 224 px, OpenCV một
   thread, DNN tối đa 2 Hz thực. Crop nằm ngang giữ 256 px.

Các file mới đáng chú ý: `rgbd_pairing.py`, `vision_regions.py`,
`posture_proposals.py`, `route_inspection.py` và `test_perception_pipeline.py`.
Các sửa khác nằm trong detector, tracking, suy luận xã hội, search, launch
và bộ điều phối lượt quan sát. Không thay D* Lite/MPC bằng backend Paper.

### NK-011 — 27/10/2026 — Kiểm chứng tối ưu và sửa khởi động DDS

**Đối chứng nhận diện:** camera Gazebo riêng nhìn rõ giường. Chạy qua các
hàm xử lý/xuất dữ liệu của node: mẫu có người nằm tạo một ứng viên; mẫu cùng
giường bỏ người không tạo ứng viên. Thời gian suy luận hai mẫu lưu được lần
lượt khoảng 776 ms và 833 ms; không coi là latency trung bình của toàn hệ.

Đây là đối chứng hai ca, không phải thống kê precision/recall hay chứng minh
mọi góc nhìn. Hiệu chuẩn camera kiểm thử là đầu vào phép chiếu; không đưa nhãn
người hoặc tọa độ scenario vào bộ nhận diện.

**Kiểm tra:** 55 kiểm tra pipeline và 50 kiểm tra điều khiển qua; lần chạy bộ
điều khiển báo 1 skipped và 2 cảnh báo SciPy clipping. Ba kiểm tra lint mẫu
`copyright`, `flake8`, `pep257` không nằm trong lệnh xác nhận vì môi trường
thiếu các gói ament tương ứng. Không gọi đó là toàn bộ kiểm tra chất lượng đã qua.

**Khởi động:** một lượt restart không có camera/pose và controller không tìm
được dịch vụ, nên không coi lượt đó là kiểm chứng thành công. Thêm profile
UDPv4 riêng `fastdds_udp.xml` cho launch động, tùy chọn `dds_udp_only`.
Không xóa `/dev/shm` hay sửa cấu hình ROS toàn máy. Lượt sau khởi động đủ
controller/camera; dùng ROS domain 31. Goal cuối được khôi phục có điều kiện,
không ghi đè nếu người dùng đã chọn goal mới.

**Lấy mẫu sau sửa:** khoảng 22 s, RTF 0,200; subscriber audit nhận 17 RGB,
22 depth và 15 timestamp trùng. Điều kiện khác lượt trước (trạng thái robot,
camera và transport), nên không tuyên bố mức tăng RTF do thuật toán hay mọi
ảnh đã hết mất đồng bộ. Bộ nhận diện chủ động chờ cặp hợp lệ thay vì suy luận
khung RGB không có depth tương ứng. Shader RViz lúc mở vẫn còn.

### NK-012 — 28/10/2026 — Dừng mô phỏng theo yêu cầu

**Yêu cầu:** “tắt các mô phỏng đang chạy”.

Đã kiểm tra tiến trình, dừng launch động và cây tiến trình con Gazebo, RViz,
MPC, cảm biến. Cho kết thúc mềm trước, xử lý tiến trình còn lại nếu cần.
Kiểm tra cuối không còn tiến trình hoạt động trong cây mô phỏng đó.

**Trạng thái vận hành cuối đã xác minh:** mô phỏng đã dừng. Không tự khởi
động lại chỉ để lập hai README.

### NK-013 — 28/10/2026 — Thiết lập nhật ký và báo cáo được duy trì cùng dự án

**Yêu cầu:** tạo hai README — một ghi trao đổi/chỉnh sửa, một báo cáo tiến độ
và thay đổi giữa các phiên bản để gửi thầy cô; cập nhật cả hai mỗi khi cập nhật dự án.

Đã tạo tài liệu này và `README_BAO_CAO_TIEN_DO.md`, thêm liên kết ở README
gốc, và đặt quy trình trong `AGENTS.md`. Giữ ảnh/JSON/log minh chứng vào
`docs/evidence/2026-10-27/` thay vì phụ thuộc duy nhất file tạm.

Đợt này chỉ bổ sung hồ sơ và quy trình, không đổi mốc chức năng M6. Kiểm tra
liên kết nội bộ, ảnh/JSON minh chứng và tính nhất quán hai tài liệu. Không
chạy lại mô phỏng hoặc ghi các kết quả test cũ thành test mới của ngày 28/10.

### NK-014 — 28/10/2026 — Rà soát phần không dùng trong cấu hình hiện tại

**Yêu cầu:** xác định các phần dự án không dùng đến.

Đã đọc chuỗi launch `dynamic_social` → `three_robot_social` →
`three_robot_dstar_mpc` → `three_robot_gazebo`, kiểm tra entry point, import,
CMake và tham chiếu trong mã nguồn. Kết luận là phạm vi sử dụng theo cấu
hình D* Lite + MPC động, không phải chứng minh mọi nhánh khác không thể chạy.

- Paper1/Paper2, hai package `multi_robot_formation` và
  `virtual_structure_3robot`, A* độc lập, Nav2/SLAM và các mẫu robot khác
  không được chuỗi launch hiện tại gọi. Giữ riêng nhánh đối chiếu nếu cần.
- `astar_node` và `pid_follower` vẫn được khai báo trong
  `astar_planner/setup.py` nhưng hai module nguồn tương ứng không tồn tại;
  đây là entry point tồn dư, không ảnh hưởng đường khởi động baseline đang chọn.
- `test_cpp_publisher`, `test_subscriber.py`, `test_run_motor.py` là demo
  không được launch hiện tại gọi; không đồng nhất với các bộ test hồi quy.
- `social_protect_uncertain` và `social_inferred_focus` là tùy chọn legacy:
  backend cảnh báo, không tạo vùng theo luật cũ. `provisional_memory` được
  khai báo nhưng không tìm thấy chỗ đọc để xử lý trong script hiện hành.
- `log/`, cache Python và backup không thuộc thuật toán runtime. `build/`
  là sản phẩm build; `install/` vẫn cần cho cách chạy ROS hiện tại, chỉ tái
  tạo sau khi build chứ không xóa tùy tiện.
- Cảnh `people`/`rooms` không được chọn trong launch động nhưng phải giữ
  để đối chiếu theo yêu cầu trước. Các generator world/model vẫn là công
  cụ tái tạo tài nguyên. `_graphics_backend.py`, `kinematics.cpp`, helper
  đội hình và mô hình perception còn được dùng trực tiếp hoặc gián tiếp.

**Kiểm tra:** rà soát tĩnh và xác nhận hai file nguồn entry point không tồn
tại; chưa chạy ROS hoặc thử gỡ thành phần. Không xóa file hay sửa thuật toán.
Cập nhật kết quả vào mục 11 của báo cáo, giữ mốc M6 và trạng thái mô phỏng dừng.

### NK-015 — 28/10/2026 — Tinh gọn dự án, giữ ba backend và hai môi trường

**Yêu cầu:** giữ thuật toán D* Lite + MPC của dự án, cả hai bài báo đã kiểm
thử, môi trường tĩnh/động; xóa file cũ mà không làm hỏng phần được giữ.

**Phạm vi chốt:** tĩnh là `social_people`, động là `social_dynamic`. Giữ
Paper1/Paper2, toàn bộ test tương ứng, perception và vùng xã hội đã sửa,
MPC/đội hình, model/trọng số và công cụ tái tạo asset. Mốc thuật toán vẫn M6.

Đã xóa hai package điều khiển cũ, demo A*/PID và pub/sub/motor, launch một
robot/Nav2/SLAM, URDF/mesh robot khác, GIF cũ, installer Jazzy/Harmonic,
scene `maze1`/`maze2`/`my_maze`/`social_rescue` và cấu hình đi kèm. Bỏ lựa
chọn `rooms`; mặc định hai launch nền chuyển sang `social_people`.
Gỡ entry point trỏ tới module đã mất và target CMake `test_cpp_publisher`.

**Đính chính NK-014:** tuy cả model URDF `3w_v2` không được spawn, file
roller của nó được `3w_v2_multi/omni_wheel.urdf.xacro` include gián tiếp.
Đã chuyển nguyên file roller sang `3w_v2_multi` trước khi gỡ URDF cũ;
mesh `meshes/3w_v2` vẫn giữ vì robot hiện tại cần. Tách nguyên hàm SDF/map
còn được dùng từ generator cũ thành `scene_geometry.py` và `map_geometry.py`;
gỡ phần sinh môi trường cũ. Không thay luật D*/MPC/paper/perception.

Đã dọn build/install/log cũ, cache và backup trong repo; build lại chỉ hai
package hiện hành. Thêm `.gitignore` cho output/cache/backup sinh ra. Các
file đã được Git theo dõi từ snapshot cũ vẫn có diff; không sửa Git index
hay commit thay người dùng. Cập nhật README chính/package, hướng dẫn MPC,
cảnh tĩnh/động và hai paper để không gọi file đã gỡ hoặc installer cũ.

**Kiểm tra và xử lý hồi quy:**

- Build sạch hai package thành công với `BUILD_TESTING=OFF` do máy thiếu
  bộ ament lint. Regression Python chạy riêng; không coi tắt lint là bỏ test.
- Lượt test đầu sau dọn phát hiện bốn ca còn dùng map mê cung cũ. Chuyển
  đúng ảnh map sang `astar_planner/test/fixtures/my_maze.pgm` và đổi đường
  đọc, giữ nguyên tình huống/assertion; không cài fixture làm world.
- Sau khi có fixture, một test lộ mock coordinator thiếu `follower_speed`
  và `narrow_follower_speed`; bổ sung hai giá trị mặc định production đã có
  là 0,22/0,12 m/s trong test, không thay controller.
- Lượt cuối toàn bộ test chức năng: **115 passed**, hai warning clipping
  bounds của SciPy trong Paper2. Ba file lint không chạy.
- So sánh generator trước/sau trong thư mục tạm: **12 file giống từng byte**.
- Bốn launch chính đọc được `--show-args`; sáu tổ hợp hai scene × ba backend
  resolve đúng world/map/bridge/RViz. Kiểm tra Xacro leader có camera và
  follower không camera; 31 tham chiếu tài nguyên robot/world hợp lệ.
- Lượt đọc launch đầu bị sandbox chặn ghi `~/.ros/log`; đã chuyển riêng
  `ROS_LOG_DIR` kiểm tra sang `/tmp`, không đổi quyền hay cấu hình máy.

**Giới hạn:** không chạy lại Gazebo hoặc kiểm thử goal trong đợt dọn này.
Kiểm tra build, test và cấu hình không thay thế kiểm thử runtime đầy đủ.
Danh mục xóa: [manifest](docs/cleanup_2026-10-28.json). Minh chứng mới:
[test log](docs/evidence/2026-10-28/cleanup_tests.log),
[validation](docs/evidence/2026-10-28/cleanup_validation.json).
Bản khôi phục trước dọn lưu tạm tại
`/tmp/three-robot-rescue-before-cleanup-20261028.tar.gz`; không coi `/tmp`
là lưu trữ lâu dài. Hai README đã cập nhật cùng thay đổi.

### NK-016 — 28/10/2026 — Chuẩn hóa tên file theo cấu trúc dự án hiện hành

**Yêu cầu:** đổi tên file cho phù hợp dự án sau khi tinh gọn.

Đã đổi **31 file**, thêm launch riêng `social_static.launch.py`. Quy ước:
tên Python/config theo snake_case, launch theo chức năng/backend, README
theo chủ đề. Hai môi trường dùng tên `social_static` và `social_dynamic`;
giá trị launch `social_scene` là `static` hoặc `dynamic`. Đổi tên world tĩnh
và topic bridge của world tương ứng, không thay hình học hoặc lịch người.

| Nhóm | Tên hiện hành |
|---|---|
| Khởi động tĩnh/động | `social_static.launch.py`, `social_dynamic.launch.py` |
| Launch chung/nền | `social_navigation.launch.py`, `dstar_mpc.launch.py`, `three_robot_sim.launch.py` |
| Hai paper | `paper1_gwo_woa.launch.py`, `paper2_apf_mpc.launch.py`; module/test có cùng tiền tố thuật toán |
| Điều phối D*/MPC | `astar_planner/astar_planner/dstar_mpc_controller.py` |
| Tạo map xã hội | `ros2_omni_robot_sim/scripts/social_costmap.py` |
| Cảnh tĩnh | `social_static.sdf`, `.yaml`, `.pgm`, `_scene.json`, `_layout.svg` và generator tương ứng |
| Bridge | `social_static_bridge.yaml`, `social_dynamic_bridge.yaml` |
| Robot | `omni_kinematics.cpp`, `three_robot_controllers.yaml` |
| Tài liệu | `README_DSTAR_MPC.md`, `README_SOCIAL_STATIC.md`, `README_SOCIAL_DYNAMIC.md`, README hai paper có tên thuật toán |

Giữ tên package ROS, console executable, node/topic điều khiển và hai README
nhật ký/báo cáo. Tên world tĩnh và đường dẫn launch cũ không còn dùng;
cập nhật launch/include, Python import, setup entry point, CMake, Xacro,
RViz, generator, test và tài liệu hướng dẫn. Giữ nguyên nội dung lịch sử
trước mục này và raw evidence; chỉ sửa đích liên kết để vẫn mở được file.

Build/install cũ được xóa và tạo lại để không còn launch/module đã đổi tên
trong bản cài. Không tạo wrapper mang tên cũ. Các tên chuẩn của ROS/build
như `package.xml`, `CMakeLists.txt`, `setup.py`, `AGENTS.md` giữ nguyên.

**Kiểm chứng:** build sạch hai package thành công (`BUILD_TESTING=OFF`);
toàn bộ **115 test chức năng qua**, hai warning SciPy ở Paper2, ba lint file
không chạy. So sánh generator trước/sau sau khi chuẩn hóa tên world/path:
12 file tương đương; 31 tham chiếu robot/world hợp lệ. Đọc tham số cả bảy
launch, resolve sáu tổ hợp scene/backend, kiểm tra Xacro leader/follower,
import module từ bản cài và xác nhận đường dẫn asset cũ không còn.

Mốc thuật toán vẫn M6. Không chạy Gazebo/goal trong đợt đổi tên.
Danh sách đầy đủ: [bảng đổi tên](docs/rename_2026-10-28.json).
Lệnh chạy hiện hành xem [README chính](README.md). Có bản khôi phục tạm
`/tmp/three-robot-rescue-before-rename-20261028.tar.gz`; minh chứng kiểm
tra được lưu vào `docs/evidence/2026-10-28/rename_*` trong repo.

### NK-017 — 28/10/2026 — Đổi tên package và làm sạch bản nguồn GitHub

**Yêu cầu:** đổi cả tên `astar_planner`, làm sạch toàn bộ dự án để người
dùng đưa lên GitHub. Điều chỉnh phạm vi so với NK-016 vốn giữ tên package.

Đổi package `astar_planner` → `social_navigation_planner`, gồm thư mục
nguồn, namespace Python, marker ament, `setup.py`, `setup.cfg`, manifest,
import và mọi launch sử dụng. Đổi `ros2_omni_robot_sim` →
`social_navigation_sim`, gồm tên project CMake, manifest, đường dẫn
package URI/Xacro, package share, launch, perception, test và hướng dẫn.
Giữ console executable, node/topic điều khiển, ba backend và hai cảnh.
Danh mục: [manifest](docs/github_cleanup_2026-10-28.json).

Đã xóa cấu hình VS Code có đường dẫn máy cũ; mở rộng `.gitignore` cho
editor, tài khoản/agent, `.env`, private key, cache, egg-info và output.
Thư mục `.agents`, `.codex`, `.aws` do môi trường mount chỉ đọc được giữ
cục bộ; không đọc nội dung, không đưa vào Git hoặc ZIP. Dọn build/install/log
sau khi kiểm chứng. Không xóa Git history/remote và không commit/push.

Thêm `scripts/prepare_github.py` kiểm tra và đóng gói theo danh sách nguồn
cho phép, không sao chép `.git` hoặc thư mục cục bộ. Thêm
[hướng dẫn GitHub](docs/GITHUB_PREPARATION.md) và [giấy phép](LICENSES.md).
Giữ MIT/attribution của simulator và model; planner trước đây chưa khai báo
giấy phép nên dùng `LicenseRef-Not-Specified`, không tự cấp lại giấy phép.
Điền mô tả package đúng chức năng, bổ sung buildtool `ament_python` và
phụ thuộc runtime simulator → planner. Không tự thay danh tính maintainer.

**Kiểm chứng:** build sạch hai package tên mới thành công; 115 test qua,
hai warning clipping của SciPy ở Paper2, ba lint file không chạy. Bảy launch
đọc tham số, sáu tổ hợp scene/backend resolve đúng asset; namespace planner
và ba module backend import từ bản cài được. Xacro leader/follower hợp lệ,
31 tham chiếu robot/world đúng. Kiểm tra bản nguồn không có file >=100 MiB
và không khớp các mẫu private key/AWS/GitHub token đã kiểm tra; đây không
phải kiểm toán bí mật đầy đủ. Minh chứng build/test lưu trong
`docs/evidence/2026-10-28/github_*`.

Mốc chức năng vẫn M6; chưa chạy Gazebo/goal sau đổi tên package. Nguồn cần
build lại trước khi chạy vì đã dọn output cuối. ZIP nguồn được tạo tại
`/tmp/three-robot-rescue-github.zip`; có thể tái tạo bằng script trong repo.
Bản khôi phục trước đổi package lưu tạm tại
`/tmp/three-robot-rescue-before-package-rename-20261028.tar.gz`.

### NK-018 — 28/10/2026 — Cập nhật repository GitHub của người dùng

**Yêu cầu:** đưa bản dự án đã làm sạch lên
`https://github.com/duc2605/three-robot-rescue`, nhánh `main`.

Đã đối chiếu remote: commit nền là
`115f150c4fd6c8660ec798838c5638e452ec5e93`, lịch sử độc lập với snapshot
Git cũ trong workspace. Chuẩn bị bản đồng bộ trong clone tạm để tạo commit
nối tiếp remote, không force-push hoặc đưa lịch sử build/log của snapshot
cũ lên repository đích. Giữ danh tính tác giả đã có trong commit remote.

Nội dung đồng bộ gồm hai package tên mới, ba backend, hai môi trường,
test/tài nguyên/tài liệu và script đóng gói. Loại các package/tài nguyên cũ
trên remote theo phạm vi tinh gọn đã được người dùng cho phép. Thư mục
Git, tài khoản/agent, build/install/log/cache không nằm trong bản nguồn.
README chính ghi đúng repository đích. Thông tin kiểm thử vẫn là kết quả
NK-017: 115 test qua và build hai package; không ghi thành lượt test mới.

Kiểm tra bộ nguồn, diff và staged paths trước commit; xác nhận remote HEAD
sau push. Trạng thái và liên kết commit được báo sau thao tác Git, không tự
ghi trước mã commit chưa được tạo. Mốc thuật toán vẫn M6, không chạy Gazebo.

**Kết quả trong phiên này:** đã tạo commit cập nhật trong clone tạm
`/tmp/three-robot-rescue-github-publish-20261028`. Push HTTPS chưa thành công:
Git không có credential helper/token và báo không đọc được username khi
terminal prompt bị tắt. SSH agent không có identity. Plugin GitHub có sẵn
để kết nối nhưng chưa được kết nối; cần người dùng đăng nhập GitHub hoặc
kết nối plugin trước khi hoàn tất. Chưa có thay đổi nào được đẩy lên remote.

### NK-019 — 28/10/2026 — Đăng nhập và đẩy bản nguồn lên GitHub thành công

Người dùng hoàn tất đăng nhập GitHub bằng tài khoản `duc2605`. Đã xác
nhận bằng `gh auth status`, cấu hình credential helper qua
`gh auth setup-git --hostname github.com` và push nối tiếp nhánh `main`.
Git xác nhận remote chuyển từ `115f150` sang commit **`d1f6b96`**:
[bản cập nhật nguồn](https://github.com/duc2605/three-robot-rescue/commit/d1f6b96).

Như vậy lỗi xác thực ở NK-018 đã được xử lý. Hai package hiện hành, hai
paper, hai môi trường, test và tài liệu đã được đưa lên repository được
chỉ định. Không force-push; không chạy lại Gazebo hoặc ghi kết quả 115 test
cũ thành lượt kiểm thử mới. Cập nhật hai README để ghi nhận kết quả đồng bộ.

### NK-020 — 28/10/2026 — Tách báo cáo cải tiến và nhật ký bàn giao cho AI

**Yêu cầu:** báo cáo chỉ nêu cải tiến bản sau so với bản trước, không ghi
đổi tên/GitHub; nhật ký phải giúp AI khác đọc và tiếp tục cải tiến dự án.

Đã biên tập lại `README_BAO_CAO_TIEN_DO.md` theo từng thay đổi kỹ thuật:
vùng TV, bằng chứng thời gian, cảnh động, ghép RGB-D, tracking, người nằm,
điều phối quan sát và giảm tải. Giữ kết quả kiểm chứng và giới hạn tương
ứng; bỏ các mục đổi tên, tinh gọn, đăng nhập/push, bảng vận hành và lịch sử
biên tập khỏi báo cáo. Không tạo mốc thuật toán mới hoặc nhận thêm thành tích.

Thêm mục 0 ở nhật ký làm điểm vào cho AI: quyết định/ràng buộc, cây nguồn
hiện hành, luồng dữ liệu, lệnh build/chạy/test, kết quả đã biết, vấn đề chưa
xong, thứ tự kiểm chứng tiếp và cảnh báo Git snapshot khác remote đích.
Giữ nguyên các mục NK-001–NK-019; các số mục của báo cáo trong NK cũ là
tham chiếu tại thời điểm ghi, không phải bố cục báo cáo mới.

Sửa `AGENTS.md` để các lần sau không chèn việc đổi tên/GitHub vào báo cáo;
đổi mô tả hai liên kết trong README chính theo vai trò mới.
Công việc vận hành vẫn ghi nhật ký; báo cáo chỉ đổi khi có nội dung cải tiến
hoặc bằng chứng kỹ thuật liên quan. Lần này kiểm tra đường dẫn, liên kết,
bố cục Markdown và tính nhất quán; không chạy lại build/test/Gazebo, không
thay thuật toán. Đợt tài liệu được đồng bộ tới repository GitHub đã được
người dùng chỉ định; kiểm tra HEAD remote sau thao tác push.

### NK-021 — 28/10/2026 — Chuẩn bị lượt chạy cạnh giường, dừng theo yêu cầu

Người dùng làm rõ chỉ push khi được yêu cầu, không tự đẩy mỗi lần. Đã thêm
quy định vào `AGENTS.md`; không commit/push thay đổi trong đợt này.

Yêu cầu ban đầu là chạy tới cạnh giường, đường ban đầu qua khu xem TV và
quay video. Đã build hai package, mở cảnh động/Gazebo/RViz bằng Intel,
xác minh controller hoạt động, chọn goal dự kiến `(-3.9,-1.35)`. Đã thử
ghi vài giây RViz vào `/tmp/rescue-record-test.webm`, chuẩn bị RViz có lớp
giữ đường đầu và helper `scripts/run_bedside_tv_demo.py`. Chưa gửi goal,
chưa xác nhận đường thực tế cắt vùng TV và chưa có video lượt chạy chính.
Physics đã được pause trong lúc bố trí cửa sổ.

Người dùng sau đó yêu cầu dừng, tắt mô phỏng và lấy code tự chạy để AI đọc
lỗi. Đã dừng cây launch/Gazebo/ROS và RViz mở riêng: 27 tiến trình trong cây
được theo dõi, kiểm tra cuối không còn tiến trình hoạt động. Không tiếp tục
ghi hình hoặc tự khởi động lại sau yêu cầu này.

Thêm `scripts/run_dynamic_with_logs.sh` và
[hướng dẫn tự chạy](docs/RUN_BEDSIDE_TV.md). Script launch ghi
`log/manual_dynamic.log`; helper gửi một goal rồi lưu đường đầu thực tế,
telemetry và summary ở `log/bedside_demo/`. Helper không sửa map/cmd_vel;
hành lang TV tham chiếu chỉ dùng hiển thị/đánh giá, không phải perception.
Chỉ mới kiểm tra cú pháp và CLI của helper, chưa chạy hết một lượt ROS.

Thêm ignore `recordings/` cho dữ liệu quay thử cục bộ; log chuẩn bị nằm
trong `recordings/2026-10-28_bedside_tv/`. Không thay thuật toán; không thêm
đợt vận hành này vào báo cáo cải tiến. Bước tiếp theo: đợi người dùng tự chạy,
đọc log/telemetry thực tế rồi kết luận lỗi, không tự coi ca chuẩn bị là thành công.

### NK-022 — 28/10/2026 — Đọc lượt người dùng tự chạy, phát hiện đứng và dữ liệu trễ

**Yêu cầu:** “đọc đi”. Đọc `log/manual_dynamic.log`, sau đó subscribe các
topic đang chạy trong 25 s thực và chụp map trong một cửa sổ riêng 8 s.
Chỉ quan sát: không gửi goal mới, không đổi tham số/map/cmd_vel và không
dừng hoặc khởi động lại mô phỏng của người dùng.

**Điều kiện thực tế:** người dùng chọn goal trong RViz
`(-5.01754,-3.02664)`, khác goal chuẩn bị cạnh giường `(-3.9,-1.35)`.
Không có `log/bedside_demo/telemetry.jsonl` hoặc đường đầu lưu bởi helper;
không xác nhận được yêu cầu đường ban đầu cắt vùng TV từ dữ liệu đã lưu.

**Kết quả quan sát:**

- Ba robot và đủ node điều khiển/sensor hoạt động. Cả coordinator và ba MPC
  subscribe `/social_navigation/map`, không phải mỗi robot dùng map khác.
- TV được phát hiện, `tv_tracks=1`; vùng TV xuất hiện từ 0 lên 1–2. Hai
  polygon không tự chứng minh trùng TV vì một TV có thể có nhiều người xem.
- Lượt tìm người xem bị hủy với `camera inference is stale`; nhiều cảnh
  báo `No fresh leader RGB images`. Trong 25 s: 5 RGB, 11 depth và 3 timestamp
  trùng tại subscriber audit. Chỉ là số nhận của subscriber này, không phải
  tỷ lệ mất gói toàn hệ hoặc số capture đã được detector xử lý.
- Clock từ 14,334 tới 16,562 s mô phỏng, RTF khoảng 0,0893. Ba vị trí đo
  đầu/cuối mẫu gần như không đổi. Leader ở khoảng `(1.80877,-2.36910)`;
  chưa tới goal. Không có path mới nhận trong cửa sổ audit.
- Coordinator nhiều lần báo `D* Lite: no route for the leader with current
  obstacles`. Tuy nhiên chạy D* mới trên snapshot map vật lý và map xã hội
  gần đó cho lần lượt 138 và 160 cell đường; cell start/goal đều không bị
  chặn với inflation 0,18 m. Phép này chưa cộng lớp LiDAR động của coordinator
  và không phải snapshot đồng bộ đúng mọi lần cảnh báo; chưa kết luận lỗi D*
  hoặc vùng TV chặn kín map.

**Hướng kiểm tra tiếp:** chụp cùng timestamp map đầu vào, lớp LiDAR sau
overlay, start/goal connector và trạng thái D* incremental; đồng thời đo
capture RGB-D/tuổi kết quả theo cả thời gian thực và mô phỏng. Không sửa
TTL hoặc tắt social avoidance chỉ để xe đi khi chưa xác định nguyên nhân.

Minh chứng ở [thư mục audit](docs/evidence/2026-10-28/manual_run_audit/),
gồm dữ liệu nhận topic, hai map, phép tìm đường và log trích. Bổ sung kết
quả kiểm chứng có giới hạn vào báo cáo; không nhận có cải tiến thuật toán
mới, không chạy lại bộ test và không đẩy GitHub.

### NK-023 — 28/10/2026 — Chẩn đoán RTF, giữ nguyên goal người dùng chọn

**Yêu cầu:** giữ goal hiện tại, kiểm tra vì sao RTF thấp. Không gửi goal,
không pause/reset/restart, không đổi tham số hoặc tắt thành phần của lượt chạy.

Đọc `/world/social_dynamic/stats` trực tiếp và lấy mẫu CPU/process/thread
trong khoảng 8 s. Xác nhận PID 154403 là Gazebo server, 154404 là GUI;
luồng chính server dùng khoảng 99,96% một CPU, toàn process 104,44%.
GUI dùng 97,47%, RViz 5,73%, coordinator 1,37%, mỗi MPC khoảng 2,7–2,9%.
Máy có 16 CPU logic, tổng CPU bận 16,19%, RAM khả dụng khoảng 6 GB.
Những tỷ lệ trên là một cửa sổ lấy mẫu, không phải phần trăm đóng góp
nhân quả vào thời gian bước mô phỏng.

RTF đọc trực tiếp từ Gazebo sau mẫu NK-022 giảm xuống 0,0003, rồi mẫu sau
0,0004–0,0005; không phải chỉ một phép tính clock ROS sai. World cấu hình
bước 0,001 s. Có cặp stats chỉ tăng 1 iteration/1 ms mô phỏng trong khoảng
1,5–3,6 s thực. Không có `paused: true` trong các mẫu stats đã nhận; server
vẫn tiến từng iteration rất chậm. Camera theo simulation time vì vậy có
thể không đủ frame mới cho các timeout theo wall time.

Log nạp physics engine DART. Process maps của server/GUI/RViz có
`iris_dri.so` và thư viện Mesa; không thấy `swrast` trong kết quả lọc.
URDF đã expand cho mỗi robot có 21 continuous joint, 25 collision của link,
22 collision mesh và 18 roller bật `selfCollide=true`. Đây là ứng viên gây
chi phí physics/contact, chưa phải chứng minh hàm nào của DART bị nghẽn.

Thử perf sampling bị kernel chặn vì `perf_event_paranoid=4`; thử gdb đọc
stack bị ptrace chặn, không attach được. Không đổi sysctl, không chạy sudo
hoặc thay quyền kernel để vượt hạn chế. Vì chưa có stack và chưa làm A/B
thành phần, kết luận chắc hiện chỉ là nghẽn ở Gazebo server main thread;
collision/solver là giả thuyết cần kiểm chứng, không gọi đã sửa RTF.

Minh chứng: [profile CPU](docs/evidence/2026-10-28/rtf_profile/rtf_cpu_profile.json),
[stats Gazebo](docs/evidence/2026-10-28/rtf_profile/rtf_gazebo_stats.txt),
[kết luận/giới hạn](docs/evidence/2026-10-28/rtf_profile/diagnosis.json).
Ưu tiên kiểm chứng mô hình collision/joint và chi phí DART trong lượt có
kiểm soát, giữ cùng goal/scene; không chỉ giảm camera rồi nhận đã xử lý
nguyên nhân. Lượt người dùng hiện tại được giữ nguyên, không push GitHub.

### NK-024 — 28/10/2026 — Đối chiếu với NK-008, không phủ nhận ca chạy trước

Người dùng chỉ ra tại NK-008 đường đã tạo và robot vẫn đi được. Đọc lại
minh chứng xác nhận đúng: từng báo no route nhưng sau đó có đường 144 điểm
và robot di chuyển. Lượt hiện tại có giai đoạn đứng và RTF tụt mạnh, không
được dùng để diễn giải ngược rằng lượt NK-008 chưa từng chạy được.

Đối chiếu mã với snapshot local HEAD `5ac6982`: AST lớp DStarLiteGrid và
các hàm map_callback/update_dynamic_layer/invalidate_blocked_motion/control_tick
không đổi. File roller sau chuẩn hóa tên package cũng không đổi; world
động khớp bản sao trước đợt đổi tên file khi chuẩn hóa tên package. Snapshot
HEAD này không phải bản lưu chính xác mọi file tại thời điểm NK-008, nên
không dùng so sánh đó để khẳng định mọi thay đổi sau NK-008 đều vô can.

**Đính chính cách diễn giải NK-023:** nhiều khớp, mesh và self-collision
là cấu hình đã có, chưa phải bằng chứng một thay đổi mới gây lỗi. Profile
xác nhận nghẽn server Gazebo ở lượt này nhưng chưa giải thích được tại sao
lượt trước hồi phục còn lượt này không. Chưa có căn cứ quy lỗi cho đổi
tên, D* đã bị sửa hỏng, hoặc kết luận chắc DART/contact solver là nguyên nhân.

Sau các đợt chỉnh sửa mới có build/test/cấu hình, chưa có kiểm chứng lại
toàn bộ cùng goal và thời gian chạy như ca cũ; 115 test không thay thế
hồi quy runtime. Tiếp tục xem đây là vấn đề ổn định cần tái hiện với điều
kiện có kiểm soát; giữ goal người dùng. Minh chứng đối chiếu:
[source comparison](docs/evidence/2026-10-28/rtf_profile/source_comparison.json).
Không thay thuật toán, không đổi lượt chạy và không đẩy GitHub.

### NK-025 — 28/10/2026 — Kiểm tra trạng thái mới nhất, chưa xác nhận chạy ổn định

**Yêu cầu:** “hiện tại ổn chưa”. Đọc lại log và lấy mẫu ROS 12 s, không
thay goal/tham số và không điều khiển mô phỏng. Goal RViz mới nhất trong
log là `(-4.94944,-2.96966)`.

Log đã có `Formation: column / tracking / narrow passage` và hoàn tất thu
thập bằng chứng xã hội. Mẫu clock từ 56,526 đến 58,015 s cho RTF 0,12435;
stats Gazebo gần đó lần lượt 0,0943 và 0,15. Không còn mức gần đóng băng
0,0003 trong cửa sổ này, nhưng vẫn chậm hơn thời gian thực khoảng 8 lần.

Leader hiện ở khoảng `(-1.18083,-4.47059)`, còn cách goal khoảng 4,06 m;
hai follower xếp phía sau. Như vậy đã có tiến triển di chuyển từ xuất phát.
Trong chính mẫu 12 s, các vị trí gần như không đổi và trạng thái là
`search=inspect_person`, nên chỉ xác nhận đang dừng quan sát ở thời điểm
đo, chưa gọi là kẹt vĩnh viễn hoặc đã tới đích. Có một vùng TV, vẫn có
cảnh báo ảnh/cặp RGB-D chưa mới trong log; audit nhận 5 RGB/8 depth với
5 timestamp trùng. Không có path mới nhận trong cửa sổ, không có nghĩa
mọi đường cũ đã mất.

Kết luận: có phục hồi/tiến triển ở lượt hiện tại nhưng chưa đủ để xác nhận
ổn định. Chưa có sửa thuật toán/cấu hình làm căn cứ quy mức RTF này cho
một bản tối ưu. Minh chứng: [audit](docs/evidence/2026-10-28/status_recheck/audit.json).
Không restart, không push GitHub; tiếp tục giữ nguyên goal đang được chọn.

### NK-026 — 28/10/2026 — Người dùng chỉ ra va chạm người–leader khi nghẽn

**Quan sát người dùng:** nghẽn xảy ra khi người trong nhóm TV chạm leader;
khả năng né người động chưa ổn. Ghi nhận đây là quan sát trực tiếp của
người dùng, khác với contact-sensor/pose đồng bộ mà AI chưa thu được.

Đọc code cho thấy hai điểm yếu phù hợp với hiện tượng:

1. Người kịch bản được tạo static và plugin dùng `SetWorldPoseCmd` theo
   lịch mỗi 0,05 s mô phỏng; không kiểm tra robot để nhường hoặc điều chỉnh
   tuyến. Có collision body không có nghĩa người sẽ tự dừng khi chạm robot.
2. `DistributedRobotMPC` chỉ giữ điểm LiDAR gần trong bán kính 0,8 m và
   kiểm tra `swept_separation(..., o, o)`, coi điểm đó đứng yên suốt horizon.
   Dự báo vận tốc camera có ở lớp map xã hội, nhưng MPC không trực tiếp
   nhận quỹ đạo theo thời gian của từng người. Khi thiếu đường/tham chiếu,
   `control_tick` phát stop; chưa có cơ chế né khẩn độc lập để tránh người
   tiếp tục tiến tới một robot đang đứng.

Đối chiếu lịch `tv_viewer_a_walking` với vị trí leader cũ đã ghi
`(1.80877,-2.36910)`: ở sim 26,641 s, người theo lịch ở
`(1.44863,-2.5)`, cách vị trí đó khoảng 0,383 m; tổng bán kính cấu hình
người/robot là 0,47 m. Thời gian này khớp vùng clock khi RTF đã tụt mạnh.
Tuy nhiên vị trí robot dùng so sánh được ghi ở sim 14–16 s, không đồng bộ
26,641 s; đây chỉ là kiểm tra hình học có điều kiện nếu leader còn ở đó,
không được ghi thành xác nhận contact. Minh chứng:
[đối chiếu thời gian](docs/evidence/2026-10-28/collision_investigation/timeline_comparison.json).

Hướng xử lý kỹ thuật cần ưu tiên: dự báo người động/TTC có kiểm tra tuổi
đo, kiểm tra cả phương án đứng yên trước người đang tiến tới, ứng viên né
ngang/lùi được kiểm tra swept geometry và teammate khi đủ cảm biến. Phải
giữ hành vi dừng khi thiếu dữ liệu; không cho robot né mù. Kịch bản người
nhường có thể là chế độ riêng, không dùng việc dừng người để giả làm robot
đã né tốt. Không tắt collision để che lỗi tiếp xúc.

Trong đợt đọc này chưa sửa controller/plugin hoặc restart mô phỏng, không
đổi goal và không push. Giả thuyết va chạm kích hoạt tải contact DART phù
hợp hơn với quan sát mới, nhưng vẫn cần log contact/pose/RTF cùng timestamp
để xác định nguyên nhân trực tiếp và kiểm chứng bản sửa sau này.

### NK-027 — 28/10/2026 — Sửa dự báo và né người đi vào robot đứng yên

**Yêu cầu:** “chỉnh code đi”, sau hiện tượng người trong nhóm TV chạm
leader và mô phỏng nghẽn. Giữ goal/lượt chạy hiện tại, không push GitHub.

**Nguồn thay đổi:**

- Thêm `moving_obstacles.py`: track map-frame từ quan sát camera và cụm
  LiDAR, ghép một-một, ước lượng vận tốc qua ít nhất ba capture/0,2 s,
  loại chuyển động quá nhanh/nhiễu và hết hạn 0,8 s. Không đọc timeline GT.
- MPC subscribe `/leader/people/poses`, dự báo vật cản theo thời gian và
  kiểm tra khoảng cách swept giữa robot/người ở mỗi bước. Mở phạm vi điểm
  LiDAR xem xét từ 0,8 lên 2,5 m. Lọc tường theo map vật lý để vùng xã hội
  không làm mất chính dữ liệu LiDAR về người đang tiến tới.
- Khi đứng yên dự kiến va chạm trong khoảng 2 s, tìm bước nhường ngắn ở
  16 hướng, có giới hạn tốc độ/gia tốc, map vật lý, LiDAR và dự báo teammate.
  Ưu tiên thoát ngang hướng tiến của người thay vì chỉ lùi để rồi bị đuổi kịp.
  Có thể chạy dù thiếu tham chiếu toàn cục, nhưng không khi motion bị tắt,
  trạng thái/LiDAR cũ, scan thiếu coverage hoặc chưa có map vật lý.
- Nhánh này ưu tiên tránh tiếp xúc vật lý nên có thể vượt keepout xã hội;
  không tắt collision và không đổi map/goal. Không có bước né kiểm chứng
  được thì vẫn dừng, phát chẩn đoán; chưa bảo đảm tránh mọi ca bị dồn/trapped.
- Giữ watchdog theo thời gian thực khi đang né; không cho scan phát lại
  làm mới tuổi dữ liệu. Empty reference không ghi đè lệnh né đang còn hợp lệ.
- Tách input MPC qua parameter `planning_map_topic`; thêm subscription
  map vật lý `/map`, bỏ remap `/map` riêng ở ba MPC trong launch. Coordinator
  vẫn dùng map xã hội như trước. Thêm `/robotX/safety_status` để đọc lý do giữ/né.
- Giới hạn cấu hình MPC `0 < dt <= 0,25 s`, horizon không quá 2 s để giữ
  dự báo trong khoảng ngoại suy được hỗ trợ. Mặc định 8 × 0,15 s giữ nguyên.

**Kiểm chứng:** bộ chức năng toàn dự án 138 passed, hai warning SciPy ở
Paper2; ba lint file không chạy. Ca feedback kinematic có người 0,35 m/s
tiến tới leader không có reference kiểm tra swept separation luôn lớn hơn
0,47 m trong 80 bước; có ca LiDAR-only, dữ liệu cũ, replay scan, đồng đội,
không có chỗ né, clock rewind và map xã hội không che mất LiDAR.
Ca đầu đã bắt lỗi chọn lùi liên tục rồi bị đuổi kịp, đã sửa tiêu chí chọn
thoát ngang. Sau chỉnh watchdog cuối chạy lại toàn bộ 23 ca safety, đều qua.

Node ROS thật trong domain 94 tách biệt xác nhận map vật lý trống/map
planning bị chặn được nhận riêng, vẫn phát được lệnh nhường với reference
rỗng. Build hai package thành công, launch parse được. Không gửi goal hoặc
lệnh điều khiển vào domain 31, không restart tiến trình của người dùng.

**Giới hạn:** chưa replay ca chạm người–leader trong Gazebo, chưa đo contact
hoặc mức cải thiện RTF; không tuyên bố đã hết nghẽn. Code mới chỉ có hiệu
lực khi người dùng chạy lại tiến trình. Người kinematic/collision body giữ
nguyên để kiểm chứng không che lỗi. Báo cáo cập nhật so sánh trước/sau và
giới hạn; không commit/push. Minh chứng:
[validation](docs/evidence/2026-10-28/moving_obstacle_fix/validation.json),
[test](docs/evidence/2026-10-28/moving_obstacle_fix/regression_tests.log),
[safety](docs/evidence/2026-10-28/moving_obstacle_fix/safety_tests.log),
[ROS isolated smoke](docs/evidence/2026-10-28/moving_obstacle_fix/ros_smoke.json).

### NK-028 — 28/10/2026 — A* chọn đích né theo tốc độ và hủy quét camera khi có nguy cơ

**Yêu cầu:** xe ước lượng vận tốc người để né; xem hai hướng A* tạo đích
sau/trái/phải theo quỹ đạo người và kiểm tra camera quét làm xe đứng.
Người dùng ghi “vận tốc thấp” và “vận tốc chậm”; đã nêu giả định xử lý hai
trường hợp chậm/nhanh, chưa coi đây là hai khái niệm khác nhau được xác nhận.

**Xác minh camera:** `ObservationSweep` dùng XY neo ban đầu và tạo reference
quay/giữ chỗ. Bản NK-027 có MPC né độc lập, nhưng coordinator chưa nhận
phản hồi để hủy lượt quét ngay. Không cần vô hiệu camera; cần ưu tiên tránh
va chạm hơn việc giữ điểm neo.

**Thay đổi:**

- Ước lượng chuyển động hỗ trợ tốc độ từ 0,05 m/s nếu có đủ capture/độ dời
  và fit ổn định. Băng chậm `[0,05;0,5)` và nhanh `>=0,5 m/s` là ngưỡng
  kỹ thuật mặc định, không phải phân loại học được. Tốc độ fit tối đa 1,7 m/s;
  thấp/nhiễu/chưa đủ bằng chứng là chưa xác nhận chuyển động, không chứng
  minh người thật đang đứng.
- Tính TTC vào vùng đệm quanh robot đứng yên; chỉ người tiến tới/đường
  chuyển động cắt vùng đó mới kích hoạt. Chậm dùng lookahead 2 s, nhanh
  2,5 s và reserve lớn hơn. Không chỉ nhìn nhãn nhanh/chậm để cho lệnh.
- Thêm `local_escape.py`: A* không gian–thời gian cục bộ, lưới 8 cm,
  bin thời gian 0,3 s, phạm vi 0,8 m và 3 s, tối đa 1200 expansion. Đích
  ứng viên nằm sau/trái/phải thân xe ở 0,56/0,72 m; kiểm tra swept với
  map vật lý, LiDAR, người và teammate theo thời gian tới. Đích phải giữ
  được một khoảng ngắn và tránh hành lang tiếp cận của người chưa đi qua.
- A* chỉ đề xuất đích/hướng cục bộ, cache 0,4 s; MPC kiểm tra lại rollout
  có gia tốc trước khi phát lệnh. Không tìm được A* trong ngân sách thì
  còn ứng viên né trực tiếp được kiểm tra, không gán “không có đường” vĩnh viễn.
  Không xuất `/goal_pose` hoặc sửa `goal_xy`.
- MPC phát heartbeat safety. Coordinator nhận nguy cơ từ bất kỳ robot,
  hủy observation đang quét, chặn sweep mới và tạm ngừng reference giữ neo/
  lập đường toàn cục; nhánh né của MPC vẫn hoạt động với dữ liệu mới.
  Hết nguy cơ thì lập lại đường từ vị trí đo, goal chính không đổi. Có TTL
  và watchdog để thông báo cũ không giữ quét bị khóa mãi.
- Thêm `/robotX/escape_goal`, `/robotX/escape_path`; RViz hiển thị đường né
  tạm màu cam. `/robotX/safety_status` ghi speed/band/TTC/phía A*. Đường A*
  là đề xuất, không phải khẳng định quỹ đạo đã thực hiện.

**Kiểm chứng:** 153 test chức năng qua, hai warning SciPy, ba lint file
không chạy; 38 ca safety/A*/camera qua. Ca feedback kinematic có tốc độ
người 0,08/0,35/0,80 m/s cho khoảng cách tâm nhỏ nhất khoảng
0,675/0,643/0,692 m, với ngưỡng kiểm tra thân cấu hình 0,47 m. Có test chọn
rear/left/right, vòng vật cản, giữ đích an toàn theo thời gian, ngân sách
A*, chặn quét và giữ goal chính. Không lấy số liệu này làm benchmark Gazebo.

Hai node ROS thật trong domain 94 riêng xác nhận safety message hủy
observation, MPC vẫn có lệnh né và goal chính không đổi. Build hai package
thành công. Không restart hoặc thay goal của domain 31, không push GitHub.
Chưa replay ca tiếp xúc hoặc đo mức tăng RTF. Minh chứng:
[validation](docs/evidence/2026-10-28/astar_camera_priority/validation.json),
[test](docs/evidence/2026-10-28/astar_camera_priority/regression_tests.log),
[safety](docs/evidence/2026-10-28/astar_camera_priority/safety_tests.log),
[ROS](docs/evidence/2026-10-28/astar_camera_priority/ros_smoke.json).

### NK-029 — 28/10/2026 — Phiên hiện tại chưa nạp A*, dữ liệu mô phỏng ngừng tới

**Phản hồi:** người dùng thấy leader vẫn không tự né người để đến đích.
Đọc log và subscribe chỉ đọc 12 s, kiểm tra graph và thời gian process,
không gửi goal hoặc đổi trạng thái mô phỏng.

Controller/MPC hiện tại khởi động 14:36:55; module local_escape có mtime
14:44:26 và controller source chỉnh cuối 14:57:13. Quan trọng hơn, graph
có `/robot3/safety_status` nhưng không có publisher `/robot3/escape_path`
hoặc `/robot3/escape_goal`, hai interface được tạo trong constructor bản
A*. Đây là bằng chứng phiên hiện tại chưa nạp đầy đủ bản A*/hủy quét mới,
không chỉ dựa vào so sánh timestamp file.

Trong 12 s nhận 60 cmd_vel của leader, tất cả zero; không nhận clock,
team poses, scan hoặc RGB mới. Đọc stats Gazebo 9 s không có phản hồi.
Server/GUI vẫn còn sống, dùng CPU (PID 165014/165015), nên không ghi thành
server đã thoát. Không có dữ liệu mới là lý do không thể ước lượng vận
tốc/kiểm tra né an toàn từ phiên này; watchdog phát stop là hành vi dự
kiến khi thiếu pose/reference/cảm biến. Chưa xác định chắc đang mắc ở
physics, sensor/render, bridge hay đường truyền tại thời điểm đó.

Goal mới nhất từ log RViz là `(1.26517,-4.54311)`; giữ nguyên, không thay
bằng các goal giường ghi trong lịch sử. Không thể coi unit/ROS smoke đã
qua là xác nhận hành vi của phiên đang chạy này. Cần một lượt mới nạp
bản sửa và có clock/cảm biến khỏe, rồi theo dõi speed/TTC/escape/contact
với goal của người dùng. AI chưa tự restart hoặc push.

Minh chứng: [audit](docs/evidence/2026-10-28/leader_live_version/read_only_audit.json),
[diễn giải và giới hạn](docs/evidence/2026-10-28/leader_live_version/interpretation.json).
Không thay thuật toán hoặc thêm mục vận hành này vào báo cáo cải tiến.

### NK-030 — 28/10/2026 — Chạy lại mô phỏng động với bản sửa mới

Người dùng yêu cầu chạy lại mô phỏng. Khi kiểm tra, các tiến trình mô phỏng
cũ đã thoát. Build lại hai package bằng symlink-install thành công (2,45 s),
chạy `bash scripts/run_dynamic_with_logs.sh` lúc 15:12:55; mở Gazebo và RViz,
ROS domain 31. Không gửi goal mới, không push GitHub. Sau restart người dùng
cần chọn lại đích trong RViz; tọa độ goal lịch sử không được tự phát lại.

Kiểm tra đọc topic 12 s: có 1.402 clock, 9 scan, 6 ảnh RGB, 14 team states;
đã có publisher `/robot3/escape_path`, `/robot3/escape_goal` và
`/robot3/safety_status`. RTF đo theo clock trong mẫu khởi động khoảng 0,126;
chưa phải benchmark hay xác nhận ổn định. Lệnh vận tốc cuối bằng 0 khi chưa
gửi goal. Chưa kiểm chứng ca né người tiến tới hoặc tới đích trong Gazebo.

Minh chứng: [mẫu khởi động](docs/evidence/2026-10-28/dynamic_restart/startup_audit.json).
Log phiên mới: `log/manual_dynamic.log`; log trước restart sao lưu ở
`log/manual_dynamic_before_restart_20261028.log`. Giữ nguyên báo cáo tiến độ
vì đây là thao tác vận hành, chưa có bằng chứng cải tiến thuật toán mới.

### NK-031 — 28/10/2026 — Hai follower đứng yên, phiên mới tiếp tục nghẽn

Người dùng quan sát hai robot theo chưa né được và yêu cầu kiểm tra phiên
hiện tại. Chỉ đọc dữ liệu, giữ mô phỏng và goal; không sửa thuật toán/restart.
Goal RViz mới nhất trong log: `(2.27774,-2.54233)`.

Mẫu 15 s: robot1 nhận 75 lệnh, robot2 76 lệnh, robot3 71 lệnh; tất cả bằng 0.
Chỉ 12 clock, RTF theo clock ~0,000818; không nhận team states, LiDAR, ảnh
hoặc safety_status mới trong mẫu. Cả ba có publisher escape_path, nên không
còn dùng kết luận phiên cũ chưa nạp A* tại NK-029 cho lượt này. Gazebo stats
đọc độc lập: sim 26,420 s, real 243,026 s, iterations 26420, RTF 0,0008.
Server và GUI vẫn sống. Không thể ước lượng vận tốc người hoặc xác nhận
quỹ đạo né khi không nhận được dữ liệu mới; watchdog dừng theo thời gian thực.

Log trước mẫu báo `Formation: yield / leader passing; followers clear corridor`
và `robot2 clearance 0.126 m is below the 0.15 m footprint limit; motion held.`
Đây là nhường leader của đội hình, không phải bằng chứng né người. Đọc code
cho thấy coordinator lấy clearance từ map planning đã gồm vùng xã hội và
LiDAR động; tên hard_collision_grid không có nghĩa là map vật lý riêng tại
coordinator. Chưa đủ chứng cứ để khẳng định robot2 xuyên vật cản thật hoặc
đã va người. MPC override có map vật lý riêng nhưng vẫn cần sensor/state mới.

Minh chứng: [audit](docs/evidence/2026-10-28/followers_live/audit.json),
[stats và giới hạn](docs/evidence/2026-10-28/followers_live/interpretation.json).
Việc tiếp theo: xác định hotspot nghẽn Gazebo, ghi đồng bộ pose người/robot
khi dữ liệu khỏe và kiểm tra điều kiện recovery xã hội so với vật lý.
Giữ báo cáo tiến độ vì chưa triển khai hay kiểm chứng cải tiến mới.

### NK-032 — 28/10/2026 — Lưu vùng va chạm và sửa né của follower

Yêu cầu: người dùng chỉ ra người va robot xanh trong ảnh, cho phép dừng
phiên để sửa và yêu cầu nhớ vị trí để thử lại. Chấp nhận ảnh là bằng chứng
vùng tiếp xúc/chồng lấn quan sát được; không lấy watchdog dừng làm bằng
chứng an toàn. Chưa có contact sensor xác nhận lực/độ xuyên vật lý.

Trước khi dừng, lấy được `/world/social_dynamic/pose/info` ở sim 26,483 s.
Robot2 gần người nhất: robot2 `(1.676173,-2.759862)`, yaw `-1.977858`;
người `tv_viewer_a_walking` `(1.392629,-2.5)`, khoảng cách tâm 0,384611 m.
Robot1 `(2.186248,-2.214115)`, robot3 `(1.660210,-3.334562)`; đầy đủ Z/yaw,
pose thô, log và lịch goal ở thư mục minh chứng. Goal cuối `(2.27774,-2.54233)`.
Đã dừng cả Gazebo/RViz/controller; không tự gửi goal hoặc push GitHub.

Các lỗi tìm được và thay đổi:

- `moving_obstacles.py`: cụm một tia bị loại; phép kiểm tra trước sửa tái
  hiện lỗi (mong 2 cụm nhưng chỉ 1). Giữ cụm thưa, vẫn cần ba capture để
  có vận tốc; radius tối thiểu 0,32 m. Lookahead 3 s cả hai band, reserve
  0,12/0,16 m để có thời gian thoát ngang trước khi quá sát.
- `dstar_mpc_controller.py`: dùng toàn bộ tia thay stride 120; mỗi MPC
  nhận scan các robot khác, track riêng theo nguồn. Peer scan không được
  làm mới own scan/state và không cho phép né mù. Lọc teammate về radius
  thân + 0,05 m thay 0,26 m để bớt xóa người sát đồng đội. Điểm đã thuộc
  track động không còn đồng thời là điểm đứng yên trên cả rollout; vẫn
  kiểm tra va chạm theo thời gian của track đó. Watchdog báo stale data.
- Coordinator thêm physical-map alias và chẩn đoán riêng khoảng hở
  planning/LiDAR với vật lý/LiDAR; không đổi chính sách đường thường tránh
  vùng xã hội. `dstar_mpc.launch.py` remap `/physical_map` → `/map`, giữ
  remap planning cũ. Không kết luận thông báo clearance cũ là va chạm thật.
- Xacro thân xe/khung bánh/con lăn: collision mesh → cylinder theo kích
  thước bao đo từ STL; visual không đổi. Tắt selfCollide con lăn, giữ
  external collision, 21 khớp, quán tính và controller. Đây là giảm độ
  phức tạp contact, chưa chứng minh hotspot nghẽn đã được khắc phục.

Kiểm chứng: build hai package thành công 1,21 s. Toàn bộ 159 test chức
năng qua, 2 warning SciPy ở Paper2, 3 lint file không chạy. Nhóm safety
43 ca qua, thêm cả hai follower dùng sparse peer scan/camera bị che, không
thay own scan freshness, giữ tia lẻ và tránh đóng băng track động. Ca theo
bố trí đã lưu, bắt đầu trước tiếp xúc với feedback động học và map trống,
giữ swept centre separation nhỏ nhất 0,687 m > 0,47 m. Có test phân biệt
chẩn đoán physical/social và vẫn giữ chính sách social bình thường.
Xacro→URDF→SDF follower giữ 23 collision/21 continuous joints, 18 roller
cylinder, không bật selfCollide; còn 1 collision mesh camera.

Giới hạn: chưa chạy lại Gazebo với bản này, chưa xác nhận tiếp xúc/RTF,
độ bám bánh và tracking khi dùng collision xấp xỉ. Không coi kinematic
regression là replay đầy đủ. Snapshot chỉ là dữ liệu đánh giá/tái hiện,
không đưa pose/vận tốc người tác giả vào controller. Đổi nhiều goal và
lịch sử track ở phiên cũ khiến chỉ phục hồi pose chưa phải replay xác định.

Minh chứng: [pose và goal](docs/evidence/2026-10-28/follower_collision/replay_state.json),
[log phiên cũ](docs/evidence/2026-10-28/follower_collision/runtime.log),
[test](docs/evidence/2026-10-28/follower_collision/regression_tests.log),
[safety](docs/evidence/2026-10-28/follower_collision/safety_tests.log),
[hình học](docs/evidence/2026-10-28/follower_collision/geometry_validation.json),
[build](docs/evidence/2026-10-28/follower_collision/build.log).
Báo cáo bổ sung so sánh kỹ thuật ở mục 9; không ghi thao tác vận hành thành
phiên bản thuật toán.

### NK-033 — 28/10/2026 — Người dùng báo bản sửa vẫn va chạm; sửa vòng đời guard

Người dùng tự chạy theo lệnh đã cung cấp và gửi ảnh báo “đã đâm”. Chấp nhận
đây là ca chưa đạt sau NK-032. Không khẳng định test động học chứng minh
khả năng tránh ngoài Gazebo. Giữ nguyên phiên/goal, không restart hay push.
Goal mới nhất đọc được trong tác vụ: `(-5.06358,-3.07267)`.

Mẫu sau ảnh 15 s: nhận 2.921 clock, 30 team states, 15 scan robot1/2,
10 scan robot3, 15 ảnh RGB. RTF theo clock ~0,20693; Gazebo stats độc lập
sim 35,660 s, real 167,779 s, RTF 0,201. Số lệnh khác 0: robot1=5,
robot2=6, robot3=5; xen các trạng thái no verified escape, stale data và
nhường có kiểm tra. Vì vậy không áp dụng kết luận phiên nghẽn hoàn toàn
tại NK-031 vào lượt này. Không so RTF khác điều kiện để tuyên bố cải thiện.
Lưu pose ở 35,580 s sau ảnh; không gán pose này thành đúng lúc tiếp xúc.

Test tái hiện và sửa:

- Phát hiện nguy cơ nhưng không có escape làm publish_stop xóa guard.
  Test mới thất bại trước sửa. Cờ nguy cơ nay bật trước tìm đường, lệnh dừng
  không xóa cờ; watchdog giữ tiền tố moving_obstacle khi nguy cơ chưa được
  xử lý, để coordinator không hiểu nhầm đã hết nguy cơ. Nhả khi đánh giá
  lại không còn nguy cơ hoặc clock reset. Có đối chứng tránh giữ cờ mãi.
- `collision_risk` trước đây bỏ mọi track có tốc độ <0,05 m/s. Test người
  xác nhận qua ba capture đang đứng cách 0,62 m bị báo normal trước sửa.
  Nay có nhánh close khi nằm trong khoảng radius người + radius robot +
  0,12 m, horizon 1,5 s, yêu cầu ba capture kéo dài ít nhất 0,2 s. Tách
  trạng thái confirmed khỏi vận tốc; không chia cho 0 khi chấm hướng né.
  Ca một capture chưa xác nhận vẫn giữ dừng khi không có reference.
- File nguồn: moving_obstacles.py, dstar_mpc_controller.py; thêm ba ca
  trong test_moving_obstacle_safety.py. Chưa thay đổi kịch bản người, chưa
  dùng ground truth vào perception, không nới kiểm tra vật lý để thoát.

Nhóm safety có 46 ca qua, build planner thành công. Hồi quy đầy đủ có
162 test qua trong 135,85 s, 2 warning SciPy ở Paper2; 3 lint file không
chạy. Bản source mới chưa được nạp vào các tiến trình
Gazebo/ROS đang chạy; cần lượt khởi động mới do người dùng thực hiện.
Giới hạn: chưa replay tiếp xúc; chưa chứng minh hai lỗi là nguyên nhân duy
nhất. Khi đã chồng lấn hoặc không có đường thoát được kiểm tra an toàn,
robot vẫn dừng và người kinematic vẫn có thể tiếp tục tiến vào.

Minh chứng: [audit](docs/evidence/2026-10-28/collision_retest/audit.json),
[pose sau ảnh](docs/evidence/2026-10-28/collision_retest/poses_after_event.pbtxt),
[log](docs/evidence/2026-10-28/collision_retest/runtime.log),
[diễn giải](docs/evidence/2026-10-28/collision_retest/interpretation.json),
[safety](docs/evidence/2026-10-28/collision_retest/safety_tests.log),
[test đầy đủ](docs/evidence/2026-10-28/collision_retest/regression_tests.log),
[build](docs/evidence/2026-10-28/collision_retest/build.log).
Báo cáo ghi rõ thử lại còn va chạm và so sánh sửa kỹ thuật ở mục 10.

### NK-034 — 28/10/2026 — Đính chính robot va chạm trong lượt thử trước

Người dùng làm rõ: “trong bản trước thì chỉ đâm con leader, 2 con follower
vẫn né được”, kèm ảnh người áp sát robot có cột camera. Ghi nhận kết quả
lượt tự chạy sau NK-032, được audit ở NK-033: leader robot3 còn tiếp xúc,
robot1/robot2 đã né được theo quan sát người dùng. Không coi đây là bằng
chứng follower tránh được mọi tình huống hoặc benchmark có lặp.

Đính chính phạm vi nhận định “bản trước vẫn va chạm”: không có nghĩa cả
ba robot đều va chạm. Mẫu audit sau ảnh có lệnh né ở cả ba cũng không đủ
tự xác định robot nào đã tránh thành công. Snapshot robot2 tại NK-032
thuộc lượt cũ khác, vẫn giữ nguyên bằng chứng và lịch sử đó.

Chưa sửa code hoặc chạy kiểm thử mới; không thao tác mô phỏng, goal hay
GitHub. Cập nhật bàn giao và báo cáo để tập trung lỗi còn lại ở leader.
Chưa có dữ liệu xác nhận projector LiDAR/camera/ràng buộc teammate là
nguyên nhân; cần đối chiếu trước tiếp xúc, không suy nguyên nhân từ ảnh.

### NK-035 — 28/10/2026 — Vùng viewing biến mất trong cùng phiên đang chạy

Người dùng gửi ảnh, làm rõ vẫn là phiên trước và dữ liệu vùng xem TV mất.
Chỉ đọc log/tham số, không restart/reset memory/đổi goal hay sửa thuật toán.
Log node xác nhận Social map updated: 0 group regions; tv_tracks=0,
tv_raw_tracks=0, color_targets=0, color_regions=0 dù còn remembered_viewers=2.
Vì node đã công bố không còn region, đây không đơn thuần là mất marker RViz.

Đọc tham số thật: object_memory=60, color_object_memory=75, tv_view_memory=75.
Code tick/prune dùng đồng hồ node mô phỏng: raw object hết hạn, object
ColorAttention và hình học màn hình hết hạn, zone cache cũng có TTL riêng.
Log wall ROS time: raw TV còn ở 1793177059, không còn ở 1793177069;
remembered TV còn ở 1793177132, không còn ở 1793177143. color_regions còn 1
ở 1793177216, về 0 ở 1793177227. Không lấy chênh thời gian wall làm tuổi TTL.

Hết hạn sau mất quan sát phù hợp chuỗi trên; chưa log stamp/key/reason
ngay lúc xóa polygon, nên chưa khẳng định đó là nguyên nhân duy nhất thay
vì invalidation do bằng chứng người di chuyển/đổi hướng. Lượt nhìn lại còn
bị cooldown, thiếu processed frame và có lần aborted vì không quay an toàn.
Không coi ảnh detector People/TV=0 ở một góc nhìn là bằng chứng người/TV
đã biến mất khỏi phòng. tv_regions tối đa 0 trong toàn log lượt này;
vùng viewing trước đó được đếm ở color_regions, không được báo thành TV
polygon chuyên biệt đã xác nhận chỉ vì nằm ở khu vực xem TV.

Hướng sửa cần đánh giá: tách bộ nhớ vị trí TV tĩnh khỏi bằng chứng người
đang xem; mất quan sát không tự xác nhận người đã rời chỗ. Không giữ mọi
vùng vĩnh viễn hoặc dùng pose kịch bản để khôi phục. Chưa triển khai tại đây.
Minh chứng: [timeline](docs/evidence/2026-10-28/tv_memory_loss/status_timeline.log),
[tham số và giới hạn](docs/evidence/2026-10-28/tv_memory_loss/interpretation.json).
Báo cáo cập nhật giới hạn kiểm chứng; không tạo phiên bản cải tiến mới.

### NK-036 — 28/10/2026 — Giữ vùng viewing đã xác nhận qua lúc camera nhìn đi nơi khác

Người dùng yêu cầu sửa code sau NK-035. Giữ nguyên mô phỏng/goal, không
restart, thay tham số live, đưa ground truth vào perception hoặc push GitHub.

Thay đổi:

- `color_attention.py`: thêm cached_regions chỉ cho corridor vượt xác nhận
  thời gian. Giữ landmark TV đã quan sát nhiều lần và geometry đo được;
  giữ vị trí/alias người liên quan để ghép lại sau che khuất. Hướng người
  và timestamp vẫn hết hạn, không giả vờ có phép đo mới. Target màu gắn với
  corridor xác nhận cũng được giữ vì ca thực tế đếm tại color_regions;
  không đổi nhãn nó thành TV hoặc giữ mọi ứng viên màu chưa xác nhận.
- Vùng cache được trả với persistent và needs_recheck khi chỉ còn ký ức.
  Thu hồi khi người được đo đang đi, đổi hướng/mục tiêu, ID bị merge/retire
  hoặc đường nhìn trên map bị chặn; vùng người khác còn lại. Camera không
  thấy người/TV trong ảnh riêng lẻ không tự xác nhận đối tượng đã biến mất.
- `social_costmap.py`: cả lớp vùng sinh ra và zone cache bỏ TTL ngắn riêng
  với corridor đã lưu; không chỉ giữ marker mà vẫn rasterize vào map/keepout.
  Xóa cache khi reset_memory, clock quay lui hoặc geometry map đổi. Các vùng
  chưa xác nhận/vùng hội thoại vẫn dùng TTL. Status bổ sung số vùng nhớ và
  số vùng cần recheck. Không gán nhãn fresh cho ký ức cũ.
- `social_search.py`: vùng needs_recheck không ngăn yêu cầu kiểm tra mới
  hoặc tự kết thúc camera check như bằng chứng mới. Vẫn giữ keepout trong
  khi chưa có bằng chứng thay đổi; không phát thêm lệnh điều hướng trực tiếp.
- `test_tv_attention.py`: thêm 7 ca về vắng camera lâu, stamp không đổi,
  dữ liệu chưa xác nhận hết hạn, viewing màu không đổi nhãn, thu hồi riêng
  người rời, đổi hướng sau che khuất, ghép lại TV và camera check không được
  hoàn tất chỉ vì cache. Các hành vi liên quan có ca ghép chung trong test.

Kiểm chứng: bộ đầy đủ trước phần search cuối có 168 test qua, 2 warning
SciPy Paper2, không chạy 3 lint file. Sau sửa search cuối, toàn bộ 62 test
social qua. Build social_navigation_sim thành công. Smoke gọi tick node
ROS thật domain 94, map trống và dữ liệu tổng hợp: giữ 2 corridor/832 ô
keepout sau 200 s không quan sát, stamp vẫn 1,7; khi đo một người đi còn
1 corridor/576 ô. Tick sau không tái tạo vùng đã thu hồi. Reset geometry
map và rewind clock xóa cache. Không đưa command sang domain31 người dùng.

Giới hạn: chưa replay Gazebo/DNN, chưa khẳng định mọi ID switch được xử lý.
Cache là giả thuyết bảo thủ trong RAM của phiên, không lưu qua restart.
Người/TV có thể đã thay đổi khi ngoài tầm camera; giữ vùng chưa xác minh có
thể hạn chế đường đi cho đến khi quan sát lại hoặc người dùng reset bộ nhớ.
Không coi vùng nhớ là bằng chứng hoạt động đang diễn ra. Source sửa không
tự nạp vào process cũ; cần phiên mới và quan sát tạo vùng ban đầu.

Minh chứng: [hồi quy](docs/evidence/2026-10-28/persistent_viewing/regression_tests.log),
[social cuối](docs/evidence/2026-10-28/persistent_viewing/social_tests.log),
[ROS tick](docs/evidence/2026-10-28/persistent_viewing/ros_tick_smoke.json),
[script tái lập](docs/evidence/2026-10-28/persistent_viewing/check_ros_tick.py),
[build](docs/evidence/2026-10-28/persistent_viewing/build.log).
Báo cáo bổ sung mục 11 về thay đổi kỹ thuật và giới hạn.

### NK-037 — 28/10/2026 — Leader không di chuyển trong phiên đang chạy

Người dùng gửi ảnh và báo leader không đi. Chỉ đọc, giữ nguyên goal và
phiên chạy; không thay code/tham số hay restart. Mẫu 15 s có 92 lệnh leader
bằng 0, robot1 có 5 lệnh khác 0, robot2 có 12. RTF ~0,21098; có clock,
pose, scan và ảnh. Leader báo no verified safe escape / thiếu fresh input
xen normal. Không dùng kết luận nghẽn toàn bộ từ lượt NK-031 cho mẫu này.

Đối chiếu 12 s tiếp: leader XY không đổi `(0.791960,-2.926719)`, 42 cmd
đều 0, prediction đứng tại chỗ. Nhận 28 reference, 14 không rỗng/14 rỗng;
reference có yêu cầu leader tiến từ khoảng `(0.755,-2.912)` tới
`(0.665,-2.878)`, nhưng safety báo no verified safe escape. Như vậy có
đường/reference không đồng nghĩa MPC chấp nhận quỹ đạo. Chưa có telemetry
đếm lý do loại từng candidate nên không kết luận duy nhất ràng buộc nào.

Đọc map thật tại cùng vị trí: vật lý clearance 0,482132 m, social 0,196171 m,
cả hai footprint_free=True cho radius 0,15 m. Đây là kiểm tra điểm đứng,
không chứng minh toàn quỹ đạo tự do. Không khẳng định leader bị chồng ô
social hoặc va tường dựa vào screenshot hay clearance riêng này.

Shadow tracker chỉ đọc topic bằng phép biến đổi/cluster hiện tại tìm thấy
đối tượng gần `(0.40,-3.34)`, cách leader ~0,55–0,59 m. Bán kính đã cộng
dự phòng ở các nguồn ~0,42–0,50 m; cùng radius robot có thể không còn
margin của guard. Đây là tái ước lượng ngoài process, không phải track nội
bộ của controller cũ. Shadow dùng code mới có band close, còn phiên cũ
chưa nạp các sửa NK-033/036; không coi mọi risk shadow là risk live.

Hướng tiếp: đo nguyên nhân rejection và tuổi dữ liệu/reference ngay trong
controller khi thử phiên mới; phân biệt biên dự phòng/đo sai đối tượng với
va chạm thực, không bỏ constraints để ép xe đi. Source sửa TV không gây
ra việc dừng của process cũ vì chưa được nạp. Báo cáo tiến độ giữ nguyên
vì đây là chẩn đoán vận hành, chưa có cải tiến mới được triển khai.

Minh chứng: [team audit](docs/evidence/2026-10-28/leader_hold/team_audit.json),
[reference](docs/evidence/2026-10-28/leader_hold/reference_audit.json),
[maps](docs/evidence/2026-10-28/leader_hold/maps.json),
[shadow](docs/evidence/2026-10-28/leader_hold/shadow_tracks.json),
[diễn giải](docs/evidence/2026-10-28/leader_hold/interpretation.json).

### NK-038 — 28/10/2026 — Phân tích lý do loại quỹ đạo leader ở phiên hiện tại

Người dùng yêu cầu kiểm tra trực tiếp phiên hiện tại sau khi chỉ ra follower
né còn leader đứng. Không restart, gửi lệnh điều khiển hoặc đổi goal.

Mẫu live mới 15 s: leader vẫn gần `(0.791816,-2.927776)`, RTF ~0,2034,
đủ clock/scan/pose/camera. Cả ba có toàn cmd=0 trong mẫu này (robot1/2=31,
robot3=30), không dùng mẫu mới phủ nhận follower đã né trong quan sát trước.
Không nhận safety_status mới trong mẫu; trạng thái có thể không đổi vì
publisher chỉ phát lúc đổi state, không suy vắng message là mất node.

Để đếm rejection mà không sửa controller đang chạy, tạo bản sao MPC với
publisher Capture chỉ ghi RAM, nhận map vật lý/social, pose/reference/scan,
camera và prediction từ các topic đang chạy. Instrument bản sao bằng AST.
Dùng trigger moving-only như code cũ; không dùng nhánh stationary-close
mới để giả làm dữ liệu nội bộ phiên cũ. Không điều khiển hay can thiệp process.

Kết quả shadow:

- Lượt 1 có 18 mẫu/robot. Leader: 68 proposal bị loại do track, 12 do
  planning-map. Hai follower không có các rejection này trong mẫu phân
  tích đó; có mẫu bản sao follower tìm được command né. Đây chưa phải
  command thực đo hay kết luận bảo đảm follower tránh được mọi tình huống.
- Lượt 2 có 10 mẫu/robot. Leader: 110 do track, 18 do planning-map;
  follower không có rejection cùng loại trong bản sao ở khoảng đó.
- Có proposal đứng tại chỗ và proposal đi một bước nhỏ đều bị loại ngay
  step 1. Track camera quanh `(0.40114,-3.34043)` có radius sau dự phòng
  0,4688 m, gap ban đầu -0,05139 m. Track LiDAR quanh
  `(0.40024,-3.33289)` có radius 0,52711 m, gap -0,11452 m (đã trừ
  radius robot 0,15 m). Các track này có velocity 0 trong ví dụ.

Nhận định có căn cứ: normal MPC kiểm tra mọi track, kể cả velocity=0,
và đòi swept clearance >=0,03 m ngay bước đầu. Khi hình tròn ước lượng đã
chồng điểm đứng, mọi segment chứa điểm xuất phát đều không qua được
kiểm tra này. Điều kiện tương tự tồn tại trong guard/A*: không chỉ tìm
đích xa hơn là tự có đường. Tọa độ/bán kính đến từ mô hình đo có dự phòng,
không chứng minh thân người và robot thật đã chồng lấn. Không bỏ kiểm tra
vật lý hoặc ép command để giải quyết. Cần tách uncertainty khỏi giới hạn
thân và đánh giá nhánh thoát tăng khoảng hở có kiểm chứng, đồng thời ghi
telemetry trực tiếp khi chạy bản mới.

Giới hạn: track histories, rolling command và prediction ở shadow có thể
khác process live. Đếm là số proposal bị loại, không số thử độc lập; chưa
đếm được rejection guard khi guard không active trong mẫu sau. Không gọi
kết quả này là đọc biến nội bộ của process hay bằng chứng va chạm vật lý.
Chưa sửa code thuật toán/launch hoặc chạy phiên mới; báo cáo tiến độ giữ
nguyên vì đây là chẩn đoán, chưa có cải tiến được triển khai/kiểm chứng.

Minh chứng: [live audit](docs/evidence/2026-10-28/leader_rejection_analysis/live_audit.json),
[shadow 1](docs/evidence/2026-10-28/leader_rejection_analysis/normal_replay.json),
[shadow 2](docs/evidence/2026-10-28/leader_rejection_analysis/second_shadow.json),
[tổng hợp](docs/evidence/2026-10-28/leader_rejection_analysis/summary.json),
[script](docs/evidence/2026-10-28/leader_rejection_analysis/check_shadow.py).

### NK-039 — 28/10/2026 — Phục hồi leader trong vùng dự phòng, giải thích camera–LiDAR–điều khiển

Người dùng yêu cầu sửa lỗi từ NK-038, rồi giải thích dữ liệu camera/LiDAR,
thuật toán di chuyển, xung đột giữa ba phần và cách tối ưu. Sau khi tác vụ
bị ngắt để bổ sung AGENTS.md, tiếp tục hoàn tất cùng yêu cầu. Không restart
phiên của người dùng, phát command sang domain31, đổi goal hoặc push GitHub.

Test mới trước sửa tái hiện leader đứng: người cách 0,54 m, track đã xác
nhận có outer envelope phủ điểm xuất phát, normal body model còn khoảng
hở; controller báo no verified safe escape. Sau sửa có command rời buffer.

Thay đổi chính:

- `moving_obstacles.py`: thêm body_radius vào MovingObstacle, giữ radius
  đầy đủ cho uncertainty envelope. Camera body model dùng radius quan sát
  đầu vào (0,32 m ở controller). LiDAR tách 0,12 m unseen-surface reserve
  khỏi kích thước; body giữ ít nhất 0,32 m và không nhỏ hơn extent cụm đo.
  Bỏ cap radius cụm 0,45 m để cụm rộng vẫn được bao đủ sau khi tách padding.
  Dự phòng tuổi phép đo 0,08+0,10×age vẫn giữ trên outer radius.
- `escape_step_free`: thường vẫn cần full clearance >=0,03 m. Chỉ khi
  bắt đầu đã trong buffer, track confirmed và có body_radius riêng, cho
  bước phục hồi nếu swept body gap >=0,03 m, outer gap không giảm trên
  đoạn và tăng ở cuối. Kiểm tra chuyển động tương đối, không chỉ endpoints.
  Không cho recovery khi thân ước lượng đã chạm, một capture chưa xác
  nhận, hoặc bắt đầu ngoài buffer rồi đi vào.
- Guard/A* dùng cùng predicate phục hồi. Rollout bắt đầu trong buffer
  phải kết thúc/giữ ngắn ở ngoài full buffer; không áp thêm yêu cầu hold
  cuối này cho các ca né thường vốn đã ở ngoài buffer. Hồi quy follower
  được giữ nguyên; không bỏ tường, điểm LiDAR thô, teammate hoặc freshness.
  Normal MPC vẫn kiểm tra full envelope; close-risk có ưu tiên chuyển qua
  guard để phục hồi thay vì âm thầm nới mọi quỹ đạo bám đường.
- `safety_status` báo uncertainty_recovery khi có command; khi không có
  escape báo estimated_body_gap và buffer_gap. Normal MPC không còn chỉ
  dừng im lặng khi beam rỗng: báo step và counters map/lidar/track/peer.
- Fixture test dùng đúng surface_padding của LiDAR. Thêm ca step tương
  đối, chưa xác nhận, body/wall/raw-LiDAR/stale scan chặn phục hồi, extent
  rộng không bị cắt nhỏ, geometry leader với map dự án và diagnostics.
- Viết docs/LEADER_CAMERA_LIDAR_DIEU_HUONG.md: luồng, thứ tự ưu tiên,
  xung đột, mặc định rate/đồng hồ, thay đổi đã làm và đề xuất chưa triển
  khai. README gốc dẫn tài liệu; không đổi tần số cảm biến hay scheduler.

Kiểm chứng:

- Build hai package thành công 1,51 s.
- Toàn bộ 179 test chức năng qua, 2 warning SciPy Paper2, không chạy ba
  lint file. Nhóm safety/A*/camera 56 ca qua. Ca follower cũ giữ khoảng
  cách tâm nhỏ nhất 0,687 m; không sửa ngưỡng để che hồi quy.
- Ca geometry leader dựng từ track/pose đã ghi, map vật lý social_dynamic
  và feedback động học: khoảng cách tới LiDAR track 0,563→0,803 m, body
  gap model nhỏ nhất 0,085 m. Đây là tái dựng geometry, không toàn bộ
  lịch sử frame/velocity/physics tại thời điểm ảnh cũ.
- ROS domain94: node MPC thật nhận map, camera pose, scan 360 độ tổng
  hợp; outer gap có giá trị -0,105 m nhưng body gap ~0,09 m. Phát command
  (-0,08; ~0; 0), band close, A*=rear, uncertainty_recovery=True. Làm
  scan cũ thì watchdog phát stop. Không có Gazebo/DNN trong smoke này.

Giới hạn: body_radius vẫn là model cảm biến/giả định kích thước, không
phải kích thước thật được chứng nhận. Chưa hiệu chuẩn uncertainty, chưa
fusion camera/LiDAR thành identity chung, chưa benchmark RTF/deadline,
chưa replay contact Gazebo hoặc xác nhận mọi đường thoát. Không được
khẳng định thêm ba cảm biến là tự an toàn; vẫn dừng khi không còn quỹ đạo
hợp lệ. Process cũ không hot reload; cần lượt mới do người dùng thực hiện.

Minh chứng: [hồi quy](docs/evidence/2026-10-28/leader_uncertainty_recovery/regression_tests.log),
[safety](docs/evidence/2026-10-28/leader_uncertainty_recovery/safety_tests.log),
[ROS](docs/evidence/2026-10-28/leader_uncertainty_recovery/ros_smoke.json),
[script ROS](docs/evidence/2026-10-28/leader_uncertainty_recovery/check_ros_smoke.py),
[build](docs/evidence/2026-10-28/leader_uncertainty_recovery/build.log).
Báo cáo bổ sung so sánh kỹ thuật ở mục 12, không coi đây là release Git.

### NK-040 — 01/11/2026 — Mở phiên động mới để người dùng thử leader

Người dùng yêu cầu giải thích trạng thái dự án và mở mô phỏng để tự kiểm
tra khả năng né leader. Đã đọc lại hai README/AGENTS và kiểm tra host:
không còn Gazebo/RViz/MPC chạy trước khi mở. Build lại hai package thành
công 1,27 s, chạy `bash scripts/run_dynamic_with_logs.sh` lúc 11:50:19
giờ Việt Nam, domain31, rendering Intel như script hiện tại. Không đổi
source/tham số, không phát goal hoặc command, không push GitHub.

Mẫu chỉ đọc 12 s khi khởi động nhận 3.325 clock, 30 team states, 16 scan
robot1/2, 8 scan robot3, 13 ảnh RGB; publisher escape_path đủ ba. RTF
theo clock khoảng 0,27789. Status đã có remembered_viewing_regions và
viewing_recheck_required của bản mới. Các controller bánh đã activate.

Trong lúc kiểm tra, RViz nhận goal `(1.24217,-2.67986)` (người dùng thao
tác, AI không publish). Log sau đó có cảnh báo D* Lite no route với
obstacles hiện tại và có status stale_data holding. Đây không phải lỗi
khởi động toàn hệ hay bằng chứng sensor ngừng tới; chưa xác định điều
kiện tuyến/goal cụ thể. Giữ nguyên goal để người dùng tiếp tục kiểm thử.

Đã giải thích nền D* Lite + ba MPC; camera RGB-D tạo nhận thức/vùng xã
hội, LiDAR đo vật cản, MPC có ưu tiên né và phục hồi uncertainty buffer.
Hai môi trường và hai backend paper vẫn giữ. Kết quả 179 test là kiểm
chứng 28/10, không chạy lại hôm nay; không tuyên bố né Gazebo đã thành công.

Log trực tiếp `log/manual_dynamic.log`; log trước lượt này sao lưu
`log/manual_dynamic_before_20261101.log`. Minh chứng:
[build](docs/evidence/2026-11-01/dynamic_start/build.log),
[audit](docs/evidence/2026-11-01/dynamic_start/audit.json),
[goal và cảnh báo](docs/evidence/2026-11-01/dynamic_start/startup_status.log),
[giới hạn](docs/evidence/2026-11-01/dynamic_start/launch_summary.json).
Giữ nguyên báo cáo tiến độ kỹ thuật vì đây là thao tác vận hành, chưa có
cải tiến hoặc benchmark mới.

### NK-041 — 01/11/2026 — Theo dõi 10 phút; người dùng xác nhận leader chưa né

Yêu cầu ban đầu: đọc phiên hiện tại khoảng 10 phút. Trong lúc theo dõi,
người dùng báo leader vẫn chưa né. Ghi nhận quan sát đó, không suy có
command né hoặc đứng gần goal thành tránh được người. Tiếp tục lượt audit,
không coi tin nhắn giữa lượt là yêu cầu hủy theo dõi. Không restart/đổi
goal/parameter/source hay phát command robot; chỉ subscriber/read log.

Theo dõi từ 11:59:03 đến 12:09:03 (Asia/Ho_Chi_Minh), 600,001 s thực.
Clock 101,901→216,678 s, tiến 114,777 s; RTF trung bình khoảng 0,1913.
Trong đoạn khoảng phút 7–8 RTF có mẫu gần 0,01 rồi phục hồi. Gazebo stats
đọc riêng ở sim 192,978 s cho RTF 0,0245 (khác cửa sổ tính). Không xác
định được hotspot physics hoặc quy nhân quả cho contact chỉ từ các số này.

Kết quả chuyển động và giới hạn:

- Goal giữ `(1.24217,-2.67986)` suốt mẫu, AI không phát lại. Leader có
  3.001 cmd, 153 cmd có vận tốc tịnh tiến khác 0, 180 cmd có ít nhất một
  thành phần khác 0. Đây là số message, không phải tỷ lệ thời gian hay
  số lần tránh thành công. Ghi nhận 53 transition sang status yielding,
  trong đó 5 transition uncertainty_recovery=True; không gọi là 53 ca né.
- Leader có đoạn gần như không đổi XY dài 143,326 s, khoảng elapsed
  226,661–369,987; một đoạn khác 73,467 s. Dùng ngưỡng dịch chuyển 2 mm
  giữa snapshot ~1 s, không khẳng định yaw cũng bất động hoặc không có
  chuyển động nhỏ giữa snapshot. Tại lúc người dùng báo, ref đang rỗng
  dù state mới; cả ba xe đã có khoảng giữ dừng dài.
- Cuối lượt leader cách goal 0,03171 m, từng gần nhất 0,00382 m; trước đó
  cũng từng rời goal ~0,40 m. Khoảng cách tới goal không chứng minh tránh
  được người hoặc toàn đội hoàn tất. Không có contact sensor; không tuyên
  bố collision-free. Pose camera chỉ là phép đo, không phải ground truth.

Hai vấn đề cụ thể:

1. Reference rỗng ở 497/596 snapshot có reference quan sát được. Log
   trong đúng cửa sổ có 325 dòng Follower yield ready và 323 dòng Leader
   passed followers. Source cho thấy yield target leader bị giới hạn
   theo độ dài route; khi goal gần hơn 0,05 m, leader_completion có thể
   finished ngay, coordinator clear_paths trước publish rows rồi lập lại.
   Reproduction riêng tại pose elapsed 299,798: leader cách goal 0,02681 m,
   follower target dựng còn cách 0,28284 m nhưng maneuver finished sau
   preview đầu. Đây là kiểm tra predicate với callback không gian trống,
   không phải đọc target/maneuver nội bộ chính xác của process live.
2. Input scan leader có capture age >0,3 s ở 122/596 snapshot; P95=0,567 s,
   max=1,15 s mô phỏng, vượt điều kiện guard. Receipt gap lớn nhất 17,815 s
   thực; RGB max 14,703 s, team states max 9,057 s trong giai đoạn chậm.
   Follower scan trong mẫu không có capture age >0,3 s, nhưng cũng có gap
   thực lớn khi physics chậm. Không nhầm tuổi sim nhỏ với dữ liệu mới theo
   đồng hồ thực; không gọi mọi stale_data là scan lỗi vì reference rỗng
   cũng khiến watchdog giữ dừng.

TV region và remembered viewing region đều 0 trong toàn cửa sổ; tv_tracks
vẫn có. Do vùng đã vắng từ đầu audit, mẫu này không xác định nhánh đã xóa
vùng trước đó hoặc chứng minh bộ nhớ mới giữ được vùng đã xác nhận.
Log có 21 cảnh báo no fresh RGB, không có ERROR trong cửa sổ lọc; đây
không phải xác nhận không có mọi loại lỗi. Không có no-route warning mới
trong cửa sổ này, tách với cảnh báo ở khởi động NK-040.

Không sửa code hay chạy tests mới. Cập nhật giới hạn ở mục 12 báo cáo,
không đặt phiên bản cải tiến mới. Bước tiếp: xử lý vòng completion gần
goal, telemetry lý do reference rỗng và đường LiDAR projector/TF; sau đó
thử né có kiểm soát cùng điều kiện, không chỉ nới body/buffer.

Minh chứng: [phân tích](docs/evidence/2026-11-01/audit_10min_115903/analysis.json),
[summary](docs/evidence/2026-11-01/audit_10min_115903/summary.json),
[snapshot](docs/evidence/2026-11-01/audit_10min_115903/snapshots.jsonl),
[log đúng cửa sổ](docs/evidence/2026-11-01/audit_10min_115903/runtime_log_during_audit.log),
[reproduction completion](docs/evidence/2026-11-01/audit_10min_115903/near_goal_completion_reproduction.json),
[biểu đồ](docs/evidence/2026-11-01/audit_10min_115903/runtime_plot.png).
Script monitor/analyze và pose/stats Gazebo trong cùng thư mục. Monitor
chỉ chạy trong lượt này, không phải dịch vụ theo dõi nền sau khi kết thúc.

### NK-042 — 01/11/2026 — Thử tắt RGB-D, giữ LiDAR của cả ba robot

Yêu cầu: tắt camera leader để kiểm tra riêng khả năng né. Thêm arg
`leader_rgbd` qua xacro/launch, chỉ bỏ sensor RGB-D và bridge RGB-D; giữ
hình học leader, mast và LiDAR đa tầng. Profile `lidar_only_dynamic` tắt
DNN, pose, social observation/avoidance và annotation; giữ D* Lite/MPC/đội hình.
Thêm script `scripts/run_lidar_only_with_logs.sh`, 4 test profile; README
hướng dẫn chạy. Profile thường giữ mặc định bật camera. Không push GitHub.

Kiểm tra: build thành công; 183 test chức năng qua (2 warning SciPy, 3 file
ament lint không chạy). Lượt đầu domain31 lỗi khởi động controller_manager
sau 60 s, chưa xác định nguyên nhân duy nhất; dừng và chạy sạch domain32
thành công. Topic camera/people/social map không có publisher; actual URDF
có RGB-D=0, GPU LiDAR leader=1, vertical samples=91. Query parameter
coordinator timeout, không coi là đã đọc được giá trị service.

Theo dõi 180 s thực, clock tiến 53,895 s (RTF ~0,2994); cả ba robot có
lệnh dịch chuyển/yield. Quãng đường XY lấy mẫu robot1/2/3 lần lượt khoảng
2,695/3,632/3,495 m. Leader cuối mẫu cách goal mới nhất khoảng 0,119 m.
Không phát lại goal cũ: helper xác nhận người dùng đã chọn goal khác.
Vẫn có no-safe-escape 90/50/63 lần và scan leader quá tuổi .3 s ở 24/179
snapshot; reference rỗng 100/178 snapshot. Không có contact sensor; lệnh né
không chứng minh tránh thành công. Điều kiện restart/domain/goal khác NK-041,
không quy chênh RTF riêng cho camera và không gọi đây là A/B kiểm soát.

Minh chứng và cấu hình: [trial summary](docs/evidence/2026-11-01/lidar_only_trial/three_robot_trial_summary.json),
[runtime analysis](docs/evidence/2026-11-01/lidar_only_trial/runtime_180s/analysis.json),
[URDF sensors](docs/evidence/2026-11-01/lidar_only_trial/sensor_description.json),
[tests](docs/evidence/2026-11-01/lidar_only_trial/regression_tests.log).
Báo cáo thêm mục kiểm chứng ablation, không đặt phiên bản thuật toán mới.

### NK-043 — 01/11/2026 — Người tăng giảm tốc, nhường robot và có bước chân

Yêu cầu: người di chuyển thực tế hơn, người dùng chọn **cả hành vi và hoạt
ảnh bước chân**. Bản trước kéo mesh cứng theo đoạn thẳng, tốc độ đổi tức
thời, lịch toàn cục tiếp tục chạy dù người gặp robot.

Triển khai:
- `scenario_motion.py`: route tăng/giảm tốc .45 m/s², dừng ở góc; quay
  smoothstep tối đa .75 rad/s. Bộ sinh dùng cùng giới hạn khi kết thúc vòng
  tuần tra và quay về ghế. Tốc độ tối đa giữ .35/.4 m/s. Chu kỳ danh định
  mới TV ~129,4 s, tuần tra ~118,8 s; thời gian thực tế dài hơn khi nhường.
- `social_scenario_motion.cpp`: ước lượng tốc độ robot từ pose Gazebo để
  người dự báo closest approach 1,5 s, giảm tốc/dừng. Slew rate đồng hồ
  nhóm 1,5/s khi giảm, .6/s khi tăng; hard stop kiểm tra bước dịch chuyển
  dưới .55 m nếu đang tiến gần. Ngưỡng này là thiết kế kịch bản, chưa hiệu
  chuẩn. Viewer dùng chung clock cho mọi giai đoạn; patrol riêng. Resume
  không nhảy bù thời gian; reset clock khởi động lại. Khi kiểm tra bước cuối giai đoạn, chặn sample
  tại ranh giới trước khi wrap để không kiểm tra nhầm một đoạn nhảy qua chu kỳ.
- `models/person_walking/`: asset walking Gazebo Classic Apache-2.0, URL
  revision/SHA-256 và LICENSE được giữ. `generate_walking_people.py` khóa
  root, blend đầu/cuối, giữ animation khớp. Plugin đặt trajectory cùng
  proxy collision và tính phase theo distance/.24 m/s, đứng yên thì không
  bước. .24 là tốc độ tham chiếu gần đúng của clip, chưa hiệu chuẩn gait.
- `generate_social_dynamic_world.py` tạo actor riêng cho đi/đến/tuần tra;
  proxy vật lý không còn mesh cứng trùng actor. `social_scene_markers.py`
  lấy pose thật từ bridge Gazebo thay vì lịch danh định. Không cấp pose
  người kịch bản vào perception hay MPC. Cảnh tĩnh giữ nguyên.
- CMake và test C++/Python, README động, README gốc, LICENSES và hai tài
  liệu bàn giao/báo cáo được cập nhật cùng thay đổi.

Kiểm chứng: build plugin thành công (lỗi compile đầu khi so sánh component
Actor đã sửa bằng truy vấn Name duy nhất). Test C++ gọi plugin thật với ECM
và robot chắn đường: giữ khoảng cách tâm ít nhất .55 m trong mô hình test,
clock/vị trí và phase bước chân dừng, robot rời đi thì resume không catch-up,
reset về đầu tuyến. Ca chắn đường được chạy riêng với từng tên robot1/2/3.
Đây không phải physics/contact test. Test đầu có fixture
UpdateInfo.paused=true mặc định, đã sửa fixture false rồi chạy lại qua.
Ba test Python mới kiểm tốc độ/gia tốc/quay, skin khớp/root/loop và ánh xạ
actor–collision/clock nhóm. Hồi quy cuối: **186 test Python qua**, 2 warning
SciPy, 3 file ament lint không chạy; **1/1 CTest C++ qua**.

Gazebo mới domain32 khởi động thành công ở profile camera-off, log xác
nhận pose physics patrol và người rời ghế. Đã lưu ECM có actor/trajectory,
animation walk/time và ảnh GUI hiển thị người. Lượt smoke đầu dùng chu kỳ
123,1 s trước khi hoàn tất làm mượt góc quay cuối vòng; tách với asset cuối
129,4 s, không coi ảnh đó là test đủ mọi giai đoạn của bản cuối.
Đã mở lại bản cuối domain32: log startup xác nhận controller cả ba robot
activate thành công và pose patrol khớp physics. Giữ Gazebo/RViz đang mở,
không phát goal. Log lưu `runtime_final_startup.log`. Test C++ trong sandbox
có cảnh báo không ghi được `~/.ignition/auto_default.log`; kết quả assert
và output đã lưu trong repo, không làm thất bại test.

Giới hạn: còn chuyển avatar/tư thế ở đứng–ngồi, chưa animation uống; human
kinematic không phản ứng lực như người thật; chưa nhường người khác hay
đổi tuyến đi vòng. Robot có thể đâm người đã dừng; cải tiến tác nhân không
chứng minh sửa xong bộ né leader. Chưa benchmark lặp/collision-free hay đo
độ trượt chân bằng video. Chụp desktop PIL thất bại trên X/Wayland; đã dùng
dịch vụ screenshot Gazebo thay thế. Không push GitHub.

Minh chứng: [ECM test](docs/evidence/2026-11-01/realistic_people/plugin_ecm_test.log),
[hồi quy](docs/evidence/2026-11-01/realistic_people/regression_tests.log),
[runtime smoke](docs/evidence/2026-11-01/realistic_people/runtime_initial_walk.log),
[ảnh Gazebo](docs/evidence/2026-11-01/realistic_people/gazebo_walking.png),
[trạng thái kiểm chứng](docs/evidence/2026-11-01/realistic_people/verification.json).
Báo cáo thêm so sánh kỹ thuật mục 14, nêu rõ giới hạn.

### NK-044 — 01/11/2026 — Đọc lại leader chưa né trong phiên camera-off

Người dùng báo leader vẫn chưa né. Giữ phiên và goal, không sửa điều khiển;
đọc topic trong 60 s rồi 120 s, domain32. Trong mẫu đầu chưa nhận goal mới,
reference rỗng và watchdog giữ dừng; sau đó người dùng chọn
`(1.08155775,-2.57732916)` và leader chạy. Không tự publish goal.

Ở mẫu 120 s: leader có 10/120 snapshot trạng thái normal_mpc không tìm được
rollout ngay bước 1, reject do track (map/lidar/peer đều 0 trong các ví dụ
đó); ví dụ sim51,190 reference có 27 pose, scan tuổi 0,190 s, track reject 11.
Không coi mọi dừng là do scan/camera. Đồng thời 20 snapshot scan leader tuổi
>.3 s, reference rỗng33/120; có đoạn gần đứng yên XY (<5 mm mỗi mẫu) ~9 s.
Leader phát lệnh yield A* right/rear/left và reactive fallback, xen dừng do
freshness. Đây là transition/lệnh, không phải ca né thành công.

Leader có lúc cách goal ~3 cm; cuối mẫu ~10,9 cm. Không có contact sensor,
không xác định track gây chặn là người hay ước lượng sai từ LiDAR; chưa có
track telemetry đủ để gán danh tính. Snapshot world sau đó cho thấy hai
người động ở xa đội robot, không suy tất cả track là người đang tới.
Log tiếp theo còn báo peer spacing dưới footprint, team held; lỗi đội hình
vẫn mở. Không sửa code/test controller, không restart ở bước audit này.

[Analysis](docs/evidence/2026-11-01/leader_audit_encounter/analysis.json),
[events](docs/evidence/2026-11-01/leader_audit_encounter/events.jsonl),
[summary](docs/evidence/2026-11-01/leader_audit_encounter/summary.json).
Báo cáo bổ sung kết quả kiểm chứng, không đặt phiên bản cải tiến.

### NK-045 — 01/11/2026 — Đính chính hiển thị người và sửa đồng bộ actor GUI

Người dùng không thấy người đi trong Gazebo và gửi ảnh. Đính chính NK-043:
pose physics và một ảnh có người chưa chứng minh GUI đang cập nhật chuyển
động. Lượt trả lời đầu đã dựa vào pose để nói người vẫn đi, chưa xác minh
hình hiển thị. Camera/annotation tắt giải thích RViz, không giải thích ảnh
Gazebo đứng yên.

Đã đo hai pose sim 92,963→98,464: viewer_returning dịch chuyển 1,294 m,
patrol gần đứng yên (5e-6 m, phù hợp nhường robot), lưu `people_visibility/`.
Sau đó chụp hai ảnh GUI cách nhau ~23 s thực: actor hiển thị đứng nguyên
trong khi server pose thay đổi. Đọc mã nguồn chính thức Fortress
[Actor.cc](https://github.com/gazebosim/gz-sim/blob/ign-gazebo6/src/Actor.cc):
hai setter mutate Data() mà không đánh dấu component changed.

Sửa `src/social_scenario_motion.cpp`: SetChanged OneTimeChange cho
TrajectoryPose và AnimationTime sau khi đặt giá trị. Server ECM/sensor và
GUI nhận cập nhật cùng chuyển động, kể cả ẩn avatar inactive. Mở rộng
`test/test_pedestrian_plugin.cpp`: chủ động xóa change flag rồi tick và
assert hai component được đánh dấu lại; giữ test nhường từng robot1/2/3.
Build mới và CTest đều qua; 3 Python test chuyển động qua. Toàn bộ 186 test
đã qua ở NK-043, không chạy lặp lại trong sửa GUI này. Lần compile đầu
thiếu include Pose.hh và fixture gọi API protected, đã sửa và build/test
lại thành công; kết quả CTest cũ sau build lỗi không tính là kiểm chứng.

Dừng phiên cũ và mở lại LiDAR-only domain32 để nạp .so; không tự gửi goal.
Sau sửa, hai ảnh GUI và state tại sim 9,791→12,934 cho thấy người áo xanh
lá/quần xanh dịch chuyển rõ từ mép phải về sau khu ghế TV, proxy patrol
đi 1,254 m. AnimationTime cũng đổi; hai ảnh không phải video/benchmark gait.
Giữ phiên mới đang mở cho người dùng kiểm tra, không push GitHub.

Giới hạn: chưa xác minh đầy đủ TV cycle, tiếp xúc, độ trượt chân; lỗi leader
và peer spacing ở NK-044 chưa được sửa bởi thay đổi render. Người đứng áo
trắng trong cảnh vẫn là avatar tĩnh, không phải bằng chứng patrol bị đứng.

[Ảnh trước](docs/evidence/2026-11-01/actor_visibility/2026-11-01T12:50:55.499954617.png),
[ảnh sau thứ nhất](docs/evidence/2026-11-01/actor_visibility/after/first.png),
[ảnh sau thứ hai](docs/evidence/2026-11-01/actor_visibility/after/second.png),
[so sánh](docs/evidence/2026-11-01/actor_visibility/after/comparison.json),
[CTest](docs/evidence/2026-11-01/actor_visibility/ctest.log).
Báo cáo mục14 được đính chính và bổ sung kết quả render thực.

### NK-046 — 01/11/2026 — Căn hướng thân và vận tốc người đi bộ

Yêu cầu: người trong Gazebo đang đi ngang/đi lùi. Đây là lỗi khác NK-045:
GUI đã cập nhật vị trí, nhưng hướng skeleton chưa khớp quỹ đạo. Kiểm tra
asset walking: rest LeftFoot→LeftToeBase và RightFoot→RightToeBase đều
hướng gần +X; root locomotion gốc cũng đi +X. Bản trước sao chép yaw forward
-pi/2 từ model khác và plugin cộng +pi/2, khiến thân lệch hướng đi 90°.

Sửa:
- `generate_walking_people.py`: tính mesh_forward_yaw từ trung bình hướng
  hai bàn chân ở rest skeleton; tốc độ tham chiếu từ tổng quãng đường XY
  root chia thời lượng clip, thay .24 cố định. Kết quả yaw≈.000576 rad,
  speed≈.241573 m/s. Tái sinh `loops.json` và asset bằng cùng bộ sinh.
- `generate_social_dynamic_world.py`, world/config: chuyển giá trị này qua
  `animation_forward_yaw`. `social_scenario_motion.cpp` dùng actor yaw =
  route yaw − mesh_forward_yaw; không cộng cố định 90°. Giữ SetChanged
  cho GUI, phase chân theo distance và các ràng buộc nhường robot.
- `test_pedestrian_motion.py`: đối chiếu hướng metadata với root locomotion
  gốc, kiểm metadata trong XML/world và route không dịch ngang/lùi so với
  yaw. Test plugin C++ đối chiếu trajectory thật gửi render với vector
  dịch chuyển proxy qua hai chu kỳ tuyến, bỏ qua chuyển avatar hidden.

Kiểm chứng: build thành công, 187 test Python qua, 2 warning SciPy Paper2,
3 file ament lint không chạy. 1 CTest qua; 4.730 mẫu dịch chuyển có dot
hướng render với vận tốc >.999 (đây là sample, không phải 4.730 ca độc lập).
Giữ các test dừng/nhường/resume/reset với từng robot1/2/3. Test C++ cảnh
báo không ghi được log mặc định ~/.ignition trong sandbox; assert/output
lưu trong evidence, không coi cảnh báo này là thất bại test.

Đã dừng phiên cũ để nạp .so, mở lại LiDAR-only domain32, không gửi goal.
Hai ảnh/state Gazebo sau sửa: sim 3,900→8,004, patrol đi khoảng 1,638 m,
trajectory yaw≈−.000576 và forward mesh≈+.000576 nên hướng render khớp
chiều +X. Ảnh đầu người ở ngoài mép phải, ảnh sau thấy người áo xanh lá đi
vào khung hình. Đã đưa góc nhìn GUI tới patrol để kiểm tra gần hơn; không
thay camera cảm biến của leader. Đây là smoke đoạn thẳng; kiểm hai chu kỳ
hướng là ECM tổng hợp, chưa phải hai chu kỳ Gazebo/render được đo đầy đủ.

Giới hạn: chưa kiểm định sinh cơ học, độ trượt chân hay động tác quay chân
khi xoay tại chỗ; ngồi/đứng/uống vẫn gần đúng. Lỗi né leader/peer spacing
không được sửa bởi việc căn hướng model. Không push GitHub. Hai README và
hướng dẫn môi trường động được cập nhật cùng thay đổi.

[Hồi quy](docs/evidence/2026-11-01/walk_heading/regression.log),
[plugin test](docs/evidence/2026-11-01/walk_heading/plugin_heading.log),
[so sánh state/ảnh](docs/evidence/2026-11-01/walk_heading/comparison.json),
[ảnh thứ hai](docs/evidence/2026-11-01/walk_heading/rendered/second.png),
[góc nhìn gần](docs/evidence/2026-11-01/walk_heading/rendered/close_view.png).
Báo cáo mục14 thêm so sánh sửa hướng, không đặt release hay phần trăm.

### NK-047 — 01/11/2026 — Người tiếp tục đi, robot chịu trách nhiệm né

Quyết định mới của người dùng: người phải tiếp tục di chuyển, không đứng
lại giữa đường để tránh xe. Quyết định này thay cơ chế người nhường robot
ở NK-043; không coi thay đổi đó là cải tiến khả năng né của controller.

Đã xóa toàn bộ robot-pose lookup, ước lượng vận tốc robot, closest approach,
rate giảm/tăng, hard-stop khoảng cách và clock nhóm bị trì hoãn khỏi
`src/social_scenario_motion.cpp`. Pose người lấy trực tiếp từ lịch sim time.
Giữ acceleration/deceleration và góc quay theo route, phase chân theo quãng
đường, căn hướng NK-046 và SetChanged để cập nhật GUI ở NK-045. Người xem
TV vẫn đứng lên/đến bình nước/dừng/quay về/ngồi theo kịch bản; người tuần
tra tiếp tục tuyến, quay ở góc. Pause/reset Gazebo vẫn dừng/reset toàn cảnh.

Bộ sinh `generate_social_dynamic_world.py` và world/config ghi
`reactive_yield=false`, `schedule_clock=simulation time; independent of robots`.
Marker quay về nhánh sample lịch danh định, khớp plugin chạy trực tiếp sim
time. Test Python cập nhật chính sách; C++ thay test người nhường bằng test
đặt từng robot1/2/3 chắn đường: patrol vẫn vượt qua vị trí robot theo lịch,
phase bước chân tiếp tục; di chuyển robot ra xa và chạy lại cùng thời điểm
cho pose/gait giống nhau. Giữ test GUI change flags, reset và hướng render.

Kiểm chứng: build thành công; 187 test Python qua, 2 warning SciPy Paper2,
3 file ament lint không chạy. 1 CTest qua, gồm 3 ca tên robot và 4.730 mẫu
hướng render trên hai chu kỳ tuyến trong ECM tổng hợp. Các test này xác
nhận lịch không bị robot kéo chậm, **không** xác nhận tránh va chạm. Test
C++ vẫn có cảnh báo ghi log ~/.ignition trong sandbox, output đã lưu repo.

Đã dừng phiên cũ để nạp .so rồi mở lại profile LiDAR-only domain32; giữ
camera tắt, không publish goal thay người dùng. Smoke Gazebo xác nhận
pose active khớp lịch danh định trong sai số <0,05 m, avatar inactive ẩn,
controller ba robot activate; chưa có ca chặn có kiểm soát.
README môi trường động và
hai README bắt buộc cập nhật. Không commit/push GitHub.

Giới hạn: người là kinematic, có thể tiếp tục đi vào robot không né kịp;
không còn cơ chế người dừng để che lấp lỗi né robot. Lỗi leader/đội hình
vẫn mở, cần đo contact/clearance khi thử. Chưa thử có kiểm soát tình huống
robot chặn người trong Gazebo; ca đặt robot chặn ở trên là ECM tổng hợp.

[Chính sách cảnh](docs/evidence/2026-11-01/pedestrians_no_yield/scenario_policy.json),
[test plugin](docs/evidence/2026-11-01/pedestrians_no_yield/plugin_test.log),
[hồi quy](docs/evidence/2026-11-01/pedestrians_no_yield/regression.log).
Báo cáo mục14 ghi rõ trước/sau chính sách, không đặt phiên bản giả.

### NK-048 — 01/11/2026 — Điều chỉnh né và tải runtime theo đối chiếu NK-034

Người dùng yêu cầu xem lại vì NK-034 ghi nhận hai follower đã né được,
nhưng phiên hiện tại né kém và RTF chậm. Tôn trọng kết quả quan sát NK-034;
đây không phải source tag nên không có căn cứ rollback nguyên trạng một
phiên bản Git tên NK-034. Mở rộng ca hình học follower đã lưu sang hai vai
robot1/robot2 để giữ hành vi đó trong kiểm thử.

Phát hiện ban đầu: chỉ còn Gazebo server/GUI, không còn coordinator/MPC/
bridge/RViz. Audit 60 s không nhận clock/state, không phải phép đo né hợp lệ.
Gazebo vẫn có stats RTF .0783; CPU 10 s server~130%, GUI~104% một lõi.
Không kết luận ai đã đóng ROS hoặc lỗi thuật toán gây mất node. Mở lại đủ
stack bằng setsid/nohup để không phụ thuộc vòng đời terminal công cụ; không
cài dịch vụ hay tự khởi động hệ thống.

Tái hiện số học bằng production MPC: người đứng (.75,0), đã xác nhận,
ngoài vùng nguy cơ của robot đang đứng nhưng chắn target (1.2,0). Bản trước
cả ba vai dừng ở rollout step 6, track reject 58; không vào nhánh né vì chỉ
xét stationary TTC. Bản sau gọi nhánh né đã kiểm tra khi track confirmed
chặn rollout, ưu tiên dịch ngang; latch 2,5 s để reference rỗng không cắt
lệnh né ngay tick sau. Vẫn giữ toàn bộ kiểm tra sweep/body/map/raw LiDAR/
peer/freshness/gia tốc; không bỏ track chưa xác nhận khỏi hard constraint.

Tối ưu local search: thử thẳng tới các đích trái/phải/sau bằng cùng edge/
hold predicates trước A*, giữ budget hữu hạn cả hai giai đoạn. Benchmark
50 lần cùng đầu vào dựng: median edge checks 171→7, median thời gian local
plan khoảng 1,13→0,040 ms. Đây chỉ là microbenchmark hàm local, không phải
MPC/Gazebo/RTF benchmark; path preference đổi rear→left trên ca này.

Đo CPU đủ stack cho thấy cả GUI/server và các node Python đều cao. GDB
attach bị OS ptrace từ chối; không thay sysctl hay quyền bảo vệ. Dùng
cProfile 20 s với một follower và coordinator, lần lượt dừng/thay node cùng
tham số, không tạo hai cmd publisher đồng thời. Sau đo phục hồi rồi mở
sạch cả stack ở bước kiểm chứng cuối. Profiler có overhead; không dùng nó
để tuyên bố mức tăng RTF. Kết quả quan trọng: coordinator tốn ~14,3/20 s ở
_take_subscription, tạo hàng chục nghìn TransformStamped từ stream toàn
link; follower phần lớn ở executor chờ/xử lý sự kiện, không ở rollout MPC.

Sửa tải dữ liệu: C++ NavigationStateStream chỉ phát 3 pose model robot ở
20 Hz sim, clock điều hướng 100 Hz sim. Giữ clock đầy đủ cho điều khiển
bánh xe và toàn ROS khác, chỉ remap coordinator/ba MPC sang clock gọn.
Header stamp ghi ở từng pose để TF bridge giữ đúng epoch; coordinator
không gắn timestamp nhận thay capture. Callback scan cho phép 20 ms future
skew do transport/clock 100 Hz, không tăng TTL stale .3 s. Không đưa pose
người/timeline vào perception hay điều hướng. Được cài trong cả hai scene.
Actor flag chuyển OneTimeChange→PeriodicChange; state GUI dynamic 30/10 Hz
wall thay vì phát event liên tục. Physics step, raw scan 240×91 leader,
follower scan và tần số LiDAR không bị đổi.

Lượt đo trung gian phát hiện robot2/leader tới quá gần (<footprint), nên
không gọi đó là kết quả đã sửa né thành công. Thêm margin peer bước đầu
theo tuổi state; tách cặp từ <.48 m tới .56 m thay vì đợi tới gần.37 m.
Không cho phép hồi phục xuyên footprint .32 m. Giữ checks peer dự báo và
pose đo đồng thời khi phát escape. Status thiếu sensor bổ sung tuổi state/
scan, coverage và physical_map; status rollout bị chặn bổ sung nearest track.

File: controller, local_escape, test_avoidance_regression và test follower;
CMake, src/navigation_state_stream.cpp, social_scenario_motion.cpp,
scene_geometry, generate_social_dynamic_world, hai world và bridge config,
dstar_mpc.launch.py, test_pedestrian_motion/plugin. Hướng dẫn động và tài
liệu camera–LiDAR–điều khiển cập nhật, giữ hai paper và scene tĩnh/động.

Kiểm tra: 199 test Python qua; 2 warning SciPy Paper2, 3 file ament lint
không chạy; CTest plugin qua. Ca follower cũ và hoán đổi vai đều qua;
ca route-blocked cả 3 vai có command ngang thay vì 0; reference rỗng không
cắt lệnh nhưng stale scan vẫn dừng. Có test phục hồi cặp .45 m lên>=.56 m,
và chấp nhận9 ms future scan nhưng từ chối stamp tương lai xa. Compile đầu
publisher gặp API Time không nhận chrono, đã dùng ghi sec/nsec đúng schema
và build lại qua; probe stamp 0 đầu tiên được sửa per-Pose header và chạy lại.

Runtime và giới hạn: các mẫu CPU trước/sau khác đoạn hoạt động, không là
A/B kiểm soát. Mẫu trung gian CPU coordinator~96→30%, MPC~77–83→16–17%
một lõi chỉ là quan sát; chưa chứng minh toàn bộ chênh lệch do một thay đổi.
Probe xác nhận clock gọn≈100 Hz sim và pose≈20 Hz sim, mỗi message chỉ có
robot1/2/3. Lượt trước đó chỉ còn Gazebo không dùng làm baseline đầy đủ.
Goal cuối từ log được lưu rồi restore sau khi nhận đủ state, nhường ưu tiên
cho mọi goal mới của người dùng; không phát helper goal mặc định từ lượt cũ.
Giữ camera tắt và người đi không nhường xe. Không push GitHub.

Chưa có contact sensor, benchmark lặp cùng seed/goal/timeline/hardware hoặc
xác nhận hết mọi lỗi leader/follower. Các số liệu ca dựng không thay thế
va chạm thực; cần tiếp tục kiểm controlled encounter của cả ba và track
identity/freshness khi có stop. Minh chứng runtime cuối và đánh giá được
lưu cạnh code test, không phụ thuộc duy nhất /tmp.

[Ca trước/sau](docs/evidence/2026-11-01/avoidance_rework/blocked_route_after.jsonl),
[local benchmark](docs/evidence/2026-11-01/avoidance_rework/escape_benchmark.json),
[profiler](docs/evidence/2026-11-01/avoidance_rework/coordinator_profile.txt),
[hồi quy](docs/evidence/2026-11-01/avoidance_rework/regression_final.log),
[stream](docs/evidence/2026-11-01/avoidance_rework/compact_stream_probe.json).
Báo cáo thêm mục15, phân biệt sửa code, test số học và Gazebo có giới hạn.

### NK-049 — 01/11/2026 — Tạm dừng phiên và chốt bàn giao ngắn

Theo yêu cầu người dùng, pause Gazebo dynamic, giữ trạng thái/đích; không
resume khi chưa được yêu cầu. Công việc lâu vì lần lượt phát hiện tải
message/executor, rollout bị track chặn và quán tính xe gây tiếp xúc đồng
đội dù command đã giảm. Đính chính bổ sung NK-048: reserve cuối dùng vận
tốc tương đối đo từ pose và khoảng hãm với giả định .15 m/s², không chỉ
margin cố định. Test có lag hai trục qua; hồi quy cuối199 test qua, 2 warning
SciPy, 3 lint file không chạy. Một thử tăng recovery target lên.70 m làm
hỏng ca connector maze, đã trả về.48/.56 m và kiểm lại qua.

Mẫu cuối60 s ghi nhận khoảng cách tâm nhỏ nhất lấy mẫu robot2/leader.427 m,
RTF trung bình.39; lượt trước từng xuống.291 m. Điều kiện hai lượt khác
pha/goal nên không gọi là A/B kiểm soát; chưa chứng minh hết va chạm.
[Phân tích cuối](docs/evidence/2026-11-01/avoidance_rework/runtime_braking/analysis.json).
Không tiếp tục mở thử/chỉnh thuật toán sau yêu cầu pause; không push GitHub.

### NK-050 — 01/11/2026 — Thêm đo contact physics để xác nhận người chạm robot

Yêu cầu: người dùng vẫn quan sát người đâm leader, muốn thêm collision để
nhận biết rõ hơn. Ghi nhận quan sát mới; NK-048/NK-049 chỉ có min khoảng
cách lấy mẫu, không có căn cứ phủ nhận contact giữa các mẫu hoặc mesh/proxy
khác nhau. Collision hình học đã có sẵn; thay đổi này bổ sung đo lường,
không coi là bản sửa xong tránh va chạm.

Triển khai `src/collision_audit.cpp`, CMake và config helper
`contact_audit_config.py`: đăng ký ContactSensorData trên tất cả human
collision proxy và robot parts ngoài roller. Physics sinh contact với ID
collision; lookup model theo cây entity, không dùng khoảng cách để suy.
Đọc mỗi bước physics để giữ tiếp xúc ngắn; gộp các điểm/part theo cặp model,
phát begin/update10 Hz sim/end/reset. Bỏ self-contact và ground_plane.
Giám sát human proxy vẫn nhận robot roller đối diện; robot–robot chỉ qua
roller có thể không ghi, nêu giới hạn thay vì tuyên bố giám sát mọi bề mặt.

`collision_monitor.py` đọc JSON, ghi append `log/collision_events.jsonl`,
log WARN khi chạm, publish điểm và nhãn đỏ tại `/collision_audit/markers`.
`contact_events.py` quản lý session/epoch, không đếm update như begin mới,
không nhận sự kiện từ epoch cũ để xóa contact mới. Header marker map dùng
vị trí tiếp xúc, không phỏng đoán điểm khi backend thiếu. Status có pause,
coverage_complete và physics_sample_received để không coi chưa lấy mẫu
là không va chạm. Node dùng wall time cho log, không thêm thuê bao clock
1000 Hz. Không dùng topic contact làm perception hoặc đầu vào điều khiển.

Hai generator/world và bridge YAML bật cùng bộ đo; launch
`social_navigation.launch.py` thêm monitor trong simulation, kể cả profile
LiDAR-only. RViz có display Physics Contacts. Hướng dẫn chi tiết
[COLLISION_AUDIT.md](docs/COLLISION_AUDIT.md). Không đổi body collision,
ngưỡng né, kịch bản người đi hay goal; không thêm cơ chế người nhường robot.

Kiểm chứng physics thực ở partition riêng: fixture người tiến vào/rời thân
robot đơn giản cho robot1/2/3. Mỗi ca có1 begin và1 end; robot1 begin
sim1.062 s, end2.979 s (số liệu fixture, không phải phiên robot thật).
Ca lệch y1 m không có begin/end; sàn không tạo báo chạm giả. File
`test/contact_fixtures/contact.sdf` và `physics_validation.json` giữ nguồn/
log để kiểm tra. Không dùng test khoảng cách thay contact trong kết luận này.

Kiểm thử kín Gazebo→ROS bridge→CollisionMonitor ở ROS_DOMAIN_ID94 và
IGN_PARTITION riêng: ghi begin/end human_robot vào JSONL, nhận22 marker
messages, có sphere đỏ và end. Toàn bộ process thử đã đóng, không phải
replay phiên chính hay chứng minh leader đã tránh được người.

Build qua sau sửa hai warning indentation. Tests pure kiểm schema,
lifecycle/reset/late epoch, tất cả human có proxy collision và profile tắt
camera vẫn bật diagnostic. Hồi quy đầu206 qua/1 fail vì test ablation cũ
đòi tắt mọi node; sửa test để chỉ tắt perception/social, giữ monitor. Ghi
kết quả cuối: **208 test Python qua**, 2 warning SciPy Paper2, 3 file
ament lint không chạy; [log](docs/evidence/2026-11-01/collision_audit/regression.log).
Hai bài báo và cả hai môi trường giữ.

Đã thử nạp plugin bằng dịch vụ entity/system/add để giữ pause/goal nhưng
timeout. Kiểm tra sau đó không còn Gazebo/ROS của phiên chính, log có
shutdown SIGINT/SIGTERM; không xác định ai/đâu gửi, không quy cho thuật toán.
Không tự mở lại hoặc resume. Không có xác nhận bộ đo đã nạp phiên cũ;
launch mới sẽ tự nạp. Chỉ các fixture độc lập được chạy cho tác vụ này.

Giới hạn: proxy contact khác visual mesh/áo/tay; chưa đo lực/độ xuyên,
chưa benchmark chi phí GetContacts, chưa replay leader đầy đủ hoặc xác nhận
né an toàn. Số contact tính theo cặp model vật lý, có thể đổi khi chuyển
avatar; không phải số người độc nhất. Không push GitHub.

[Physics](docs/evidence/2026-11-01/collision_audit/physics_validation.json),
[wire](docs/evidence/2026-11-01/collision_audit/wire_validation_verified.json),
[JSONL thật](docs/evidence/2026-11-01/collision_audit/wire_events.jsonl),
[build](docs/evidence/2026-11-01/collision_audit/build.log).
Báo cáo thêm mục16 chỉ ghi cải tiến đo lường và mức kiểm chứng.

### NK-051 — 01/11/2026 — Audit contact trong phiên LiDAR-only hiện tại

**Yêu cầu:** kiểm tra mô phỏng đang chạy. Chỉ đọc ROS/Gazebo/log; không sửa
thuật toán, gửi goal, pause/resume/restart hoặc push GitHub.

**Kết quả:** phiên domain32 có diagnostic physics đủ 3 robot, 14 proxy người,
31 collision được theo dõi. Contact `robot3|tv_viewer_a_walking` bắt đầu sim
29.751 s tại `(1.7482,-2.3801,0.1094)` trên base_link collision của leader,
kết thúc sim35.557 s, kéo dài5.806 s. Đây là contact physics thật, không phải
suy từ ảnh hay khoảng cách tâm. Log được sao lưu trước/sau audit.

Mẫu đầu chưa hoàn tất60 s (chỉ giữ khoảng9 s snapshot); mẫu kế tiếp hoàn tất
15 s wall, sim83.83→87.51 s, RTF≈.246; một mẫu stats riêng≈.2111. Leader cuối
mẫu cách goal người dùng≈.0483 m. Robot1/2/3 lần lượt có6/51,10/41,3/47 lệnh
tịnh tiến khác0. Leader xen kẽ hold do no verified safe escape và dữ liệu
quá tuổi; robot2 có checked local escape. Không suy lệnh khác0 là né thành công.

**File/minh chứng:** hai README và
[analysis](docs/evidence/2026-11-01/collision_live_audit_143718/analysis.json),
[contact log](docs/evidence/2026-11-01/collision_live_audit_143718/contacts_after_audit.jsonl),
[summary](docs/evidence/2026-11-01/collision_live_audit_143718/followup/summary.json).
Không chạy lại unit test vì không sửa code ứng dụng.

**Giới hạn:** dữ liệu ROS lấy sau khi contact đã kết thúc, không đủ chứng minh
nguyên nhân trước contact. RTF không phải A/B. Leader gần goal khiến đứng yên
không tự chứng minh lỗi bám đường. Chưa sửa xong né người; báo cáo mục16 được
bổ sung kiểm chứng toàn scene, không tạo phiên bản thuật toán mới.

### NK-052 — 01/11/2026 — Thoát đệm map khi né và giảm backlog LiDAR

**Yêu cầu:** sửa né sau giải thích cơ chế đội hình/đến goal. Đọc lại code
cho thấy nhánh khẩn cấp đã hoạt động trước kiểm tra reference và coordinator
đã yêu cầu replan khi safety trở về normal. Không thêm một cơ chế phục hồi
trùng lặp; đính chính diễn giải trước rằng reference rỗng đồng nghĩa không
có tự phục hồi. Việc replan vẫn phụ thuộc pose/map và điều kiện đường đi.

**Hạn chế phát hiện:** escape đòi clearance inflation ngay từ đầu sweep.
Khi tracking đã vào đệm nhưng thân vẫn cách vật cản, cả chuyển động đi ra
xa cũng bị loại. Đây là lỗi chứng minh được bằng test dựng; chưa có bằng
chứng nó là nguyên nhân chính của contact NK-051.

**Sửa:** `social_navigation_planner/social_navigation_planner/dstar_mpc_controller.py`
thêm predicate map dùng chung search và rollout: clearance đầu>=radius+.01m,
không giảm trên sweep và tăng tại endpoint; dừng cuối recovery phải ngoài
đệm đầy đủ. Không nới khoảng hở với người/peer hoặc freshness. Khi hold,
log `rejected` đếm lý do đầu tiên mỗi ứng viên; không coi là tổng mọi ràng
buộc vi phạm. Bỏ duyệt tốc độ trùng nếu max_speed trùng mẫu cố định.
`social_navigation_sim/scripts/leader_obstacle_scan.py` và subscriber scan
của MPC dùng BEST_EFFORT depth1 để ưu tiên mẫu mới. Không giảm số tia hay
đổi TTL. Không hứa QoS sửa được trễ từ GPU/TF/bridge.

**Kiểm chứng:** thêm4 ca tại `test/test_avoidance_regression.py`: ba vai ở
clearance .17m, inflation .18m, không reference, người đi tới; xe rời đệm
và giữ swept separation người>.47m trong mô hình kinematic. Ca còn lại loại
đi vào tường, đi song song trong đệm, thiếu reserve thân và sweep xuyên ô
occupied. Ablation cùng code chỉ đổi predicate map: cũ fail3/mới pass3;
không phải benchmark toàn phiên bản. Đã qua70 test né mục tiêu và212 test
toàn bộ Python (2 warning SciPy Paper2,3 file ament lint bỏ qua). Lần gọi
pytest đầu ghi3 skipped do ghi đè PYTHONPATH làm mất ROS; đã sửa môi trường
và chạy lại thật. Một thử nghiệm kiểm hold cho mọi rollout làm fail2 ca
follower cũ; đã giới hạn hold bổ sung cho map/uncertainty recovery, chạy
lại cả2 ca và toàn bộ hồi quy đều qua. Build2 package thành công; projector
installed so sánh bằng cmp trùng nguồn.

[Hồi quy](docs/evidence/2026-11-01/escape_margin_fix/regression.log),
[build](docs/evidence/2026-11-01/escape_margin_fix/build.log),
[ablation](docs/evidence/2026-11-01/escape_margin_fix/predicate_ablation.json).

**Giới hạn/bước tiếp:** chưa khởi động lại hoặc replay Gazebo, chưa đo RTF/
latency sau đổi QoS, chưa bảo đảm hết va chạm. Reserve1cm là ràng buộc kỹ
thuật của nhánh recovery, chưa hiệu chuẩn động học thật. Giữ phiên hiện tại
và goal; code mới chỉ có hiệu lực trên process khởi động sau. Không push.
Báo cáo thêm mục17, chỉ ghi cải tiến cục bộ và mức kiểm chứng thực tế.

### NK-053 — 01/11/2026 — Xác nhận leader vẫn contact trong phiên mới

**Yêu cầu:** đọc phiên đang chạy, giải thích ba xe dùng A* và khoảng cách
LiDAR/an toàn. Chỉ đọc topic/log và nguồn; không sửa thuật toán hoặc vận hành
phiên. Người dùng quan sát contact được physics xác nhận: session
`1793519553895176935`, cặp `robot3|tv_viewer_a_returning`, sim106.239→108.617s,
duration2.378s, bắt đầu ở `(0.8400,-2.3788,0.0202)` trên base_link collision.
Coverage đủ3 robot/14 proxy. Không gọi bản sửa NK-052 đã giải quyết contact.

**Mẫu15s sau contact:** sim149.24→153.43, RTF≈.282; leader có11/58 lệnh
linear khác0, đi≈.379m theo snapshot, cuối cách goal≈.107m. Có status
`A*=rear` nhưng nhãn này bao gồm direct-goal shortcut, không chứng minh
A* mở lattice ở lần đó. Có reactive fallback, no verified safe escape
với64 ứng viên bị track loại, và stale scan. Robot2 cũng có fallback/hold.
Gap ước lượng âm không chứng minh overlap physics. Mẫu không thu trước
contact nên không kết luận nguyên nhân chính. Goal không đổi.

**Đối chiếu nguồn:** cả3 cùng class MPC; chỉ gọi search khi nguy cơ/TTC
hoặc route bị chặn, không phải thấy người là gọi A*. Thử6 đích .56/.72m
trái/phải/sau, shortcut trước space-time lattice; sau đó mọi lệnh vẫn qua
rollout. LiDAR sensor .08–10m/5Hz; projector leader self_radius .16m,
height .025–.40m; MPC dùng điểm trong3.5m, normal rollout lấy điểm tĩnh
trong2.5m. Robot_radius .15m, inflation .18m; raw point cách tâm>=.18m.
Người dùng envelope track +.15+.03m, track radius có .08+.10*age uncertainty;
không phải cố định .18m từ tâm người. Peer nominal .46m + braking reserve,
nhánh escape preferred .42m, physical separation .32m với recovery rules.
Không sửa các tham số trong audit.

[Summary](docs/evidence/2026-11-01/leader_contact_recheck/summary.json),
[events](docs/evidence/2026-11-01/leader_contact_recheck/events.jsonl),
[contact](docs/evidence/2026-11-01/leader_contact_recheck/contacts.jsonl).
Không chạy lại unit test vì chỉ đọc và ghi tài liệu. Báo cáo bổ sung bằng
chứng phủ định hết lỗi; chưa benchmark A/B, không push.

### NK-054 — 01/11/2026 — Chia sẻ hướng né đã kiểm tra giữa các xe

**Yêu cầu:** leader tận dụng đường follower tìm được, giảm chọn hướng né
riêng lẻ gây cản nhau. Triển khai phối hợp phân tán bằng prediction/status
đang có; không thêm ground truth hoặc gỡ kiểm tra va chạm đồng đội.

**Nguồn:** `social_navigation_planner/social_navigation_planner/cooperative_escape.py`,
`dstar_mpc_controller.py`, `local_escape.py`; test `test_cooperative_escape.py`.
Nhận safety của peer chỉ khi đang yielding với checked local escape; dùng
prediction MPC, không dùng đề xuất `/escape_path`. Chọn peer ưu tiên index
nhỏ hơn (robot1 rồi robot2 rồi leader) nhằm tránh vòng tham khảo. Peer phải
trong2.5m, prediction/status còn hạn .4s sim/2s wall, khớp measured pose
trong .12m, có dịch chuyển .04m trở lên. Thu hồi khi peer hold/normal hoặc
clock reset. Không có handshake/lịch khóa hành lang, không ép robot đang
bị đe dọa đứng chờ. Đây là ưu tiên hướng, chưa phải scheduler hoàn chỉnh.

Search thử thêm hướng world của peer từ vị trí chính xe nhận, .56/.72m;
rollout thêm candidate hướng đó và alignment cost, nhưng tất cả vẫn chịu
map, raw LiDAR, track, peer sweep và braking reserve. Nếu không hợp lệ,
xe chọn hướng khác hoặc giữ dừng. Goal/đội hình phục hồi giữ cơ chế cũ.
Status thêm `team_owner` (index0=robot1,1=robot2;None khi không tham khảo).

**Kiểm chứng ban đầu:**12 test mới qua: ưu tiên không tạo chu kỳ, hết hạn
sim/wall, thiếu status, peer đứng yên, vị trí lệch, nonfinite, future stamp,
peer xa; search không nhận hướng bị chặn; production leader phát hướng
follower, thu hồi khi hold, và tránh hướng bị xe thứ ba chắn. Đối chứng
cùng hình học: không có trạng thái peer yielding thì cmd_y≈+.07391m/s;
có trạng thái hợp lệ thì cmd_y≈−.07391m/s. Đây là mô hình kinematic/đầu vào
dựng, không phải chứng minh hành lang Gazebo an toàn. Build planner qua.
Một test mới ban đầu đặt follower ngoài2.5m nhưng kỳ vọng có gợi ý, đã
sửa fixture để phù hợp và thêm ca âm peer xa; không nới điều kiện nguồn.
Lượt toàn bộ đã khởi chạy trước sửa fixture ghi222 qua/1 fail; lưu riêng
`regression_before_fixture_fix.log`. Lượt cuối với fixture đúng: **224 test
Python qua**,2 warning SciPy Paper2;3 file ament lint không chạy. Không có
Gazebo trong các test này. Import module từ install thành công.
[Hồi quy cuối](docs/evidence/2026-11-01/cooperative_escape/regression.log).

[Tests](docs/evidence/2026-11-01/cooperative_escape/guidance_tests.log),
[đối chứng](docs/evidence/2026-11-01/cooperative_escape/direction_comparison.json),
[build](docs/evidence/2026-11-01/cooperative_escape/build.log).

**Giới hạn:** chưa replay contact NK-053, chưa đo RTF/latency hoặc chứng
minh hết va chạm. Nhánh track/stale có thể vẫn chặn. Giữ phiên chạy/goal,
không restart hoặc push. Logic mới cần process khởi động lại để có hiệu lực.
Báo cáo thêm mục18, phân biệt phối hợp hướng với lịch nhường độc quyền.

### NK-055 — 01/11/2026 — Phản ứng sớm, TTC tương đối và tách nhận dữ liệu

**Yêu cầu:** sửa các chỗ có thể gây leader nhận biết/phát lệnh né muộn.
Người dùng tiếp tục báo va chạm; không yêu cầu kiểm thử lại để xác nhận
hiện tượng đã có. Việc kiểm tra trong tác vụ nhằm xác minh sửa code, không
phủ nhận quan sát đó. Không tự vận hành lại phiên Gazebo chính.

**Thay đổi:** hoàn thiện các nhánh phản ứng sớm/budget/ingress có trong
workspace, kiểm tra tích hợp và bổ sung test. `moving_obstacles.py` cho
hai quan sát nhất quán tạo velocity provisional (span>=.1s, displacement
>=.03m, speed .05–1.7m/s); vẫn cần ba mẫu/span>=.2s để confirmed. Ở scan5Hz,
hai mẫu liên tiếp trải .2s so với .4s của ba mẫu, chỉ là giới hạn theo lịch
capture, không phải latency runtime đã đo. TTC dùng velocity người trừ
velocity world của xe lấy từ measured team poses. Noise/duplicate stamp
không tạo provisional motion. Không cho unconfirmed tự thoát body overlap.

`latest_inputs.py` lưu message mới nhất mỗi topic bằng lock ngắn; mỗi
MPC có ingress group riêng và MultiThreadedExecutor2 threads. Callback
nhận chỉ đưa message vào inbox; callback control drain map/pose trước scan,
state không bị hai thread sửa cùng lúc. Control và watchdog cùng nhóm mặc
định. Giữ receipt wall time cho pose/scan/reference/prediction/status, không
làm dữ liệu cũ thành mới do chờ drain. Python GIL vẫn tồn tại.

`dstar_mpc_controller.py` thêm control_budget_ms60 và escape_search_budget_ms8,
kiểm0<search<control<100ms. `local_escape.py` kiểm deadline giữa các bước
search, MPC kiểm giữa các ứng viên/rollout; chỉ dùng candidate đã kiểm đủ,
không phát đoạn path dở. Hết budget chưa có quỹ đạo đủ thì stop; normal MPC
hết budget cũng stop. Thử hướng đội hình/local/hướng ngang trước để giới hạn
thời gian không cứ ưu tiên compass0°. Kiểm lại tuổi scan/state trước lệnh
escape. Đây là deadline mềm: một phép geometry/map processing hoặc GIL có
thể quá hạn; không quảng cáo bảo đảm60ms tuyệt đối.

**File:** planner `moving_obstacles.py`, `latest_inputs.py`, `local_escape.py`,
`dstar_mpc_controller.py`; `test_early_reaction.py`, cập nhật kỳ vọng velocity
hai mẫu provisional trong `test_moving_obstacle_safety.py`; hai README.

**Kiểm chứng thực hiện:**82 test né mục tiêu qua;10 test mới qua (hai mẫu,
noise/duplicate, relative TTC/parallel motion, search deadline, inbox latest
và ordering, cả ba vai phản ứng mẫu thứ2, hết budget không phát lệnh dở).
Hồi quy toàn bộ **234 test Python qua**,2 warning SciPy Paper2,3 file ament
lint không chạy. Build planner qua. Kiểm ROS riêng domain99 trên class MPC
thật nhận scan khi callback thuộc control group đang chờ Event; không nối
vào domain32/không chạy Gazebo, probe nhả GIL nên không phải benchmark tải
CPU. Các node kiểm tra đã shutdown.

[Hồi quy](docs/evidence/2026-11-01/early_reaction/regression.log),
[test mới](docs/evidence/2026-11-01/early_reaction/new_tests.log),
[ROS ingress](docs/evidence/2026-11-01/early_reaction/ingress_validation.json),
[script tái hiện](docs/evidence/2026-11-01/early_reaction/check_ingress.py),
[build](docs/evidence/2026-11-01/early_reaction/build.log).

**Giới hạn:** chưa đo end-to-end GPU→bridge→MPC→chuyển động hoặc replay
contact NK-053. Provisional2 mẫu dễ chịu sai số hơn confirmed; giữ các
ngưỡng và kiểm clearance. Người đã vào estimated body reserve vẫn có thể
làm mọi hướng bị loại; không nới safety để ép chạy. Không khẳng định hết
va chạm/RTF tăng. Giữ phiên chính/goal, không push. Code mới cần process
khởi động sau; báo cáo thêm mục19 theo đúng mức bằng chứng.

### NK-056 — 01/11/2026 — Chạy bản mới và sửa hồi quy xe đứng im

**Yêu cầu:** mở bản mới; người dùng tiếp tục báo xe không chạy. Đã xác
nhận không còn stack cũ trước khi mở profile LiDAR-only domain32 bằng
script hiện hành; Gazebo/RViz lên, wheel controller đủ3 xe hoạt động,
contact coverage đủ3 robot/14 proxy. Runtime param leader60ms/8ms. Log có
RViz GLSL sampler link error nhưng RViz vẫn gửi goal; không tự quy đây là
nguyên nhân xe đứng. Không publish goal. Startup/backup log ở
`docs/evidence/2026-11-01/new_session_182452/`.

**Lỗi hồi quy của NK-055:** trong8s lấy mẫu cả3cmd đều0 dù clock/pose và
reference có dữ liệu. Inbox dùng topic làm khóa làm hai subscriber `/map`
(cùng input nhưng planning-map callback và physical-map callback khác)
loại nhau. Sửa `latest_inputs.py` dùng (topic,callback) để coalesce từng
consumer. Test tái hiện gửi3 map, cả2 callback phải nhận mẫu mới nhất.
Restart riêng3 MPC với nguyên args/env/params, giữ Gazebo và goal. Sau
sửa này cả3 vẫn đứng, đã có status rõ `compute_budget: normal MPC stopped
before complete rollout`; không kết luận thành công sớm.

**Lỗi budget tiếp theo:** beam12 phát triển nhiều nhánh ở depth đầu, hết
60ms trước khi quỹ đạo đủ8 bước. Sửa finite-budget normal pass giữ1 branch
mỗi depth, nhánh không deadline giữ12; không dùng rollout dở để phát lệnh.
Thêm3 test cho cả3 vai hoàn tất9 pose prediction và lệnh tiến với60ms trong
corridor trống. Restart riêng3 MPC lượt cuối. Goal gần nhất người dùng chọn
`(1.03515,-2.67986)` giữ nguyên; lịch người không reset.

**File:** `latest_inputs.py`, `dstar_mpc_controller.py`, `test_early_reaction.py`,
hai README. Test đầu11 ca qua cho inbox, cuối25 ca gồm early/input/budget
và formation MPC qua. Build planner thành công. Không chạy lại toàn bộ
234 test sau thay đổi này; không mượn kết quả đó làm xác nhận bản mới.

**Kết quả live:** mẫu10s sau lượt sửa cuối có8/37,11/32,8/37 lệnh khác0
lần lượtrobot1/2/3; dịch chuyển tâm snapshot≈.184/.161/.094m. Không đồng
nhất count khác0 với né thành công. Cuối mẫu leader vẫn hold vì track
loại15 ứng viên trước hết budget; follower2 cũng hold. Không khẳng định
xe chạy liên tục/đạt goal/hết va chạm. Beam1 có thể giảm khả năng thoát
local minimum so với beam12; cần đánh giá đường đi và retry có kiểm soát.

[Tests](docs/evidence/2026-11-01/map_inbox_fix/tests_final.log),
[build](docs/evidence/2026-11-01/map_inbox_fix/build_apply.log),
[trước](docs/evidence/2026-11-01/map_inbox_fix/runtime_before_summary.json),
[inbox sửa nhưng budget còn lỗi](docs/evidence/2026-11-01/map_inbox_fix/runtime_inbox_only.json),
[sau](docs/evidence/2026-11-01/map_inbox_fix/runtime_summary.json).

**Vận hành:** ba process MPC thay thế detached, PID66269/66270/66271;
launcher chính không quản lý lifecycle chúng. Khi đóng phiên, dừng cả3
PID sau khi xác minh cmdline để tránh sót node. Các node observer đã dừng.
Không push GitHub. Báo cáo mục20 chỉ nêu sửa hồi quy và bằng chứng giới hạn.

### NK-057 — 01/11/2026 — Giải thích điều khiển lúc có lúc mất

**Yêu cầu:** vì sao xe chạy rồi lại dừng. Mẫu10s chỉ đọc domain32, giữ nguyên
phiên/goal, không sửa thuật toán. Robot1/2/3 lần lượt2/28,6/27,2/31 lệnh khác0.
Đây là count message, không phải phần trăm thời gian hay tỷ lệ né thành công.
Leader có11 lần status đổi sang no verified safe escape,9 fresh-data stop,
3 stale sensor stop,1 checked escape,1 normal và1 normal compute-budget stop.
Các count là thay đổi chuỗi status, không phải số encounter độc lập.
Cuối mẫu leader scan_capture_age hiển thị .300s sát ngưỡng .3; track hold
và budget_expired=True ở hai follower. Không tăng TTL hoặc giảm safety.

**Đối chiếu code:** guard chuyển normal trước nhánh bám reference nên normal
không đảm bảo xe chạy. Coordinator xóa/phát reference rỗng khi moving safety
active và replan khi normal; nếu escape cũng fail, có thể tạo dừng–replan
lặp. Mẫu này không thu reference đồng bộ nên không quy toàn bộ gián đoạn
cho vòng lặp. Beam1 của NK-056 vẫn có lượt quá budget: chỉ gỡ đứng im hoàn
toàn, chưa khôi phục điều khiển ổn định. Giữ lịch sử và đính chính phạm vi
kết luận bằng mục này, không sửa kết quả đo cũ.

[Runtime](docs/evidence/2026-11-01/stop_go_audit/runtime.json),
[observer](docs/evidence/2026-11-01/stop_go_audit/observe.py).
Chỉ thêm tài liệu/minh chứng, không chạy lại unit test. Báo cáo bổ sung
bằng chứng giới hạn của mục20; không tạo phiên bản thuật toán. Không push.

### NK-058 — 01/11/2026 — Sửa chuyển bám đường–né–phục hồi và kiểm nhanh

**Yêu cầu:** sửa hiện tượng lúc chạy lúc mất lệnh sau audit NK-057. Giữ
ràng buộc safety, goal, Gazebo và lịch người; không dùng lệnh cũ chưa kiểm
để làm chuyển động trông liên tục.

**Coordinator:** giữ route khi nhận moving safety thay vì xóa cả đội.
Trong safety mode, reference vẫn đủ horizon: xe đang né được target giữ
ở pose đo để không kéo ngược về đội hình; xe khác lấy phần tương lai còn
lại của reference trước đó và giữ endpoint khi hết horizon. Timestamp gốc
của cache không được gia hạn nên không ngoại suy tuyến vô hạn. Local MPC
vẫn kiểm từng lệnh. Thiếu pose mới thì vẫn reference rỗng. Hazard_clear
hoặc normal kết thúc hold có .4s hysteresis trước phục hồi; `control_tick`
replan một lần từ measured pose sau khi hết safety, không replan theo mọi
message dao động. Reset clock xóa cache/hold/release state.

**MPC:** guard không phát normal ngay trước nhánh bám đường; khi hết nguy
cơ phát hazard_clear riêng. Normal chỉ sau emit tracking. Thêm một rollout
bám reference đủ8 bước được kiểm trước branching finite-budget MPC; nếu
đủ map,raw LiDAR,track,peer,braking/gia tốc thì phát ngay. Nếu bị chặn thì
vẫn thử beam. Escape finite-budget chọn candidate đầu tiên đã kiểm đủ thay
vì luôn duyệt hết tốc độ/hướng. Không dùng path dở hay lặp lệnh cũ. Emit
tracking kiểm lại tuổi scan/state; không nới TTL. Chi phí chọn quỹ đạo này
không tối ưu toàn bộ tập ứng viên như nhánh duyệt đầy đủ.

**File:** planner `dstar_mpc_controller.py`; test mới `test_stable_handoff.py`,
fixture `test_mpc_formation_motion.py`, kỳ vọng status/reference mới trong
`test_escape_and_observation.py`, `test_moving_obstacle_safety.py`, và chuẩn
bị scan fresh cho test finite-budget trong `test_early_reaction.py`.

**Kiểm chứng:**3 test mới qua: route còn nguyên qua nhiều safety message,
cache không gia hạn/không ngoại suy, target xe active giữ ở actual pose,
release có hysteresis; tracking nhanh bị raw scan/peer chắn thì bị loại,
scan hết tuổi không emit. Hai kỳ vọng cũ empty-reference/normal được đổi
đúng hợp đồng mới. Một lỗi so sánh float ở biên .4s được sửa tolerance1e-9;
fixture mới bổ sung observation=None. Cuối cùng **241 test Python qua**,2
warning SciPy Paper2;3 file lint không chạy. Build planner qua.

Áp dụng bằng restart riêng4 node navigation, giữ Gazebo. Lưu đúng goal
endpoint path `(1.0351457595825195,-2.6798601150512695)` và phát lại sau khi
subscriber mới sẵn sàng; không chọn đích mới. Mẫu live20s: lệnh khác0 theo
robot1/2/3=30/63,28/57,11/56; sampled travel≈.074/.321/.175m. Cuối mẫu
leader cách goal≈.039m, reference cuối27 pose. Không có normal-MPC compute
budget stop trong status changes; vẫn có50 status đổi chứa budget_expired
True ở nhánh escape, track hold và stale sensor. Không xem các count là
thời lượng hoặc tỷ lệ né thành công; hai mẫu khác pha không phải A/B.

[Hồi quy](docs/evidence/2026-11-01/stable_handoff/regression.log),
[build](docs/evidence/2026-11-01/stable_handoff/build.log),
[phân tích live](docs/evidence/2026-11-01/stable_handoff/analysis.json),
[goal/node đã nạp](docs/evidence/2026-11-01/stable_handoff/applied.json).

**Giới hạn/vận hành:** chưa benchmark lặp, chưa chứng minh hết contact.
Người/track đã quá sát hoặc scan stale vẫn có thể giữ dừng. Reference tạm
chỉ kết thúc horizon cũ, không hứa cả đội tiếp tục tới goal khi đang safety.
Coordinator PID68536 và MPC68537/68538/68539 là process detached thay thế;
không do launcher chính quản lý, khi đóng phiên phải dừng riêng sau xác
minh. Observer đã dừng; log mới ở thư mục minh chứng. Không push GitHub.
Báo cáo mục21 nêu đúng hành vi và giới hạn, không tạo release giả.

### NK-059 — 01/11/2026 — Thừa nhận chưa bảo toàn baseline follower NK-034

**Phản hồi:** người dùng nhắc mục9 báo cáo/NK-034: hai follower đã né được,
nhưng phiên hiện tại cả3 gặp lỗi. Giữ nguyên kết luận thành công của hai
follower ở lượt đó, không dùng giới hạn một lượt để phủ nhận quan sát.
Đối chiếu nhật ký/source, không chạy hoặc đổi trạng thái mô phỏng tác vụ này.

**Giải thích có bằng chứng:** sửa leader đã tác động class MPC/coordinator
chung cho3 xe, không có backend follower cũ được đóng băng độc lập. Sau
NK-034 còn đổi track/body-envelope/peer reserve, điều phối reference,
provisional motion, executor/inbox và deadline. NK-056 xác nhận hai hồi
quy do thay đổi chung: callback map ghi đè và timeout trước đủ horizon làm
cả3 đứng. Các lỗi đó đã sửa nhưng không chứng minh mọi hồi quy đã hết;
NK-057/058 còn track/stale/budget hold. Chưa đủ dữ liệu để chỉ một thay đổi
là nguyên nhân duy nhất của toàn bộ suy giảm hiện tại.

**Thiếu sót quy trình:** đã giữ test hình học follower và hoán đổi vai,
nhưng test dùng input dựng/phản hồi kinematic, phần lớn fixture không khởi
động node/executor/deadline thực. Vì vậy test qua không bảo vệ đủ chuỗi
Gazebo→LiDAR→MPC→actuator. Chưa giữ snapshot đầy đủ tương ứng NK-034 và
replay cùng scenario/goal/timeline làm điều kiện chặn trước khi tiếp tục
sửa shared controller. Việc thiếu tag không phải lý do hợp thức hóa mất
kết quả cũ. NK là nhật ký, không cam kết phiên bản có thể rollback chính xác.

**Hướng xử lý được giải thích:** ưu tiên khôi phục/đối chiếu follower theo
hành vi NK-034 trên ca runtime tái hiện được; tách thử nghiệm sửa leader
khỏi follower, chỉ ghép lại sau khi giữ được baseline. Đây là hướng đề xuất,
chưa triển khai nhánh cũ hoặc tuyên bố đã tìm đúng source snapshot. Không
rollback, không commit/push hoặc vận hành phiên trong lượt giải thích này.
Báo cáo bổ sung giới hạn bảo toàn baseline, không tạo phiên bản thuật toán.

### NK-060 — 01/11/2026 — Khôi phục baseline follower NK-034 và bắt buộc backup

**Yêu cầu mới:** khôi phục về bản hai follower đã né tại NK-034; từ nay
mỗi cải tiến phải có file backup bản cũ. Đã tạo archive trước mọi sửa nguồn,
giữ cả file chưa commit. Archive đầu585 file/≈70MB, đọc và đối chiếuSHA256
thành công. Có checkpoint thứ2 trước áp dụng candidate. Không commit/push.

**Tìm lại nguồn:** Git chỉ có commit cũ, không có tagNK-034. Tìm được bản
vá/edit nguồn của phiên27–28/10 trong lịch sử local. NK-034 ghi quan sát
lượt sau NK-032; NK-033 nói source mới chưa nạp process. Vì vậy khôi phục
mã đang chạy ở lượt thành công, trước sửa NK-033, không tự gán code mới
cho kết quả cũ. Tái dựng candidate riêng từ base5ac6982 cùng patch/edit
được đối chiếu; không chạy lại các shell lệnh vận hành trong history.
Các edit Python đã lọc chỉ thao tác facade Path trong bộ nhớ để không ghi
nhầm workspace. Sau đó sinh world động từ generator cũ, chạy hồi quy.

**Phạm vi:** thay35 file nguồn/cấu hình đối chiếu được, đưa25 file thử
nghiệm sau baseline khỏi nguồn dùng (đã có trong backup). Giữ nguồn hai
paper, hai môi trường, hiện tên package chuẩn. Bốn file controller/moving/
local_escape/peer_safety khớp byte candidate. Giữ wiring paper ở setup và
hai launch để không mất tích hợp có từ trước nhưng không nằm trong Git
base. File paper untracked giữ từ bản trước khôi phục; không khẳng định
workspace đầy đủ bit-for-bit tại thời điểm NK-034. Thống kê/hash/provenance
ở restoration_manifest.json/source_edit_evidence.json. Lịch sử README cũ
không bị ghi đè; hướng dẫn hiện hành bỏ lệnh LiDAR-only đã không còn.

**Kiểm chứng:** candidate159 test Python qua,2 warning SciPy Paper2;
3 lint file không chạy. Build sạch2 package qua. Kiểm launch4 chế độ đầu
bị chặn vì ROS log mặc định ngoài sandbox read-only; đặt ROS_LOG_DIR=/tmp
rồi chạy lại tất cả `--show-args`, exit0. Không mở Gazebo ở phép kiểm này.
Bổ sung import PythonExpression/wiring Paper1/Paper2, giữ baseline mặc định.
Không lấy unit test làm bằng chứng né Gazebo sau khôi phục.

**Backup từ nay:** script `scripts/create_backup.py` tạo archive,manifest,
git-status; SHA256 từng file và archive, kiểm khớp nguồn, giữ symlink. Có
`--verify` kiểm archive độc lập. Test fixture có source,binary,symlink,
credentials giả/build/cache: giữ đúng nguồn, loại private/generated và
phát hiện archive bị sửa. AGENTS.md bắt buộc bước backup trước thay đổi
đầu tiên mỗi tác vụ cải tiến; khi đổi hướng/ghi đè trạng thái cần giữ thì
thêm checkpoint. Không tự xóa backup, không dịch vụ nền hoặc tự push.
`.gitignore`/COLCON_IGNORE loại backups khỏi Git/build mặc định.

**Vận hành:** dừng launcher64804 và4 node68536–68539, sau đó dừng trực tiếp
Gazebo64882/64883 còn sót; GUI cần SIGTERM. Không mở lại hoặc tự phát goal.
Baseline bật camera/perception như cũ; đi bộ trở lại lịch/tư thế cũ, không
hoạt ảnh/contact audit mới. Leader có lỗi lịch sử vẫn được giữ rõ, chưa
khẳng định follower hiện tại né lại thành công. Snapshot baseline cuối
được giữ riêng, xem `backups/README.md`.

[Phạm vi](docs/RESTORE_NK034.md),
[manifest](docs/evidence/2026-11-01/nk034_restore/restoration_manifest.json),
[hồi quy](docs/evidence/2026-11-01/nk034_restore/regression.log),
[build](docs/evidence/2026-11-01/nk034_restore/build_final.log),
[launch](docs/evidence/2026-11-01/nk034_restore/launch_validation.json),
[backup validation](docs/evidence/2026-11-01/nk034_restore/backup_validation.log).
Báo cáo ghi đổi baseline kỹ thuật và mức kiểm chứng; cơ chế backup chỉ
thuộc nhật ký/quy trình, không coi là phiên bản cải tiến thuật toán.

### NK-061 — 01/11/2026 — Chạy camera và ghi dữ liệu chẩn đoán theo phiên

**Yêu cầu:** chạy lại mô phỏng với camera và tạo nơi cập nhật dữ liệu để AI
đọc lỗi. Backup trước mọi sửa bằng script mới, snapshot
`backups/20261101_191847_271564_before_camera_session_diagnostics/` xác minh
với nguồn thành công. Đọc hai README, giữ nguyên nội dung kỹ thuật báo cáo
vì tác vụ là vận hành/quan sát, không cải tiến thuật toán né.

**Thực hiện:** thêm `scripts/run_diagnostic_session.py` làm supervisor cho
launch và observer; `scripts/session_recorder.py` chỉ subscribe, không phát
goal/cmd hoặc đổi tham số. Wrapper `run_dynamic_with_logs.sh` gọi supervisor,
source môi trường hiện có, domain mặc định31 có thể override. Mỗi run tạo
`log/sessions/<timestamp_Viet_Nam>/`, symlink `log/current` và pointer text.
File riêng launch/recorder/commands-status-events/scan/telemetry/session
metadata; summary được atomic replace mỗi1s wall. Lock tránh hai wrapper
cùng chạy. Supervisor ghi PID/lifecycle, chuyển signal để đóng launch và
observer, thu hồi cây process thuộc session theo PID+birthtime khi stop.
Không cài daemon hoặc cơ chế nền tự cập nhật README.

Ghi scan ranges (nonfinite=null), capture stamp và góc; command, pose,
reference, endpoint route và goal/status thay đổi. Nhận Image chỉ đếm frame,
stamp/kích thước/encoding, không lưu hoặc giải mã pixel. Chọn không nghe
raw clock tốc độ cao; sim_estimate lấy từ header pose. Có receipt age và
capture age ước lượng, không giả giá trị cho topic mất. DDS image traffic
vẫn tăng bởi subscriber metadata; chưa benchmark overhead. Viết hướng dẫn
`docs/CHAN_DOAN_PHIEN_CHAY.md`, cập nhật README gốc/dynamic cho đường dẫn log.

**Chạy thực tế:** không thấy stack cũ trước khởi động. Mở session lúc19:22:55
ngày01/11, domain31 với leader_camera:=true. Supervisor73993, launch74012,
recorder74011. Không tự chọn đích; RViz goal được thu theo topic, người dùng
có thể tự chọn và xem dữ liệu liên tục. Cả3robot có pose và scan; đã nhận
RGB/depth. Một mẫu lúc≈67s wall ghi74 RGB/93depth,97/97/61 scan theo robot;
đây là count subscriber, không phải loss rate hoặc fps benchmark.
Detector có status chờ matched RGB-D, vẫn giữ cảnh báo đó thay vì kết luận
perception hoạt động tốt. RViz GLSL sampler error cũ còn trong launch log;
RViz vẫn hoạt động/gửi goal. Không chỉnh detector hoặc graphics trong tác vụ.

**Kiểm chứng:** py_compile hai script và bash -n wrapper qua; hash4 module
core khớp baseline NK-060. Startup live có3pose, đủ3scan, cả2camera topic;
summary/session running, không diagnostics_error. Parse20 dòng cuối của
cả3 JSONL qua. Observer vẫn chạy theo phiên được người dùng yêu cầu;
không dừng mô phỏng để test shutdown. Không chạy lại159 test navigation vì
không sửa core; không dùng count log làm bằng chứng né/contact an toàn.

[Validation](docs/evidence/2026-11-01/camera_diagnostics/validation.json),
[core không đổi](docs/evidence/2026-11-01/camera_diagnostics/core_unchanged.json),
[snapshot startup](docs/evidence/2026-11-01/camera_diagnostics/live_summary.json),
[session](docs/evidence/2026-11-01/camera_diagnostics/session.json).

**Giới hạn:** chưa đo chi phí ghi scan/nhận metadata camera; không ghi rosbag
hay toàn bộ ảnh. Baseline không có contact sensor nên không suy không va
chạm từ log im lặng. Dữ liệu log/ bị gitignore; khi kết luận cần giữ lâu dài,
copy chọn lọc sang docs/evidence/ trong cùng cập nhật nhật ký. Không push.
Báo cáo kỹ thuật giữ nguyên, không tạo mốc thuật toán từ công việc logging.

### NK-062 — 01/11/2026 — Dừng phiên, đối chiếu hướng leader khi follower né

**Yêu cầu:** dừng phiên và cho biết leader quét được gì/ở khoảng cách nào
khi né phải vào phía người; người dùng sẽ chỉ ra vấn đề trước khi sửa.
Sau câu hỏi xác định thời điểm, người dùng trả lời “khi mà con follower
né người”. Giữ yêu cầu dừng, không sửa thuật toán. Đã gửi SIGINT supervisor
73993, supervisor đóng launch/recorder exit0 lúc19:30:56; xác nhận không
còn Gazebo/MPC. Toàn bộ dữ liệu session vẫn giữ tại
`log/sessions/20261101_192255_199210/`.

**Backup:** trước ghi tài liệu/evidence dùng snapshot
`backups/20261101_194101_886130_before_stopped_right_escape_audit/`, kiểm tra
nguồn/archive theo script. Không commit/push.

**Phương pháp:** lọc command robot3 bodyvy<−.04m/s và status yielding của
follower còn mới<2s wall. Đối chiếu latest preceding scan/camera/team pose
mà observer nhận, không giả rằng đây chính là frame MPC tiêu thụ. Có3đoạn:

| Giờ VN | Sim estimate | Follower đang yielding | Min LiDAR vùng phải −135..−45° | Cam candidate gần nhất |
|---|---:|---|---:|---|
|19:26:08|45.496|robot1|1.088m tại−89.6°|1.343m tại+38.8°|
|19:27:23|61.299|robot2|1.422m tại−91.1°|1.218m tại+11.7°|
|19:29:29|87.996|robot1 và robot2|1.086m tại−110.7°|.853m tại+28.7°|

Hai lệnh1/3 chủ yếu lùi có lệch phải, không phải dịch ngang thuần. Góc
cam dương ở đây là trước-trái theo thân xe; đoạn2 còn ứng viên xa4.427m
ở góc−42.3°. Không biết người dùng nói ai trong các ứng viên/kịch bản.
Raw LiDAR không có nhãn người; nhiều return có thể là ghế/map/xe khác.
Khung ảnh pixel không được lưu nên không tái xác nhận hình ảnh lúc đó.

Scan được chiếu về robot3/base_link, khoảng cách ngang, giữ độ cao .025–.40m,
tầm cấu hình .16–10m sau projector; scan_world_points dùng .18<r<3.5m rồi
lọc map/teammate. Số đo bảng là scan nhận được trước các lọc trong MPC.
Đoạn2 latest scan stamp60.4 so với command sim estimate61.299, cũ≈.899s
ước lượng; receipt trước lệnh4.398s wall. Không kết luận MPC chắc dùng
scan cũ đó vì các subscriber có thể nhận khác nhau. Ray null/không có
return không được coi là free-space. Đồ thị đã xem lại trục body: trước
lên, phải sang phải; arrow chỉ hướng command, không phải trajectory thực.

[Phân tích](docs/evidence/2026-11-01/right_escape_audit/analysis.json),
[hình](docs/evidence/2026-11-01/right_escape_audit/body_frame_comparison.png),
[events](docs/evidence/2026-11-01/right_escape_audit/selected_events.jsonl),
[scans](docs/evidence/2026-11-01/right_escape_audit/selected_scans.jsonl),
[session đã dừng](docs/evidence/2026-11-01/right_escape_audit/stopped_session.json).
Chỉ phân tích offline; không chạy unit test navigation, không tạo bản sửa.
Báo cáo bổ sung giới hạn kiểm chứng baseline đã được chạy, không tuyên bố
đây là kết quả cải thiện hoặc xác định xong nguyên nhân.

### NK-063 — 01/11/2026 — Ghi pose thật và phát lại quỹ đạo mô phỏng

**Yêu cầu:** lưu vị trí mọi vật thể, quãng đường người/xe và trình phát lại
có ảnh để xác định xe né phía nào, người đi ra sao; cung cấp lệnh chạy.

**Backup:** `backups/20261101_195516_955149_before_ground_truth_replay/` trước
thay đổi đầu tiên. Snapshot nguồn/assets/config/test/tài liệu gồm thay đổi
chưa commit, loại private/build/install/log/cache; archive đọc được và
SHA-256 so với nguồn qua, có `manifest.json`. Không xóa backup trước.

**Triển khai:** plugin PostUpdate chỉ đọc worldPose ECM,20Hz thời gian sim,
bao gồm model/actor cấp world và đối tượng ẩn. Lưu entityID/tên/pose6D,
time/epoch/pause. Không đưa ground truth vào navigation. Supervisor tạo
scene metadata và bật recorder qua biến môi trường; direct launch không
có biến thì không ghi. Viewer localhost đọc JSONL tăng dần, bỏ dòng dở,
hỗ trợ xem trực tiếp/tua/bước/chạy, vệt tách khi ẩn hoặc reset, heading và
vận tốc đo, hướng theo thân robot, PNG và HTML độc lập. Scene có geometry
primitive và actor proxy; không suy diễn trajectory từ lịch kịch bản.

**File:** `social_navigation_sim/src/replay_recorder.cpp`, CMake, hai world,
`social_navigation_sim/scripts/replay_plugin_config.py` và hai generator;
`scripts/run_diagnostic_session.py`, `scripts/replay_data.py`,
`scripts/view_replay.py`, `scripts/replay_viewer.html`,
`scripts/tests/test_replay_data.py`; README và hai tài liệu hướng dẫn
chẩn đoán/phát lại, hai README bắt buộc.

**Kiểm chứng thực chạy:** build plugin qua;164 test Python qua với2 warning
SciPy,3 file lint không chạy. Thử Gazebo headless world động ghi50 đối tượng;
fixture world riêng thêm3 cylinder robot có chuyển động scripted ghi53
đối tượng,90 frame (t.001–4.451s). Robot3 dịch1.111m, patrol1.7776m trong
fixture; không phải hiệu năng robot URDF hoặc MPC. HTTP incremental không
lặp frame/reset offset qua. Firefox xác minh nhãn phải/trái theo thân,
overlap và tách chiều cao, step/seek/play và screenshot. Lượt Firefox đầu
không chạy được do profile /tmp với snap; chuyển profile thử riêng vào
snap/common rồi chạy qua, không sửa profile người dùng. Bốn module core
byte-match backup; XML geometry hai world không đổi ngoài recorder.
Minh chứng bền vững: [thư mục kiểm chứng](docs/evidence/2026-11-01/ground_truth_replay/),
[ảnh viewer](docs/evidence/2026-11-01/ground_truth_replay/viewer.png),
[hồi quy](docs/evidence/2026-11-01/ground_truth_replay/regression_final.log),
[bảo toàn baseline](docs/evidence/2026-11-01/ground_truth_replay/baseline_integrity.json).

**Giới hạn:** chồng lấn là ước tính geometry, không physics contact. Envelope
robot radius.15m cao.2m không đủ bánh/mast; mesh chỉ có marker nếu thiếu
primitive; root roll/pitch chưa áp dụng đầy đủ;20Hz có thể bỏ qua va chạm.
Chưa benchmark overhead/RTF hoặc chạy main3 URDF/MPC với replay. Phiên cũ
`20261101_192255_199210` không có dữ liệu pose để phát lại chính xác.
Mô phỏng chính vẫn tắt; các world thử riêng đã kết thúc. Không sửa né hoặc
push. Báo cáo chỉ thêm năng lực chẩn đoán, không tuyên bố né tốt hơn.

### NK-064 — 01/11/2026 — Bỏ lưu chẩn đoán tự động của NK-061

**Yêu cầu:** xóa dữ liệu sessions và bỏ cơ chế lưu dữ liệu mỗi lần chạy
mô phỏng được thêm tại NK-061.

**Thực hiện:** xóa `log/sessions/` gồm hai phiên (~41MB), current/latest,
lock và log/PID supervisor. Không có observer đang chạy khi kiểm tra trước
xóa. Gỡ `scripts/run_diagnostic_session.py` và `scripts/session_recorder.py`;
launcher mới `scripts/run_dynamic.sh` exec trực tiếp ROS launch, bật camera,
không tạo session/log chẩn đoán. Script tên cũ chuyển sang alias không ghi.
Giữ ghi pose/phát lại NK-063 chỉ khi chủ động dùng `--record-replay DIR`;
không ghi scan/Image/command. Viewer yêu cầu `--session DIR`. Mặc định unset
SOCIAL_REPLAY_DIRECTORY; opt-in không cho ghi đè thư mục có sẵn.

**Backup:** `backups/20261101_232836_268483_remove_nk061_session_logging/`,
archive đọc được, SHA-256 nguồn/archive kiểm thành công và manifest có đủ.
Nguồn/assets/config/test/tài liệu gồm thay đổi chưa commit; không sao lưu
runtime log bị xóa, credentials/build/install/cache. Không đụng backup cũ.

**Tài liệu:** README root, README_SOCIAL_DYNAMIC, CHAN_DOAN_PHIEN_CHAY,
PHAT_LAI_MO_PHONG và bàn giao đầu nhật ký cập nhật cách chạy mới. Lịch sử
NK-061–063 giữ nguyên như đã diễn ra. Minh chứng đã trích trong docs/evidence
được giữ; báo cáo tiến độ không thêm mục vì không đổi thuật toán/hành vi né.

**Kiểm chứng:** `bash -n` hai launcher qua. Chạy logic launcher với executable
ROS launch thay bằng stub: không tạo sessions/không truyền biến ghi pose ở
chế độ thường, launch args được giữ; opt-in tạo scene đúng leader và từ chối
thư mục có sẵn.5 test replay Python qua. Không khởi động/dừng mô phỏng trong
lượt này; không tuyên bố tăng RTF hoặc sửa va chạm. Không commit/push.

### NK-065 — 01/11/2026 — Xác nhận contact từ physics trong bản ghi

**Yêu cầu:** người dùng làm rõ viền đỏ phải xác nhận tiếp xúc vật lý,
không chỉ ước lượng hai hình chồng lên nhau.

**Backup:** `backups/20261101_233137_788739_physical_contacts_replay/` trước
sửa; archive đọc được, SHA-256 so nguồn kiểm qua và có manifest. Gồm
nguồn/assets/config/test/tài liệu, loại log/private/build/install/cache.

**Thay đổi:** `social_navigation_sim/src/replay_recorder.cpp` tạo yêu cầu
ContactSensorData trên collision sẵn có của cả3 xe trong PreUpdate khi
bật ghi replay. Physics của Gazebo điền contact; PostUpdate đọc từng bước,
gom cặp vào frame20Hz, lưu tên model/collision, thời điểm đầu/cuối, điểm
contact đầu tiên, số bước và max_depth nếu có. Thiếu depth giữ null,
không gán0. Không thay collision geometry, phản ứng vật lý hoặc điều khiển.
`scripts/replay_viewer.html` viền đỏ cho contact physics, cam cho geometry;
hiển thị cặp/thời điểm/độ xuyên nếu có, bản ghi cũ báo thiếu dữ liệu.
Contact nền vẫn lưu nhưng ẩn cảnh báo. Hướng dẫn và bàn giao/báo cáo cập nhật.

**Kiểm chứng:** build plugin qua;5 test replay qua. Fixture Gazebo headless
riêng2500 bước có50 frame/78 khoảng cặp contact: robot3 rơi xuống khối
person_contact và robot1 chạm nền; robot2 giữ cách mặt khối10mm không có
contact, frame đầu chưa chạm không báo. Có điểm tiếp xúc, engine không có
depth nên giữ null. Bốn module core navigation byte-match backup. Firefox
kiểm thông báo cặp physics, không ghi nhận contact, depth thiếu và dữ liệu
cũ; screenshot lưu trong thư mục minh chứng. Lượt browser đầu fixture
thiếu z envelope nên render thất bại; bổ sung metadata fixture. Script kiểm
trình duyệt cũng chuyển từ gán biến index trong sandbox sang thao tác slider
thật; lần cuối toàn bộ assertion qua.
[Minh chứng](docs/evidence/2026-11-01/physical_contacts/),
[physics](docs/evidence/2026-11-01/physical_contacts/validation.json),
[trình duyệt](docs/evidence/2026-11-01/physical_contacts/browser_validation.json).

**Giới hạn:** chỉ thử primitive physics riêng, chưa thử lại3 URDF/MPC và
người đi. Người dùng proxy collision nên xác nhận là va vào proxy, không
mesh hoạt ảnh. Actor thiếu collision/mask hoặc engine bỏ sót thì không có
contact để đọc; không tự suy ra “không va chạm”. Cặp trong frame là sự kiện
trong khoảng gom, không nhất thiết còn tiếp xúc ở pose cuối. Chưa đo
RTF/overhead. Giữ NK-064 không ghi dữ liệu tự động; không mở main, không
sửa né hoặc push. Báo cáo thêm cải tiến xác nhận tiếp xúc, không kết luận
leader tránh được người.

### NK-066 — 01/11/2026 — Đọc bản ghi mới nhất, xác nhận hai ca va chạm

**Yêu cầu:** đọc bản ghi mới nhất. Chọn thư mục `recordings/thu_ne_01`
mới nhất có world_frames.jsonl;1619 frame đầy đủ, epoch0,0.001–80.901s sim.

**Backup trước lưu minh chứng/tài liệu:**
`backups/20261101_234926_315176_audit_latest_replay_contacts/`, archive đọc
được, SHA-256 so nguồn/archive và manifest qua; nguồn/assets/config/test/
tài liệu, loại private/build/install/log/cache và recordings runtime.

**Phát hiện:** contact engine robot3↔tv_viewer_a_walking t29.701–32.268s;
robot2↔patrol_person t79.626–80.901s, contact còn ở cuối bản ghi. Không có
contact ngoài nền robot1.905/457 bản ghi cặp collision không phải905/457
lần đâm: gồm nhiều collision base/cột/bánh/roller và nhiều frame liên tiếp.
Phân tích gom khoảng theo cặp model/epoch với gap≤.1s.

Leader gần(1.65,−1.89) đứng trước khi người x1.6 tiến+Y≈.35m/s, chỉ dịch
net≈2.08cm trong28–33s. Follower2 gần(1.404,−2.018), người tiến−Y≈.4m/s,
xe chỉ dịch net≈.225cm trong78–80.901s. Khoảng cách root tối thiểu lần
lượt≈.0403m tại31.001s và≈.1992m tại80.551s; không phải surface clearance.
Hai ca đều cho thấy chưa né được, không khẳng định né sai hướng theo lệnh.
Trước chạm người ở phía trái thân xe theo pose heading; không gán phải/trái
của màn hình Gazebo cho hệ thân xe.

**Minh chứng/kiểm tra:** chạy script offline `analyze.py`, lưu analysis.json,
scene và các frame contact/lân cận, SHA256 input và ảnh trajectories.png
trong `docs/evidence/2026-11-01/latest_replay_audit/`; đã xem lại hình.
Không chạy navigation test/build hoặc mô phỏng mới vì chỉ đọc bản ghi.
Không sửa thuật toán, không push. Báo cáo bổ sung bằng chứng runtime cho
công cụ NK-065 và lỗi baseline còn tồn tại.

**Giới hạn:** không có goal/cmd_vel/raw scan/camera/status trong replay;
không xác định được sensor trễ hay controller hold. Dịch chuyển có thể gồm
phản ứng physics, không phải lệnh né. Không đo RTF. Chưa biết kết cục ca
robot2 sau80.901s. Thiếu contact robot1 chỉ đúng đoạn ghi, không chứng minh
an toàn mọi tình huống. Metadata scene còn chuỗi mô tả cũ “no contact events”
từ NK-063; audit đọc trường contacts thực của từng frame NK-065, chưa sửa
metadata/giao diện trong tác vụ chỉ đọc này.

### NK-067 — 02/11/2026 — Chẩn đoán cửa sổ dừng xe theo yêu cầu

**Yêu cầu:** triển khai cách đối chiếu cảm biến→quyết định→lệnh→pose để tìm
nguyên nhân xe đứng yên. Giữ quyết định NK-064 không lưu dữ liệu mỗi lần
chạy thường. Đây là thêm công cụ chẩn đoán, chưa sửa lỗi né NK-066.

**Backup trước thay đổi đầu tiên:**
`backups/20261102_000006_014767_opt_in_stop_diagnostics/`. Archive đọc được,
SHA-256 nguồn/archive xác minh thành công, có manifest; gồm nguồn/assets/
config/test/tài liệu và thay đổi chưa commit, loại private/build/install/
log/cache/recordings runtime. Không đụng backup cũ.

**Triển khai:** --diagnose-stop DIR bật biến môi trường riêng và ghi pose/
contact cùng cửa sổ nội bộ controller/coordinator. Mặc định unset cả hai
biến, không tạo writer; --record-replay không tự bật chẩn đoán. Từ chối
thư mục đã có. Không thêm observer/ROS topic subscription hoặc ảnh/raw
scan. diagnostics_config.json giữ đường dẫn/hash module thực tế đã source.

Writer ghi bộ nhớ vòng3s wall, mở khi zero command/empty reference/pose
đội gần đứng yên kéo dài≥.5s wall, giữ trong suốt hold và5s wall sau phục
hồi,≤10Hz wall. Lấy fresh team pose không đổi≥.5s sim để phát hiện command
khác0 nhưng xe có vẻ không chạy. Coordinator giữ ngữ cảnh khi có xe dừng,
kể cả reference còn hợp lệ. Bounded queue256 và20MiB mỗi stream; lỗi/drop
có trạng thái riêng, không thay quyết định chuyển động.

Instrument publish_stop với reason; ghi camera candidate/scan callback
stamp/receipt/acceptance, ray min theo sector và lọc map/peer/range,16 điểm
giữ gần nhất, tracks tốc độ/radius/TTC, freshness, peer predictions, A*
side/goal/cache-age, counters ràng buộc map/LiDAR/moving/peer ở A*/escape/
MPC và thời gian tick. Giữ nguyên thứ tự/ngưỡng kiểm và cost/chọn command.
Analyzer ghép contact với sample cùng epoch/time; thiếu sample phải báo
thiếu. Sửa chuỗi metadata replay cũ nói không có contact thành mô tả đúng
schema NK-065, không sửa frame lịch sử.

**File:** planner `stop_diagnostics.py`, `dstar_mpc_controller.py` và
`test_stop_diagnostics.py`; scripts `run_dynamic.sh`, `replay_data.py`,
`analyze_stop_diagnostics.py` và test analyzer; hướng dẫn CHAN_DOAN_DUNG_XE,
PHAT_LAI_MO_PHONG/CHAN_DOAN_PHIEN_CHAY, README và hai README bắt buộc.

**Kiểm chứng:** build planner qua;180 test full regression qua,2 warning
SciPy,3 lint file không chạy. Các test mới kiểm default không writer,
pre/post window kéo dài khi hold, snapshot không alias dữ liệu, reset
sim/epoch, IO failure, lệnh khác0 nhưng pose đội đứng, metadata sensor cũ,
map reject trong A*/escape, analyzer không suy dữ liệu thiếu. Tracking
cả3 xe và escape có command/rollout giống khi tắt/bật capture chẩn đoán.
ROS domain211 smoke với constructor/timer thật: mặc định tắt, opt-in ghi
controller+coordinator và reason thiếu state/reference; không Gazebo hoặc
sensor thật. Wrapper chỉ thay executable launch bằng stub kiểm bật/tắt,
truyền args, từ chối thư mục cũ và thiếu tham số. Không chạy main hay tự
đặt goal. [Minh chứng](docs/evidence/2026-11-02/stop_diagnostics/).

**Giới hạn:** chưa có full Gazebo/3 xe/perception với mode mới; không biết
nguyên nhân cụ thể của thu_ne_01 vì dữ liệu cũ không thể bổ sung ngược.
Không tuyên bố né tốt hơn hoặc tăng RTF. Camera candidate/output stamp
không phải ảnh pixel hoặc latency inference độc lập; callback receipt
không phải thời điểm DDS nhận packet. First-reject counters không phải
số đường độc lập/number of impacts; cache A* có thể không chạy mỗi tick.
Thời gian wall gồm overhead chẩn đoán, chưa benchmark. Pose đội đứng
cần xác minh bằng replay ground truth. Chưa commit/push.

### NK-068 — 02/11/2026 — Đánh dấu điểm goal trong RViz và phát lại

**Yêu cầu:** thêm điểm đánh dấu khi người dùng chọn goal.

**Backup:** lần gọi bắt buộc ban đầu tạo archive
`backups/20261102_002443_772396_mark_selected_goals_in_replay/` nhưng kiểm
nguồn thất bại vì file stop_coordinator.jsonl của phiên đang chạy đổi.
Chưa sửa nguồn tại thời điểm đó. Nạp create_backup trong bộ nhớ và thêm
recordings vào EXCLUDED, tạo snapshot nguồn
`backups/20261102_002544_359477_mark_selected_goals_in_replay_source_only/`;
archive đọc được, SHA-256 so nguồn/manifest qua, verify lại645 file qua.
Không xóa archive hỏng hoặc dữ liệu phiên. Sau backup thành công, sửa
scripts/create_backup.py loại recordings vĩnh viễn, test snapshot kiểm
runtime không lọt manifest. Các backup cũ giữ nguyên.

**Thay đổi:** module planner goal_history.py ghi sự kiện goal khi có cờ
replay, gồm sim time/epoch/sequence/xy; set_goal vẫn giữ nguyên điều kiện
và tọa độ. Coordinator bổ sung Marker tím và nhãn GOAL. scripts/view_replay.py
cấp feed /goals, export nhúng sự kiện; replay_viewer.html vẽ marker/tọa độ/
thời điểm chọn, tua không lộ goal tương lai, đổi goal và phân tách epoch;
input offline hỗ trợ goals.jsonl, PNG giữ marker. Bản ghi cũ thiếu goal
không suy dữ liệu. Cập nhật hướng dẫn và hai README bắt buộc.

**Kiểm chứng:**9 test Python mục tiêu, clock reset, không ghi mặc định,
export/partial line và backup exclusion qua. Lần gọi test đầu nhầm tên
file test_backup_workflow.py không tồn tại nên không chạy test; đã sửa
lệnh và chạy9 ca thực tế qua. ROS callback coordinator domain212 xác nhận
set_goal ghi xy(2,1), marker có tọa độ đó, navigation goal giữ nguyên.
Không spin hoặc gửi lệnh/goal cho phiên người dùng. Firefox fixture với
hai goal test tổng hợp xác nhận chọn theo timestamp, thay goal, khác epoch
không hiện, tua trước chọn không hiện và screenshot; HTTP /goals trả hai
event qua. Build planner qua. Không chạy full regression, không mở Gazebo.
[Minh chứng](docs/evidence/2026-11-02/goal_markers/).

**Giới hạn/trạng thái:** giữ phiên launch115277 của người dùng đang chạy;
không stop/restart. Process cũ chưa nạp mã mới, cần lượt mới để ghi goal.
Marker báo mục tiêu đã chọn, không bảo đảm route feasible/goal reached.
Chưa thử goal mới trong full simulation, không sửa né, không benchmark
RTF hoặc push. Báo cáo chỉ thêm khả năng quan sát mục tiêu, không đưa sửa
backup thành cải tiến thuật toán.

### NK-069 — 02/11/2026 — Audit chẩn đoán mới nhất, khoanh nhánh gây đứng

**Yêu cầu:** kiểm tra bản ghi mới nhất, xác định vấn đề ở đâu.

**Dữ liệu:** recordings/chan_doan_01 có diagnostics_config,4 stream dừng,
pose/contact.1800 frame,0.001–89.951s sim; thiếu goals.jsonl vì phiên dùng
code NK-067 trước dấu goal. Goal có trong coordinator≈(1.0351,−2.0358).
Config hash controller/stop_diagnostics khớp nguồn trong backup trước
NK-068, đã xác minh không gán ngược phiên cho code mới.

**Kết quả trực tiếp:** patrol va robot2 78.918–83.774s, patrol va leader
83.269–85.393s; người xem TV trở về va robot2 86.305–88.834s. Leader t83.3
có2 risk từ LiDAR nhưng dừng do state wall2.081s>2s; scan sim.1s còn mới
nhưng wall1.978s gần giới hạn. T83.0 scan wall4.074s/state wall2.101s cũng
chặn escape. Camera candidate0 không chứng minh camera là nguyên nhân;
coordinator observation_active=false quanh các contact.

Robot2 t78.9 có64 lần first-reject escape.moving, không có A* plan.
Track buffer gap ở start≈−.18333m trong khi rule đòi≥.03m. Sử dụng đúng
MovingObstacle.clearance, probe16 hướng đều fail; do swept min gồm start,
bất kỳ đoạn xuất phát từ pose này đều fail cùng buffer rule. Không đồng
nhất đó là penetration vật lý hoặc chứng minh không có đường thực tế.

T75.3 escape robot2 mất≈3627.9ms wall; command phát với state wall≈4.201s,
đổi sang0 sau≈.12506s wall bởi invalid_or_empty_reference rồi watchdog.
Source dùng guard_wall lấy từ trước tìm kiếm; tick dài có thể làm guard
quá hạn khi vừa xuất lệnh. Coordinator moving safety liên tục rút reference
về0, còn controller ngoài guard yêu cầu reference mới, gây chuỗi stop.
Không đề xuất bỏ ràng buộc an toàn; cần phối hợp trạng thái và kiểm dữ
liệu ở thời điểm phát command. Thời gian đo gồm scheduling/diagnostics,
không quy toàn bộ CPU cho A*/camera hoặc tuyên bố RTF tăng/giảm so baseline.

**Giới hạn bộ ghi:**3 file robot≈20MiB, last_t robot1/2/3=83.101/82.639/
83.533, phù hợp trần cấu hình20MiB; replay vẫn tới89.951s. Không có ngữ
cảnh controller đủ cho contact86.305; không gọi đó là node crash. Queue
samples đã lưu có dropped_records0 không phủ nhận file-cap hoặc dữ liệu
ngoài cửa sổ bị thiếu. Đếm message reason không phải tỷ lệ thành công né.

**Backup/minh chứng:** trước ghi tài liệu/evidence chạy
`backups/20261102_003151_391359_audit_stop_diagnostics_root_causes/`, archive
đọc được/SHA-256 nguồn và manifest qua, loại runtime/private/generated.
Chạy script offline analyze.py, source hash verify và probe số học, lưu
analysis.json, config, selected_diagnostics và contact_frames tại
[thư mục audit](docs/evidence/2026-11-02/stop_diagnostics_audit/).
Không build/test navigation hoặc mở/dừng simulation vì đây là audit dữ
liệu. Khi kiểm không còn launch. Không sửa thuật toán hoặc push. Báo cáo
bổ sung bằng chứng hạn chế runtime; các hướng sửa nêu ở bàn giao mới chỉ
là đề xuất, cần yêu cầu tiếp theo để triển khai.

### NK-070 — 02/11/2026 — Làm rõ nguồn phát hiện vật động và ưu tiên LiDAR

Người dùng yêu cầu ưu tiên né ổn cả3 xe trước, hiện không quan tâm kết quả
camera, nêu tầm LiDAR2m và hỏi nguồn dữ liệu nhận diện người di chuyển.
Đọc lại lidar.urdf.xacro, leader_obstacle_scan.py và subscriptions/callback/
scan_world_points/control_tick của dstar_mpc_controller.py: sensor10m,
360°/5Hz; track scan lọc3.5m, static rollout gần2.5m. Không gọi đó là cấu
hình2m. Mỗi controller nhận3 LiDAR và camera leader; moving list nhập chung
hai nguồn. LiDAR cluster/track là vật động, không nhãn người chắc chắn.
Tại các snapshot NK-069 risk đến từ LiDAR, camera candidate0, nên camera
thiếu nhận diện không phải điều kiện khiến không có track để né.

Đã ghi ưu tiên bàn giao; chưa sửa code/tầm quét/camera hoặc chạy thử mới.
Không cam kết né ổn chỉ từ thay nguồn. Báo cáo kỹ thuật giữ nguyên.
Backup trước tài liệu: `backups/20261102_004008_185380_record_lidar_first_avoidance_priority/`,
archive đọc được/SHA-256 nguồn/manifest qua, loại runtime/private/generated.
Không start/stop mô phỏng hoặc push.

### NK-071 — 02/11/2026 — LiDAR2m và né vật động độc lập camera cho cả3 xe

**Yêu cầu:** áp dụng bán kính quét2m, chỉ quan tâm vật động, ưu tiên cả3 xe
né hợp lý trước kết quả camera. Lượt “tiếp đi” tiếp tục cùng tác vụ.

**Trước/sau và nguồn:**

- Sensor10m/5Hz đổi2m/10Hz/240tia trong `lidar.urdf.xacro` và projector.
  Dynamic launch/wrapper mặc định camera/perception/social/observation OFF;
  `avoidance_use_camera=False` không subscribe pose camera. Ba controller
  nhận own/peer scans, không dùng actor ground truth cho navigation.
- `scan_pose_history.py` mới nội suy pose tại timestamp scan, giữ4 packet
  chờ pose và throttle capture-time; tránh biến chuyển động robot/receipt
  trễ thành vận tốc giả. `moving_obstacles.py` gom spatial components, fit
  tâm cung, deduplicate local/remote, giữ vận tốc cuối≤.4s khi gián đoạn.
- Recovery cho phép giảm nguy cơ từ buffer đã overlap, giữ kiểm map/raw
  LiDAR/moving/peer; không coi overlap buffer là penetration vật lý. A*
  connector + space-time search có budget; escape chỉ phát rollout đầy đủ,
  kiểm freshness lại trước lệnh. Normal MPC thử checked rollout trước beam.
  Freshness wall thích nghi2–12s theo clock tiến, capture sim≤.3s; clock
  frozen/sensor cũ vẫn dừng. Guard timestamp lấy tại publish thực tế.
- Coordinator giữ route/goal và reference giữ tại pose đo trong moving
  safety, rồi replan; không dùng reference rỗng làm mất lệnh né. Watchdog
  vẫn kiểm dữ liệu. Không sửa người thành nhường/đứng chờ xe.
- Trial08 phát hiện lỗi mới trong scoring: biến speed vật ghi đè speed
  candidate robot. Đã sửa biến riêng và thêm hồi quy command/prediction
  segment≤.28m/s trước trial09. Không che kết quả lỗi ở trial08.
- Trial09 hai follower không contact ngoài nền90s nhưng leader contact
  patrol83.901–86.051s. Soi pose/command cho thấy leader quay về goal khi
  patrol tạm dừng/rẽ. Đã checkpoint trước sửa và thêm nearby-approach,
  hold1.25s sau risk cuối, clear khi reset clock; không đổi goal.
- Thêm `test_lidar_2m_avoidance.py`, `test_scan_pose_history.py`; sửa fixture
  legacy để có capture/fresh reference thực tế. Các nguồn liên quan khác:
  `local_escape.py`, `dstar_mpc_controller.py`, launch common/dstar/three_robot
  (thêm server-only tùy chọn), wrapper/runbook và hướng dẫn replay/diagnostic.

**Kiểm chứng đã chạy:** build hai package qua; ROS constructors cả3 xác
nhận range2m, không subscription camera, đủ3 scan sources; resolved URDF
xác nhận2m/10Hz/240ray. Ca kinematic raw-ray mỗi xe ở.15/.35/.8m/s, đội3xe,
đổi hướng+dừng ngắn, buffer recovery, bounded search, data expiry sau tính,
clock chậm/frozen, capture-pose và speed cap qua. Hồi quy đầy đủ và Gazebo
cuối xem kết quả chốt ngay bên dưới; không suy ca số học thành xác nhận
tránh va chạm trong Gazebo.

**Các lượt Gazebo và lỗi giữ lại:** test riêng goal(1.03514576,−2.03577352),
không publish vào domain người dùng. Lượt01 GUI pilot;02 trước fusion có
TV↔robot1;03 lỗi startup services không đủ scans;04 trước capture alignment
TV↔robot2;05 trước queued retry có contact robot2/3;06 trước spatial/persistence
còn contact;07 startup lỗi, không là ca né thành công;08 speed-shadow còn
lỗi, TV không contact nhưng patrol contact;09 như trên. Lượt08–10 dùng
server-only/rvizfalse/DDS async/localhost0; không so RTF với các lượt điều
kiện khác. Harness chờ input rồi mới gửi goal, giới hạn90sim/240wall,
dừng process thuộc test. Pilot01 còn orphan Gazebo đã kiểm domain/partition
rồi dừng riêng; không dùng pkill chung hoặc dừng phiên người dùng.

**Backup bắt buộc:** nguồn/assets/config/test/tài liệu gồm thay đổi chưa
commit; loại credentials/private/build/install/log/recordings. Archive đọc
được, SHA-256 nguồn lúc tạo và manifest qua. Các checkpoint và hash xác
minh lại trong [backups.json](docs/evidence/2026-11-02/lidar_2m_avoidance/backups.json):

- `backups/20261102_004332_583001_lidar_2m_dynamic_avoidance_all_robots/` (đầu tác vụ).
- `backups/20261102_010219_745310_before_checked_tracking_rollout_lidar_2m/`.
- `backups/20261102_011027_106836_before_lidar_track_deduplication/`.
- `backups/20261102_012150_729470_before_scan_capture_pose_alignment/`.
- `backups/20261102_013237_472143_before_buffered_scan_pose_retry/`.
- `backups/20261102_013735_098651_before_spatial_cluster_motion_persistence/`.
- `backups/20261102_081417_792428_before_escape_speed_shadow_fix/`.
- `backups/20261102_082817_438821_trial09_followers_no_contacts_before_turn_guard/`
  giữ riêng trạng thái hai follower qua90s trước sửa góc rẽ leader.

**Kết quả chốt lượt10:**217 test qua,2 warning SciPy,3 lint file không
chạy; build2package qua. Gazebo0.001–90.101s sim, domain54/partition10,
scan cả3 đúng2m/240tia, camera tắt, không ghi nhận contact ngoài nền.
Quãng đường root XY lấy mẫu robot1/2/3≈10.82/10.35/8.20m, có chuyển động
né; đây không là độ dài tối ưu hoặc toàn bộ chuyển động odom. Leader
ở(1.04,−2.04) gần goal lúc74s, sau đó né sang−X rồi−Y khi patrol rẽ−X;
cuối90s leader(−.422,−2.922), cách goal≈1.71m; follower đang pause-hold.
Vì vậy chỉ xác nhận không contact trong lượt này, chưa xác nhận khôi phục
đội hình/đến lại goal sau né cuối, hoặc toàn chu kỳ người quay về. Không
coi guard là giải pháp đã tối ưu trong mọi trường hợp. Không còn Gazebo/
launch thuộc test sau cleanup. Năm module runtime hash khớp nguồn chốt.
[Summary10 lượt](docs/evidence/2026-11-02/lidar_2m_avoidance/validation_summary.json),
[quỹ đạo](docs/evidence/2026-11-02/lidar_2m_avoidance/final_trajectories.png),
[checkpoint góc rẽ](docs/evidence/2026-11-02/lidar_2m_avoidance/turn_checkpoints.json),
[raw frame nén](docs/evidence/2026-11-02/lidar_2m_avoidance/final_replay/world_frames.jsonl.gz).

**Bàn giao:** [runbook](docs/LIDAR_2M_AVOIDANCE.md),
[minh chứng](docs/evidence/2026-11-02/lidar_2m_avoidance/). Chạy thường không
writer, --diagnose-stop hoặc --record-replay mới ghi thủ công. Không bật
lại NK-061 sessions. Không commit/push. Báo cáo cập nhật đúng phạm vi
kiểm chứng; chưa có benchmark lặp/đảm bảo cho mọi mật độ, tốc độ hoặc che
khuất; fallback buffer không phải chứng minh an toàn từ trạng thái quá sát.

### NK-072 — 02/11/2026 — Audit điểm né và contact trong bản ghi lidar_2m_01

**Yêu cầu:** người dùng thấy cả3 xe né nhưng chọn điểm chưa tốt, vẫn va
chạm; kiểm bản ghi mới trước khi quyết định sửa. Không tự chạy/dừng phiên.

**Kết quả:**4943 frame0.001–247.101s sim, goal chọn8.69s≈(1.035534,−1.979021).
Năm module hash khớp NK-071; camera tránh=false, scan mẫu max2m. Physics
có8 cặp/9 đợt contact ngoài nền, cả3 xe đều liên quan; gồm robot1↔leader.
Danh sách đầy đủ, first_t/last_t/điểm tiếp xúc và hash snapshot trong
[analysis.json](docs/evidence/2026-11-02/lidar_2m_01_audit/analysis.json).
Đợt cuối leader↔TV chưa kết thúc tại247.101s. Cả3 có lệnh né nhưng không
coi số lệnh là số lần thành công. Đính chính phạm vi NK-071: không contact
ở một lượt90s không dự đoán kết quả lượt mới dài247s/goal khác nhẹ; giữ
nguyên lịch sử và kết quả test cũ, không dựng benchmark RTF.

**Nguyên nhân có bằng chứng:** robot2 local track t30 đo ngược chiều người
trong khi peer đo đúng; local-priority suppress gần.45m không kiểm velocity.
Sau pause và moving-reject, né+X quá muộn. Leader đổi hướng né, t83 lùi dọc
corridor−X của patrol thay vì sớm đủ khoảng ngang; vận tốc estimate phản
ứng chậm ở góc rẽ. A* chỉ thử6 điểm thân xe/first-feasible connector, MPC
không cam kết tới proposal và đổi plan sau.4s. Robot1 command0 bảy mẫu
147–147.6 nhưng thực đi.270m; stationary prediction trong publish_stop
không phản ánh xe còn chuyển động, sau đó chạm leader147.650. Chưa chứng
minh root cause trôi do physics/actuator/lệnh khác; thiếu wheel/effort.

**Thay đổi:** chỉ thêm script audit/readme/JSON/raw windows nén/ảnh quỹ đạo
trong `docs/evidence/2026-11-02/lidar_2m_01_audit/` và hai README bàn giao/
báo cáo. Không sửa navigation, sensor, launch hoặc goal người dùng.
**Kiểm tra thực chạy:** script phân tích complete prefix qua; kiểm5 source
hash đều khớp; đọc code fusion/A*/MPC/stop, đối chiếu actual root pose với
command và xem ảnh4panel. Không chạy test hồi quy/controller mới hoặc
Gazebo mới vì không sửa hành vi. Không có full raw rays để rerun perception.

**Hướng đề xuất:** fusion theo chất lượng/bất đồng vận tốc trước; điểm né
ra khỏi corridor và kiểm arrival/turn uncertainty, giữ phía né nếu an toàn;
peer/stop dựa vận tốc robot đo và khoảng phanh. Cần tái hiện các mốc contact
rồi kiểm nhiều chu kỳ; chưa triển khai các đề xuất trong audit này.

**Backup:** `backups/20261102_095303_803811_audit_lidar_2m_01_escape_contacts/`,
nguồn/assets/config/test/tài liệu, loại private/generated/runtime; archive
đọc được và SHA-256 nguồn lúc tạo/manifest qua; verify lại721 file qua.
Giữ backup và bản ghi cũ, không commit/push. Báo cáo bổ sung bằng chứng
runtime hạn chế NK-071, không tạo phiên bản thuật toán mới.

### NK-073 — 02/11/2026 — Sửa fusion vận tốc, lựa lối né và dự báo xe đang phanh

**Yêu cầu:** sửa các lỗi có bằng chứng ở NK-072; giữ LiDAR2m, ưu tiên cả3
xe né vật động, giữ goal gốc và backup trước cải tiến. Không push GitHub.

**Thay đổi:**

- `moving_obstacles.py`: khi controller truyền source IDs, mỗi observer
  chỉ1 vote/nhóm gần.45m, tuổi≤.35s. Hai nguồn velocity cách≤.20m/s có thể
  sửa local bất đồng>.20m/s; giữ local geometry, thêm.04m uncertainty khi
  sửa. Không lấy hai track trùng của một xe thành hai nguồn độc lập.
  API cũ thiếu source IDs giữ cách chọn cũ cho caller legacy. Không phân
  loại người hoặc dùng authored human pose để điều hướng.
- `local_escape.py`/`dstar_mpc_controller.py`: hướng vật chính chọn theo
  TTC và speed để giảm noise chậm TTC0; điểm bên theo pháp tuyến flow.
  Chấm các connector đã kiểm thay lấy first-feasible. Thêm preference
  giữ heading1.25s, bỏ khi quá hạn/flow đổi>60° so lần chọn trước; candidate
  khác vẫn được phép khi hợp lệ hơn. Không khóa cứng goal nguy hiểm.
- Lượt thử đầu còn contact follower khi tới patrol. Phát hiện rollout
  chỉ cruise có thể đi qua nơi trú rồi chạm vật tĩnh, từ đó loại lối né.
  Đã thêm proposal giảm tốc/dừng tại goal, giữ cả cruise đã kiểm để bảo
  toàn ca sparse/close-peer cũ. Thử chỉ-stop làm4 test cũ fail; giữ failure
  logs và sửa lại cả2 mode, không hạ threshold/assert để che hồi quy.
- MPC ghi `selected_escape_goal`/`selected_escape_stops`/heading bên cạnh
  A* proposal. Chỉ đọc như quyết định mới tại checked_escape_command;
  khi reason khác có thể còn giá trị từ lệnh né trước. Không nhầm proposal
  với target thực; mode cruise không có một target dừng được cam kết.
- `scan_pose_history.py`: đo robot world velocity bằng pose capture-time
  cửa sổ.15–.35s, reject dữ liệu cũ/nhảy>1.5m/s; cache theo state_time.
  `robot_motion.py` mới: reserve coast.3s rồi giảm tốc.4m/s². Stop vẫn gửi
  Twist0 nhưng prediction theo velocity đo; peer kiểm cả advertised path
  và envelope đo trong A*/escape/normal MPC. Diagnostic thêm measured
  robot velocities; wrapper hash thêm module mới, không ghi tự động.
- Đây là bù dự báo, không chứng minh đã sửa nguồn vật lý làm robot trôi.
  Chưa calibrate coast/deceleration hoặc biết wheel/effort; không đổi
  physics/actor/đích người dùng để né ca khó.

**Kiểm chứng số học/build:** build2package qua;234 test qua,2 warning SciPy,
3 ament lint file không chạy. Thêm17 test trong
`social_navigation_planner/test/test_motion_consensus_and_braking.py`:
replay checkpoint robot2 t30 sửa dấu velocity, duplicate source không
đủ vote, vote cũ không sửa local, ranking connector/flow normals, vận tốc
pose/expiry/jump, stop còn chuyển động, peer stationary-advertisement có
coast, khoảng phanh hữu hạn, refuge gần static object dùng dữ liệu lỗi
lượt thử đầu, map-supported centre không tạo motion track nhưng raw rays
vẫn được giữ làm vật cản, phản ứng recent-turn/pause reserve hết hạn,
warm direction được kiểm trước trong budget và bỏ nếu map mới chặn.
Toàn bộ ca escape/formation/paper legacy chạy lại trong hồi
quy; ca số học không thay kiểm chứng Gazebo.

**Thử Gazebo trung gian:** domain55/partition nk073_validation_01, goal
(1.03553379,−1.97902071) gửi sau8.69s như mốc chọn của bản ghi người dùng,
server-only/cameraoff/manual diagnostic. Qua TV nhưng follower còn contact
patrol. Dừng test riêng khi đã đủ bằng chứng, trước sửa stop-at-goal;
không coi là thành công. SIGINT gây rcl_shutdown already called khiến
finally harness cũ chưa cleanup hết; đã dừng đúng các PID mang cả domain55
và partition riêng, kiểm PID birth trước signal. Sửa harness để shutdown
lặp không bỏ qua cleanup. Không pkill chung/dừng phiên người dùng. Giữ
`recordings/nk073_validation_01` và minh chứng nguồn/log lỗi.

**Bổ sung sau lượt02:** prototype refuge đã giúp leader qua patrol nhưng
robot2 còn contact84.484–86.002s; dừng riêng test tại130.101s để sửa tiếp,
không coi là đạt. Diagnostics cho thấy fit centre gần(.52,−.96) có noise
velocity≈.1–.15m/s dù physical-map clearance chỉ≈.02m; bed-return centre
(.25,−3.35) clearance≈.15m cũng bị dự báo như moving. Map-support gate
<.18m được thêm riêng cho motion observation, giữ toàn bộ raw local rays
và static-map constraints. Không loại vật khỏi collision checks. Đây là
heuristic dựa map, còn giới hạn vật thật đi rất sát map/che khuất.

**Bổ sung sau lượt03:** map gate còn contact leader↔TV31.713–33.102,
và leader↔TV-console35.707 trong đoạn kiểm lúc đầu; giữ toàn bộ kết quả
cuối của pha03 trong summary. Checkpoint t29 có track TV velocity0 trong
lúc xe bị một track khác kéo heading về gần đó. Đã thêm cập nhật velocity
recent-turn và pause reserve hữu hạn như bàn giao đầu file. Không coi
radius reserve là body size. Giữ prototype03 và backup riêng trước sửa.

**Bổ sung sau lượt04:** vẫn contact patrol↔robot1 từ85.546s trong
phần đọc lúc kiểm; mốc chốt toàn record ở summary. Log t83 budget exhausted,
t84.5 mọi rollout bị loại; lệnh dừng xen kẽ làm xe không tăng tốc thoát.
Đã thêm warm direction theo heading chốt trước, kiểm mới ngay đầu budget.
Không dùng cached command hoặc giảm margin. Pha04 dừng riêng khoảng158.3s
để checkpoint/sửa; không coi là ca thành công.

**Bổ sung sau lượt05 và hồi quy refuge:** vẫn có contact và simulation
slowdown, log source/pose giữ ở summary. Probe55s wall chỉ thu pose
107.099–107.299s sim, không đủ mẫu động command/wheel/pose; không kết luận
root cause actuator/physics. Phát hiện target stopping đặt lại theo pose
mỗi tick, khó tới điểm rồi chờ. Đã giữ refuge world, có wait cho flow
đi qua; mỗi tick vẫn kiểm mới, không sửa global goal/reference. Siết
recovery floor khoảng cách tâm (cap estimated object radius.30m), không
cho risk-reducing so với holding đồng nghĩa được đi vào body tùy ý.

Bản latch/refuge + hard parking làm hồi quy ca follower chật cũ; không
hạ assert>.47m. Nguyên nhân thuật toán còn ép mọi cruise phải dừng an toàn
ở cuối3s, dù cần đi tiếp ra chỗ thoáng rồi né ngang. Đã tách stop (bắt buộc
terminal holding-safe) và cruise (toàn horizon checked, penalty2 nếu chưa
có nơi dừng, không latch endpoint chưa terminal-safe).17 test mới và full
234 test qua,2 warning SciPy. Ca helper không chứng minh physical radius
mọi loại vật; chưa chứng minh chữa nguồn robot trôi sau command0.

**Backup:**

- `backups/20261102_100114_990952_improve_motion_fusion_escape_and_braking_nk072/`:
  trước cải tiến, verify archive/manifest/SHA-256 nguồn lúc tạo và verify
  lại727 file qua; source/assets/config/test/docs, loại private/generated/
  recordings. Giữ cả trạng thái chưa commit.
- `backups/20261102_101135_425789_nk073_before_stop_at_escape_goal_fix/`:
  checkpoint sau fusion/braking/commit, trước đổi rollout giảm tốc tại
  điểm né; archive đọc được/manifest/SHA-256 nguồn lúc tạo qua.
- `backups/20261102_102207_761045_nk073_before_map_supported_motion_filter/`:
  trước map-supported filter, giữ nguồn và kết quả pha02; archive đọc
  được/manifest/SHA-256 nguồn lúc tạo qua; verify lại737 file qua.
- `backups/20261102_103108_248760_nk073_before_pause_motion_uncertainty/`:
  trước reserve pause/recent-turn, archive/manifest/SHA-256 nguồn lúc tạo
  và verify lại748 file qua. Checkpoint trước stop-at-goal verify733 file.
- `backups/20261102_104011_237946_nk073_before_warm_start_escape_search/`:
  trước warm direction, giữ nguồn pha04; archive/manifest/SHA-256 nguồn
  lúc tạo và verify lại754 file qua. Hash6 module của4 prototype khớp
  các checkpoint tương ứng trong prototype_source_provenance.json.
- `backups/20261102_105053_078886_nk073_before_fixed_refuge_goal/`:
  trước fixed world refuge, archive/manifest/SHA-256 nguồn lúc tạo qua.
- `backups/20261102_105520_050510_nk073_before_physical_recovery_floor/`:
  giữ bản refuge trước floor/terminal split; archive/manifest/SHA-256
  nguồn lúc tạo qua. Không xóa snapshot hoặc thay lịch sử cũ.

**Minh chứng và bàn giao:** `docs/evidence/2026-11-02/nk073_motion_escape/`;
runbook `docs/LIDAR_2M_AVOIDANCE.md`. Kết quả lượt Gazebo chốt ghi tiếp dưới
đây, đã đối chiếu contact, chuyển động và goal; không tự suy test số
học thành xác nhận3xe an toàn, không so RTF giữa các điều kiện khác nhau.
Không commit/push. Hướng còn mở: response actuator thực, che khuất, nhiều
vật đổi hướng và hồi phục đội hình sau né.

**Kết quả Gazebo chốt NK-073:** pha06 domain60/partition riêng, goal gốc
(1.03553379,−1.97902071) sau sim≥8.69, cameraoff/server-only. Frame0.001–247.951s
(wall cap720s, không đạt250s dự kiến). Không có non-ground contact trước
193.260s, robot2 không có trong các cặp contact toàn lượt; robot1/leader
còn6 cặp/8 đợt như acceptance/summary. Contact cuối còn active khi kết thúc.
Các xe có chuyển động thật (root XY sampled≈32.19/18.60/18.44m), cuối lượt
chưa hồi phục goal/đội hình. Không gọi hoàn thành mục tiêu3xe né ổn định.

Giữ source/snapshot/prototype thất bại, không sửa lịch sử NK-071/072 hoặc
chọn chỉ đoạn đẹp làm kết quả.6 source module hash khớp runtime chốt;
raw frames và diagnostic windows nén giữ trong thư mục evidence.234 test,
17 test mới và build2package qua;2 warning SciPy,3 lint file không chạy.
Test kết thúc/cleanup riêng, không còn Gazebo/launch của tác vụ. Không push.

Bước tiếp: raw LiDAR/capture pose/drive trước các mốc contact, kiểm mismatch
render-vs-collision của seated body và tracking-response. Model viewer B
body envelope box.88x.62, offset.18; generator loại people khỏi map có chủ
đích, không coi GT actor là perception. Đây là bằng chứng hình học cần
đối chiếu, chưa kết luận nguyên nhân duy nhất. Probe55s khi sim chậm chỉ
có pose107.099–107.299, không đủ mẫu động wheel/command để sửa actuator.
[Chi tiết](docs/evidence/2026-11-02/nk073_motion_escape/README.md),
[ảnh quỹ đạo](docs/evidence/2026-11-02/nk073_motion_escape/final_trajectories.png).

Checkpoint cuối nguồn đã kiểm nhưng còn lỗi:
`backups/20261102_112203_374500_nk073_checkpoint_partial_avoidance/`.
Archive/manifest/SHA-256 nguồn lúc tạo và verify archive qua; giữ cả
minh chứng/nguồn/tests/tài liệu, loại private/generated/runtime. Không
đánh dấu đây là phiên bản né ổn định. Các checkpoint trước không bị xóa.

### NK-074 — 02/11/2026 — Ghi vùng quét LiDAR và điểm né A*/MPC

Yêu cầu: người dùng muốn thấy vùng LiDAR, lúc người đi vào vùng quét và
điểm xe chọn bằng A* trong trình ghi/phát lại để đọc hướng né từ ảnh.
Trước đây replay chỉ có pose/contact/goal; stop diagnostics không lưu raw
ranges đầy đủ và điểm A* không đồng nghĩa điểm MPC thực dùng.

Trước sửa đã tạo và verify snapshot
`backups/20261102_112403_715273_replay_lidar_coverage_and_astar_targets/`:
archive đọc được, manifest có, SHA-256 nguồn lúc tạo qua; verify archive
lại qua821 file. Phạm vi nguồn/assets/config/test/docs và thay đổi chưa
commit; loại credentials/private/build/install/log/cache/runtime theo
backup script. Không xóa/ghi đè backup trước.

Triển khai node replay ROS riêng, chỉ bật theo SOCIAL_REPLAY_DIRECTORY
khi wrapper ghi thủ công. navigation.jsonl lưu scan từng xe, TF sensor,
capture/receipt, epoch, A* path/goal và MPC selected target/clear. Writer
nền có queue1024/cap128MiB, status/drop/error; không publish command.
Controller chỉ publish telemetry tùy chọn sau nhánh lệnh đã kiểm hoặc
khi dừng; không đổi thuật toán né. Thêm exec dependency tf2_msgs.

Viewer/HTTP/export đọc stream tăng dần và bỏ dòng dở, vòng2m theo scan,
returns thực, entry interval theo mẫu, A*◇ và MPC× riêng. Chiếu theo pose
capture/TF thực, ẩn khi quá tuổi hoặc thiếu transform; clear/reset không
bám điểm cũ. Phân biệt trong bán kính với tia gần khối người (GT ước lượng,
không phải nhận dạng người hoặc chứng minh track controller). PNG giữ
các marker và timestamp. Phiên cũ thiếu stream vẫn xem pose, không bịa scan.

File: recorder mới; three_robot_sim.launch.py/package.xml; controller
telemetry; scripts/run_dynamic.sh, view_replay.py, replay_viewer.html và
scripts/tests/test_replay_sensors.py. Đồng thời cập nhật runbook phát lại,
chẩn đoán, bàn giao và báo cáo kỹ thuật.

Kiểm chứng:244 test qua,2 warning SciPy,3 ament lint file không chạy;
10 test mới, gồm không đổi command/rollout ở fixture và lỗi publisher.
Build2 package qua. ROS kiểm soát cả3 xe/TF alias/capture delay/clear/reset;
installed observer start/stop sạch. Firefox kiểm che khuất/entry/pose khi
quay/A* khác MPC/stale/legacy/HTTP partial/tăng dần/exportPNG/HTML qua.
[Minh chứng và lệnh](docs/evidence/2026-11-02/replay_lidar_astar/README.md).
Ảnh/pose fixture là tổng hợp, không phải dữ liệu thử né mới trong Gazebo.

Giới hạn: chưa kiểm toàn stack Gazebo mới, chưa đo overhead RTF hoặc
benchmark. Không đổi kết luận contact NK-073; tính năng chỉ giúp audit.
Không mở/dừng mô phỏng người dùng, không push. Báo cáo bổ sung so sánh
khả năng quan sát dữ liệu trước/sau, không tạo phiên bản né giả.

### NK-075 — 02/11/2026 — Xác định robot3 dừng do deadline MPC

Người dùng hỏi vì sao robot3 không về goal. Đọc phiên đang chạy
recordings/lidar_vung_01, không đổi goal/khởi động/dừng mô phỏng.
Backup trước cập nhật minh chứng/tài liệu:
`backups/20261102_141819_502020_nk075_audit_leader_mpc_timeout/`;
script tạo archive/manifest và kiểm SHA-256 với nguồn thành công, phạm vi
nguồn/assets/config/test/docs/thay đổi chưa commit, loại private/runtime.

Cửa sổ106.025–126.025s sim có173 mpc_compute_budget_exhausted,12
moving_obstacle_pause_hold,2 checked_escape_command,2 escape timeout,
1 invalid/empty và1 stale reference. Code đặt normal_deadline wall100ms;
sau tracking rollout, fallback beam hết hạn gọi publish_stop → Twist0.
Đây là nguyên nhân dừng trực tiếp; không đồng nghĩa chứng minh không có
đường. Frame126.301 robot3 ở(0.5254,−0.3754), goal giữ(1.0816,−2.0020),
cách≈1.72m; frame chỉ contact nền. Camera vẫn false. Nguồn/install
controller cùng SHA-256. ROS safety topic probe timeout12s không có mẫu,
không dùng làm bằng chứng. [Analysis](docs/evidence/2026-11-02/nk075_leader_timeout/analysis.json),
[decision gốc](docs/evidence/2026-11-02/nk075_leader_timeout/decisions.jsonl),
[frame](docs/evidence/2026-11-02/nk075_leader_timeout/frame.json).

Chỉ thêm minh chứng và cập nhật hai README; không đổi code/config,
không test/build lại vì không sửa hành vi. Chưa profile chi phí check,
CPU/DDS hoặc nguồn rejection khiến rollout nhanh không qua. Hướng tiếp
đo các chi phí đó trước khi sửa; không tăng deadline mù hoặc bỏ check
collision. Báo cáo bổ sung giới hạn mới có bằng chứng, không gọi cải tiến
thuật toán. Không commit/push.

### NK-076 — 02/11/2026 — Hoàn tất quỹ đạo bám goal sau khi né

Yêu cầu/đính chính: người dùng thấy cả3 xe né rất ổn trong bản ghi vừa
rồi, chỉ không đi tiếp về goal sau người qua khỏi vùng quét. Người dùng
chỉ cho chạy mô phỏng test1 lần để nhanh. Audit toàn lidar_vung_01
0.001–165.201s không contact ngoài nền engine ghi nhận, phù hợp quan sát.
Không quy lỗi cho escape hoặc lấy contact lượt NK-073 khác phủ nhận lượt
này. NK-075 timeout tracking là lý do trực tiếp, không chứng minh không
có đường hay camera giữ xe.

Backup trước sửa:
`backups/20261102_142358_806135_nk076_resume_goal_after_escape/`.
Archive/manifest/SHA-256 với nguồn lúc tạo qua; snapshot nguồn/assets/
config/test/docs và thay đổi chưa commit, loại private/runtime. Giữ cũ.

Thay đổi: normal MPC trước fallback beam12 ngay thường hết100ms wall
trước khi kiểm xong horizon. Sau thử full horizon beam1, ngõ cụt thử3/12
trong cùng deadline; giữ acceleration, cost, clearance, map, LiDAR,
moving, peer và kiểm freshness trước publish. Không phát partial hoặc
bỏ collision checks. Đánh đổi: nghiệm hợp lệ beam hẹp có thể kém cost
beam12 nếu có đủ thời gian. Chỉ đổi fallback normal; AST escape/yield,
checked tracking rollout, stationary scan filter, peer sweep so backup
khớp. Normal command gửi telemetry xóa marker né cũ.

File: dstar_mpc_controller.py, test_resume_tracking_after_escape.py mới;
evidence/run harness và hai README. Không sửa goal, timeline người,
collision, ngưỡng né hoặc camera/LiDAR. Test đầu bắt lỗi tên biến khi
refactor helper, đã sửa trước Gazebo; giữ log lỗi. Sau sửa15 test liên
quan qua, hồi quy248 test qua/2 warning SciPy/3 lint file không chạy;
build2package qua.4 test mới kiểm full horizon/work budget, deadline,
collision và release pause về reference. Test không dùng ROS commands.

**Đúng một lượt Gazebo** server-only domain64/partition riêng, cameraoff,
LiDAR2m, cùng goal(1.0815577507,−2.0020322800). Record0.001–75.051s không
contact ngoài nền ghi nhận. Leader vào cách goal<.15m ở12.151s, rời xa
>.5m ở24.051s khi né (xa nhất≈1.54m), quay lại<.15m ở58.501s; cuối lượt
ở goal. Cả3 status cuối normal. Leader có527 mpc_tracking_command,
103 checked_escape_command; không mpc_compute_budget_exhausted trong
lượt này, vẫn có1 escape timeout/1 beam empty. Đây là số mẫu, không phải
số thử độc lập. Dừng chủ động sau xác nhận trở về goal, không chạy lại.
Không còn launch/Gazebo của lượt kiểm chứng; không tác động phiên người
dùng (đã không còn chạy lúc test). Không push.

[Minh chứng](docs/evidence/2026-11-02/nk076_resume_goal/README.md),
[analysis](docs/evidence/2026-11-02/nk076_resume_goal/analysis.json),
[phạm vi/hash](docs/evidence/2026-11-02/nk076_resume_goal/source_scope.json).
Giữ frames/goals/scene/config nén và decision/scans excerpt để kiểm sau.

Giới hạn: chỉ1 lượt75s, chưa kiểm lại mốc>193s của NK-073 hoặc tất cả
chu kỳ người/goal/ngõ cụt. Server-only khác GUI nên không suy benchmark
RTF hay tỷ lệ tốt hơn. Chưa chứng minh toàn đội luôn tái lập đội hình;
đã xác nhận leader trở về và cả3 cuối normal. Báo cáo ghi đúng cải tiến
tracking và giới hạn, không tuyên bố hoàn tất tránh va chạm tổng quát.

### NK-077 — 02/11/2026 — Nút xem các bản ghi cũ trên máy

Người dùng muốn chọn bản ghi cũ ngay trong giao diện. Trước phải khởi
động viewer với --session khác hoặc chọn nhiều JSON thủ công.
Backup trước thay đổi:
`backups/20261102_144440_678855_nk077_replay_recording_picker/`;
archive đọc được, manifest và SHA-256 nguồn lúc tạo qua. Phạm vi nguồn/
assets/config/test/docs/thay đổi chưa commit, loại private/generated/
runtime. Không xóa hoặc ghi đè backup.

Triển khai: thanh danh sách bản ghi trong recordings/, refresh và Mở
bản ghi; endpoint /recordings chỉ liệt kê folder scene+frames hợp lệ,
không expose arbitrary path hoặc symlink ngoài recordings. Mỗi tab
chọn qua query URL riêng và reload cả stream/offset. Thêm Mở thư mục
khác… dùng webkitdirectory đọc local/browser không upload; folder và
file import chung loader, bỏ tail JSONL dở, không nhận lẫn nhiều folder.
Khi import local, dừng poll HTTP và đợi poll đang chạy xong trước thay
state để không bị ghi đè. HTML standalone vẫn chọn folder được.

File: scripts/view_replay.py, scripts/replay_viewer.html,
scripts/tests/test_replay_recording_picker.py mới; runbook và hai README.
Kiểm chứng:20 test scripts/tests qua; HTTP thật kiểm tất cả endpoint
cùng session, Unicode, refresh, tab độc lập, invalid/path/symlink. Firefox
kiểm nút mở/tải scene-frame-goal, import local không bị poll ghi đè,
partial tail và standalone qua. Harness browser ban đầu lỗi escape
newline fixture, đã sửa trước kết quả chốt; không lỗi navigation.
[Minh chứng](docs/evidence/2026-11-02/nk077_recording_picker/README.md).

Không sửa điều hướng, build hoặc chạy/dừng Gazebo, không push. Không chạy
lại toàn bộ planner vì chỉ thay replay, không dùng số test cũ làm kết
quả mới. Folder import là snapshot, không tự theo dõi file mới; bản ghi
thiếu/xóa không được khôi phục. Người dùng cần restart server viewer cũ
một lần để nạp backend mới, không phải restart mô phỏng. Báo cáo bổ sung
khả năng truy cập/phát lại bản ghi, không tạo phiên bản thuật toán né.

### NK-078 — 02/11/2026 — Một lượt120s có nhận diện vùng xã hội

Người dùng yêu cầu kiểm đúng1 lần khi thêm nhận diện vùng xã hội, chạy
120s. Hiểu120s là thời gian mô phỏng, giữ goal lượt trước. Backup trước
thay đổi harness/tài liệu:
`backups/20261102_145128_553508_nk078_social_camera_120s_once/`;
script kiểm archive/manifest/SHA-256 nguồn lúc tạo thành công, snapshot
nguồn/assets/config/test/docs/chưa commit, loại private/generated/runtime.
Không xóa/ghi đè backup, không thay source navigation/defaults.

Chạy một lượt server-only không GUI/RViz, domain66/partition riêng;
leader_camera/person_detection/head_pose/body_pose/social_avoidance/
social_observation/social_auto_observe=true. Camera480x360/6Hz, inference
max2Hz wall/1CPU thread, LiDAR2m/240 rays giữ. Social map cấp D* và3MPC;
né vật động vẫn LiDAR (avoidance_use_camera=false). Không đưa ground
truth/kịch bản vào perception hoặc điều khiển. Goal giữ
(1.0815577507,−2.0020322800); outputs nhận diện/regions/keepout/diagnostic/
pose/contact được ghi trực tiếp.7 file params thực của launch lưu lại.

**Kết quả:**frames0.001–120.001s, đạt120s và dừng, không chạy lần2.
Physics xác nhận patrol↔robot3 84.180–86.253s và patrol↔robot2
85.647–87.771s; robot1 không contact ngoài nền ghi nhận. Leader gần
 goal20.801s, né ra>.5m24.001s, trở lại<.15m55.101s, cuối ở goal
(cách≈.000122m). Không chứng minh toàn đội luôn tái lập formation.
Như vậy **chưa đạt cả3 né ổn khi bật nhận diện xã hội**.

Nhận diện có tối đa6 person,2 bodies,1TV trong các status đã ghi;
viewing_tv11 mẫu14.033–18.235s, facing_group/person vùng khác hoạt động.
Chưa lying candidate hoặc lying_person, không suy ra nhận diện người
ngủ/đúng hành vi. TV region chỉ xuất hiện trong đoạn ngắn; chưa đánh giá
accuracy/recall/persistence độc lập khi góc nhìn thay đổi.

Checkpoint sát contact: robot3 t84.1 command0, reason
escape_all_rollouts_rejected,140 moving rejects, compute≈26.4ms;
robot2 t85.6 command0,132 moving rejects,≈13.4ms. State/scan tuổi≈.1–.2s
sim. Đây là lý do dừng trực tiếp, chưa căn nguyên geometry/estimate/
actuator/chọn hướng; không đủ cơ sở quy tất cả cho camera xử lý chậm.
Các lỗi timeout/sensor expiry ở thời điểm khác vẫn lưu, không bỏ qua.
Lượt NK-076 chỉ75s, contact mới ở84–88s nên chưa có baseline120s cùng
điều kiện để quy thay đổi cho camera. Không tự chạy thêm lượt để so.

Vận hành: harness nhận SIGTERM lúc cleanup nên live.json/samples.json
cuối không được ghi; không bịa lại service results/wall chính xác.
completion.json xác nhận hoàn tất bằng raw frames/goals/events/params;
navigation writer status kết thúc sạch0 dropped/no error. Không còn
process test. Sau đó thêm pre_cleanup checkpoint cho harness để giữ
state trước phát signal, compile qua; chưa chạy lại vì ràng buộc1lượt.
Không gọi exit143 là kết quả navigation pass. Không build/hồi quy248
test lại vì nguồn navigation không sửa; chỉ kiểm compile harness.

File: evidence validate_once.py/analyze.py, ảnh camera, frames/scene/
goals/config nén, social_events, raw scans81–89s+mọi decision, diagnostic
quanh contact và params/provenance; cập nhật hai README cùng tác vụ.
[Minh chứng](docs/evidence/2026-11-02/nk078_social_camera_120s/README.md),
[analysis](docs/evidence/2026-11-02/nk078_social_camera_120s/analysis.json),
[completion](docs/evidence/2026-11-02/nk078_social_camera_120s/completion.json).
Runtime mở được bằng viewer ở recordings/nk078_social_camera_120s_once.
Báo cáo bổ sung bằng chứng giới hạn tích hợp, không tuyên bố cải tiến
né hoặc so RTF. Giữ thuật toán hiện tại/backup và các lượt trước; không
push. Bước tiếp audit81–89s trước khi đề xuất sửa, không sửa trong lượt
kiểm này.

### NK-079 — 02/11/2026 — Camera leader và vùng xã hội trên trang xem

Yêu cầu: thêm ảnh camera leader và vùng xã hội đã nhận vào viewer. Đồng
thời ghi ràng buộc từ lượt trước: sau mỗi kiểm thử gửi lệnh mở đúng bản
chạy để người dùng xem. Không chạy lại mô phỏng để làm UI.
Backup trước sửa:
`backups/20261102_151105_604099_nk079_replay_camera_social_overlay/`;
archive/manifest/SHA-256 nguồn lúc tạo thành công, gồm nguồn/assets/config/
test/docs/chưa commit, loại private/generated/runtime. Không xóa cũ.

Triển khai panel camera chọn tự động/raw/nhận diện, lớp vùng từ snapshot
camera_social_regions trong map và status; cùng receipt/capture/epoch.
Không chọn ảnh tương lai; ảnh cũ/thưa ghi tuổi rõ, vùng quá2s ẩn hoặc
snapshot rỗng xóa. PNG ghép camera và map; standalone/folder import/
HTTP chọn cùng session vẫn có ảnh/regions. Xử lý client đóng HTTP không
phát lỗi BrokenPipe lặp khi chuyển HTML.

Recorder read-only hiện có thêm perception.jsonl writer riêng queue32/
cap256MiB; subscribe raw camera/people image/social markers/status. JPEG
75/max cạnh640 encode background, mỗi nguồn tối đa2Hz theo cả sim/wall;
không làm ở controller. Metadata wrapper ghi stream; status/drop/error
riêng. Chỉ opt-in ghi thủ công, không tự bật camera/nhận diện hoặc sửa
controller/launch profile/navigation. Node helper được build/install.

NK-078 còn social_events gốc và6 JPEG thật nên import vào stream bổ sung
của runtime, không thay nguồn frames/scans/goal/ảnh gốc. Import từ chối
file có sẵn/reset nhiều epoch; giữ hashes/provenance. Ảnh chỉ snapshot
receipt từ tên file, capture không còn biết→null/false, không nội suy
video hoặc bịa region. Bản cũ khác thiếu dữ liệu không hồi điền giả.
Vùng xemTV14–18s và ảnh84.704s xem được ngay sau restart viewer.

File: replay_sensor_recorder.py/replay_perception.py dưới sim/scripts;
root scripts/view_replay.py, replay_viewer.html, import_perception_replay.py,
run_dynamic.sh và test_replay_perception.py; thêm HTTP test stream, docs
phát lại/chẩn đoán và hai README. Evidence giữ screenshot/PNG camera/
HTML export nén, original import provenance và fixture ROS.

Kiểm chứng:23 test scripts qua,3 test mới về JPEG/throttle/capture/reset,
marker clear/frame và stream/status/export. Test float bằng tuyệt đối
ban đầu lệch biểu diễn, đã dùng approx; không đổi timestamp logic.
ROS domain79 fixture gửi raw/detection/markers/status, actual recorder
cho JPEG/clear/receipt, writer0drop/noerror; không publish command hoặc
Gazebo. Firefox bản ghi thật NK-078 kiểm TV14.5,84.5 không dùng ảnh84.704
sau đó,84.9 dùng đúngảnh; sparse/stale labels/clear/TTL/epoch/legacy,
PNG ghép camera/HTML qua. Sim package build qua. Không rerun full planner
hoặc test Gazebo vì không thay thuật toán. [Minh chứng](docs/evidence/2026-11-02/nk079_camera_social_replay/README.md).

Giới hạn: chưa benchmark overhead JPEG/IO/RTF ở Gazebo, raw camera mới
chỉ ROS fixture. Vùng là contour publisher, không phải ô raster đã carve
hoặc chứng minh nhận diện/né đúng; ảnh rời rạc cũ không phải video.
Kết luận contact NK-078 giữ nguyên. Không start/stop mô phỏng, không push.
Các HTML export tự tạo cho test được giữ dạng gzip để tránh file28MiB;
không xóa bản ghi/backup người dùng. Cập nhật báo cáo chức năng chẩn đoán,
không tạo phiên bản thuật toán né giả. Bước tiếp mở runtime đã gửi,
không cần mô phỏng mới để xem dữ liệu cũ.

### NK-080 — 02/11/2026 — Đối chiếu nguyên nhân va chạm NK-078

Người dùng hỏi lỗi và lý do từ bản ghi. Đọc pose/diagnostic/source,
không sửa navigation hoặc chạy mô phỏng. Backup trước thêm phân tích/
tài liệu: backups/20261102_153113_128946_nk080_audit_nk078_collision_causes/;
script kiểm archive/manifest/SHA-256 nguồn lúc tạo qua, gồm nguồn/assets/
config/test/docs/chưa commit, loại private/generated/runtime; giữ cũ.

Audit tìm được chuỗi cụ thể hơn NK-078: patrol đứng rồi đi−X≈.404m/s,
robot3 t83.0 track chỉ≈.14, chọn goal−Y cắt y=−2. T83.1 goal đảo+Y
nhưng command vẫn−Y trong giới hạn gia tốc;83.2 timeout,83.3 trở đi
all_rollouts_rejected,84.180 contact. Robot2 t84.0/85.1 track0 khi GT
vẫn≈.404, đi vào pause_hold; khi vận tốc phục hồi thì moving checks loại
hết candidate,85.647 contact. collision_risk gate speed<.05 bỏ risk dù
pause reserve nới radius; cần phân biệt uncertain với đứng yên. Ba nguồn
ở83s đều thấp, không chỉ riêng thiếu sensing một xe.

Pose root leader còn dịch≈5.94cm83.201–84.151 sau command0 từ83.2, chưa
đo wheel/effort/all publishers để kết luận lý do thực thi. Scan/state
sát contact≈.1–.2s sim, compute13–26ms, reject moving, không chỉ map/
peer. Camera không trực tiếp tạo moving tracks ở profile này; chưa có
căn cứ quy contact cho camera chậm. Giữ giới hạn khác nhau75/120s.

[Analysis](docs/evidence/2026-11-02/nk080_nk078_cause_audit/analysis.json),
[giải thích/lệnh](docs/evidence/2026-11-02/nk080_nk078_cause_audit/README.md).
Script analyze.py chạy offline và kiểm các checkpoint/GT ở đúng stamp;
không nhận diện identity semantic và không cấp GT vào controller.
Không build/tests/navigation changes hoặc start/stop sim, không push.

Giới hạn: chuỗi trên có dữ liệu hỗ trợ, nhưng chưa quy zero velocity
riêng cho fit/association/fusion vì thiếu history/trackID. Không chứng
minh có đường vật lý khả thi tại83.3 hoặc actuator sai là nguyên nhân
độc lập. Đề xuất chưa triển khai: vận tốc uncertain/restart, dự báo
corridor có biên bất định, pause safety và calibrate phanh. Không bỏ
hard check hoặc ép A* để đi được. TV region14–18/lying absent chưa đủ
kết luận memory lỗi thay vì đổi hành vi/FOV. Báo cáo bổ sung audit,
không tạo phiên bản thuật toán mới.

### NK-081 — 02/11/2026 — Sửa dự báo mất vận tốc và lối né sau audit NK-080

Người dùng yêu cầu sửa code. Đã backup trước thay đổi tại
`backups/20261102_153811_755576_nk081_motion_uncertainty_corridor_escape/`;
trước đổi hướng thu hẹp tại
`backups/20261102_155547_550541_nk081_checkpoint_prior_trial_before_narrowing/`.
Cả hai archive đọc được, SHA-256 đối chiếu nguồn thành công và có manifest;
phạm vi nguồn/assets/cấu hình/test/tài liệu, loại build/log/credentials.

Sửa moving_obstacles/controller và thêm 8 test: vận tốc đo gần nhất làm
hypothesis khi mất fit, fusion không tăng phiếu; loại A*/rollout cắt phía
trước luồng người; dùng vận tốc trôi đo từ pose khi lệnh đã0 và phanh nếu
vượt giới hạn lệnh. Giữ map/LiDAR/peer/freshness/gia tốc/full horizon và
normal tracking NK-076. Không đổi goal, world hoặc dữ liệu GT vào control.

Bản thử ban đầu còn thêm speed prior cho người mới chuyển động; đúng1 lượt
Gazebo camera/xã hội120s cho contact leader–tv_viewer_a_walking32.117–34.595s,
cuối leader cách goal4.222m. Robot1/2 không contact ngoài nền ghi nhận.
Không đạt. Có vận tốc prior lớn hơn nominal và nhiều nhánh bị loại; chưa
chứng minh một nguyên nhân duy nhất. Đã tạo checkpoint, bỏ synthetic prior,
chỉ giữ vận tốc đo gần nhất khi mất fit và thêm overspeed guard. Mã cuối
**chưa chạy Gazebo**, tuân thủ chỉ1 lượt. Raw125.601 gồm tail đóng phiên;
chỉ0.001–120.001 tính đánh giá. Không xóa/sửa lịch sử NK-078/NK-080.

Mã cuối260 test qua,2 warning SciPy; ba ament lint chưa chạy. Hai package
build thành công và install khớp hash nguồn cuối. Bản thử258 test qua vẫn
thất bại vật lý, không coi test số học là bằng chứng sửa hết va chạm.
Tài liệu tiến độ cập nhật bằng chứng/giới hạn này. Không commit/push.

[Minh chứng và hash từng bản](docs/evidence/2026-11-02/nk081_motion_uncertainty/README.md).
Xem lượt thử: `python3 scripts/view_replay.py --session recordings/nk081_social_motion_120s_once`.
Còn mở: kiểm chứng mã cuối tránh người và trở lại goal; không tự chạy lại.

### NK-082 — 02/11/2026 — Ưu tiên né ngoài vùng xã hội

Theo yêu cầu người dùng, sửa `dstar_mpc_controller.py`: A* tìm trên planning
map trước (8ms trong tổng ngân sách A*15ms); không tìm thấy thì thử lối vật
lý trong ngân sách còn lại. MPC xếp quỹ đạo đã qua hard checks theo ưu tiên:
không xuyên planning keepout → endpoint ngoài vùng → ít bước xuyên vùng →
điểm né cũ. Xe đang trong vùng có thể thoát; không cấm tuyệt đối lối khẩn cấp.
Không thay ngưỡng vật lý/LiDAR/peer hay bỏ kiểm tra vận tốc/horizon NK-081.

Backup trước sửa: `backups/20261102_161459_438064_nk082_social_escape_priority/`;
script xác minh archive/SHA-256 nguồn và manifest thành công; phạm vi nguồn,
assets, cấu hình, test, tài liệu; không gồm build/log/credentials.

Planner build thành công; `git diff --check` qua. 40 test qua gồm test mất fit/corridor/moving safety và 4 test mới
`test_social_escape_priority.py`. Lần thu thập test đầu lỗi tên class import,
đã sửa và chạy thành công. Không chạy Gazebo mới, không benchmark hiệu năng;
không tuyên bố hết va chạm. Kết quả NK-081 vẫn là bản thử không đạt.

Giới hạn: ưu tiên trong các ứng viên kiểm tra được dưới ngân sách thời gian,
không chứng minh hết mọi đường ngoài vùng. Dùng planning map hiện hành (sau
carve escape), không phải toàn bộ contour marker. Chưa có cơ chế chuyên biệt
đưa xe ra khỏi vùng sau khi threat hết ngoài normal tracking về goal.
Không commit/push. Minh chứng: `docs/evidence/2026-11-02/nk082_social_escape_priority/`.

### NK-083 — 02/11/2026 — Một lượt120s kiểm tra NK-082 có camera/xã hội

Người dùng yêu cầu chạy thử rồi tiếp tục. Đã chạy đúng1 lượt server-only,
ROS domain69, goal(1.0815577507,−2.00203228), camera/person/head/body/social
map/observation/auto-observe bật, LiDAR2m. Không đổi thuật toán trong tác vụ.
Đã dừng sau120s sim. Không chạy lần2 và không push.

Kết quả không đạt: trong cửa sổ0.001–120.001s, contact physics ghi nhận
patrol_person–robot2 từ85.445 tới97.334, robot2–robot3 từ88.111 tới89.318,
robot2–tv_console từ88.218 tới90.460. Đây là mốc đầu/cuối theo cặp, không
khẳng định tiếp xúc liên tục trong toàn khoảng. Robot1 không contact ngoài
nền ghi nhận. Leader từng vào bán kính15cm goal ở20.351s, rời xa hơn50cm
ở23.101s, chưa trở lại15cm; cuối cách0.963m. Robot2 cuối ở(−4.383,−3.160).
Có195 mẫu marker viewing_tv từ14.067 tới76.434s; không chứng minh nhận diện
đúng toàn bộ hoặc vùng liên tục tồn tại. Không coi hết contact leader–người
là thành công chung vì vẫn có contact giữa xe và lỗi trở về goal.

Nguồn NK082 cùng hash lưu source_hashes.json; params thực tế/live và dữ liệu
nén tại `docs/evidence/2026-11-02/nk083_social_escape_120s/`. Chưa audit riêng
quỹ đạo xuyên planning keepout hoặc định lượng tác động carve; chưa thể quy
chuỗi contact cho ưu tiên vùng xã hội, camera hay một nhánh cụ thể. Decision
có nhánh timeout, all-rollouts-rejected, overspeed và freshness; cần đối
chiếu timeline trước khi kết luận nhân quả. Một lượt không là benchmark.

Backup trước tạo harness/tài liệu:
`backups/20261102_161727_010342_nk083_social_escape_validation/`; script đã
xác minh archive đọc được/SHA-256 nguồn/manifest. Phạm vi nguồn, assets,
cấu hình, test, tài liệu, không log/build/credentials. Không chạy lại unit
test vì không đổi controller; kết quả40 test NK082 không chứng minh vật lý.

Xem: `python3 scripts/view_replay.py --session recordings/nk083_social_escape_120s_once`.

### NK-084 — 02/11/2026 — Ưu tiên vùng trống phía sau xe khi né

Người dùng yêu cầu chọn điểm né đằng sau xe. Quy ước phía sau theo yaw
thân xe hiện tại, nón±45 độ và lùi hơn8cm; không theo hướng nhìn camera
hay hướng chuyển động người. A* xét connector sau trước, cộng penalty
cho endpoint ngoài nón sau. MPC xét hướng lùi chính xác sớm và ưu tiên
endpoint phía sau có holding_safe, sau ưu tiên vùng xã hội NK082, trước
điểm tiện lợi cũ. Nếu sau bị chắn/người tới/xe khác hoặc không an toàn để
dừng thì vẫn xét hai bên. Không bỏ kiểm tra vật lý/LiDAR/peer/corridor/
full horizon/gia tốc. Không đảm bảo mọi tick tìm được đường sau.

Sửa `dstar_mpc_controller.py`, `local_escape.py`; thêm
`test_rear_escape_preference.py`. Backup đã kiểm archive/SHA-256/manifest:
`backups/20261102_163208_394000_nk084_rear_escape_preference/`, gồm nguồn,
assets/cấu hình/test/tài liệu; loại log/build/credentials. 44 test qua,
gồm hướng thân xe, sau trống, sau bị chặn và sau không an toàn để dừng.
Không chạy Gazebo mới; chưa chứng minh giảm contact NK083. Không push.
Minh chứng: `docs/evidence/2026-11-02/nk084_rear_escape_preference/`.

### NK-085 — 02/11/2026 — Hướng dẫn build/chạy trước và giới hạn đọc file

Người dùng yêu cầu tránh quét nhiều file không cần thiết, cung cấp lệnh để
người dùng tự chạy và sắp lại README cho người tiếp nhận. Đã sửa README
gốc, README package sim, DSTAR_MPC, SOCIAL_STATIC, SOCIAL_DYNAMIC và hai
paper: đưa build/chạy lên đầu, chuyển chú giải file xuống cuối khi có;
sửa đường dẫn workspace ví dụ. Thêm `docs/FILE_CAN_DOC_VA_LENH_CHAY.md`
chỉ file tối thiểu theo lỗi, phân biệt tài nguyên ROS cần nạp với file AI
cần đọc. Ghi quy ước tự chạy vào AGENTS và bàn giao đầu nhật ký.

Backup trước sửa: `backups/20261102_164141_563346_nk085_docs_run_first_minimal_reads/`;
script hoàn tất xác minh archive đọc được, SHA-256 với nguồn và manifest.
Phạm vi nguồn/assets/cấu hình/test/tài liệu; loại credentials/build/log.
Không đổi code/thuật toán, không build/test hoặc chạy/dừng mô phỏng. Chỉ
kiểm cấu trúc Markdown, đường dẫn file liên quan và diff whitespace.
Báo cáo tiến độ đã đọc; giữ nguyên nội dung vì đây là cập nhật tài liệu/
quy trình, không tạo cải tiến kỹ thuật hay kết quả kiểm thử mới. Giữ lịch
sử README và evidence cũ. Không commit/push.

### NK-086 — 02/11/2026 — Mỗi phần README có bộ lệnh độc lập

Người dùng làm rõ mỗi phần phải đủ lệnh, không tách build chung rồi chỉ
đưa launch ở mục khác. Đã tổ chức README gốc: 1 động (camera/xã hội và
LiDAR-only), 2 tĩnh, 3 từng paper, 4 test nhanh/hồi quy, 5 ghi lỗi/xem/
phân tích; mỗi chế độ có cd/build/source/domain/chạy đầy đủ. Viewer và
phân tích offline có trọn lệnh riêng, không thêm build không cần thiết.
Giữ trạng thái kiểm chứng và chú giải ở cuối. Không đổi code/thuật toán.

Backup trước sửa: `backups/20261102_164854_224999_nk086_self_contained_readme_commands/`;
archive đọc được, SHA-256 đối chiếu nguồn và manifest đã xác minh bởi script.
Phạm vi nguồn/assets/cấu hình/test/tài liệu; loại credentials/build/log.
Kiểm tra cấu trúc Markdown, file/link nội bộ và cú pháp các khối bash bằng
`bash -n` (không thực thi lệnh). Không build/test hoặc chạy mô phỏng.
Đã đọc báo cáo, giữ nguyên vì thay đổi hướng dẫn không là tiến độ kỹ thuật.
Không push. Tiếp tục giữ quy ước chỉ tự chạy khi người dùng yêu cầu rõ.

### NK-087 — 02/11/2026 — Tích hợp 10 phương pháp ba tầng từ hội thoại chia sẻ

Người dùng yêu cầu thêm10 bài như hai paper hiện có từ liên kết
https://chatgpt.com/share/6ae85d47-5250-83ec-80a5-0b07b13a65e6 . Web reader
không có dòng đọc được; đã lấy payload công khai và trích module literal
trong generator ba tầng cuối bằng AST, không chạy shell/generator/installer
của trang. Không lấy được ZIP sandbox của phiên khác, không giả là artifact
ZIP nguyên bản. Bản chia sẻ cũng ghi rõ prototype/xấp xỉ.

Backup trước sửa: `backups/20261102_165433_691056_nk087_ten_three_stage_comparison_backends/`;
archive đọc được/SHA-256 nguồn/manifest đã xác minh. Phạm vi nguồn/assets/
cấu hình/test/tài liệu; loại credentials/build/log. Không xóa backup cũ.

Thêm10 thư mục method có formation/trajectory/control/pipeline, common math/
memory và registry trong package planner hiện có. Thêm adapter ROS chung:
tracking gọi pipeline, giữ full-horizon map/LiDAR/moving/peer/acceleration/
freshness và emergency escape NK084; không tracking fallback baseline.
Canonical đổi leader người dùng chọn về index2 theo công thức prototype;
chỉ commit memory của bước đầu khi command đã được chấp nhận phát.

Mở rộng choices launch compare01–10, ba node mới thay ba robot MPC khi chọn
comparison, coordinator baseline D* giữ cấp reference. Paper1/2 không đổi
thuật toán. Thêm launch chung và10 wrapper paper3–12, script run_comparison
và nhánh opt-in trong run_dynamic dùng lại recorder, scene/hash xác định
method thực. Chạy bình thường baseline không tự ghi. Không thêm package,
không tải model/dependency mới cho các prototype.

README gốc có đủ bộ lệnh build/source/chạy cho từng paper, bảng ánh xạ và
10 README riêng kèm phạm vi từng tầng/test/ghi lại. Có test numerical,
adapter để người dùng chạy. Đã kiểm tĩnh AST/import nội bộ/khối bash/path/
whitespace; chưa build, chưa pytest, chưa ROS/Gazebo theo quy ước NK085/086.
Không chuyển kết quả30/60 test trong hội thoại thành kết quả repository.

Giới hạn: các phương pháp là prototype của danh sách chia sẻ, nhiều phần
CTC/vision/slip/car-like/DEFORM chưa phải phương trình/mã tác giả đầy đủ;
chưa xác minh DOI/tác giả toàn bộ10 bài. Hạ tầng né chung vẫn có lỗi NK083,
không bảo đảm tránh va chạm hay tái lập kết quả bài báo. Minh chứng phạm vi
ở `docs/evidence/2026-11-02/nk087_ten_comparison_methods/`, hướng dẫn
`README_PAPERS_03_12.md`. Không tự build/test/chạy mô phỏng hoặc push.

### NK-088 — 02/11/2026 — Ghép ghi bản chạy vào từng chế độ, lưu mỗi lượt

Người dùng yêu cầu không tách phần bản ghi thành bước riêng, vì mỗi lượt
mô phỏng đều cần lưu. README gốc và các README hướng dẫn cảnh/paper đã
được sửa để mỗi khối chạy có build/source, tên recording_dir mới, chạy kèm
--diagnose-stop và viewer sau Ctrl+C. Bỏ mục chạy ghi riêng ở README gốc và
10 README phương pháp mới. Giữ test riêng, vì test số học không là mô phỏng.

Thêm `scripts/run_simulation.sh` chọn dynamic/static/paper1–12 hoặc
compare01–10. Mở rộng run_dynamic --profile cho tĩnh/hai paper cũ; runner
động/comparison mặc định tự tạo đường dẫn timestamp/PID khi không truyền
flag ghi. Giữ khả năng đặt --diagnose-stop hoặc --record-replay với thư mục
mới; từ chối thư mục cũ. Scene ghi đúng cảnh/backend, diagnostics hash có
module paper1/2 hoặc method mới. Không thay control/map/world/launch hay
ngưỡng né, không bật camera ở profile LiDAR-only. Việc ghi chỉ xảy ra khi
chạy wrapper, không là cơ chế bắt mọi ros2 launch hoặc dịch vụ nền.

Cập nhật AGENTS, bảng file cần đọc và hướng dẫn chẩn đoán/phát lại để ghi
nhận quyết định mới thay opt-in NK064/067/079. Giữ lịch sử nhật ký/evidence
cũ. Đã đọc báo cáo; nội dung kỹ thuật giữ nguyên vì đây là thay đổi vận hành,
không có bằng chứng cải tiến thuật toán mới.

Backup: `backups/20261102_170953_270249_nk088_record_every_documented_run/`;
script đã xác minh archive đọc được, SHA-256 đối chiếu nguồn và manifest.
Phạm vi nguồn/assets/cấu hình/test/tài liệu; loại credentials/build/log.
Kiểm tĩnh:3 shell script,2 embedded Python,93 khối bash tài liệu;56 ví dụ
mô phỏng có ghi/viewer cùng khối; link nội bộ và diff whitespace qua.
Không thực thi các lệnh build/test/mô phỏng. Chưa kiểm runtime tạo/đóng file
hoặc overhead, không khẳng định recorder không ảnh hưởng RTF. Recorder vẫn
có giới hạn dung lượng/queue; các backend có mức chi tiết diagnostics khác
nhau. Minh chứng `docs/evidence/2026-11-02/nk088_inline_recording/`.
Không commit/push. AI vẫn chỉ đưa lệnh khi người dùng chưa yêu cầu tự chạy.

### NK-089 — 02/11/2026 — Chỉ giữ backup đầu/cuối và dọn build cũ

Người dùng yêu cầu xóa backup/build cũ, giữ2 backup đầu/cuối. Xác định bản
đầu theo tên thời gian là `20261101_185410_before_nk034_restore`; tạo bản
cuối mới từ nguồn hiện tại trước sửa tài liệu/dọn tại
`backups/20261102_173137_174092_nk089_final_before_backup_build_cleanup/`.
Script xác minh archive đọc được/SHA-256 nguồn/manifest. Kiểm bổ sung bản
đầu: hash archive và585 file trong tar khớp manifest. Không khôi phục nguồn.

Đã xóa47 thư mục backup trung gian, gồm bản chưa hoàn tất không manifest;
giữ README/COLCON_IGNORE quản lý backup. Xóa build/, install/ và66 mục
build log/alias dưới log/. Không xóa log chẩn đoán hoặc recordings. Mã nguồn,
assets, docs/evidence và lịch sử/nhánh Git giữ nguyên. Nhật ký các mốc cũ
vẫn giữ; đường dẫn backup đã xóa nay chỉ là tham chiếu lịch sử. Người dùng
đã cho phép việc xóa backup trong tác vụ này, không yêu cầu tạo cơ chế
retention tự động cho tương lai.

Chỉ kiểm thao tác file và hậu điều kiện2 snapshot; không build/test/mô
phỏng, không có tiến trình mô phỏng khi kiểm tra. Từ đây install/setup.bash
không còn cho tới khi người dùng build lại bằng README. Đã đọc báo cáo,
giữ nguyên nội dung vì dọn dữ liệu không là tiến bộ thuật toán. Nhật ký,
backups/README và `docs/evidence/2026-11-02/nk089_backup_build_cleanup/`
lưu danh sách/kết quả. Không commit/push hoặc xóa Git backup branch.

### NK-090 — 02/11/2026 — Audit bản ghi mới: goal bị chặn sau né

Người dùng yêu cầu kiểm bản ghi để giải thích xe không trở về goal.
Đọc `dynamic_20261102_173439_286642343`, goal duy nhất(1.0355337858,
−1.9560085535), baseline; hash source controller trùng diagnostics_config.
Chỉ đọc config/goal, đoạn quyết định cuối, contour xã hội và log coordinator
cùng lượt, rồi đoạn plan/publish_reference liên quan. Không chạy mô phỏng
hoặc thay goal. Phạm vi đến106.245s, không coi là trạng thái kết thúc phiên.

Log planner lặp reject goal vì clearance. T106.245 observation/moving safety
đãfalse nhưng replan_requiredtrue, reference_rows0. Controller3 t106.235
state0.037s/scan0.035s còn mới, reference1.734s; cả3 giữ dừng. Leader còn
cách goal2.047m. Trong plan, goal không free thì return trước tạo route;
không còn convoy/structure/maneuver thì phát reference rỗng. Đây là nguyên
nhân trực tiếp sau né không tiếp tục goal, không kết luận camera chậm.

Khoảng hở map vật lý hiện hành1.052m; contour viewing_tv90–100s cách goal
0.146m, contour color_attention105–106s cách0.137m, dưới planning margin
0.18m. Phù hợp lớp xã hội cộng biên làm goal không hợp lệ; thiếu raster
planning/keepout sau carve nên không quy chính xác ô/lớp duy nhất. Đề xuất
phân biệt social blockage tạm và physical blockage, giữ goal, chờ ở vị trí
an toàn và replan khi clear. Chưa triển khai hay chứng minh fix.

Backup trước sửa tài liệu: `backups/20261102_175016_860682_nk090_audit_goal_blocked_after_escape/`,
archive đọc được/SHA-256 nguồn/manifest qua theo script. Giữ bản đầu01/11,
xóa bản cuối NK089 sau khi có bản mới verified để duy trì yêu cầu chỉ2 bản
đầu/cuối; không xóa bản ghi/runtime log. Cập nhật report bằng chứng audit,
không tạo phiên bản thuật toán mới. Minh chứng tại
`docs/evidence/2026-11-02/nk090_goal_blocked_after_escape/`. Không build/test,
không khởi động/dừng mô phỏng và không push.

## 5. Minh chứng đã lưu trong repository

| File | Ý nghĩa | Giới hạn |
|---|---|---|
| [Ảnh có người nằm](docs/evidence/2026-10-27/posture_with_person.png) | Ảnh xuất từ pipeline kiểm thử, có nhãn ứng viên | Một góc camera |
| [Ảnh giường trống](docs/evidence/2026-10-27/posture_empty_bed.png) | Đối chứng không sinh ứng viên người nằm | Một ca âm tính |
| [Kết quả pose](docs/evidence/2026-10-27/posture_validation.json) | Số ứng viên, vị trí đo, latency hai ca | Không phải bộ dữ liệu đánh giá |
| [Mẫu runtime trước](docs/evidence/2026-10-27/runtime_before.json) | Clock, topic, lệnh, trạng thái và dữ liệu audit | Khoảng 22 s, tình huống cụ thể |
| [Mẫu runtime sau](docs/evidence/2026-10-27/runtime_after.json) | Mẫu sau cấu hình mới và UDP | Điều kiện khác, không phải A/B kiểm soát |
| [Log lịch người](docs/evidence/2026-10-27/scenario_motion_validation.log) | Trích log giai đoạn và xác minh pose physics | World tạm chạy nhanh, không phải toàn bộ stack robot |

Các file trên được sao lưu từ minh chứng của phiên làm việc trước khi viết
README; không phải kết quả được chạy mới ngày 28/10/2026.

## 6. Cách cập nhật từ các lần sau

Thực hiện theo [AGENTS.md](AGENTS.md). Thêm mục `NK-091` tiếp theo; không viết
đè nhật ký cũ. Sau mỗi thay đổi code/world/config/test hoặc kết luận thực nghiệm:

1. Ghi yêu cầu và lý do đổi.
2. Liệt kê phần nguồn bị tác động và hành vi trước/sau.
3. Ghi đúng kiểm tra đã chạy, kết quả, điều kiện và việc chưa kiểm tra.
4. Nếu có cải tiến chức năng/bằng chứng mới, cập nhật so sánh trong báo cáo;
   việc vận hành chỉ ghi nhật ký, không chèn vào báo cáo.
5. Giữ minh chứng cần thiết trong repo và kiểm tra liên kết.

Mẫu mục mới:

```markdown
### NK-XXX — DD/MM/YYYY — Tên cập nhật

Yêu cầu/bối cảnh:
Thay đổi và lý do:
File liên quan:
Kiểm tra đã chạy và kết quả:
Giới hạn/việc còn lại:
Ảnh hưởng tới báo cáo tiến độ:
```

Quy trình áp dụng cho các tác vụ làm việc trong repo. Không có dịch vụ nền
tự đọc ý định của mọi sửa đổi ngoài Codex; người sửa bằng công cụ khác cũng
cần cập nhật hai file trong cùng thay đổi.

### NK-091 — 02/11/2026 — Tiếp cận goal bị chặn, giữ yêu cầu gốc

- Yêu cầu: sửa đứng yên sau né; khoảng hở ít nhất1cm; làm rõ yêu cầu chạm chân.
- Backup nguồn/assets/cấu hình/tài liệu trước sửa:
  `backups/20261102_180407_004374_nk091_goal_approach_recovery/`.
  Script xác minh archive, SHA-256 nguồn và manifest thành công; kiểm lại SHA
  archive trước dọn bản cuối NK090. Giữ bản đầu và bản cuối theo yêu cầu2backup.
- `dstar_mpc_controller.py`: không bỏ cuộc ngay tại goal thiếu clearance.
  Tìm endpoint bên ngoài keepout trong bán kính0.1–1m quanh goal, tối đa8
  kiểm tra đường tới các ứng viên gần nhất; tuyến đi vẫn kiểm footprint/map/
  dynamic/peer. Goal người dùng giữ nguyên, endpoint tạm riêng. Khi goal gốc
  clear, control_tick yêu cầu lập lại đường; log thêm approach_goal và
  goal_route_status. Không ghi đè vùng xã hội để đi xuyên vào goal.
- Thêm ràng buộc inflation >= robot_radius+0.01 cho coordinator và MPC.
  Mặc định0.18−0.15=0.03m giữ nguyên; đây là ngưỡng cấu hình map, không phải
  bảo đảm mọi quỹ đạo thực đạt1cm hoặc giảm mọi lớp dự báo người về1cm.
- Goal RViz là vị trí tâm xe. Chạm chân bằng mép xe cần task tiếp xúc riêng,
  mục tiêu bề mặt và feedback contact; CHƯA triển khai task đó. Không báo
  hoàn thành goal gốc chỉ vì đến endpoint tiếp cận. Chưa bổ sung marker riêng
  cho endpoint tạm; dữ liệu có trong stop diagnostics.
- Viết `test_goal_approach_recovery.py` cho giữ goal, không có approach và
  quay lại goal gốc. Chỉ kiểm AST/diff; chưa pytest/build/Gazebo theo NK085.
- Giới hạn:8 ứng viên không bảo đảm tìm được mọi đường; goal trong vùng xã
  hội tồn tại lâu vẫn phải chờ. Map5cm không chứng minh độ chính xác1cm.
  Cần người dùng kiểm thử bản mới, không suy ra thành công từ NK090.

### NK-092 — 02/11/2026 — Audit va chạm robot1 và vùng xem TV

Theo yêu cầu đọc bản mới, đối chiếu contact, lệnh né, perception và nguồn
xóa vùng. Xác nhận contact vật lý, không chỉ chồng lấn hình học; vùng TV
đã xuất hiện rồi bị gỡ. Chi tiết và giới hạn tại evidence NK092. Chưa sửa
thuật toán, không chạy/dừng Gazebo/build/test. Backup nguồn trước cập nhật
tài liệu tại backups/20261102_181512_918371_nk092_audit_robot1_contact_tv;
script kiểm archive/SHA nguồn/manifest thành công, kiểm SHA archive lại
trước thay backup cuối NK091, giữ hai bản đầu/cuối. Kiểm diff tài liệu.

### NK-093 — 02/11/2026 — Né liên tục và quay quanh goal ở20cm

- Yêu cầu: chỉ sửa lỗi1 NK092; lỗi2 mất vùng TV chưa sửa. Thêm quay360
  khi leader cách goal20cm. Người dùng tự chạy, không mở/dừng mô phỏng.
- Backup trước sửa: backups/20261102_181917_162847_nk093_continuous_escape_goal_scan.
  Script kiểm archive/SHA nguồn/manifest thành công; kiểm lại SHA archive
  trước thay backup cuối NK092, giữ hai bản đầu/cuối theo yêu cầu.
- Controller chung3xe: chờ refuge chỉ khi đã cách điểm đó<=12cm. Loại
  pause giữ dừng1.25s khi mất fit; giữ giả thuyết vận tốc đo cũ tối đa0.5s
  và kiểm lại đường nếu vẫn nguy hiểm. Không tự tạo vận tốc người.
- Dự trữ tối đa25ms (40% budget) cho rollout ngắn>=0.6s khi không có
  phương án đầy đủ3s; từng bước giữ map/scan/corridor/moving/peer/gia tốc.
  Chỉ thực hiện lệnh đầu rồi tính lại tick sau. Endpoint ngắn có thể chưa
  dừng an toàn, không bảo đảm thoát hết mọi tình huống; không bỏ check
  physical để ép xe di chuyển. Diagnostics thêm escape_horizon_seconds.
- Tự yêu cầu full ObservationSweep khi leader<=0.20m từ goal gốc. Dùng
  camera processed frames và cổng safety hiện có; chỉ đánh dấu done sau
  completed; ngắt bởi người/stale/clearance thì retry sau cooldown. Mỗi
  goal mới reset done. Không cho search tự động thay thế full goal scan.
- Full sweep vẫn feedback theo yaw từng60deg, điểm cuối thêm0.15rad để
  bù tolerance0.12rad, tránh báo đủ360 khi thiếu góc. Qua MPC; followers
  giữ anchor nhưng có quyền né người. Camera/observation phải bật, không
  thể nhận diện nếu profile LiDAR-only. Không xác nhận vùng chỉ vì quay.
- File: dstar_mpc_controller.py, social_observation.py; test_goal_scan_rotation.py
  (đứng yên không hoàn thành, qua wrap đủ vòng) và test_escape_and_observation.py
  (refuge chưa tới, mất fit ngắn). README thêm hành vi mới. Không sửa
  social_costmap/color_attention, TTL hay gate vùng TV.
- Kiểm thực sự: AST4file, git diff --check. Chưa chạy pytest/build/Gazebo;
  không khẳng định hết va chạm NK092. Lệnh test/chạy giao người dùng.

### NK-094 — 02/11/2026 — Đọc bản mới để giải thích mất vùng TV

Yêu cầu audit, không sửa perception. Đã đối chiếu transitions và dữ liệu
camera/coordinator quanh74–82s với TTL và stamp trong nguồn; lưu evidence
`docs/evidence/2026-11-02/nk094_tv_region_expiry/`. Phân biệt phù hợp expiry
với xác nhận gate xóa, không quy mọi lần chớp tắt cho TTL. Không test/build/
Gazebo/push. Backup nguồn/assets/docs trước cập nhật:
`backups/20261102_184257_206365_nk094_tv_region_expiry_audit`, script kiểm
archive/SHA nguồn/manifest thành công; kiểm SHA archive lại trước thay bản
cuối NK093, giữ hai bản đầu/cuối. Kiểm diff tài liệu.

### NK-095 — 02/11/2026 — Giữ bản né chưa có contact trước sửa goal

Yêu cầu: backup trạng thái vừa đạt trong một lượt, đưa lên GitHub rồi mới
sửa trở về goal. Tạo snapshot nguồn/assets/config/docs có manifest và kiểm
SHA nguồn/archive thành công trước thay đổi. Bằng chứng và giới hạn của
lượt130.801s lưu docs/evidence/2026-11-02/nk095_contact_free_checkpoint/.
Không đổi thuật toán trong checkpoint; push theo yêu cầu hiện tại, không
kèm build/install/log/recordings/backups. Không chạy lại mô phỏng/test.
