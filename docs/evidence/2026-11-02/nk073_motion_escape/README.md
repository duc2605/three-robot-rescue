# NK-073 — motion consensus, lựa lối né và dự báo xe đang phanh

Nguồn phát triển từ NK-071, sửa các lỗi có bằng chứng NK-072. Giữ goal gốc,
LiDAR2m/10Hz, camera không tham gia né. Không đổi timeline người/collision
mesh/map hoặc wheel physics để cho test qua. Không dùng ground truth người
cho controller; root pose người chỉ dùng để đánh giá bản ghi.

## Thay đổi đã triển khai

- **Motion consensus:** giữ local geometry nhưng không ép local velocity
  thắng hai nguồn khác đồng thuận. Mỗi observer tối đa1 vote trong nhóm
  gần.45m, tuổi≤.35s; đồng thuận khi chênh velocity≤.20m/s. Khi sửa local
  bất đồng>.20m/s, thêm.04m reserve. Không gán identity người.
- **Temporal uncertainty:**2 displacement gần nhất nhất quán cho phép
  phản ứng sớm sau rẽ; không dùng một jump đơn lẻ để đổi hướng. LiDAR
  track vừa có speed≥.15m/s rồi chậm<.12m/s giữ thêm radius theo speed
  đã thấy, tối đa.4m/2s. Đây là reserve dự báo, không body size vật lý.
- **Map-supported motion:** fit centre gần occupied physical map<.18m
  không đủ bằng chứng để dự báo bề mặt map đang di chuyển. Không tạo
  motion observation từ đó; giữ raw local rays làm static hard obstacle.
  Còn hạn chế khi vật thật đi rất sát map hoặc map sai.
- **Lựa lối né:** flow xét TTC và speed; điểm bên theo pháp tuyến flow.
  Chấm connector đã kiểm theo khoảng ngang/heading, có preference giữ
  heading1.25s và cho đổi khi không an toàn. Thử cả cruise và giảm tốc ở
  nơi trú; không ép rollout đi qua điểm trú rồi mới đánh giá collision.
- **Search warm start:** mô phỏng/kiểm lại heading đã chọn ở tick trước
  đầu tiên, để không bị budget loại muộn một hướng đang né được. Dữ liệu
  map/ray/moving/peer/acceleration/freshness đều kiểm mới, không replay
  cached command. Có test map vừa chặn phải bỏ hướng cũ.
- **Fixed refuge:** giữ điểm trú trong map qua nhiều tick, tránh target
  bị đặt lại cách xe.72m mỗi tick. Điểm trú phải qua holding-safe; cruise
  chỉ được phép nếu toàn horizon đã qua checks, không ép dừng ở nơi cuối
  horizon chưa thể chờ. Cruise chưa có terminal-safe không được latch làm
  nơi trú; ưu tiên terminal-safe có penalty2 cho phương án chưa dừng được.
  Khi đã ra khỏi corridor, chờ flow đang tiến lại gần đi qua trong lease,
  vẫn cho risk mới preempt. Global goal/reference không bị sửa.
- **Recovery floor:** khi đã overlap buffer, ngoài việc tốt hơn holding
  còn giữ khoảng cách tâm dự báo≥min(khoảng cách ban đầu,
  robot_radius+min(obstacle.radius,.30)+.03). Đây là floor kỹ thuật dựa
  kích thước mô hình đang xét, không đo physical body size tổng quát.
  Đang ở quá sát không chứng minh có lối tránh contact.
- **Braking/peer:** pose capture-time đo world velocity robot; stop vẫn
  Twist0 nhưng prediction có coast.3s/deceleration.4m/s². Kiểm peer cả
  advertised path và envelope theo vận tốc đo. Đây là reserve kỹ thuật,
  chưa calibrate hoặc sửa nguồn vật lý làm xe trôi sau command0.
- **Chẩn đoán:** thêm measured_robot_velocities và selected_escape_goal/
  selected_escape_stops/heading/terminal_safe. Chỉ đọc các trường selected như quyết
  định mới tại reason checked_escape_command; A* proposal ghi riêng.

Nguồn chính: `moving_obstacles.py`, `local_escape.py`, `scan_pose_history.py`,
`robot_motion.py`, `dstar_mpc_controller.py`, wrapper hash. Camera tracker
không bật pause reserve mặc định. Không ghi dữ liệu nếu chạy thường.

## Kiểm chứng

`regression.log`:234 test qua,2 warning SciPy;3 ament lint file không chạy.
`measured_regressions.log`:17 test mới qua. `defaults.json`/`defaults.log`:
ROS constructors3xe domain219 xác nhận2m, không camera subscription, đủ3
scan sources, LiDAR trackers bật pause reserve; không spin/publish command.
`build.log` lưu build2package. Các test kinematic không là chứng nhận
collision-free trong Gazebo.

