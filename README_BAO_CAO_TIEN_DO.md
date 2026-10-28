# Báo cáo tiến độ — Cải tiến giữa các phiên bản

**Cập nhật:** 28/10/2026. **Bản chức năng hiện hành:** M6.

Các mốc M0–M6 là mốc phát triển kỹ thuật, không phải số phiên bản phát hành.
Nền điều hướng được tiếp tục sử dụng là D* Lite + ba MPC và đội hình thích
nghi. Paper1/Paper2 là hai phương án đối chiếu, chưa có benchmark cùng điều
kiện để kết luận phương án nào tốt hơn.

## 1. Tổng hợp khác biệt trước và sau

| Chuyển phiên bản | Hạn chế ở bản trước | Cải tiến ở bản sau | Kết quả và giới hạn đã kiểm chứng |
|---|---|---|---|
| M0 → M2: hình học vùng xem TV | Ghép vùng chung theo nhóm và bề ngang giả định có thể tạo vùng chắn dư; khó biểu diễn từng quan hệ người–TV | Kiểm tra từng người với TV quan sát được; dùng đoạn màn hình đo từ RGB-D; tạo polygon riêng rồi hợp trên map | Có hồi quy hình học; chưa đo IoU trên bộ dữ liệu gán nhãn |
| M2 → M3: nhận diện TV trong runtime | Người và TV thường không xuất hiện đồng thời; hướng người ngồi thiếu ổn định; điều kiện thời gian dễ làm mất bằng chứng | Giữ lịch sử quan sát nối tiếp, bổ sung hướng thân/người ngồi, kiểm tra mặt trước TV và tách thời gian thực/mô phỏng | Đã quan sát được `tv_regions > 0` trong Gazebo; audit sau đó vẫn phát hiện trùng track |
| M3 → M4: hỗ trợ cảnh động | Cảnh tĩnh chưa kiểm tra được người thay đổi hoạt động và vị trí | Thêm người nằm, người rời TV đi bình nước rồi quay lại, người tuần tra; lịch theo thời gian mô phỏng và có collision body | Xác minh lịch/pose qua chu kỳ 112 s mô phỏng trong world headless chạy nhanh; chưa là benchmark đầy đủ ba robot |
| M4 → M6: ghép cảm biến | RGB mới nhất thiếu depth có thể làm bỏ qua cặp hợp lệ; xử lý ảnh không đủ điều kiện gây lãng phí suy luận | Chọn cặp RGB-D hợp lệ trước DNN, kiểm tra timestamp/frame/kích thước, giữ depth tương ứng trong suốt lượt xử lý | Có test hồi quy cho cặp lệch, cũ, tương lai và khung RGB mồ côi; chưa bảo đảm không mất dữ liệu ở toàn hệ |
| M4 → M6: tracking và vùng TV động | Hai track gần trùng và các mảnh TV tạo vùng lặp; vùng xem cũ có thể còn khi người đã di chuyển | Ghép track bằng dự báo ngắn có giới hạn, hợp mảnh TV/alias ID, thu hồi vùng của track đo được là đang di chuyển | Có hồi quy tránh đếm trùng và quản lý vùng; cần thử lâu để đo ID switch và thời gian thu hồi |
| M4 → M6: người nằm và quan sát | Detector người có thể bỏ sót tư thế nằm; ca tránh giường chưa cho thấy robot nhận diện người nằm | Thêm đề xuất bề mặt thấp RGB-D, crop xoay, kiểm tra khớp 3D và footprint; yêu cầu nhiều capture; nhìn có giới hạn vào vật cản sát tuyến | Một ca có người tạo 1 ứng viên, ca cùng giường trống tạo 0; chưa chứng minh robot tự quan sát đủ trên mọi tuyến |
| M4 → M6: điều phối lượt nhìn | Các kiểu tìm kiếm có thể thay thế nhau, gây dừng hoặc quay lặp | Dùng cooldown chung, giữ lượt kiểm tra vật cản khỏi bị tìm TV thay ngay; lệnh quay vẫn qua coordinator/MPC | Có hồi quy điều phối; cần đo thời gian dừng/quay trong nhiều lượt điều hướng |
| M4 → M6: tải xử lý và khởi động | Tải camera/DNN cao; có lượt restart thiếu camera/pose và controller | Giảm tải profile động, giới hạn tần số/crop/thread và thêm DDS UDP riêng có tùy chọn tắt | Lượt sau có đủ controller/camera; chưa có A/B kiểm soát để quy mức tăng RTF cho thuật toán |

M5 là mốc quan sát lỗi và thử goal làm căn cứ cho M6, không tính thành một
bản cải tiến thuật toán riêng. M1 là nhánh đối chiếu Paper1/Paper2, không
phải bản kế nhiệm đã được chứng minh tốt hơn nền.

## 2. Vùng xem TV: từ hình học chung đến bằng chứng theo từng người

Ở bản đầu, cách gom người và tạo vùng chung chưa biểu diễn tốt từng quan
hệ người–màn hình. Bản M2 chuyển sang polygon của từng người tới đoạn màn
hình RGB-D rồi hợp các polygon, giảm phụ thuộc vào bao lồi của cả nhóm.
Nếu chỉ có tâm TV, bề ngang dự phòng 1,1 m vẫn là ước lượng.

