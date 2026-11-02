# Né vật động bằng LiDAR 2 m — NK-071, cập nhật NK-073

Mục tiêu hiện tại là tránh vật động cho cả3 xe, không cần phân loại người.
Môi trường động mặc định tắt camera/perception/quan sát và lớp social từ
camera để cô lập nhánh né LiDAR. Hai môi trường và hai backend paper vẫn
được giữ; tầm cảm biến của robot dùng chung nay là2m. Các kết quả paper cũ
không được coi là benchmark mới ở cấu hình2m.

## Chạy

```bash
cd ~/three-robot-rescue
bash scripts/run_dynamic.sh
```

Để ghi dữ liệu kiểm tra (thư mục mới):

```bash
bash scripts/run_dynamic.sh --diagnose-stop recordings/lidar_2m_01
```

Terminal khác:

```bash
python3 scripts/view_replay.py --session recordings/lidar_2m_01
```

Chọn goal RViz như trước. Ctrl+C dừng lượt tự chạy. Không tự ghi khi chạy
thường. `gazebo_gui:=false rviz:=false` cho chạy server riêng nếu cần thử
không GUI; mặc định vẫn mở Gazebo/RViz. Camera ảnh có thể bật lại bằng
`leader_camera:=true` nhưng controller vẫn mặc định không dùng camera để
né; các detector/social layer cần bật riêng theo cấu hình nghiên cứu.

## Cách ba xe xử lý

- LiDAR vật lý quét ngang360°, tối đa2m,10Hz sim,240 tia. Leader không camera
  dùng LiDAR2D như hai follower; projector khi bật camera cũng giới hạn2m.
- Mỗi controller dùng scan của chính xe và hai xe đồng đội, đổi về map và
  loại ray map/xe đã biết. Có kiểm state/scan freshness và coverage scan
  của chính xe trước khi cho phép né. Không dùng pose thật của người từ
  recorder để tạo track hoặc điều khiển.
- Scan được chiếu bằng pose robot tại capture stamp (nội suy yaw qua±π),
  không dùng pose lúc callback chạy. Nếu pose đến muộn, giữ tối đa4 scan
  mỗi xe, xử lý theo thứ tự capture; dữ liệu quá tuổi không được làm mới
  freshness. Throttle theo capture stamp, tránh mất frame do jitter receipt.
- Gom nhóm điểm và theo dõi nhiều lần để ước lượng vận tốc vật động.
  Ưu tiên geometry từ LiDAR chính xe; scan đồng đội bổ sung đối tượng
  bị che. NK-073 thêm consensus vận tốc: mỗi nguồn một vote, chỉ nhận
  vote≤.35s tuổi. Hai nguồn độc lập có velocity cách nhau≤.20m/s được
  dùng để sửa local bất đồng>.20m/s, thêm4cm uncertainty. Một nguồn có
  nhiều track trùng không tự thành hai vote. Đây không phải gán identity. Khi
  cung LiDAR khớp đường tròn, ước lượng tâm/bán kính cung thay vì đặt vòng
  lớn trên mặt trước; cung không khớp dùng envelope bảo thủ. Không suy ra
  danh tính hay hành vi của người từ LiDAR.
- Track có vận tốc hợp lệ được giữ hướng cuối tối đa.4s khi ước lượng
  gián đoạn. Vật đang tiến lại gần trong envelope nearby kích hoạt né cả
  khi đường thẳng dự đoán vừa lệch xe, để dự phòng góc rẽ. Khi risk vừa mất,
  giữ dừng1.25s trước khi trả quyền bám goal; risk mới vẫn được xử lý ngay.
  Đây là heuristic có giới hạn, không dự đoán được ý định người.
- Dự báo TTC, ưu tiên ứng viên ngang quỹ đạo vật động, kiểm cả hướng khác
  khi bên cạnh bị chắn. Từ NK-073 chọn hướng chủ đạo xét TTC và tốc độ,
  tránh noise chậm TTC0 lấn vật đang tiến tới. Điểm hai bên đặt theo pháp
  tuyến hướng vật động; connector đã kiểm được chấm điểm ngang corridor
  và giữ hướng, thay vì lấy điểm hợp lệ đầu tiên. Khi cần vẫn dùng A*
  không gian/thời gian với số mở rộng/thời gian giới hạn. MPC vẫn kiểm toàn horizon,
  gia tốc, physical map, ray gần, vật động và dự báo hai xe còn lại.
- Nếu đã ở trong buffer dự báo, xét bước đi giảm nguy cơ so với đứng yên
  và không đi về/cắt qua tâm track; tường và peer vẫn phải qua kiểm tra.
  Đây là recovery có rủi ro, không chứng minh có đường an toàn từ tình
  trạng đã quá sát. Khi không xác minh được hướng, xe vẫn dừng.
