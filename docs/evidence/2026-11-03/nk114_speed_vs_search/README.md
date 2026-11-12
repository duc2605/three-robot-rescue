# NK114 — Va chạm do tốc độ hay tìm điểm chậm?

03/11/2026. Bản người dùng102805 tới80.501s, hash đúng NK113 hiện hành.
Physics contact patrol_person/robot2 từ79.778s tới hết bản ghi80.501s;
robot1/leader chưa ghi ngoài nền trong lượt này. Không khẳng định contact
liên tục giữa mọi mốc. Không tự chạy lại hoặc đổi source.

## Kết luận có căn cứ

Nguyên nhân trực tiếp: robot2 không duy trì được đường thoát hợp lệ, rồi
phát0 khi người tiếp tục tới. Có đóng góp của tiến triển thực thấp và né
gần cùng hướng người; không đủ bằng chứng kết luận động cơ/max speed
không đủ hoặc CPU đơn thuần chậm. Chưa có thử tăng tốc/tăng budget có kiểm soát.

## Timeline và tốc độ

- 76s chọn điểm(2.078,-2.994), cách1.195m, horizon5.85s.77s đổi sang
  (1.079,-3.083), cũng1.195m;77.5s dùng refuge đó. Radius mới đã hoạt động.
- 76.001→78.001s robot2(1.5166,-1.9394)→(1.4907,-2.1005), dịch+/-X
  rất ít và-Y0.161m; tốc độ dịch chuyển ròng0.0816m/s. Người giữx1.6,
  đi-Y0.7892m, tốc độ0.3946m/s. Xe còn trên cùng hành lang người.
- Lệnh76s có speed~0.083m/s,77s~0.138m/s,77.5s~0.205m/s; không phải
  một thử nghiệm xe chạy đều0.28m/s. Vận tốc thực/mean có độ trễ/phanh/dừng,
  không dùng để kết luận giới hạn động cơ hoặc chỉ tăng max speed sẽ ổn.
- 78s không có social-clear rollout; rear/left bị corridor/target_not_reached,
  right/front bị peer. Trial ví dụ bị robot3 prediction chặn. Chưa chứng
  minh mọi phương án vật lý đều bất khả thi; lúc đó emergency=false nên
  không mở physical fallback. Có lệnh escape xen kẽ tới78.4s, không nói
  cả đoạn từ78s đều dừng liên tục.
- Sau78.4s không còn checked escape trước contact.78.5s emergency=true;
  79.8s compute_budget_exhausted,101trials/0accepted,100escape.moving
  rejections và1trial bị ngắt budget. Lệnh0, speed đo~0.0064m/s, contact
  đã bắt đầu79.778s. Không phải không thấy người: scan/state age~0.1s sim.

## Thời gian tính toán

Search fail75s→contact dùng61.75–64.10ms wall so budget60ms. Đã thử nhiều
phương án nhưng bị gates loại, không chỉ đứng chờ tính một điểm chưa xong.
Hai giây sim đoạn76–78 mất10.566s wall; không đem62ms wall so thẳng thời
gian người đi trong simulation hoặc dùng số này tuyên bố RTF tăng/giảm.
Mở horizon5.85s làm mỗi candidate tốn nhiều kiểm hơn; budget cố định có
thể giới hạn số phương án đã xem. Chưa đo đủ để tách tác động horizon,
CPU, topology, nhiều hypothesis hoặc chặn của đồng đội.

## Hướng tiếp theo, chưa triển khai

Ưu tiên duy trì lối tách ngang khả thi từ sớm, kiểm tiến triển thực so với
rollout và lý do đổi refuge. Khi peer prediction chặn, cần phối hợp nhường
hành lang thay vì chỉ thêm điểm xa. Xem lại phân bổ budget/horizon và
điều kiện fallback khi đường social thất bại trước khẩn. Không bỏ moving
checks/giảm footprint hay tăng tốc mù khi chưa có đường. Chỉ audit, không
sửa code, build/test/Gazebo hoặc push.
