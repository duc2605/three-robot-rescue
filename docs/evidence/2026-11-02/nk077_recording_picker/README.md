# NK-077 — Chọn bản ghi cũ trên máy

Thêm danh sách các bản ghi đủ scene.json/world_frames.jsonl trong
recordings/, nút làm mới/mở và nút chọn thư mục khác bằng trình duyệt.
HTTP chọn bản ghi theo khóa danh sách và URL riêng từng tab; chuyển trang
xóa offset/state cũ. Không nhận đường dẫn tùy ý từ URL. Folder import
đọc phía trình duyệt, dừng polling HTTP để dữ liệu cũ không ghi đè.

[tests.log](tests.log):20 test scripts/tests qua. Test mới dùng HTTP thật
trên fixture tạm, kiểm mọi stream cùng bản ghi, hai tab độc lập, tên Việt,
refresh phát hiện thư mục mới, loại folder thiếu file và symlink ngoài
recordings, từ chối khóa/path không thuộc danh sách.

[browser_validation.json](browser_validation.json),
[browser_checks.log](browser_checks.log), validate_browser.py: Firefox
kiểm nút chuyển tên Việt, scene/frame/goal đồng bộ, import thư mục không
bị poll thay sau1.3s, bỏ tail dở và HTML standalone vẫn có nút thư mục.
[picker.png](picker.png) là giao diện trên **fixture tổng hợp rỗng**,
không phải lượt Gazebo. offline.html là fixture export cùng mục đích.
Harness lúc đầu lỗi escape newline khi tạo File tổng hợp; đã sửa harness,
không phải lỗi product; kết quả trên là lượt browser đã qua.

Lệnh từ root:

```bash
source /opt/ros/humble/setup.bash
PYTHONPATH="$PWD/social_navigation_planner:$PYTHONPATH" /usr/bin/python3 -m pytest scripts/tests -q -p no:cacheprovider
python3 docs/evidence/2026-11-02/nk077_recording_picker/validate_browser.py
```

Không build/navigation change hoặc chạy/dừng Gazebo. Không benchmark RTF;
thư mục chọn trực tiếp là snapshot lúc mở, không tự cập nhật file mới.
Không phục hồi bản ghi đã xóa hoặc scan không có trong dữ liệu cũ.
