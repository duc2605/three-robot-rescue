# Ghi và phát lại vị trí Gazebo nhìn từ trên xuống

Bộ ghi đánh giá đọc pose thực từ ECM Gazebo sau cập nhật,20Hz thời gian
mô phỏng. Bộ ghi còn yêu cầu ContactSensorData trên collision có sẵn của cả3 xe
để lấy contact physics từng bước mô phỏng. Nó không lấy lịch di chuyển
người để thay pose đo, không cấp
nhãn/pose người thật vào perception, D* hoặc MPC. Phần điều hướng baseline
khôi phục giữ nguyên; hai world dùng plugin recorder, không đổi hình học hoặc lệnh điều khiển.

## Chạy mô phỏng luôn kèm ghi dữ liệu — NK-088

Từ NK-088, mỗi lệnh wrapper động/tĩnh/paper tự ghi vào thư mục mới;
README đã ghép bước ghi vào từng khối chạy. Quyết định này thay lựa chọn
opt-in trước đó, không khôi phục observer NK-061 hoặc `log/sessions/`.
Ví dụ dưới đây đặt tên thủ công; bỏ flag thì wrapper tự tạo tên theo giờ.

Bản hiện tại đã build. Khi lấy nguồn mới trên máy khác, build như README.
Terminal1 tại root:

```bash
cd ~/three-robot-rescue
bash scripts/run_dynamic.sh --record-replay recordings/thu_ne_01
```

Từ NK-071 profile động mặc định tắt camera để thử né LiDAR2m. Chọn goal trong RViz như trước. Thư mục
`recordings/thu_ne_01/` lưu bản ghi đánh giá:

- `scene.json`: tên các model/actor, hình học primitive từ SDF, bounds bản đồ
  và envelope robot. Dữ liệu này được cố định theo phiên.
- `perception.jsonl`/`perception_status.json`: ảnh camera JPEG và snapshot
  vùng xã hội khi có publisher (NK-079); stream riêng có giới hạn.
- `navigation.jsonl`: scan LiDAR thực và đầu ra A*/MPC của cả3 xe (NK-074).
- `navigation_status.json`: dung lượng, số mẫu rơi, lỗi IO/giới hạn và trạng thái
  writer; được ghi khi writer kết thúc hoặc dừng vì lỗi/đạt giới hạn.
- `world_frames.jsonl`: pose thực từng model/actor cấp world, tên/entityID,
  x/y/z/roll/pitch/yaw, thời gian sim, epoch và trạng thái pause; thêm
  contacts gồm tên model/collision, first_t/last_t, tọa độ tiếp xúc, số
  bước có contact và độ xuyên nếu engine cung cấp (thiếu thì null).

Plugin chỉ mở file khi có `SOCIAL_REPLAY_DIRECTORY`, do wrapper đặt trước
khi chạy launch. Chạy trực tiếp `ros2 launch` không qua wrapper sẽ không
có bản ghi pose này. Không cần recorder publish thêm topic ground truth.
Không ghi từng khớp hoặc biến dạng skeleton/mesh; model/actor là đơn vị.
Các model ẩn ởz≈−50 vẫn nằm trong dữ liệu và được ẩn trong hình.

## Mở trình xem đang cập nhật

Chờ terminal1 tạo phiên rồi mở terminal2:

```bash
cd ~/three-robot-rescue
python3 scripts/view_replay.py --session recordings/thu_ne_01
```

Trình duyệt mở tại `http://127.0.0.1:8765`. Server chỉ bind localhost.
Nếu trình duyệt không tự mở, chép URL đó vào trình duyệt. Viewer mở thư mục --session ban đầu; từ NK-077 có thể chuyển
bản ghi ngay trên giao diện, không cần khởi động lại để đổi phiên.
Nếu port đã dùng, thêm `--port 8766`.

- Bỏ “Bám phiên đang ghi” để tua lịch sử. Chạy/dừng, bước từng mẫu và tốc độ
  .25/.5/1/2/4 dựa trên thời gian mô phỏng.
