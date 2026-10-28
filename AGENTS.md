# Quy trình cập nhật dự án

## Hai tài liệu bắt buộc

Đọc trước khi chỉnh sửa và duy trì đồng thời:

1. `README_NHAT_KY_DU_AN.md`: lịch sử yêu cầu, quyết định, thay đổi và kiểm chứng.
2. `README_BAO_CAO_TIEN_DO.md`: trạng thái hiện tại và so sánh các mốc để báo cáo giảng viên.

Người dùng yêu cầu hai file này được cập nhật cùng mỗi lần cập nhật dự án.
Đây là công việc đã được cho phép; không hỏi lại để cập nhật tài liệu.

## Khi thay đổi code, cấu hình, world, model, map, launch, test hoặc tài liệu dự án

- Thêm một mục có ID tiếp theo vào nhật ký, ghi ngày theo `Asia/Ho_Chi_Minh`,
  yêu cầu, lý do, file thay đổi, kiểm tra thực sự đã chạy và việc còn tồn tại.
- Cập nhật ngày, mốc hiện hành, bảng tiến độ, khác biệt phiên bản, kết quả
  kiểm chứng và các hạn chế tương ứng trong báo cáo. Nếu một mục không đổi,
  có thể ghi rõ điều đó trong lịch sử cập nhật; không tạo phiên bản thuật toán giả.
- Thực hiện cập nhật này trước khi kết thúc tác vụ, trong cùng nhóm thay đổi.
- Giữ lịch sử cũ. Nếu kết luận cũ bị sửa, thêm mục đính chính có dẫn ID;
  không sửa lịch sử để làm như kết quả mới đã có từ trước.
- Khi người dùng đưa ra quyết định mới hoặc kiểm thử thực tế làm thay đổi kết
  luận, cũng ghi lại. Không cần tạo mục cho từng lần đọc file, thao tác tool,
  build lặp lại hoặc log tự sinh không có thông tin mới.
- Chỉ chỉnh sửa hai file này thì cả hai vẫn phải ghi nhận lần cập nhật tài liệu.
  Sửa chính `AGENTS.md` cũng là cập nhật dự án.

## Tính chính xác khi báo cáo

- Tách rõ: đề xuất; đã triển khai; kiểm thử số học; kiểm thử Gazebo có giới hạn;
  benchmark có lặp; chưa kiểm chứng. Không đồng nhất các mức này.
- Không tự đặt phần trăm hoàn thành, số liệu thành tích, ngày thử nghiệm,
  commit, Git tag hoặc khẳng định tốt hơn baseline khi chưa có bằng chứng.
- Các mốc `M0`–`M6` trong tài liệu là nhãn lịch sử nội bộ, không phải Git release.
- Nhận diện tư thế nằm không chứng minh người đang ngủ. Dừng tại bình nước
  trong kịch bản không chứng minh camera nhận ra hành vi uống nước.
- Tránh giường có sẵn trên map không chứng minh nhận diện người nằm. Marker
  kịch bản, lịch người và pose ground truth không được coi là kết quả perception.
- Không dùng số liệu RTF ở điều kiện khác nhau để tuyên bố mức tăng hiệu năng.
- Nêu test chưa chạy, test bị bỏ qua, phụ thuộc thiếu và lỗi chưa xử lý.
- Dẫn file nguồn/test/minh chứng có thể kiểm tra. Minh chứng cần giữ lâu dài
  nên lưu trong `docs/evidence/`; không để báo cáo phụ thuộc duy nhất `/tmp`.
- Không khởi động hoặc dừng mô phỏng chỉ để cập nhật tài liệu, trừ khi tác vụ
  hiện tại yêu cầu chạy kiểm chứng. Giữ yêu cầu dừng mô phỏng của người dùng.

## Giới hạn cơ chế cập nhật

Đây là quy trình cho các tác vụ làm việc trong repository, không phải dịch vụ
theo dõi nền. Nếu sửa bằng editor/công cụ khác không đọc quy trình này, người
sửa cần cập nhật hai README trong cùng thay đổi. Không mô tả quy trình này
thành cơ chế tự động ghi lại mọi thay đổi ngoài phiên làm việc.