- Trong lúc né, coordinator giữ route và phát reference giữ tại vị trí
  đo hiện tại để các controller không thiếu reference. Xe có nguy cơ
  tự ưu tiên né, sau đó về bám đội hình/replan từ vị trí đã đo. NK-073
  thêm phạt đảo heading trong1.25s, cho bỏ cam kết khi hướng vật đổi>60°
  hoặc không còn candidate an toàn. Đây là preference, không khóa cứng
  một waypoint khi dữ liệu mới cho thấy nguy hiểm.
- Normal MPC thử một rollout bám reference đầy đủ đã kiểm trước khi beam
  search. Nếu rollout không hợp lệ mới tìm trong beam. Cách này không tối
  ưu cost trên toàn bộ cây trong mọi tick. Không dùng quỹ đạo dở hoặc lệnh
  cũ khi hết budget.

## Giới hạn và freshness

Né giới hạn khoảng60ms wall, riêng A* tối đa160 expansion và khoảng15ms
trong budget chung. Beam normal giới hạn khoảng100ms. Đây là deadline hợp
tác kiểm trước từng bước, không thời gian cứng của hệ điều hành; một lần
kiểm hình học/scheduler có thể vượt. Chỉ dùng candidate hoàn chỉnh và kiểm
lại state/scan trước phát lệnh. Guard ghi timestamp tại lúc phát lệnh.

Capture-age theo sim vẫn≤.3s cho né; wall liveness thích nghi tốc độ sim
trong khoảng2–12s. Clock không tiến trong2s wall khôi phục giới hạn2s;
sensor im lặng/capture quá tuổi/scan thiếu coverage vẫn chặn chuyển động.
Không đơn giản nới timestamp để cho phép dùng dữ liệu cũ vô hạn.

LiDAR track padding cơ bản2cm, fit cung có padding hình học3cm và tăng
uncertainty theo tuổi track. Đây là thông số kỹ thuật của mô phỏng, chưa
calibrate cho cảm biến thật. Không cam kết tránh được vật chạy quá nhanh,
phía bị che, vật không có collision, hành lang không đủ chỗ hoặc mọi mật
độ người/đội hình. Các test và lượt Gazebo cụ thể ghi trong nhật ký/báo cáo.

## Minh chứng và hạn chế kiểm thử

Lưu kết quả từng lượt tại
[thư mục minh chứng](evidence/2026-11-02/lidar_2m_avoidance/).
Lượt09: hai follower không có contact ngoài nền trong90s, leader vẫn
contact patrol83.901–86.051s khi vật đổi hướng. Giữ snapshot riêng trước
sửa góc rẽ; không coi lượt này là cả3 xe né thành công. Lượt thử trước có
các lỗi scan-pose trễ, track trùng và một lỗi biến speed bị ghi đè trong
scoring; đã sửa và thêm test giới hạn tốc độ lệnh/rollout≤.28m/s.

Các ca số học chạy controller thật với scan tia tổng hợp và động học đơn
giản, không thay thế Gazebo. Contact thật lấy từ physics engine của bản
ghi tùy chọn; quỹ đạo root/bao tròn không tự xác nhận tiếp xúc. Không dùng
RTF giữa các lượt khác GUI hoặc DDS để kết luận tăng hiệu năng.

Lượt10 sau sửa guard: không ghi contact ngoài nền của3xe trong90.101s sim;
217 test qua. Có chuyển động thực trong Gazebo, leader gần goal trước
patrol rồi rời goal để né; cuối lượt chưa xác nhận phục hồi đội hình/đến
lại goal. Xem `validation_summary.json`, `turn_checkpoints.json` và ảnh
quỹ đạo trong minh chứng. Test đã dừng; không tự mở phiên GUI cho người
dùng. Chưa có kiểm thử lặp hoặc toàn chu kỳ dài hơn90s.

## Bổ sung vận tốc thực và dự báo phanh — NK-073

Pose history cùng capture stamp dùng để đo velocity world của robot trong
cửa sổ khoảng.15–.35s. Dữ liệu cũ>.3s, thiếu mẫu hoặc nhảy>1.5m/s không
được biến thành vận tốc hợp lệ. Không đo vận tốc người bằng ground truth.

`publish_stop` vẫn gửi Twist0 nhưng prediction dùng chuyển động đo, dự
phòng coast.3s rồi giảm tốc.4m/s². Các kiểm peer trong A*/escape/normal
MPC xét cả prediction nhận và envelope từ vận tốc đo; không coi một peer
vừa báo dừng là đã đứng yên ngay. Diagnostic thêm measured_robot_velocities,
config hash thêm robot_motion. Không tạo recorder nếu chạy thường.