- Vệt quỹ đạo, vị trí đồ vật, tên người/xe, heading và chọn một đối tượng.
- Mũi tên xanh: hướng model/đầu xe; mũi tên đỏ: vận tốc world đo từ các mẫu
  trước khoảng .2s. Nhãn tiến/lùi/trái/phải theo thân robot, không theo góc
  nhìn Gazebo. Proxy người dạng cylinder dùng yaw actor đã hiệu chỉnh nếu có.
- Viền đỏ: Gazebo physics ghi nhận contact có ít nhất một xe trong khoảng
  thời gian mẫu; bảng ghi cặp va chạm và thời điểm. Contact với ground_plane
  được lưu nhưng ẩn khỏi cảnh báo. Viền cam: envelope chồng lấn ước tính,
  chưa phải xác nhận contact.
- “Lưu ảnh PNG”: xuất canvas có timestamp, epoch, tên và các mũi tên để
  gửi AI. Từ NK-079 PNG kèm ảnh camera đang xem và timestamp nếu có;
  lớp vùng lấy đầu ra publisher, không phải nhãn kịch bản.

## Dừng và mở lại bản ghi

Ctrl+C ở terminal1 dừng mô phỏng; terminal2 chỉ phục vụ xem.
Ctrl+C ở terminal2 chỉ đóng viewer, không điều khiển robot.

Đọc một phiên cũ:

```bash
python3 scripts/view_replay.py --session recordings/TEN_BAN_GHI
```

Xuất một file HTML độc lập chứa cả geometry và toàn bộ frame đã ghi:

```bash
python3 scripts/view_replay.py --session recordings/thu_ne_01 --export recordings/thu_ne_01/replay.html
```

Mở `recordings/thu_ne_01/replay.html` bằng trình duyệt, không cần server/network.
Có thể gửi chính file HTML đó. Hoặc dùng nút chọn file trong viewer để mở
`scene.json`, `world_frames.jsonl`, `navigation.jsonl` và nếu có
`navigation_status.json`, `perception.jsonl`, `perception_status.json` cùng phiên. Khi còn đang ghi, file export
chỉ chứa phần đã ghi đến lúc xuất; xuất lại sau khi dừng để có đủ dữ liệu.
File HTML có thể lớn với phiên dài. Dòng JSONL cuối đang ghi dở được bỏ qua.

Phiên `20261101_192255_199210` cũ đã xóa theo NK-064; trước đó không có pose ground truth đầy đủ nên
không thể được phát lại chính xác bằng tính năng này. Không tự điền đường
người theo kịch bản để biến log cũ thành dữ liệu đo.

## Xác nhận tiếp xúc vật lý và giới hạn

Từ NK-065, viền đỏ lấy **ContactSensorData do hệ Physics Gazebo điền**,
không suy từ khoảng cách. Yêu cầu contact trên mọi collision của robot1/2/3
khi đang ghi replay, kể cả bánh/cột nếu URDF có collision đó. Không thêm
hình học, đổi mask hoặc điều chỉnh phản ứng vật lý. Ghi tên collision thật,
điểm tiếp xúc đầu tiên của cặp và khoảng thời gian first_t–last_t trong
mỗi cửa sổ frame. Một cặp có thể xuất hiện nhiều frame khi còn tiếp xúc.
Engine có thể không cung cấp depth; null là thiếu số đo, không phải 0mm.

Contacts được gom **mỗi bước physics**, trước khi giảm pose xuống20Hz;
vì vậy contact engine đã báo giữa hai frame được giữ tới frame sau.
Cảnh báo ở frame là contact trong khoảng vừa ghi, không nhất thiết còn
chạm ở đúng pose cuối khoảng. Không suy ra lực va chạm từ max_depth.

