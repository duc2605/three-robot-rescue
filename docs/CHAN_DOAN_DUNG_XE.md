# Chẩn đoán xe đứng yên — ghép trong lượt chạy

Từ NK-088, wrapper chạy tự tạo bản ghi/chẩn đoán cho mỗi lượt. Observer,
`log/sessions` và cơ chế NK-061 vẫn được gỡ. Phần chẩn đoán ghi ngay tại nơi
controller/coordinator đưa ra quyết định; phần stop instrumentation không
subscribe thêm camera/scan hoặc publish lệnh thử nghiệm. Từ NK-074, chế độ
ghi thủ công còn chạy node replay riêng subscribe scan/đầu ra kế hoạch để
vẽ vùng quét và điểm né; từ NK-079 node replay cũng subscribe camera và
social markers để ghi perception.jsonl riêng, không thêm input cho controller. Nó không đổi ngưỡng né, goal hay chi phí MPC.

## Chạy một lượt cần tìm lỗi

Terminal1, sau khi build theo README (máy hiện tại đã build):

```bash
cd ~/three-robot-rescue
bash scripts/run_dynamic.sh --diagnose-stop recordings/chan_doan_01
```

Thư mục phải mới; nếu đã có, chọn `chan_doan_02`. Từ NK-071 profile động mặc định tắt camera để thử né LiDAR2m. Chọn goal
trong RViz như trước. Chỉ mở một phiên; Ctrl+C ở terminal1 dừng ROS launch.
Không tự chọn hoặc đổi goal. Tuỳ chọn này bao gồm cả ghi pose/contact để
phát lại, không cần thêm --record-replay.

Terminal2, mở viewer:

```bash
cd ~/three-robot-rescue
python3 scripts/view_replay.py --session recordings/chan_doan_01
```

Sau khi thấy lỗi, dừng terminal1 rồi tổng hợp để đọc:

```bash
python3 scripts/analyze_stop_diagnostics.py --session recordings/chan_doan_01 \
  > recordings/chan_doan_01/stop_analysis.json
```

Có thể đọc khi còn đang chạy; dòng JSONL chưa hoàn chỉnh được bỏ qua.
File tổng hợp ghép contact với tối đa hai mẫu trước và một mẫu sau ở
controller/coordinator trong khoảng−1/+0.5 giây sim quanh lúc bắt đầu
contact. Nếu không có mẫu thì ghi rõ thiếu, không suy dữ liệu thay thế.
Viewer hiển thị pose/contact, vùng LiDAR và điểm A*/MPC (NK-074);
chi tiết lý do dừng vẫn nằm trong JSONL và file phân tích, không được chèn thành thông báo perception của robot.

## Dữ liệu được ghi

Ngoài scene.json và world_frames.jsonl, `diagnostics_config.json` ghi giới
hạn và đường dẫn/SHA-256 module Python thực tế trong môi trường đã source.
Các file cửa sổ:

| File | Ý nghĩa |
|---|---|
| stop_robot1.jsonl | Quyết định/lệnh và đầu vào của controller robot1 |
| stop_robot2.jsonl | Tương tự robot2 |
| stop_robot3.jsonl | Tương tự leader mặc định robot3 |
| stop_coordinator.jsonl | Goal hiện hành, reference, chế độ quan sát và trạng thái điều phối |

Chỉ tạo file khi có trigger. Không thấy file trước trigger chưa phải lỗi.
Trigger: lệnh tịnh tiến<.01m/s và quay<.02rad/s, reference rỗng hoặc một robot trong pose đội đứng lại (đối với coordinator), hoặc có
lệnh nhưng pose đội còn mới thay đổi<.015m/<.03rad qua≥.5 giây sim.
Tình trạng đó phải kéo dài≥.5 giây wall mới mở cửa sổ.

