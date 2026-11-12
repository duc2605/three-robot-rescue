# NK121 — ba nguồn mới làm Paper8,9,10

Yêu cầu bắt đầu03/11 và tiếp tục04/11/2026. Chỉ số8/9/10 được thay bằng
nguồn mới trong ba ảnh của người dùng; bản ghi/hướng dẫn lịch sử NK120
không được coi là đã chạy ba nguồn này.

## Nguồn đối chiếu

- Paper8: [trang tác giả](https://ddebenedittis.github.io/managing_conflicting_tasks_website/), [DOI10.1109/LRA.2025.3559843](https://doi.org/10.1109/LRA.2025.3559843), [repository](https://github.com/ddebenedittis/hierarchical_optimization_mpc/tree/4f4f0898d555c3864b7bc025e5099860c83f6cb9). Đọc HOMPCMultiRobot, TasksCreator, robot model và example_multi_robot; QP phụ thuộc commit2139fa438300ac0fa14ad514f18a175319a93bab. Chỉ tải file nguồn để đọc, chưa cài cache runtime hoặc chạy solver.
- Paper9: [repository ở commit đã chọn](https://github.com/Fangtnw/Formation-Control-of-the-Mobile-Robot-with-Different-Drivetrains/tree/5b3912443cdae2aff31897816c2641fc0d7fb593), đọc formation_controller, pure_pursuit_controller_revised và hybrid_astar. Là seniorproject, chưa có DOI xác minh. Công thức follower được viết lại cho cùng hướng/3xe; không giả ArUco đang hoạt động.
- Paper10: [repository ở commit đã chọn](https://github.com/SuneshSundarasami/Robile-Multi-Robot-Formation-Simulation-Environment-Using-Pybullet-And-ROS2/tree/1af1a4c802621e4d8a22791e28daf3728271eb08), đọc multi_robot_sim và robot_controller. VectorPID dùng gain1/.1/.1, integralcap10; source có dt1/240. Bản port dùng dt callback và chống xung đạo hàm đầu, giảm4follower→2 và bổ sung leadergoaltracking. Chưa có DOI xác minh.

Các repo gốc chưa có license tổng thể rõ ràng qua metadata đã đọc. Không
chép/vendoring cây mã, URDF hoặc assets tác giả vào repo. Paper8 dùng cache
ngoài workspace do người dùng tải, kiểm HEAD và tracked diff; adapter
trong dự án chỉ gọi API. Paper9/10 là mã mới triển khai cấu trúc luật với
các thay đổi công bố, không gọi là tái lập nguyên vẹn repository.

## Thay đổi có thể kiểm tra

`paper_models/{catalog,upstream_sources,ho_mpc,drivetrains,robile}.py`,
`paper_experiment_node.py`, helperlaunch, runner metadata và
`scripts/prepare_paper8.py`. Launch/README tên mới cho ba mục; tên cũ làm
alias để không phá liên kết cũ. Các chế độ khác giữ ranh giới điều khiển.
`diagnostics_config.json` và `decision.search.upstream` ghi repo/commit để
phân biệt bản trước/sau đổi nguồn. Không chuyển nhãn bản ghi cũ sang mới.

## Kiểm đã chạy

- Backup trước sửa03/11: `backups/20261103_161952_273035_nk121_replace_papers08_10_upstream_repositories`, verify1163file, archive/source/manifest đã kiểm khi tạo.
- Checkpoint khi tiếp tục04/11: `backups/20261104_095952_039090_nk121_continue_papers08_10_partial_checkpoint`, verify1166file.
- `static_checks.json`: AST21file, syntax23khối lệnh Bash trong README, liên kết local hiện hành,9file baseline/Paper1/2 SHA giữ nguyên so checkpoint. Kiểm này chỉ đọc/parse, không thực thi thuật toán.
- `bash -n scripts/run_dynamic.sh`, `git diff --check`: qua.
- Đã viết test_paper_replacements.py, test_paper8_optional.py và cập nhật danh sách mục bị chặn trong test_independent_papers.py. **Chưa chạy pytest; chưa build/pip/chuẩn bị cache runtime/Gazebo/benchmark.** Không tự mở/dừng phiên hay push.

## Giới hạn và bước kiểm tiếp

HO-MPC giải tập trung đồng bộ, chỉ4bước; yawngoàiMPC; cấu hình leadergoal
thay centroidvelocity ví dụ gốc. Collision là tuyến tính hóa đĩaLiDAR;
mapxãhội/vật lý kiểm bằng veto sau solve. Walllimit kiểm sau tính không
phải ngắt solver. HybridA* hếtbudget có thể chưa tìm được đường; chưa
port Reeds–Shepp/pallet. PID chưa antiwindup theo veto và target có thể
nằm trong vùngxãhội. Cảba có thể bị lớp veto giữdừng, chưa có chứng cứ né
hoặc hội tụ đạt. Người dùng tự chạy theo từngREADME, giữ đủ bản ghi để
đo formation/goal/contact/RTF cùng điều kiện trước kết luận so sánh.
