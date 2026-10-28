# Quy trình cập nhật dự án

## Hai tài liệu bắt buộc

Đọc trước khi chỉnh sửa và duy trì đồng thời:

1. `README_NHAT_KY_DU_AN.md`: lịch sử yêu cầu, quyết định, thay đổi và kiểm chứng.
2. `README_BAO_CAO_TIEN_DO.md`: chỉ so sánh cải tiến kỹ thuật giữa bản sau và bản trước để báo cáo giảng viên.

Người dùng yêu cầu duy trì cả hai tài liệu. Theo yêu cầu làm rõ ở NK-020,
nhật ký theo dõi mọi thay đổi cần bàn giao; báo cáo chỉ theo dõi cải tiến
kỹ thuật và bằng chứng. Đây là công việc đã được cho phép; không hỏi lại.

## Khi thay đổi code, cấu hình, world, model, map, launch, test hoặc tài liệu dự án

- Thêm một mục có ID tiếp theo vào nhật ký, ghi ngày theo `Asia/Ho_Chi_Minh`,
  yêu cầu, lý do, file thay đổi, kiểm tra thực sự đã chạy và việc còn tồn tại.
- Nếu thay đổi hành vi/thuật toán hoặc có bằng chứng mới về cải tiến, cập
  nhật báo cáo theo cấu trúc: hạn chế bản trước → sửa ở bản sau → kết quả
  kiểm chứng → giới hạn còn lại. Không tạo phiên bản thuật toán giả.
- Đổi tên, dọn file, GitHub, đăng nhập, build, đóng gói hoặc sửa tài liệu
  chỉ ghi trong nhật ký; không thêm các việc này thành mục tiến độ báo cáo.
  Khi chỉ có thay đổi vận hành, giữ nguyên nội dung kỹ thuật của báo cáo.
- Đầu nhật ký phải có phần bàn giao hiện hành cho AI khác: quyết định và
  ràng buộc người dùng, đường dẫn nguồn, kiến trúc, cách build/chạy/test,
  trạng thái kiểm chứng, lỗi còn mở và bước tiếp theo. Cập nhật phần này
  khi tình trạng đổi; không để AI phải suy ra đường dẫn mới từ lịch sử cũ.
- Thực hiện cập nhật này trước khi kết thúc tác vụ, trong cùng nhóm thay đổi.
- Giữ lịch sử nhật ký cũ. Nếu kết luận cũ bị sửa, thêm mục đính chính có dẫn ID;
  không sửa lịch sử để làm như kết quả mới đã có từ trước.
- Khi người dùng đưa ra quyết định mới hoặc kiểm thử thực tế làm thay đổi kết
  luận, cũng ghi lại. Không cần tạo mục cho từng lần đọc file, thao tác tool,
  build lặp lại hoặc log tự sinh không có thông tin mới.
- Thay đổi quy trình/tài liệu ghi trong nhật ký; báo cáo không ghi nhật ký
  biên tập. Sửa chính `AGENTS.md` cũng là cập nhật dự án cần ghi nhật ký.

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
