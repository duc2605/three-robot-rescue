# NK123 — bỏ tên trùng và đánh lại số

Số mới:1GWO-WOA,2APF-MPC,3PurePursuit/VO,4Impedance,
5HO-MPC,6DifferentDrivetrains,7Robile,8DEFORM.
Theo yêu cầu ba nguồn mới thành5/6/7; DEFORM chuyển7→8 để tránh trùng.
Các bản ghi/evidence cũ giữ số tại thời điểm ghi, không đổi nhãn lịch sử.

Xóa21file alias/prototype cũ và đổi10file; danh sách `changes.json`.
README tổng và riêng dùng tên mới, giữ đủ bộ lệnh build/chạy+ghi/viewer.
Script HO-MPC là prepare_ho_mpc.py, biến SOCIAL_HO_MPC_ROOT.
Runner paper1..8, compare01..06; catalog/dispatch/launch/metadata đã đổi cùng.
Registry prototype cũ còn1/2/5 phục vụ lịch sử, không chạy production.

Backup `backups/20261104_102119_658492_nk123_remove_duplicate_old_paper_names`:
archive/SHA nguồn/manifest kiểm khi tạo. `checks.json`: AST17file,25khốiBash
README chỉ kiểm cú pháp, liên kết hiện hành và ánh xạ launch/catalog hợp lệ;
9file thuật toán/helper baseline/Paper1/2 giữSHA. Diffcheck qua.
Chưa build/test/Gazebo hoặc push. Sửa tên/định danh, không có bằng chứng
cải tiến thuật toán mới nên giữ nguyên nội dung kỹ thuật báo cáo tiến độ.
Artifact install cũ có thể còn trên máy; build lại trước khi dùng số mới.