Buffer giữ tối đa3 giây wall trước lỗi, ghi liên tục khi tình trạng còn
kéo dài và5 giây wall sau phục hồi, tối đa10 mẫu/giây wall. Khi RTF thấp,
khoảng sim được giữ trước lỗi có thể ngắn; đây không phải rosbag đầy đủ.
Mỗi stream tối đa20MiB; ghi nền qua queue giới hạn256 mẫu, quá tải bỏ mẫu
và tăng dropped_records. Lỗi IO/đạt giới hạn báo warning, không điều khiển
xe. Dừng đột ngột process có thể mất queue chưa flush; Ctrl+C đóng thông
thường. Các file stop không sao lưu ảnh camera hoặc toàn bộ ranges LiDAR.
Riêng navigation.jsonl mới lưu ranges thực qua node replay độc lập, tối đa
128MiB. perception.jsonl lưu JPEG/social riêng (256MiB); xem [hướng dẫn lớp phủ](PHAT_LAI_MO_PHONG.md#vùng-quét-lidar-và-điểm-né--nk-074).

Mẫu controller có:

- `t/epoch`, thời gian wall, pose, command, `reason` của nhánh phát lệnh;
  tuổi state/reference/scan theo sim và wall, map có hay chưa, coverage scan.
- Sensor packet gần nhất đã được callback chạy: stamp, receipt, frame,
  accepted/reason; camera có các candidate map, LiDAR có min bốn sector
  trước/trái/phải/sau theo frame scan. Không có return ghi null, không coi
  là khoảng trống. Callback receipt không phải thời điểm packet vào DDS.
- Track camera/LiDAR dùng trong controller: vị trí, vận tốc, radius, stamp
  và risk/TTC nếu có. Không phải identity hoặc ground truth người.
- Số ray loại do range/không hữu hạn, map, đồng đội; số ray giữ và tối đa16
  điểm world gần nhất sau lọc. Giúp kiểm tra vật cản đã bị loại nhầm chưa.
- `rejected_checks`: số lần thất bại đầu tiên ở ràng buộc map/LiDAR/moving/
  peer, tách A*, escape và MPC; không phải số đường độc lập hoặc số lần
  va chạm. `rejected_checks_tick_t` cho biết tick của bộ đếm. A* dùng cache
  có thể không chạy trong tick đó, khi ấy không có bộ đếm A* mới.
- A* side/goal/stamp và tuổi cache; peer poses và tuổi dự báo; các ngưỡng
  thực tế của controller. `compute_elapsed_wall_ms` là thời gian đã trôi
  từ đầu tick tới lúc lấy mẫu; `last_completed_tick_wall_ms` của tick trước.
  Mẫu callback/watchdog ngoài tick có compute_elapsed=null. Đây chưa phải
  benchmark và có tính cả overhead instrument; không tự gọi là độ trễ camera.

Coordinator ghi goal, số hàng/đích reference đầu, nhánh reference rỗng,
quan sát camera đang bật hay không, danh sách xe gần đứng yên, tuổi output nhận diện và cờ moving
safety/replan/recovery. Output camera mới không chứng minh nhận diện đúng
người trong replay; không có ảnh pixel để xác minh tư thế/identity.

## Cách khoanh vùng nguyên nhân

- `missing_or_stale_reference` + coordinator đang observation hoặc moving
  safety: kiểm điều phối đang giữ reference vì lý do gì.
- `escape_requires_fresh_sensors_map_and_peers`: xem tuổi scan/state,
  coverage, map và peer nào thiếu. `watchdog_wall_freshness` là nhánh
  watchdog theo wall, khác capture-age của scan.
- `escape_all_rollouts_rejected`/`mpc_beam_empty_step_*`: xem ràng buộc
  nào loại ứng viên cùng tick, track/ray/peer tương ứng. Không kết luận chỉ
  từ một counter tổng; nhiều ràng buộc có thể cùng tham gia.
- `mpc_tracking_command` với lệnh0 cũng có thể là lựa chọn tối ưu giữ vị
  trí, cần đối chiếu reference/goal để phân biệt đã đến đích với lỗi dừng.
- Lệnh khác0, pose đội gần đứng yên: đối chiếu pose/contact thực trong
  replay; có thể ở truyền lệnh/động học/vật lý hoặc pose đội cập nhật sai,
  chưa tự động quy là bị kẹt.

Các bản ghi cũ thiếu chẩn đoán không thể bổ sung dữ liệu cảm biến/quyết
định đã mất. Cần lượt mới bằng --diagnose-stop. Không mặc định bật chế độ
này cho các lần mô phỏng sau, không tạo lại log/sessions.
