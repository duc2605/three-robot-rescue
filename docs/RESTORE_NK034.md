# Phạm vi khôi phục lượt follower được ghi nhận ở NK-034

Ngày thực hiện: 01/11/2026. Theo yêu cầu người dùng, khôi phục nguồn của
lượt chạy mà hai follower đã né được; leader vẫn còn lỗi đã biết.

## Nguồn được phục hồi

NK-034 là mục đính chính kết quả của lượt dùng mã NK-032. Nhật ký NK-033
ghi rõ các bản sửa nguồn lúc đó chưa được nạp vào process đang chạy. Vì
vậy target phục hồi là nguồn trước các sửa NK-033, không phải tự đặt tag
Git mang tên NK-034 hoặc lấy commit HEAD ngày13/10 làm toàn bộ baseline.

Đã tái dựng trong thư mục riêng từ Git base `5ac6982` và lịch sử bản vá /
chỉnh nguồn của phiên ngày27–28/10 đến cuối NK-032. Giữ bằng chứng các bước
nguồn trong `docs/evidence/2026-11-01/nk034_restore/source_edit_evidence.json`.
Bốn file controller, moving_obstacles, local_escape, peer_safety được đối
chiếu byte với candidate tái dựng sau khi áp dụng. Đây là nguồn tái dựng
có provenance, không phải archive nguyên bản được chụp tại thời điểm NK-034.

Phục hồi controller/coordinator, perception, cấu hình, world/generator,
plugin lịch người và robot geometry có nguồn đối chiếu. World động được
sinh lại từ generator cũ. Các phần sau mốc đó (deadline, inbox đa luồng,
cooperative hint, compact clock, walking animation và contact audit mới)
không nằm trong bản đang dùng.

Hai backend paper và hai môi trường vẫn được giữ. Mã paper đã tồn tại
ngoài Git base được giữ từ nguồn trước khôi phục; giữ wiring executable /
backend selection để không làm mất Paper1/Paper2. Không tuyên bố đây là
snapshot bit-for-bit của toàn bộ workspace cũ, đặc biệt các file untracked
trước phiên và dữ liệu runtime không được lưu tại mốc đó. Lịch sử hai
README giữ nguyên; tài liệu hiện hành được cập nhật để tránh lệnh lỗi thời.

## Kiểm chứng và giới hạn

- Candidate nguồn qua159 test Python,2 warning SciPy;3 ament lint file
  không chạy. Đây là hồi quy nguồn, không chứng minh follower luôn né được.
- Build sạch hai package; kiểm tra launch tĩnh/động và hai paper bằng
  `--show-args`, không mở Gazebo trong kiểm tra này.
- Script backup kiểm source/binary/symlink, loại credentials/build/cache
  và phát hiện archive bị sửa. Backup trước phục hồi có585 file, đã kiểm
  archive và SHA-256.
- Đã đóng phiên cũ và bốn node detached. Chưa mở lại Gazebo hoặc replay
  tình huống follower sau khi phục hồi. Giữ kết luận leader có lỗi của bản cũ.

## Chạy bản khôi phục

```bash
cd ~/three-robot-rescue
source /opt/ros/humble/setup.bash
source install/setup.bash
export ROS_DOMAIN_ID=31
ros2 launch social_navigation_sim social_dynamic.launch.py
```

Hoặc `bash scripts/run_dynamic_with_logs.sh`. Profile cũ mặc định bật camera
và vùng xã hội; không dùng script LiDAR-only của các thử nghiệm sau NK-034.

## Backup hiện tại và quy trình mới

Trước thay nguồn, đã giữ:

- `backups/20261101_185410_before_nk034_restore/`:585 file,≈70MB, nguồn cũ
  theo NK-058 cùng lịch sử đến NK-059; có SHA-256 từng file/archive.
- `backups/20261101_190427_973229_before_apply_recovered_nk034/`: checkpoint
  bổ sung trước khi áp dụng candidate, gồm bước đầu quy trình backup mới.

Bản nguồn khôi phục sẽ có checkpoint riêng sau cập nhật nhật ký. Xem
`backups/README.md` để biết đường dẫn cụ thể. Từ nay mọi tác vụ cải tiến
phải chạy `python3 scripts/create_backup.py --reason TEN_THAY_DOI` trước khi
sửa, theo AGENTS.md và [hướng dẫn](BACKUP_VA_KHOI_PHUC.md).
