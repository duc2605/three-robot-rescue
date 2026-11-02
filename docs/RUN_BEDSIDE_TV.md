# Tự chạy goal cạnh giường và lưu dữ liệu để kiểm tra

Chạy từ thư mục gốc dự án. Hai package đã build trong phiên chuẩn bị;
nếu không còn `install/setup.bash`, build lại theo README chính.

Terminal 1 — mở mô phỏng động, RViz và lưu log:

```bash
cd ~/three-robot-rescue
bash scripts/run_dynamic_with_logs.sh
```

Terminal 2 — sau khi ba robot xuất hiện, đặt goal và thu dữ liệu:

```bash
cd ~/three-robot-rescue
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=31
python3 scripts/run_bedside_tv_demo.py \
  --x -3.9 --y -1.35 --output log/bedside_demo \
  --ros-args -p use_sim_time:=true
```

Helper chờ có map và vị trí ba robot, rồi gửi một goal tại `(-3.9,-1.35)`.
Đây là điểm dự kiến cạnh phía dưới giường trong cảnh động hiện hành.
Helper không thay map, không phát lệnh vận tốc và không tắt tránh vùng xã hội.
Nhấn Ctrl+C ở mỗi terminal để dừng helper/mô phỏng tương ứng.

Các file để AI đọc sau lượt chạy:

- `log/manual_dynamic.log`: khởi động, cảm biến, planner và MPC.
- `log/bedside_demo/initial_path.json`: đường đầu tiên thực sự nhận từ
  `/dstar_lite/path`, cùng kiểm tra giao hành lang TV tham chiếu.
- `log/bedside_demo/telemetry.jsonl`: diễn biến đường, vị trí, social status.
- `log/bedside_demo/summary.json`: khoảng cách leader tới goal và trạng thái
  helper; tạo khi kết thúc bình thường hoặc Ctrl+C.

Đường trực tiếp từ vị trí xuất phát dự kiến cắt khoảng giữa người xem và TV,
nhưng đường D* thực tế còn phụ thuộc bản đồ/cảm biến lúc nhận goal. Phải
đọc `crosses_reference_tv` trong file kết quả thay vì coi việc cắt vùng là
đã được chứng minh trước khi chạy. Polygon tham chiếu là hình học kịch bản,
không phải vùng TV do camera nhận diện và không đưa vào planner.

Helper giữ bản sao đường đầu trên `/demo/initial_path` và marker tham chiếu
trên `/demo/references`; muốn xem chúng trong RViz phải thêm display tương
ứng. RViz mặc định vẫn hiển thị đường D* đang cập nhật. Helper không quay
video và chưa được chạy hết một lượt ROS trong phiên chuẩn bị bị dừng.