Bản M3 xử lý trường hợp camera lần lượt thấy người và TV: giữ bằng chứng
qua nhiều quan sát, tăng thời gian nhớ người/mục tiêu màu từ 8 lên 75 s,
bổ sung hướng người ngồi và ràng buộc mặt trước màn hình. Nhờ đó đã có vùng
TV xuất hiện trong chạy Gazebo, nhưng chưa đủ để xác nhận độ chính xác.

Bản M6 xử lý các lỗi lộ ra khi chạy động: hợp các track/mảnh TV gần trùng,
quản lý alias và thu hồi vùng xem của người được đo là đang di chuyển.
Người còn ngồi vẫn giữ vùng của mình. Mất quan sát đơn thuần chưa đủ để kết
luận người đã rời TV; đây vẫn là điểm cần đánh giá ở các ca bị che khuất.

## 3. Cảnh động: từ vị trí cố định đến thay đổi trạng thái theo thời gian

So với bản tĩnh, M4 bổ sung ba tình huống để kiểm tra pipeline khi trạng
thái xã hội thay đổi:

- Người nằm bất động trên giường.
- Người xem TV đứng dậy, đi tới bình nước, dừng rồi quay lại ghế.
- Người tuần tra di chuyển qua nhiều khu vực và lặp tuyến.

Lịch người dùng thời gian mô phỏng: pause Gazebo dừng lịch, reset clock
khởi động lại lịch. Các hình thể có collision body; chuyển động theo lịch
kinematic, chưa có animation đầy đủ hoặc hành vi nhường robot. Dừng ở bình
nước là giai đoạn kịch bản, chưa phải camera nhận diện hành vi uống nước.

## 4. Nhận thức và quan sát: sửa các lỗi phát hiện qua audit

Trước M6, audit ghi nhận mất cặp RGB-D, người trùng ID, TV phân mảnh và các
lượt nhìn lặp. M6 chuyển việc kiểm tra cặp cảm biến lên trước suy luận;
không dùng capture lặp thành bằng chứng mới; bổ sung quản lý track/alias và
cooldown chung. Đây là thay đổi về tính nhất quán của dữ liệu và điều phối.

Với người nằm, bản trước chỉ ghi nhận robot đi vòng giường có sẵn trên map,
không có bằng chứng nhận diện người nằm trong mẫu đó. M6 thêm đề xuất từ
bề mặt thấp, khớp thân/hông/chân trong RGB-D và xác nhận theo nhiều capture.
Bề mặt thấp riêng lẻ không tạo nhãn người; nhãn hiện tại là ứng viên tư thế
nằm, chưa phải kết luận đang ngủ.

| Đối chứng sau cải tiến | Kết quả | Phạm vi kết luận |
|---|---|---|
| Giường có người, camera nhìn rõ | 1 ứng viên nằm | Pipeline có thể tạo ứng viên ở góc kiểm thử này |
| Cùng giường bỏ người | 0 ứng viên nằm | Có đối chứng âm bước đầu; chưa phải đánh giá false positive tổng thể |

Minh chứng: [ảnh có người](docs/evidence/2026-10-27/posture_with_person.png),
[ảnh giường trống](docs/evidence/2026-10-27/posture_empty_bed.png),
[kết quả đo](docs/evidence/2026-10-27/posture_validation.json).

## 5. Cấu hình giảm tải của bản động

| Thành phần | Cấu hình M6 | Mục đích cải tiến |
|---|---|---|
| Camera | 480 × 360, 6 Hz mô phỏng | Giảm lượng ảnh cần xử lý |
| DNN | Tối đa 2 Hz thực, OpenCV 1 thread | Giới hạn tải CPU do suy luận |
| Pose thân | Tối đa 2 crop, đầu vào 224 px | Giới hạn chi phí khớp người mỗi lượt |
| Kiểm tra nằm | Mỗi 4 capture, crop ngang 256 px | Bổ sung góc nằm mà không quét mọi khung |
| Kết quả suy luận | Ngân sách 3 s thực và kiểm tra độ mới capture | Hạn chế sử dụng kết quả đã quá trễ |
| DDS | UDP riêng, có tùy chọn tắt | Xử lý sự cố khởi động đã ghi nhận trên máy thử |

Các mẫu RTF trước/sau là khoảng 0,160/0,200 nhưng khác cấu hình và trạng
thái robot, nên chưa dùng để kết luận phần trăm tăng hiệu năng. Mục đích
cấu hình đã rõ; hiệu quả định lượng cần phép đo cùng điều kiện.

## 6. Mức kiểm chứng của các cải tiến

Bộ hồi quy chức năng gần nhất có **115 test qua**, gồm phần điều khiển,
hai backend paper, perception, TV và kịch bản động. Có hai warning SciPy
clipping bounds ở Paper2; ba file lint không chạy. Kết quả này là kiểm
chứng hồi quy, không phải số lượt điều hướng thành công.

Các cải tiến hình học, ghép dữ liệu và điều phối đã có test tương ứng;
nhánh người nằm mới có đối chứng bước đầu. Chưa có thống kê nhiều lượt về
IoU vùng xã hội, precision/recall, ID switch, thời gian tới goal, va chạm
hoặc sai số đội hình để kết luận mức cải thiện tổng thể. Chưa đủ bằng chứng
kết luận M6 tốt hơn các bản trước hay hai paper theo một tỷ lệ định lượng.

Minh chứng hồi quy: [log 115 test](docs/evidence/2026-10-28/github_tests.log).
