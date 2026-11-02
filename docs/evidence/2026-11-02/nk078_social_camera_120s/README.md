# NK-078 — Camera/vùng xã hội và né vật động, một lượt120s sim

Người dùng yêu cầu bật nhận diện vùng xã hội và thử đúng một lượt120s.
Không đổi thuật toán/cấu hình mặc định; override profile khi launch:
leader_camera/person_detection/head_pose/body_pose/social_avoidance/
social_observation/social_auto_observe=true. Giữ camera480x360/6Hz,
inference max2Hz wall/1CPU thread và LiDAR2m/240 tia. Né vật động vẫn
LiDAR, camera đưa vùng vào planning map; không tự bật direct camera fusion.
Cùng goal(1.0815577507,−2.0020322800), gửi khi ready≥3.031s sim.

Chạy server-only, không GUI/RViz, domain66/partition riêng. Không so RTF
hoặc tỷ lệ né với GUI hay các lượt75/165s khác. Không đưa GT vào control;
pose/contact Gazebo chỉ ghi để đánh giá. Mục tiêu120s là **thời gian mô
phỏng**, không phải wall. Không chạy lượt thứ hai nếu kết quả chưa đạt.

validate_once.py ghi social_events.jsonl từ camera
outputs/social map/markers/status. Ảnh detection_*.jpg là ảnh thật từ
/leader/people/image của lượt này. Marker kịch bản không dùng làm kết quả
perception. Các nhãn region vẫn là kết quả thuật toán, không chứng minh
đúng hành vi thật hoặc người nằm là ngủ.

analyze.py chỉ đọc offline; đếm contact ngoài nền từ physics, quãng đường
root, decision reason, khoảng cách goal và status/regions. Mỗi status hay
decision là mẫu, không coi là thử độc lập. Max nhãn không là recall/accuracy.
Dùng completion.json/world_frames để xác nhận đã đạt120s,
launch_parameters/ để xem cấu hình thực đã truyền và analysis.json
để xem số liệu chốt. Có thể mở runtime recordings/nk078_social_camera_120s_once
trong viewer; thư mục runtime không đưa GitHub mặc định.

Không chạy lại hồi quy248 test vì không thay navigation; kiểm compile
harness trước khi launch. Cần giữ riêng các kết quả NK-073/NK-076, không
coi một lượt120s là kiểm toàn bộ chu kỳ hoặc benchmark lặp.


## Kết quả chốt

- **Đúng một lượt**, frames0.001–120.001s. Không sửa navigation hoặc chạy
  lại sau lỗi. Camera outputs/ngữ cảnh xã hội thực được ghi;7 file params
  thực của launch được giữ. D*/3MPC dùng /social_navigation/map, observation
  và body analysis bật; moving escape vẫn LiDAR, không direct camera fusion.
- Physics xác nhận **patrol↔leader84.180–86.253s**, **patrol↔robot2
  85.647–87.771s**. Robot1 không có contact ngoài nền ghi nhận. Đây là
  hai cặp, không phải hai mẫu ảnh ước lượng. Chưa đạt cả3 né an toàn.
- Leader gần goal20.801s, né ra xa>.5m24.001s rồi trở lại<.15m55.101s;
  cuối lượt lại ở goal (cách≈0.000122m). Không đồng nghĩa toàn đội luôn
  khôi phục formation. Robot1 vẫn có escape mới gần cuối lượt.
- Vùng viewing_tv có11 mẫu14.033–18.235s; facing_group/person cũng hoạt
  động. Chưa có lying_person/lying candidate trong lượt. Không chứng minh
  độ đúng nhận diện hoặc toàn bộ vùng xã hội được bảo vệ ổn định.
- Checkpoint sát contact có escape_all_rollouts_rejected, command0;
  scan/state còn khoảng.1–.2s sim. R3 t84.1 từ chối140 moving checks,
  compute≈26.4ms; R2 t85.6 từ chối132,≈13.4ms. Đây là lý do trực tiếp
  tại mẫu, chưa xác định căn nguyên estimate/geometry/actuator/chọn lối.
  Không đủ căn cứ quy contact cho camera chậm. Các stop vì timeout/quá
  tuổi ở thời điểm khác vẫn giữ nguyên trong analysis/diagnostics.

[analysis.json](analysis.json), [completion.json](completion.json),
[launch.log](launch.log), [validation.log](validation.log),
[contact diagnostics](contact_diagnostics.jsonl.gz),
[social events](social_events.jsonl.gz), [provenance](provenance.json).
Giữ world_frames/scene/goals/config nén gzip và navigation excerpt
(toàn decision, raw scans81–89s) để đối chiếu sau; ảnh detection thật
được giữ cùng thư mục.

**Giới hạn vận hành:** harness nhận SIGTERM khi cleanup nên không ghi
live.json/samples.json cuối, exact wall và GetParameters in-memory bị
mất. Không giả lập lại các file đó; completion.json nêu nguồn phục hồi
là raw frames/goals/events/params, recorder status kết thúc sạch0 dropped.
Không còn process test. Sau lượt này chỉ bổ sung checkpoint ghi **trước**
cleanup vào harness (compile qua), chưa chạy lại theo ràng buộc1lượt.
Dữ liệu120s và contact đã lưu, không coi exit143 là test navigation qua.

Lượt baseline NK-076 chỉ75s, trong khi contact mới ở84–88s. Chưa có
baseline cùng120s/điều kiện cameraoff để quy mức thay đổi cho camera.
Không mở lượt thứ hai để so sánh. Không đưa thêm heuristic/giảm ngưỡng
hoặc sửa thuật toán trong tác vụ chỉ kiểm thử này.