`validation_summary.json` được tạo bằng `summarize.py` sau lượt kiểm chốt:
đọc mọi contact ngoài ground_plane và trajectories, giữ kết quả xấu của
prototype. `prototype_source_provenance.json` xác nhận source hashes của
5 prototype khớp checkpoint riêng, không nhầm source đang chạy với file
đã sửa sau đó. Pha01/02/03/04/05 bị dừng sớm vì đã thấy lỗi cần sửa, không là
lượt đạt250s hoặc benchmark lặp. Pha06 dùng source sau fixed refuge và terminal/cruise split.

Goal test(1.03553379,−1.97902071) được gửi sau khi đủ input và sim≥8.69s;
server-only/rvizfalse/cameraoff, DDS UDP async/localhost0, domain riêng
55–60/partition theo từng trial. So với bản ghi GUI người dùng còn khác
điều kiện, không dùng số contact/RTF để tính phần trăm cải thiện.

Script `validate_live.py` chỉ dừng launch tree hoặc orphan Gazebo có đúng
domain/partition test, kiểm PID birth. SIGINT pha01 lộ lỗi shutdown lặp;
đã dừng đúng process còn lại và sửa finally để vẫn cleanup. Không dừng
phiên người dùng hoặc dùng pkill chung. Runtime và snapshot nguồn vẫn giữ.

## Tái kiểm

Từ root repository, chạy test:

```bash
source /opt/ros/humble/setup.bash
PYTHONPATH="$PWD/social_navigation_planner:$PYTHONPATH" /usr/bin/python3 -m pytest \
  scripts/tests social_navigation_sim/test social_navigation_planner/test \
  --ignore=social_navigation_planner/test/test_copyright.py \
  --ignore=social_navigation_planner/test/test_flake8.py \
  --ignore=social_navigation_planner/test/test_pep257.py -q -p no:cacheprovider
```

Chạy GUI với thư mục ghi mới:

```bash
bash scripts/run_dynamic.sh --diagnose-stop recordings/lidar_2m_02
python3 scripts/view_replay.py --session recordings/lidar_2m_02
```

Chạy thường chỉ `bash scripts/run_dynamic.sh`, không tự recording. Không
push GitHub. Script validation có assertion không ghi đè thư mục thử cũ;
đổi trial/domain/partition đồng bộ nếu chủ động kiểm lần mới. Script
summarize chỉ đọc record và viết minh chứng, không publish ROS.

Probe drive55s wall ở pha05 bị giới hạn bởi simulation slowdown: chỉ thu
pose107.099–107.299s, không có mẫu động đủ so command/wheel/pose. Giữ raw
`drive_probe.json` và script read-only, không kết luận đã tìm/sửa root cause
actuator hoặc quy mọi RTF cho riêng solver. Log có contact với chair và
viewer trong giai đoạn này; đây là quan sát đồng thời, chưa benchmark.

## Kết quả lượt chốt — chưa đạt hết contact

Pha06:0.001–247.951s sim (wall cap720s, không đạt mốc250s dự kiến).
Không ghi non-ground contact trước193.260s; robot2 không có contact ngoài
nền trong toàn lượt, nhưng robot1/leader vẫn có contact:6 cặp/8 đợt.
Vì vậy KHÔNG coi yêu cầu cả3 né ổn định đã đạt, không kết luận tỷ lệ thành
công hoặc mức cải thiện từ một lượt. Build2package và234 test qua vẫn
không thay thế kết quả physics này.

- leader↔TV viewer B:193.260–193.288,193.798–193.841,194.156–194.204.
- robot1↔TV returning:202.000–203.311.
- leader↔TV returning:208.159–211.035.
- leader↔TV viewer A:213.459–221.358.
- leader↔TV walking:229.159–232.098.
- robot1↔TV walking:245.868–247.951, còn contact tại cuối frame snapshot.

`acceptance.json` ghi đúng trạng thái không đạt. `final_source_matches.json`
xác nhận6 module runtime khớp nguồn hiện tại. Root XY travel lấy mẫu:
robot1≈32.19m,robot2≈18.60m,leader≈18.44m; không phải chỉ đứng im nhưng
cũng không chứng minh đường tối ưu. End goal distances≈1.09/1.95/2.14m,
chưa xác nhận về lại goal/đội hình sau né cuối.

Contact viewer B có collision body_envelope box(.88,.62,1.40), offset(.18,0,.70)
trong model. Map generator chủ động loại people/scripted paths; không
được chữa bằng chép pose người từ scene/recorder vào navigation map.
Cần capture raw scans tại capture pose, wheel velocity, command và robot
pose trước các mốc193/202/208 để phân biệt hình học nhìn bằng GPU-LiDAR
với envelope physics và lỗi dự báo/response thực. Hiện chưa có raw rays
để chứng minh nguyên nhân duy nhất. Không sửa physics hoặc actuator bằng
suy đoán, không coi giảm contact đầu lượt là đã sửa toàn hệ.

Tất cả test launch thuộc các domain riêng đã dừng. Không mở/dừng phiên
người dùng và không đẩy GitHub. Nguồn hiện tại là bản cải tiến đang cần
kiểm tiếp, không phải baseline đã chứng minh ổn định.
