# NK120 — Paper3 formation audit và tách các bản chuyển đổi theo nguồn

## Kết luận đã xác minh từ bản cũ

Trong `recordings/paper3_20261103_144328_857447632`, goal ghi t3.026 tại
(−5.04152298, −3.01570582). Coordinator vào `independent_goal` từ14.4s;
59.9s khoảng cách leader–robot1 khoảng3.407m, leader–robot2 khoảng3.014m.
Đây là khoảng cách tới leader, không phải lỗi slot đã chuẩn hóa. Tại145.3s
moving safety active và follower không có checked join. Chưa audit đầy đủ
contact phiên này, không kết luận có/không va chạm từ các số trên.

Nguồn cũ `formation.py` lấy offset từ reference do coordinator cấp, không
xác địnhV độc lập. Coordinator của compare vẫn là ThreeRobotDStarMPC nên
fallback NK116 có hiệu lực. **Đính chính:** nhận định trước đó rằng NK116
không ảnh hưởng Paper3–12 là sai; chỉ Paper1/2 qua subclass khác. Bản mới
không còn dùng coordinator đó trong launch paper.

## Nguồn đã đối chiếu

- Paper3: [bài và PDF JAREE](https://jaree.its.ac.id/index.php/jaree/article/view/433), DOI10.12962/jaree.v9i1.433, Eq3–6/12.
- Paper4: [nhà xuất bản](https://www.ieee-jas.net/en/article/doi/10.1109/JAS.2017.7510631), [bản tác giả CONICET](https://notablesdelaciencia.conicet.gov.ar/bitstream/handle/11336/63536/CONICET_Digital_Nro.6f79b276-8b2b-4545-b591-1dc795f0ee2e_A.pdf?isAllowed=y&sequence=2), Eq2/9. Không tái lập đầy đủ inverse dynamics Pioneer.
- Paper7: [PDF tác giả](https://github.com/NeSC-IV/DEFORM/blob/main/RA_L_DEFORM.pdf), DOI10.1109/LRA.2025.3552998, Eq2–8. Bản này rút gọn width iteration, solver/horizon/thư việnformation, không port toàn bộ repository tác giả.
- Paper6: DOI10.12962/jaree.v5i2.204, đã tìm được nguồn nhưng bỏ qua theo lựa chọn người dùng.
- Paper10: DOI10.3390/math13101628, đã tìm được nguồn nhưng bỏ qua theo lựa chọn người dùng.
- Paper5/8/9/11/12: trạng thái thiếu nguồn/công thức/đầu vào trong catalog và README riêng; không gọi việc tìm được DOI là đã đủ để triển khai.

Mã mới viết từ công thức/diễn giải đã đối chiếu, không chép repository của
tác giả. Không phân phối PDF toàn văn trong repo. Quy mô/mô hình chuyển đổi
được công bố trong README mỗi bài; không lấy tên thuật toán làm chứng cứ
bản tái lập đầy đủ.

## Kiểm chứng trong tác vụ

- Backup `backups/20261103_150117_828475_nk120_isolate_and_rewrite_papers03_12_from_sources`: script verify1154file, SHA archive/manifest hợp lệ; script tạo trước sửa đã so nguồn.
- `static_checks.json`: AST12file, SHA9file thuật toán baseline/Paper1/2 không đổi so backup. Launch mặc định navigation_enabled=true giữ baseline, helperpaper truyềnfalse và tạo node độc lập.
- `bash -n scripts/run_dynamic.sh`, `git diff --check`: qua.
- Đã viết `test_independent_papers.py`, **chưa thực thi**; chưa build, chưa Gazebo, chưa kiểm benchmark. Không tự dừng phiên người dùng, không push.

## Giới hạn cần kiểm tra thực tế

VO lấy mẫu hữu hạn; tracker cụm LiDAR có association/occlusion error.
A* waypoint chung và veto xã hội/vật lý là harness thêm, không thuộc nguyên
bản mọi bài. Veto có thể dừng ở mép vùng xã hội, người vẫn có thể tiến vào
robot đứng. DEFORM dùng solver đồng bộ trong một node; kiểm giới hạn1s sau
solve không phải interrupt thời gian thực. Chưa đo RTF/chu kỳ/va chạm hoặc
đảm bảo không starvation. Camera perception dùng chung, không bật sweep
của baseline. Bản ghi giữ nguyên viewer, decision có search.paper/target/
raw command và lý do; không giả đíchA*né hoặc terminal-safe đã xác nhận.
