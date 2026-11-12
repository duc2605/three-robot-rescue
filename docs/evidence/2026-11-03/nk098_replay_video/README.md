# NK098 — Thu gọn UI và video replay

Ngày03/11/2026. Đây là bằng chứng thay đổi nguồn và kiểm tra tĩnh; chưa
có chạy thử browser/Gazebo/FFmpeg. Controller hash khớp backup trước tác vụ.
Xem checks.json và nhật ký NK098. Máy chưa ffmpeg, không tự cài phụ thuộc.

Files: scripts/replay_viewer.html, replay_media.py, record_replay_media.py,
view_replay.py, run_dynamic.sh; recorder camera raw10Hz/detection2Hz.
Bản ghi mới có media/manifest.json, gazebo.mp4, rviz.mp4, camera theo
source/epoch khi đủ dữ liệu/phụ thuộc. Bản cũ chỉ có camera JPEG thì có
thể tạo camera MP4; không dựng Gazebo/RViz giả.

Cú pháp đã kiểm,5 test mới chưa chạy; chưa đo sai số đồng bộ/RTF. X11
window capture8fps640×360 không hỗ trợ portal Wayland, có thể ngắt khi
thu nhỏ/resize/đóng cửa sổ. Timestamp video wall được nối sim bằng clock
poll, chỉ gần đúng; JSONL contact là nguồn kiểm chứng va chạm.
