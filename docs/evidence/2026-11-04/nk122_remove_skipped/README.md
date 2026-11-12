# NK122 — dọn các paper đã bỏ qua

Đã xóa Paper5/6/11/12:4README,4launch và20file prototype legacy của
method03/04/09/10. Danh sách chính xác trong `deleted_files.json`.
Giữ paper1/2/3/4/7/8/9/10 và số cũ; catalog/runner/launchchoices đã dọn.
README tổng giữ các khối build/source/run+record/viewer của chế độ còn lại,
chỉ mục/cây nguồn không còn liên kết hiện hành tới file đã xóa. Các lịch sử
journal/report/evidence, backups và recordings không bị xóa.

Backup: `backups/20261104_101615_566274_nk122_remove_skipped_papers`.
Script tạo đã so SHA với nguồn; verify lại1179file thành công.
`checks.json`:14file runtime SHA không đổi, AST4file,3script shellsyntax,
16khối Bash README chỉ kiểm cú pháp, liên kết local hợp lệ; diffcheck qua.
Chưa build/test/Gazebo, không tự dừng phiên hoặc push. Artifact install
cũ có thể còn trên máy; runner/launch hiện hành đã loại các số vừa xóa.
Báo cáo tiến độ kỹ thuật giữ nguyên vì tác vụ chỉ dọn nguồn/vận hành.