Người trong mô phỏng có khối proxy collision; xác nhận là xe tiếp xúc
**khối collision người trong Gazebo**, không phải mesh da/quần áo hay cơ
thể thật. Nếu actor không có collision, collision bị mask, hoặc engine bỏ
sót do đi xuyên quá nhanh thì bộ đọc không thể tự tạo contact. Không ghi
nhận contact chưa chứng minh tuyệt đối không chạm. Bản ghi NK-063 cũ thiếu
trường contacts được hiển thị “chưa có dữ liệu”, không coi là hết va chạm.

Viền cam vẫn dùng envelope tròn robot radius.15m, z0..0.2m và primitive
SDF chiếu2D; không mô tả đầy đủ mast/bánh/mesh và root roll/pitch. Đây chỉ
là cảnh báo hình học riêng. Khi không bật --record-replay, không bật thu
contacts hoặc tạo file. Chi phí thu contact/ghi file chưa benchmark RTF.

## Kiểm chứng đã làm

- Build plugin và5 test Python metadata/projection/export/partial-line qua.
- Hồi quy toàn bộ164 test qua (2 warning SciPy,3 lint file không chạy).
- World headless riêng:50 model/actor của scene được ghi. Fixture thêm3
  cylinder robot scripted:53 đối tượng,90 frame, robot3 và patrol thay vị
  trí trong ECM. Đây không phải robot URDF/MPC hoặc kiểm né người.
- HTTP tăng dần không lặp frame, reset offset qua. Firefox kiểm overlap/
  disjoint chiều cao, nhãn phải/trái theo thân và bước/tua/chạy, có screenshot.
- Đối chiếu4 module điều hướng và geometry hai world với backup: không đổi,
  ngoài plugin recorder. Giữ mô phỏng chính tắt trong tác vụ tạo tính năng.

Bằng chứng: `docs/evidence/2026-11-01/ground_truth_replay/`.
Trước mỗi cải tiến tiếp theo phải tạo backup theo AGENTS.md.

Kiểm chứng contact NK-065: fixture physics riêng2500 bước,50 frame; robot3
rơi chạm khối person_contact, robot1 chạm nền, robot2 cách khối10mm không
có contact. Có tên collision/điểm tiếp xúc, depth thiếu giữ null. Firefox
kiểm cảnh báo physics, trạng thái không ghi nhận và bản ghi cũ qua.
Đây là primitive fixture, chưa kiểm lại toàn kịch bản3 URDF/MPC/người đi.
Bằng chứng: `docs/evidence/2026-11-01/physical_contacts/`.