.3s/.4m/s² là reserve kỹ thuật chưa calibrate với drive thật. Đây là sửa
mô hình dự báo/phòng tránh; chưa chứng minh đã sửa nguồn gây robot trôi
sau command0, và không thay physics hoặc wheel controller bằng giả định.
[Kiểm chứng NK-073](evidence/2026-11-02/nk073_motion_escape/).

Rollout né nay thử cả cruise và giảm tốc/dừng tại nơi trú. Điểm dừng dùng
speed giảm theo khoảng cách, có giới hạn gia tốc và kiểm cả endpoint hold;
không bắt xe tiếp tục đi qua một nơi trú đã an toàn. Nếu dừng tại đó vẫn
nằm trong đường vật tới, candidate vẫn bị loại. Diagnostic bổ sung
selected_escape_goal/stops/heading cho lệnh checked_escape_command;
A* proposal vẫn được ghi riêng, thông tin ở reason khác có thể là lần
chọn trước. Bản chỉ-stop từng làm hồi quy4 ca cũ, đã giữ cả2 mode và chạy
lại toàn bộ, không giảm tiêu chuẩn separation để cho test qua.

Map-support gate NK-073: chỉ fit centre có physical-map clearance≥.18m
mới tạo motion observation. Fit centre gần occupied geometry không đủ
bằng chứng để dự báo bề mặt map di chuyển. **Raw local rays vẫn giữ** và
được kiểm như static obstacle, map cũng vẫn kiểm cứng; không đơn giản xóa
vật khỏi nhánh an toàn. Diagnostic filter count thêm
map_supported_motion_clusters. Còn cần thử người đi rất sát tường/map,
map lỗi hoặc hình học bất thường; đây chưa phải nhận dạng vật tĩnh hoàn hảo.

Khi2 displacement gần nhất nhất quán và cho tốc độ≥.12m/s khác long-window
>.15m/s, tracker dùng cửa sổ ngắn để phản ứng ở góc rẽ; một jump không đủ.
LiDAR tracker còn nhớ tốc độ đã thấy≥.15m/s: khi track chậm<.12m/s, thêm
reserve radius tối đa.4m trong2s. Reserve hết hạn và chỉ áp dụng cho track
vừa chuyển động, không coi mọi vật đứng yên là người sắp đi. Đây là bất
định dự báo, không là kích thước/collision mesh đo được. Camera tracker
không bật pause reserve mặc định; bài kiểm thử LiDAR dùng đúng mode mới.

Warm start NK-073: trước hết mô phỏng lại hướng né đã chọn bằng dữ liệu
mới. Đây là ưu tiên thứ tự tìm trong budget60ms, không dùng lại lệnh cũ
hoặc bỏ checks. Map/peer mới chặn phải hủy hướng đó; có test hồi quy cho
trường hợp này. Lệnh đầy đủ để chạy hồi quy và minh chứng chi tiết tại
[kiểm chứng NK-073](evidence/2026-11-02/nk073_motion_escape/README.md).

Refuge được giữ trong tọa độ map qua nhiều tick, không liên tục đặt lại
.72m trước xe. Điểm định dừng phải qua holding-safe. Cruise vẫn kiểm toàn
horizon nhưng có thể chưa có nơi dừng ở cuối horizon (ví dụ phải ra khỏi
đội hình chật trước khi né ngang); phương án này bị phạt2 và không được
latch làm nơi trú. Field selected_escape_terminal_safe phân biệt hai loại.
Không được diễn giải cruise là có chứng minh đứng an toàn mãi ở endpoint.

Khi đã ngoài corridor, refuge wait có thể giữ xe chờ flow đang tiến lại
gần đi qua trong lease; risk mới luôn được xử lý trước hold. Global goal
vẫn giữ. Recovery từ buffer overlap bổ sung floor khoảng cách tâm theo
robot_radius+min(obstacle.radius,.30)+.03, không được giảm dưới khoảng
cách đầu nếu đã sát hơn floor. Đây là ngưỡng kỹ thuật của model, chưa
phải phép đo physical radius mọi vật động, không cứu được mọi trạng thái
đã contact. Hồi quy giữ nguyên separation assert của các ca follower cũ.

Kết quả chốt NK-073:234 test qua nhưng lượt247.951s còn contact sau193.260s
ở robot1/leader; robot2 không có non-ground contact trong lượt. Chưa coi
cả3 né ổn định hoặc đã khôi phục đội hình/goal. Xem acceptance/summary
trong evidence; giữ bản ghi lỗi và backup, không chọn riêng đoạn đầu
không contact để kết luận an toàn tổng quát.
