# Cảnh xã hội động — D* Lite + MPC

Chế độ này giữ nguyên cảnh tĩnh `social_scene:=static`. World/map/config mới
là `social_dynamic`; không ghi đè các asset của cảnh tĩnh.

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=31
ros2 launch social_navigation_sim social_dynamic.launch.py
```

Dừng phiên mô phỏng trước khi đổi cảnh. `motion_enabled:=false` chỉ dừng
robot; người trong kịch bản vẫn chuyển động khi đồng hồ Gazebo chạy. Pause
Gazebo sẽ dừng lịch người. Reset thời gian về 0 khởi động lại lịch.

## Ba tình huống

- `sleeping_person`: nằm trên giường ở phía tây, không di chuyển. Đây là nhãn
  kịch bản. Camera chỉ có thể báo `lying_posture_candidate` hoặc
  `lying_still_candidate`; bất động không chứng minh đang ngủ.
- `tv_viewer_a`: xem TV 12 giây mô phỏng, nâng tư thế trong 2 giây, đổi sang
  mô hình đứng và đi tới bình nước ở tốc độ 0,35 m/s. Dừng 6 giây, quay lại ghế,
  rồi lặp chu kỳ khoảng 106,7 giây. `tv_viewer_b` vẫn ngồi xem TV.
- `patrol_person`: đi vòng các cạnh và xuyên phần giữa bản đồ ở 0,4 m/s;
  chu kỳ khoảng 107,2 giây. Tuyến đã kiểm tra với map đồ đạc.

Chuyển động hiện tại là **kinematic**: mesh người và thân va chạm đi cùng
nhau qua plugin Gazebo, tư thế đổi theo giai đoạn. Chưa có hoạt ảnh chân bước,
tay nâng cốc hoặc động tác ngồi–đứng hoàn chỉnh. Người đi theo lịch, chưa chủ
động nhường robot; thân va chạm không phải mô hình sinh cơ học. Giai đoạn
`drinking_pause_script` biểu diễn dừng uống tại bình nước, không phải kết quả
camera nhận diện động tác uống.

## Robot sử dụng thông tin nào?

Plugin chỉ thay đổi vị trí trong Gazebo. Map tĩnh có ghế, TV, giường và bình
nước, không chứa người hoặc tuyến đi của họ. Camera/LiDAR vẫn là đầu vào
của suy luận xã hội và D* Lite/MPC; không có nhãn hành vi hoặc vị trí tác nhân
ground truth truyền vào bộ điều hướng.

Khi một track camera được đo đang di chuyển, vùng xem TV cũ của track đó bị
thu hồi, kể cả khi nó đã đi quá bán kính ghép vị trí. Vùng riêng của người
còn ngồi vẫn được giữ. Vận tốc người đi lấy từ lịch sử vị trí đo được và tạo
hành lang dự báo ngắn trên map xã hội. Khi mất quan sát, các dự báo có hạn
sử dụng; không dự báo mãi theo lịch kịch bản.

Với người nằm, cần đủ điểm khớp RGB-D tin cậy, thân gần ngang và thấp để tạo
polygon theo bề dài người cùng biên đệm. Nếu bộ nhận diện không thấy người
nằm hoặc thiếu khớp, không có khẳng định đã nhận diện người ngủ. Giường vẫn
ở map vật lý và phần thân thấp vẫn có hình học va chạm/LiDAR.

`/social_scene/people` là marker kịch bản có cập nhật vị trí, không phải kết
quả camera. `/social_navigation/keepout`, `/social_navigation/markers` và
`/social_navigation/attention_debug` là kết quả/diagnostic từ cảm biến.

## Điều chỉnh kịch bản

Trong source, tạo lại riêng asset động rồi build:

```bash
python3 social_navigation_sim/scripts/generate_social_dynamic_world.py \
  --watch-seconds 20 --walk-speed 0.35 --patrol-speed 0.4
colcon build --base-paths social_navigation_sim \
  --packages-select social_navigation_sim --symlink-install --executor sequential