Cơ chế yêu cầu dữ liệu dựa trên [Physics::UpdateCollisions của Gazebo6](https://github.com/gazebosim/gz-sim/blob/ign-gazebo6/src/systems/physics/Physics.cc):
Physics chỉ thu contact khi có component ContactSensorData và engine hỗ trợ.

## Khi cần biết vì sao xe đứng yên

Dùng `bash scripts/run_dynamic.sh --diagnose-stop recordings/chan_doan_01`
thay lệnh --record-replay; nó ghi thêm các cửa sổ quyết định trực tiếp trong
controller/coordinator. Xem [chẩn đoán dừng xe](CHAN_DOAN_DUNG_XE.md).
Từ NK-088, wrapper mặc định dùng chẩn đoán này cho mỗi lượt chạy.

## Dấu goal đã chọn — NK-068

RViz có điểm tím và nhãn GOAL tại tọa độ mục tiêu. Khi bật --record-replay
hoặc --diagnose-stop, coordinator ghi mỗi lần nhận goal map hợp lệ vào
`goals.jsonl` (tọa độ, thời điểm sim, epoch, số thứ tự). Đây là mục tiêu
được chọn, không chứng minh tìm được đường tới hoặc đã tới đích.

Viewer vẽ vòng/chữ thập tím, số goal và thời điểm chọn. Khi tua chỉ hiện
mục tiêu đã chọn trước frame đang xem, cập nhật khi đổi goal, tách epoch
khi reset clock. HTML export và PNG giữ dấu goal. Nếu mở dữ liệu bằng nút
chọn file, chọn thêm goals.jsonl cùng scene.json/world_frames.jsonl.
Bản ghi cũ thiếu goals.jsonl không được tự điền goal giả.

Từ NK-088, chạy qua wrapper có ghi file goal; chạy thẳng ROS launch
ngoài wrapper không được đảm bảo ghi. Phiên process
đang chạy trước khi cập nhật cần chạy phiên mới để nạp mã ghi goal; tác vụ
NK-068 không tự dừng hoặc restart phiên người dùng.


## Vùng quét LiDAR và điểm né — NK-074

Cần **ghi phiên mới** bằng một trong hai tùy chọn --record-replay hoặc
--diagnose-stop. Từ NK-088 wrapper mặc định tạo recorder. Bản ghi cũ thiếu
navigation.jsonl vẫn mở được, nhưng không thể bổ sung scan/điểm né đã mất.

Trong bảng “LiDAR và điểm né”, chọn cả3 xe hoặc từng xe:

- Vòng đứt nét là tầm tối đa đọc từ scan, hiện mặc định2m. Vòng không
  chứng minh nhìn xuyên đồ vật. Màu ứng với robot; dữ liệu cũ đổi xám.
- Chấm là điểm trả về hữu hạn thực tế; “Tia có điểm” nối tới các chấm.
  Không vẽ inf/NaN hoặc tia đạt max range thành vật cản.
- “Trong bán kính” đối chiếu hình học người Gazebo với vùng quét tại lúc
  chụp scan. “Vào giữa X–Y s” là khoảng giữa mẫu cuối ở ngoài và mẫu đầu
  ở trong; thiếu mẫu trước hoặc đứt dữ liệu thì chỉ báo “trong từ mẫu”.
- “Tia gần người (ước lượng)” đếm điểm scan nằm gần khối người Gazebo,
  có kiểm chiều cao. Đây là đối chiếu phục vụ đánh giá, không phải nhận
  dạng người từ LiDAR hoặc xác nhận controller đã xử lý track đó.
- ◇ và đường đứt là đề xuất A* thực được publish. × là điểm MPC thực
  chọn khi phát lệnh né; chúng có thể khác nhau. Nhãn trái/phải/trước/sau
  theo hướng thân xe tại lúc tạo kế hoạch. Điểm không hiện không đồng
  nghĩa xe không né: có thể không có kế hoạch mới hoặc dữ liệu đã quá tuổi.

Scan ghi cả stamp capture và thời điểm observer nhận; bảng hiện cả hai
cùng tuổi dữ liệu. Điểm trả về được chiếu bằng pose xe lúc capture và TF
sensor thực, không dùng pose xe lúc nhận muộn. Thiếu TF/pose thì không vẽ
đám điểm giả. Scan quá .35s sim ẩn điểm/hit người; kế hoạch A* quá .65s,
quyết định MPC quá .35s được ẩn. Thông báo xóa kế hoạch và reset epoch
không giữ điểm cũ. Hình PNG/HTML xuất giữ lớp phủ và timestamp này.

Node riêng replay_sensor_recorder.py chỉ subscribe /robotN/scan,
/robotN/escape_path, /robotN/escape_decision và /tf_static; không phát
lệnh xe hoặc cấp ground truth vào navigation. Queue ghi nền tối đa1024,
stream128MiB; quá tải có thể rơi mẫu, đạt giới hạn ngừng ghi stream này.
Từ NK-079 ảnh camera/social ghi riêng ở perception.jsonl. Chi phí IO/DDS/hiển thị chưa benchmark RTF; không
coi lớp phủ này là bản sửa va chạm. Epoch dựa trên clock observer, mất
đồng bộ/thiếu mẫu vẫn cần kiểm ở phiên thật.

Minh chứng: [kiểm thử NK-074](evidence/2026-11-02/replay_lidar_astar/README.md).
ROS kiểm soát và Firefox đã kiểm cả3 xe, che khuất, capture khác receipt,
A* khác MPC, xóa/reset, HTTP tăng dần, export và dữ liệu cũ. Pose fixture
là tổng hợp; chưa chạy Gazebo mới để kiểm tính năng trong toàn kịch bản.


## Mở các bản ghi cũ trên máy — NK-077

Thanh **Bản ghi trên máy** phía trên bản đồ có:

- Danh sách thư mục bản ghi trong recordings/; chọn tên rồi bấm **Mở bản
  ghi**. Mỗi tab có lựa chọn riêng, dữ liệu được tải lại từ đầu cùng phiên.
- **Làm mới danh sách** để thấy các thư mục vừa được tạo. Chỉ liệt kê thư
  mục có scene.json và world_frames.jsonl; không phục hồi dữ liệu đã xóa.
- **Mở thư mục khác…** để chọn một thư mục bản ghi ở vị trí khác trên máy.
  Chọn đúng thư mục chứa scene.json/world_frames.jsonl, không chọn thư
  mục cha chứa nhiều phiên. Trình duyệt có thể hỏi xác nhận quyền đọc
  thư mục. File được đọc tại trình duyệt, không upload lên server.

Khi chọn thư mục trực tiếp, viewer dùng snapshot file lúc mở và dừng poll
server. Muốn xem dữ liệu cập nhật, mở lại thư mục hoặc chọn bản ghi từ
server. Nút thư mục cũng dùng được trong HTML export độc lập; danh sách
recordings/ chỉ có khi chạy server localhost.

Sau cập nhật mã này, nếu viewer server cũ đang chạy, Ctrl+C **terminal
viewer** rồi chạy lại cùng lệnh view_replay.py và tải lại trang. Không cần
khởi động lại mô phỏng. Các lần sau đổi phiên bằng nút ngay trên giao diện.


## Ảnh camera leader và vùng xã hội — NK-079

Bảng camera ở đầu cột phải chọn Tự chọn/Ảnh nhận diện/Camera gốc. Ảnh
và vùng hiển thị theo thời gian đang tua, chỉ lấy dữ liệu đã nhận trước
mẫu hiện tại cùng epoch. Timestamp capture/receipt/tuổi được ghi rõ.
Ảnh cũ vẫn được xem nhưng có nhãn; thiếu ảnh không thay bằng ảnh tương
lai. Vùng từ publisher /social_navigation/markers có checkbox bật/tắt,
hiển thị màu/nhãn và timestamp; quá2s sim ẩn vùng, snapshot rỗng xóa ngay.
Đây là đường viền xã hội đã publish, không phải từng ô keepout đã carve
lối ra hoặc xác nhận xe tuân thủ vùng. PNG gồm cả map/vùng và camera nếu
ảnh đã tải; HTML export và chọn folder giữ dữ liệu này.

NK-078 đã đính kèm lại6 ảnh thật và marker/status gốc, nên xem được ngay
ở recordings/nk078_social_camera_120s_once. Ảnh cũ chỉ rời rạc mỗi~20s,
không có capture timestamp còn lưu: giao diện báo rõ, không phải video.
Xem viewing_tv khoảng14–18s hoặc ảnh gần contact ở84.8s.

Các lượt ghi mới qua wrapper thu raw/detection JPEG tối đa2Hz mỗi nguồn theo
sim và wall, encode thread riêng/max cạnh640/quality75, queue32/cap256MiB.
perception_status.json ghi drop/error/bytes khi kết thúc hoặc lỗi writer.
Chỉ có ảnh/region nếu camera/detector/social đang bật; ghi replay không
tự bật nhận diện. Các file stop vẫn không chứa pixel camera. Từ NK-088 wrapper
ghi mỗi lượt. Chi phí ghi/encode chưa benchmark, không coi là sửa thuật toán.
Sau mỗi lượt thử sẽ cung cấp lệnh mở đúng runtime theo yêu cầu người dùng.
