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
| Chọn/chẩn đoán method01–10 | `README_PAPERS_03_12.md`, `/comparison/robotN/status`, bản ghi đúng method | `comparison_controller.py`, ba module trong `comparison_methods/method_*` |
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
