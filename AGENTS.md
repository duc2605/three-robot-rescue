# Quy trình cập nhật dự án

## GitHub

Chỉ commit/push để đưa thay đổi lên GitHub khi người dùng yêu cầu rõ thao
tác đẩy trong tác vụ hiện tại. Không coi yêu cầu push ở một tác vụ trước là
ủy quyền tự động push những lần sửa hoặc chạy thử tiếp theo. Mặc định giữ
thay đổi cục bộ; không tự đồng bộ GitHub sau mỗi lần làm việc.

## Đọc đúng phạm vi và cung cấp lệnh để người dùng tự chạy

Theo yêu cầu NK-085, mặc định cung cấp lệnh build/chạy/test/phân tích/viewer
để người dùng tự thực hiện. Chỉ tự thực thi các bước đó khi yêu cầu hiện tại
nói rõ cần thực hiện; yêu cầu chạy ở lượt trước không tự ủy quyền lượt sau.
Không tự mở/dừng mô phỏng, đặt goal hoặc kiểm thử Gazebo chỉ vì vừa sửa code.
Backup bắt buộc và kiểm tra tài liệu/file đã sửa vẫn thực hiện trong tác vụ.

Trước khi đọc nguồn, xác định loại lỗi và chọn file theo
`docs/FILE_CAN_DOC_VA_LENH_CHAY.md`. Đọc phần bàn giao đầu nhật ký và phần
báo cáo liên quan; không quét toàn bộ nguồn/lịch sử/bản ghi nếu chưa cần.
Đọc bản tổng hợp lỗi trước rồi giới hạn JSONL quanh mốc thời gian và robot
người dùng nêu. Chỉ mở rộng khi bằng chứng còn thiếu. README hướng dẫn dùng
phải chia riêng từng chế độ (động, tĩnh, từng paper, test), mỗi phần có
đủ lệnh cd/build/source/chạy độc lập; viewer/phân tích offline chỉ cần
lệnh riêng tương ứng, không thêm build không cần thiết. Đặt giải thích
kiến trúc/file ở bên dưới; giữ nguyên
trình tự lịch sử trong nhật ký, báo cáo và minh chứng cũ.

## Ghi bản chạy trong từng bộ lệnh — NK-088

Người dùng yêu cầu lưu mỗi lượt mô phỏng. README phải ghép ghi dữ liệu vào
ngay khối build/source/chạy của từng cảnh/backend, không tách thành bước
chạy ghi riêng. Dùng `scripts/run_simulation.sh` hoặc wrapper động/comparison
đã có ghi tự động; mỗi lượt tạo thư mục mới dưới `recordings/`, in đường dẫn
và lệnh viewer. Có thể chỉ định `--diagnose-stop NEW_DIRECTORY` ngay trong
khối lệnh. Viewer sau dừng đặt cùng mục với chế độ tương ứng. Test số học
và xem lại bản cũ không tạo lượt mô phỏng/bản ghi mới.

Đây là ghi khi người dùng thực sự chạy script, không phải dịch vụ nền tự
bắt mọi lệnh `ros2 launch` bên ngoài wrapper. Giữ lịch sử NK-064/067/079;
quyết định lưu mặc định NK-088 thay thế lựa chọn opt-in của các mốc đó.
Quy ước cung cấp lệnh, không tự chạy mô phỏng khi chưa được yêu cầu vẫn giữ.

## Backup bắt buộc trước mỗi cải tiến

Theo yêu cầu người dùng từ NK-060, trước khi sửa code, cấu hình, world,
model, launch, test hoặc tài liệu trong một tác vụ cải tiến:

1. Chạy `python3 scripts/create_backup.py --reason ten_thay_doi` trước
   thay đổi đầu tiên. Mỗi tác vụ cải tiến có snapshot riêng; tạo thêm khi
   chuẩn bị thay đổi hướng hoặc ghi đè một trạng thái cần giữ.
2. Chỉ sửa sau khi archive đọc được, kiểm tra SHA-256 với nguồn thành công
   và có `manifest.json`. Nếu backup thất bại, xử lý backup trước.
3. Ghi đường dẫn backup, phạm vi và kết quả kiểm tra vào nhật ký; không
   xóa hoặc ghi đè backup cũ nếu người dùng chưa yêu cầu.
4. Snapshot gồm nguồn, assets, cấu hình, test, tài liệu và thay đổi chưa
   commit. Không sao lưu credentials/cấu hình riêng, build/install/log/cache.
   `backups/` không đưa lên GitHub mặc định và không được build bởi colcon.
5. Khi khôi phục, sao lưu bản đang có trước, kiểm tra manifest, giải nén
   vào thư mục riêng rồi kiểm tra đường dẫn trước khi thay nguồn. Không
   giải nén đè `.git`, credentials hoặc xóa lịch sử hai README.

Đây là bước bắt buộc của người sửa trong repository, không phải dịch vụ
nền tự chặn mọi editor. Yêu cầu backup không phải quyền commit/push.

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