```

Thời gian trong `config/social_dynamic_scene.json` là giây **mô phỏng**;
ở RTF 0,2 thì 12 giây mô phỏng mất khoảng một phút thực. Khi so sánh hai
backend, giữ cùng lịch, tốc độ người, map, đích và cấu hình cảm biến.

Để trở lại cảnh tĩnh:

```bash
ros2 launch social_navigation_sim social_navigation.launch.py \
  navigation_backend:=baseline social_scene:=static
```

## Sửa lỗi sau kiểm tra trực tiếp

- Chọn cặp RGB/depth cùng frame/kích thước và lệch timestamp tối đa 0,06 s
  **trước** khi chạy DNN. RGB mới nhưng thiếu depth không làm mất cặp cũ
  còn mới; không dùng lại cùng capture để tăng số quan sát.
- CameraPeople ghép theo khoảng cách dự báo có giới hạn, giữ ID qua mất dấu
  ngắn và loại điểm trùng dưới 0,25 m. Bộ nhớ xã hội hợp các mảnh người đứng
  gần trùng dưới 0,28 m, giữ timestamp nguồn; ID bị bỏ làm hết hiệu lực vùng cũ.
- Tâm TV từng phần được ghép vào đoạn màn hình đã đo. Các ID TV mới trở thành
  alias của cùng màn hình, thay vì tạo thêm vùng. Status phân biệt `tv_tracks`
  (đã hợp) và `tv_raw_tracks` (track từ đầu vào detector).
- Cooldown quan sát áp dụng cho cả tìm màn hình, tìm người và kiểm tra vật
  cản. Lượt kiểm tra vật cản đang thực hiện không bị tìm TV thay thế ngay.
- Với `social_inspect_obstacles:=true`, camera có thể nhìn một lần vào hình
  học map nằm sát phần tuyến sắp đi: kích thước vật cản, tuyến và khoảng cách
  quyết định điểm nhìn; không đọc nhãn hay tọa độ người từ scenario. Đề xuất
  này không tự tạo vùng xã hội. Lượt nhìn có dwell 1,6 s mô phỏng và vẫn đi qua
  MPC cùng các giới hạn thời gian/va chạm hiện có.

Profile động dùng camera 480×360 @ 6 Hz mô phỏng, DNN tối đa 2 Hz thực,
OpenCV 1 thread, tối đa 2 crop thân @ 224 px. Mỗi 4 capture có thể kiểm tra
thêm tư thế nằm. Một crop từ bề mặt thấp RGB-D sẽ được thử pose theo hai
hướng xoay; chỉ khi không có crop hình học mới thử detector toàn ảnh xoay.
Các crop nằm ngang dùng 256 px để giữ chi tiết. Đây là giới hạn tải, không
phải cam kết RTF trên mọi máy.

YOLO-tiny có thể bỏ sót người nằm. Nhánh bổ sung đề xuất bề mặt thấp rồi đòi
hỏi các khớp thân/chi đo được bằng RGB-D, thân gần ngang, bề dài phù hợp và
chân cùng hướng trục thân. Nếu thiếu mũi, cần hai vai tin cậy, hông và khớp
chân xa phù hợp. Giường/bàn chỉ tạo đề xuất crop, không đủ để gán người nằm.
Ứng viên cần nhiều capture trước khi có vùng; nhánh này không suy luận ngủ.

Kiểm tra mô hình trên một camera Gazebo riêng nhìn giường: ảnh có người nằm
cho một ứng viên pose/RGB-D; ảnh cùng giường bỏ người cho không ứng viên.
Đây là hai ca đối chứng, chưa phải đánh giá precision/recall trên toàn bản đồ.
Các kiểm tra hồi quy nằm trong `test/test_perception_pipeline.py`.

### Khởi động lại trên máy có cổng Fast DDS shared-memory bị kẹt

Launch động mặc định `dds_udp_only:=true`: áp dụng riêng cho các tiến trình
con profile `config/fastdds_udp.xml`, dùng UDPv4 thay builtin transports.
Cấu hình theo [tài liệu Fast DDS 2.6](https://fast-dds.docs.eprosima.com/en/2.6.x/fastdds/transport/udp/udp.html).
Không xóa `/dev/shm` hoặc thay cấu hình ROS toàn máy. Có thể chọn
`dds_udp_only:=false` nếu muốn dùng transport mặc định của môi trường.
