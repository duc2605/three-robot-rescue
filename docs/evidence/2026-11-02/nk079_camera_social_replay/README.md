# NK-079 — Camera leader và vùng xã hội trong replay

Giao diện có ảnh camera/nhận diện theo thời gian receipt/capture, lớp
vùng xã hội và PNG ghép camera. Không đổi navigation hay chạy Gazebo.
Chạy lại viewer, không cần chạy lại mô phỏng:

```bash
python3 scripts/view_replay.py --session recordings/nk078_social_camera_120s_once
```

## Bản ghi NK-078 đã có

import_perception_replay.py đính kèm **đầu ra gốc** từ social_events.jsonl
và6 detection_*.jpg của NK-078, không thay frames/scans/goal gốc.
Runtime có perception.jsonl và perception_import.json; provenance được
sao lại ở [nk078_import_provenance.json](nk078_import_provenance.json).
Ảnh chỉ6 snapshot, receipt time từ tên file, capture không còn giữ nên
stamp=null/capture_known=false. Không dựng ảnh giữa các snapshot hoặc
coi ảnh chụp cũ là video; không chọn ảnh tương lai. Social markers đủ
thời gian và snapshot rỗng xóa vùng, không bịa region từ timeline người.

## Các lượt ghi mới

Recorder opt-in hiện có thêm stream perception.jsonl độc lập. Subscribe
/leader/camera/image_raw, /leader/people/image, /social_navigation/markers
và /social_navigation/status; không publish command. JPEG75/max cạnh640
encode ở thread ghi riêng, mỗi nguồn tối đa2Hz theo cả sim và wall.
Queue32/cap256MiB, status/drop/error riêng. Navigation queue/cap giữ cũ.
Không bật camera/detector/social nếu launch chưa bật. Chạy thường vẫn
không ghi, chỉ --record-replay/--diagnose-stop.

Viewer hiển thị ảnh nhận diện hoặc gốc, timestamp và tuổi. Ảnh thưa/cũ
được ghi rõ, không thay bằng ảnh tương lai hoặc epoch khác. Lớp vùng
lấy đường viền publisher camera_social_regions trong map, không phải
ô keepout raster sau carve_escape hoặc chứng minh controller đã né.
Dữ liệu vùng>2s sim bị ẩn; snapshot rỗng xóa ngay. Màu/nhãn từ publisher.
Người nằm/nhóm/TV vẫn chỉ là kết quả thuật toán, không phải ground truth.

## Kiểm chứng

- [tests.log](tests.log):23 test scripts qua.3 test mới cho JPEG/capture/
  throttle/reset, marker/clear/frame và stream/status/export riêng; HTTP
  switch test kiểm perception cùng đúng session. Lỗi test so float1.2
  bằng tuyệt đối ban đầu đã đổi sang approx, không đổi logic timestamp.
- [ros_validation.json](ros_validation.json), [ros_checks.log](ros_checks.log):
  ROS domain79 gửi raw/detection synthetic images và marker/status,
  recorder tạo JPEG, tách capture/receipt và clear qua. Writer0drop/noerror.
  Không Gazebo, không publisher lệnh xe. Fixture ở ros_fixture/.
- [browser_validation.json](browser_validation.json), [browser_checks.log](browser_checks.log):
  Firefox đọc **bản ghi thật NK-078** qua HTTP, tua14.5 thấy viewing_tv,
  tua84.5 không lấy ảnh84.704 từ tương lai;84.9 hiển thị ảnh84.704.
  Ảnh thưa/cũ, source raw thiếu, clear/TTL/reset/legacy, PNG ghép camera
  và HTML standalone qua. [tv_overlay.png](tv_overlay.png),
  [contact_camera.png](contact_camera.png). replay.html.gz giữ bản export
  độc lập nén phục vụ minh chứng, giải nén trước khi mở. Harness nén/xóa
  chỉ file export tạm tự tạo, không xóa dữ liệu gốc.
- [build.log](build.log):package sim build qua. HTTP client đóng trang khi
  chuyển file từng gây BrokenPipe log, đã thêm xử lý disconnect riêng.
  Không rerun toàn bộ planner hay120s vì không sửa navigation.

Giới hạn: chưa benchmark IO/encode/RTF hoặc Gazebo với recorder mới.
Các ảnh chứng minh hiển thị, không chứng minh nhận diện/né đúng. Contact
NK-078 giữ nguyên kết luận. Bản ghi cũ thiếu ảnh/social không hồi điền;
NK-078 chỉ đính kèm dữ liệu thật còn lưu. HTML chứa ảnh có thể lớn.
