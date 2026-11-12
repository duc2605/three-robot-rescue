# File cần đọc và lệnh để người dùng tự chạy

## Build, chạy và kiểm tra

Các lệnh chuẩn trong từng mục [README gốc](../README.md): build → source →
chạy có ghi → xem lại. Mỗi khối chạy mô phỏng đã tích hợp lưu bản chạy;
không cần tìm mục ghi riêng. Khi chỉ cần lệnh, AI cung cấp lệnh và điều kiện sử dụng;
không tự mở Gazebo, tự đặt goal, build hay chạy test thay người dùng.
Chỉ thực hiện các bước này khi người dùng yêu cầu rõ. Đọc/sửa file và kiểm
tra cấu trúc tài liệu có thể tiến hành trong tác vụ sửa tương ứng.

## Chọn file theo tác vụ

| Việc cần làm | Đọc trước | Chỉ mở thêm khi cần |
|---|---|---|
| Hướng dẫn chạy | Phần tương ứng `README.md`, `scripts/run_simulation.sh` và runner được gọi | Launch của chế độ nếu hỏi tham số |
| Xe dừng, né sai, va chạm | `<bản ghi>/stop_analysis.json`, `goals.jsonl`, `diagnostics_config.json` | Đoạn `navigation.jsonl`, `world_frames.jsonl`, `stop_*.jsonl` quanh thời điểm lỗi |
| Chọn/chẩn đoán method01/02/03/04/05/06 | `README.md` mục1/2/3 theo map và README riêng của paper, `/comparison/robotN/status`, bản ghi đúng method | `paper_experiment_node.py`, `paper_models/catalog.py`, `kinematic.py`, `deform.py`, `ho_mpc.py`, `drivetrains.py` hoặc `robile.py`; prototype cũ không còn chạy |
| Lỗi chọn điểm né | Đoạn `yield_to_moving_obstacles` trong `social_navigation_planner/social_navigation_planner/dstar_mpc_controller.py` | `local_escape.py`, test liên quan |
| Vận tốc vật động sai | `moving_obstacles.py` cùng track/scan trong đoạn bản ghi lỗi | `scan_pose_history.py`, cấu hình LiDAR |
| Vùng TV/xã hội | `social_navigation_sim/scripts/social_costmap.py`, trạng thái/marker trong `perception.jsonl` | Node nhận diện tương ứng, planning map và launch |
| Người đi sai/quay sai | Kịch bản và `social_navigation_sim/src/social_scenario_motion.cpp` | World, `scenario_motion.py` khi cần đối chiếu |
| Giao diện bản ghi | `scripts/view_replay.py`, `scripts/replay_viewer.html` | `scripts/replay_data.py`, `perception.jsonl` nếu lỗi dữ liệu |
| Build lỗi | Đoạn lỗi terminal, `package.xml`/`setup.py` hoặc `CMakeLists.txt` của package lỗi | File được traceback/compiler chỉ tên |
| Tiếp nhận sửa dự án | `AGENTS.md`, phần bàn giao đầu nhật ký, phần tiến độ liên quan | Chỉ mục NK/minh chứng liên quan đến yêu cầu |

Không cần đọc toàn repository, toàn lịch sử nhật ký, toàn bộ recordings hay
mọi test cho một yêu cầu chạy. Nếu chưa có tổng hợp, đưa lệnh tạo tổng hợp
cho người dùng. Một JSONL lớn chỉ lấy đoạn quanh mốc lỗi, mở rộng khi thiếu
bằng chứng. Không suy kết luận từ một bản ghi khác phiên.

## Nguồn để chạy và nguồn để đọc lỗi

Chạy ROS cần package đã build cùng assets/cấu hình được launch nạp;
không thể chỉ giữ một script rồi bỏ world, mesh, model hoặc thư viện import.
AI không cần đọc hết các tài nguyên đó để đưa lệnh chạy. Build/install là
đầu ra phục vụ ROS, nhật ký và evidence là tài liệu đánh giá; chỉ mở đúng
nhóm cần cho vấn đề hiện tại. Không xóa tài nguyên để giảm số file phải đọc.

## Hiểu chức năng thư mục và nguồn gốc thuật toán

Đọc [README mục6](../README.md#6-thuật-toán-thực-sự-có-trong-dự-án-và-nguồn-gốc)
để phân biệt thuật toán gốc, bản triển khai cục bộ, heuristic và pretrained
model. [Mục7](../README.md#7-cây-thư-mục-từ-workspace-tới-từng-file-nguồn)
liệt kê tới từng file nguồn. [Phụ lục](DANH_MUC_THU_MUC_VA_FILE.md) mở rộng
tới từng file evidence lịch sử; không cần đọc hết phụ lục để sửa một lỗi.


Video replay NK098: đọc `scripts/replay_viewer.html`, `scripts/replay_media.py`,
`view_replay.py` và supervisor `record_replay_media.py`; camera tần số ghi
ở `social_navigation_sim/scripts/replay_sensor_recorder.py`. Không sửa
controller để sửa kích thước UI hoặc video. Phụ thuộc FFmpeg/X11 xem
PHAT_LAI_MO_PHONG.md; không tự chạy mô phỏng để thử giao diện.


Sau khôi phục NK116: nhánh né đọc dstar_mpc_controller.py/local_escape.py
bản NK094; không tìm các helper home/intents mới đã gỡ. Lỗi chờ formation/
về goal đọc coordinator `start_independent_goal` và
`independent_goal_progress.py`, test_independent_goal_progress.py.
Giao diện/replay giữ hiện tại, không restore các file đó để sửa điều hướng.


Map thứ ba NK136: chỉ đọc launch/street_intersection.launch.py,
src/street_traffic.cpp + street_traffic_math.hh,
scripts/generate_street_intersection.py và config/street_intersection_scene.json
trong social_navigation_sim; runner scripts/run_street.sh. Lỗi pha đèn/người
đổi tốc độ đọc traffic.jsonl của đúng lượt. Đây là trạng thái kịch bản,
không là perception. Không sửa social_static/social_dynamic hoặc controller
để thay đổi ngã tư. README mục3 có đầy đủ build/chạy/ghi/viewer cho baseline và Paper1–8.
Backend ngã tư chọn bằng navigation_backend:=baseline|paper1..paper8;
Paper3–8 dùng paper_experiment riêng, không dùng adapter prototype đã nghỉ.
