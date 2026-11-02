# Báo cáo tiến độ — Cải tiến giữa các phiên bản

**Cập nhật:** 01/11/2026. **Nguồn đang dùng:** baseline lượt follower được
ghi nhận tại mục9/NK-034, tái dựng theo NK-060. Các mục10–21 bên dưới là
lịch sử thử nghiệm đã được đưa khỏi baseline; không phải đều đang bật.
Leader có lỗi đã biết; chưa replay Gazebo sau khôi phục.

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
| M6 → bản sửa tránh người động | MPC coi điểm LiDAR đứng yên; khi mất reference chỉ dừng, có thể bị người tiếp tục đi vào | Track ngắn camera/LiDAR, kiểm tra va chạm theo thời gian; bước né ngang có kiểm tra vật lý và teammate dù thiếu reference, watchdog giữ dừng nếu dữ liệu cũ | Bộ chức năng 138 test qua, 23 ca safety qua; thử node ROS tách domain có lệnh né; chưa có replay contact/RTF Gazebo |
| Bản né người động → bản A*/ưu tiên né khi quét | Chỉ lấy mẫu hướng né, chưa có đích cục bộ; camera sweep chưa được báo để nhả neo ngay | TTC theo tốc độ, A* đề xuất đích sau/trái/phải và đường theo thời gian; coordinator hủy sweep ngay khi MPC báo nguy cơ, giữ goal chính | 153 test qua, gồm 38 ca safety; hai node ROS riêng xác nhận hủy quét và vẫn có lệnh né; chưa replay Gazebo |
| Bản A* → sửa né của follower khi bị che khuất | Bỏ tia LiDAR lẻ và thưa hóa tia có thể mất chân người; follower chỉ dùng LiDAR riêng/camera leader; điểm động còn bị đóng băng trong rollout | Giữ đủ tia, track cả cụm một tia qua nhiều capture, dùng LiDAR các robot với track riêng; tăng nhìn trước lên 3 s, tránh kiểm tra trùng điểm động tĩnh; đơn giản hóa collision robot | 159 test qua, 43 ca safety; ca động học dùng bố trí robot tại vùng va chạm giữ khoảng cách tâm nhỏ nhất 0,687 m; chưa replay Gazebo hoặc xác nhận cải thiện RTF |

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

Kiểm tra cùng phiên sau đó xác nhận vùng viewing vẫn có thể mất khi camera
không quan sát lại: raw TV track mất trước, remembered TV track mất sau,
rồi color_regions từ 1 về 0 và node công bố 0 group regions. Bộ nhớ TV và
vùng TV thực tế đều có TTL 75 s mô phỏng; chưa log nhánh xóa polygon cuối
để phân biệt hết hạn với invalidation. Trong lượt này tv_regions luôn 0,
nên vùng viewing đếm ở color_regions chưa là bằng chứng polygon TV chuyên
biệt đã xác nhận. Đây là giới hạn quan sát ở bản trước mục 11; không
đồng nhất mất quan sát với người đã rời chỗ.
Minh chứng: [timeline và tham số](docs/evidence/2026-10-28/tv_memory_loss/interpretation.json).

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

Ở mốc M6 trước bản sửa tránh người động có **115 test qua**, gồm phần điều khiển,
hai backend paper, perception, TV và kịch bản động. Có hai warning SciPy
clipping bounds ở Paper2; ba file lint không chạy. Kết quả này là kiểm
chứng hồi quy, không phải số lượt điều hướng thành công.

Các cải tiến hình học, ghép dữ liệu và điều phối đã có test tương ứng;
nhánh người nằm mới có đối chứng bước đầu. Chưa có thống kê nhiều lượt về
IoU vùng xã hội, precision/recall, ID switch, thời gian tới goal, va chạm
hoặc sai số đội hình để kết luận mức cải thiện tổng thể. Chưa đủ bằng chứng
kết luận M6 tốt hơn các bản trước hay hai paper theo một tỷ lệ định lượng.

Minh chứng hồi quy: [log 115 test](docs/evidence/2026-10-28/github_tests.log).

Kiểm chứng runtime bổ sung: vùng TV đã xuất hiện 1–2 polygon, nhưng trong
mẫu 25 s thực đoàn robot gần như đứng yên; lượt quan sát bị hủy vì suy luận
camera quá cũ và coordinator báo không có đường. RTF mẫu khoảng 0,089.
Chạy D* mới trên snapshot map vật lý/xã hội gần đó vẫn cho đường 138/160
cell, chưa gồm lớp LiDAR động của coordinator và chưa đồng bộ đúng thời
điểm mọi cảnh báo. Kết quả này cho thấy nhận diện vùng TV đã có tác dụng,
nhưng chưa đủ chứng minh cải tiến điều hướng đầu cuối; cần phân biệt dữ
liệu trễ, lớp vật cản động và trạng thái lập đường. Minh chứng:
[audit runtime](docs/evidence/2026-10-28/manual_run_audit/user_run_audit.json),
[đối chiếu hai map](docs/evidence/2026-10-28/manual_run_audit/user_map_diagnosis.json).

Kiểm tra sâu hơn cho thấy cấu hình giảm tải DNN chưa giải quyết được nghẽn
mô phỏng: mẫu sau có RTF Gazebo khoảng 0,0003–0,0005, luồng chính server
gần 100% một CPU trong khi coordinator/MPC chỉ vài %. Mô hình ba robot dùng
nhiều khớp và collision mesh/tự va chạm là ứng viên cần kiểm chứng ở phần
DART; chưa có stack hoặc A/B để khẳng định nguyên nhân chi tiết. Vì vậy
chưa thể nhận cải tiến hiệu năng tổng thể từ việc giảm camera/crop/thread.
Minh chứng: [profile](docs/evidence/2026-10-28/rtf_profile/rtf_cpu_profile.json),
[stats mô phỏng](docs/evidence/2026-10-28/rtf_profile/rtf_gazebo_stats.txt).

Lượt trước đã từng phục hồi đường 144 điểm và robot tiếp tục di chuyển.
Lượt hiện tại chưa tái hiện được tính ổn định đó. Cấu hình roller tự va
chạm đã có từ trước, nên chưa thể coi nó là thay đổi mới gây suy giảm.
Các test hồi quy chưa thay thế phép so sánh runtime cùng điều kiện; nguyên
nhân khác biệt giữa hai lượt vẫn chưa được xác nhận.

Mẫu kiểm tra tiếp theo có RTF trung bình khoảng 0,124; robot đã chuyển sang
hàng dọc và tới vùng phía dưới TV. Tuy nhiên trong mẫu đang dừng
`inspect_person`, leader còn cách goal khoảng 4,06 m và log vẫn có cảnh
báo ảnh mới. Chưa đủ căn cứ xác nhận ổn định hoặc tới đích. Không có sửa
code/cấu hình trong lần đo này để quy mức phục hồi RTF cho cải tiến mới.
[Minh chứng](docs/evidence/2026-10-28/status_recheck/audit.json).

Quan sát bổ sung của người dùng là nghẽn xuất hiện khi người trong nhóm TV
chạm leader. Đọc code xác nhận giới hạn còn lại của cải tiến dự báo: lớp
map có dự báo camera, nhưng MPC vẫn kiểm tra điểm LiDAR như đứng yên;
khi thiếu tham chiếu thì robot dừng, trong khi người kinematic tiếp tục
theo lịch. Vì vậy chưa thể nhận hệ đã tránh được người đang đi vào robot
đứng yên. Đây là hạn chế của M6 làm cơ sở cho bản sửa ở mục 7. Vẫn chưa có
contact/pose/RTF đồng bộ để xác nhận quan hệ nhân quả với nghẽn DART.

## 7. Cải tiến tránh người động so với M6

Ở bản trước, dự báo người có trong lớp map xã hội nhưng MPC kiểm tra các
điểm LiDAR như vật cản đứng yên. Nếu mất đường hoặc đang giữ chỗ quan sát,
robot dừng mà người kinematic vẫn có thể tiến vào nó.

Bản sửa thêm ước lượng vận tốc từ các capture camera/cụm LiDAR còn mới và
kiểm tra chuyển động tương đối theo thời gian. Khi phương án đứng yên có
nguy cơ tiếp xúc trong khoảng 2 s, controller tìm bước nhường ngắn, ưu tiên
thoát ngang, vẫn giới hạn vận tốc/gia tốc và kiểm tra vật cản vật lý, LiDAR,
người và đồng đội. Đây là ưu tiên tránh tiếp xúc: bước khẩn có thể vượt vùng
keepout xã hội, nhưng không bỏ kiểm tra vật cản vật lý. Không có bước né
an toàn hoặc thiếu dữ liệu thì vẫn giữ dừng, không chạy mù.

Map vật lý và map planning được tách ở đầu vào MPC để vùng dự báo xã hội
không che mất bằng chứng LiDAR hoặc khóa mọi hướng thoát. Watchdog vẫn
dừng khi dữ liệu cũ; scan lặp không được làm mới tuổi quan sát. Người và
collision body giữ nguyên, không dùng việc cho người dừng để giả kết quả né.

**Kết quả kiểm chứng:** 138 test chức năng qua; sau điều chỉnh watchdog
cuối đã chạy lại 23 ca safety, đều qua. Ca feedback kinematic có người
0,35 m/s tiến tới leader không có reference giữ swept separation trên
0,47 m trong 80 bước. Có đối chứng stale data, tường chặn, đồng đội, chỉ
LiDAR và giữ dừng khi không có chỗ né. Node ROS thật ở domain riêng xác
nhận nhận đúng hai map và phát được lệnh né với reference rỗng.

**Giới hạn:** chưa chạy lại ca va chạm trong Gazebo, chưa đo contact hoặc
mức tăng RTF. Bộ kiểm thử không chứng minh tránh được mọi hướng đổi đột
ngột, che khuất hoặc tình huống đã quá sát/không còn chỗ thoát.
Minh chứng: [test](docs/evidence/2026-10-28/moving_obstacle_fix/regression_tests.log),
[safety](docs/evidence/2026-10-28/moving_obstacle_fix/safety_tests.log),
[ROS](docs/evidence/2026-10-28/moving_obstacle_fix/ros_smoke.json).

## 8. Đích né theo vận tốc người và ưu tiên hơn camera quét

So với bản né trực tiếp, bản mới tách tốc độ đo được và nguy cơ va chạm.
Nhóm chậm dùng `0,05 <= v < 0,5 m/s`, nhóm nhanh dùng `v >= 0,5 m/s`;
đây là ngưỡng kỹ thuật, không có nghĩa người “chậm” luôn chậm hơn robot.
TTC vào vùng đệm quanh robot quyết định có cần nhường hay không. Nhóm
nhanh được xét sớm hơn với lookahead 2,5 s thay vì 2 s và reserve lớn hơn.
Người đang đi xa ra hoặc đi ngang đủ khoảng cách không bị coi là sắp đâm
chỉ vì vận tốc lớn. Ước lượng chưa đủ tin cậy không được coi là vận tốc thật.

Bản trước chỉ thử các hướng vận tốc né. Bản mới dùng A* không gian–thời
gian cục bộ chọn điểm sau/trái/phải thân xe, có xét nơi người sẽ tới khi
robot tới đích tạm. Điểm nằm trên hành lang tiếp cận của người chưa đi qua
bị loại, hạn chế việc chỉ lùi rồi bị người nhanh hơn đuổi kịp. A* có ngân
sách tìm kiếm giới hạn; MPC vẫn kiểm tra rollout và có phương án né trực
tiếp dự phòng được kiểm tra nếu A* chưa ra đề xuất. Goal chính giữ nguyên.

Camera sweep trước đó giữ XY theo điểm neo và tạo reference quay. Nay MPC
báo nguy cơ tới coordinator: lượt quét bị hủy ngay, sweep mới bị chặn trong
lúc nhường, reference giữ neo được ngừng để nhánh né ưu tiên hoạt động.
Camera vẫn nhận hình; không tắt perception để làm robot đi. Hết nguy cơ,
đường được lập lại từ vị trí đo tới goal cũ. Thông báo có TTL để tránh khóa
chức năng quan sát bởi trạng thái cũ.

| Tốc độ người trong ca feedback kinematic | Khoảng cách tâm nhỏ nhất ghi nhận | Điều kiện |
|---|---:|---|
| 0,08 m/s | 0,675 m | Quan sát tổng hợp, robot ban đầu đứng, không có reference toàn cục |
| 0,35 m/s | 0,643 m | Cùng mô hình kiểm thử, kiểm tra chuyển động liên tục giữa hai bước |
| 0,80 m/s | 0,692 m | Kích hoạt theo ngưỡng nhanh/TTC; giữ kiểm tra tường và đồng đội |

Ngưỡng thân cấu hình trong các ca trên là 0,47 m. Đây không phải dữ liệu
va chạm Gazebo hay độ chính xác detector trên ảnh thật. Có 153 test chức
năng qua, hai warning SciPy và ba lint file không chạy; nhóm safety/A*/quét
có 38 test qua. Hai node ROS trong domain riêng xác nhận hủy quét, vẫn có
lệnh né và không đổi goal. Chưa đo contact/RTF hoặc kiểm chứng mọi kiểu
đổi hướng, che khuất, phát hiện muộn và không còn chỗ thoát.

Minh chứng: [hồi quy](docs/evidence/2026-10-28/astar_camera_priority/regression_tests.log),
[các ca tốc độ/A*/camera](docs/evidence/2026-10-28/astar_camera_priority/safety_tests.log),
[ROS hai node](docs/evidence/2026-10-28/astar_camera_priority/ros_smoke.json).

## 9. Né của follower khi chân người có ít tia hoặc bị che khuất

**Kết quả thử lại thực tế:** người dùng xác nhận sau bản này, hai follower
đã né được trong lượt thử, còn leader vẫn bị người va vào. Đây là quan sát
một lượt, chưa phải benchmark hoặc kết luận follower luôn tránh được.
Mẫu sau ảnh nhận được clock, LiDAR, ảnh và có lệnh né, RTF khoảng 0,207;
không thể dùng giải thích mất toàn bộ dữ liệu của lần trước cho lần này.
Các kết quả động học bên dưới chưa chứng minh hết va chạm trong Gazebo.

Lượt Gazebo sau bản A* vẫn xuất hiện người áp sát robot2 và RTF xuống
0,0008. Snapshot ở 26,483 s cho khoảng cách tâm người–robot2 là 0,385 m;
ảnh người dùng cho thấy vùng tiếp xúc/chồng lấn. Chưa có contact sensor để
định lượng va chạm, và chưa xác nhận hotspot vật lý gây nghẽn.

Bản trước bỏ cụm một tia và chỉ giữ khoảng 120 tia/scan. Bản sửa giữ đầy
đủ tia; cụm chân đơn lẻ được theo dõi nhưng vẫn cần ba capture nhất quán
để có vận tốc. Bán kính tối thiểu của ứng viên LiDAR tăng lên 0,32 m vì
một chân nhìn thấy không đại diện toàn bề ngang người. Mỗi MPC dùng thêm
scan của các robot khác, với track riêng cho từng nguồn để tránh trộn
timestamp; scan của robot khác không thay thế điều kiện LiDAR riêng còn mới
trước khi né. Các nguồn này là đo cảm biến, không lấy pose người kịch bản.

Lookahead nguy cơ tăng lên 3 s ở cả hai nhóm tốc độ, reserve chậm/nhanh
0,12/0,16 m; thay cho giá trị của bản ở mục 8. Điểm LiDAR đã thuộc track
chuyển động được kiểm tra bằng swept trajectory, không đồng thời bị giữ
đứng yên suốt rollout. Vật cản chưa có vận tốc tin cậy vẫn là điểm tĩnh.
Watchdog phát trạng thái stale data để phân biệt dừng do mất dữ liệu với
không tìm được đường né. Coordinator báo riêng khoảng hở planning/LiDAR
và vật lý/LiDAR; đường đội hình thường vẫn tuân thủ vùng xã hội.

Phần vật lý thay collision mesh thân xe, khung bánh và 18 con lăn bằng
hình trụ gần kích thước bao của mesh; giữ nguyên visual, khớp và quán tính.
Follower sau chuyển URDF→SDF vẫn có 23 collision và 21 khớp quay, còn
1 collision mesh ở camera. Tắt self-collision con lăn, giữ va chạm ngoài
với người và môi trường. Hình học này là xấp xỉ; cần kiểm tra độ bám bánh,
quỹ đạo và tiếp xúc trong Gazebo, chưa thể tuyên bố tăng RTF.

Kiểm chứng: 159 test chức năng qua, 2 warning SciPy ở Paper2; 3 lint file
không chạy. Nhóm safety có 43 ca qua, gồm cả hai follower nhận một tia chân
qua LiDAR đồng đội khi camera bị che, và vẫn giữ dừng nếu LiDAR riêng cũ.
Ca dùng bố trí ba robot đã lưu, bắt đầu trước thời điểm tiếp xúc trong mô
hình động học có phản hồi, đạt khoảng cách tâm nhỏ nhất 0,687 m so với ngưỡng
thân cấu hình 0,47 m. Đây chưa phải replay Gazebo: map vật lý trong ca kiểm
thử trống, không mô phỏng đầy đủ vật cản, tiếp xúc hay suy luận ảnh.

Minh chứng: [snapshot tái hiện](docs/evidence/2026-10-28/follower_collision/replay_state.json),
[hồi quy](docs/evidence/2026-10-28/follower_collision/regression_tests.log),
[safety](docs/evidence/2026-10-28/follower_collision/safety_tests.log),
[hình va chạm](docs/evidence/2026-10-28/follower_collision/geometry_validation.json).

## 10. Giữ ưu tiên an toàn khi chưa có đường thoát và khi người tạm dừng

Mẫu chạy sau mục 9 ghi nhận các trạng thái `no verified safe escape`,
`stale_data` xen kẽ lệnh né. Đọc code và test tái hiện hai lỗi:

- `publish_stop()` xóa cờ nguy cơ, kể cả khi robot vừa phát hiện người
  tiến tới nhưng không tìm được đường thoát. Bản mới tách lệnh dừng khỏi
  trạng thái nguy cơ, giữ tiền tố `moving_obstacle:` khi watchdog dừng do
  dữ liệu cũ. Coordinator tiếp tục ưu tiên nhánh an toàn; chỉ đánh giá lại
  nguy cơ hoặc reset clock mới nhả cờ.
- Vận tốc ước lượng về 0 làm `collision_risk` trả về không có nguy cơ, kể
  cả khi người đang dừng sát robot để quay hướng. Bản mới thêm kiểm tra
  khoảng hở cục bộ `band=close`, yêu cầu ít nhất ba capture trong 0,2 s.
  Một điểm chưa xác nhận không đủ để kích hoạt nhánh này. Bước né vẫn phải
  qua kiểm tra vật lý, người, đồng đội và cảm biến còn mới.

Hai ca mới tái hiện lỗi trước sửa; thêm đối chứng điểm đơn chưa xác nhận.
Toàn bộ 162 test chức năng qua, 2 warning SciPy ở Paper2; 3 lint file
không chạy. Nhóm safety sau sửa có 46 ca qua. Bản mới chưa được nạp vào phiên Gazebo
người dùng đang chạy, và chưa có replay chứng minh tránh tiếp xúc.
Không khẳng định hai lỗi này là toàn bộ nguyên nhân của ảnh va chạm.
Khi đã quá sát hoặc không có quỹ đạo được xác minh an toàn, robot vẫn dừng;
người kinematic không tự nhường nên đây vẫn là giới hạn chưa giải quyết.

Minh chứng: [audit sau ảnh](docs/evidence/2026-10-28/collision_retest/audit.json),
[diễn giải](docs/evidence/2026-10-28/collision_retest/interpretation.json),
[safety](docs/evidence/2026-10-28/collision_retest/safety_tests.log),
[hồi quy](docs/evidence/2026-10-28/collision_retest/regression_tests.log).

## 11. Từ TTL ngắn sang ký ức vùng viewing cần kiểm tra lại

Trước sửa, không nhìn lại TV/người đủ lâu làm hết hạn cả target và polygon,
dù chưa có bằng chứng người đã rời chỗ. Bản mới tách landmark TV tĩnh đã
quan sát nhiều lần và corridor đã xác nhận khỏi các detection hiện thời.
Giữ stamp gốc; hướng người vẫn hết hạn. Vùng giữ theo ký ức được đánh dấu
cần kiểm tra lại, tiếp tục nằm trong costmap, không chỉ còn trên marker.
Corridor target màu đã xác nhận cũng được bảo vệ nhưng giữ nguyên nhãn
heuristic; không suy thành TV chỉ vì nằm gần khu xem TV.

Khi đo được một người đang đi hoặc đổi hướng/mục tiêu, hệ thống thu hồi
corridor tương ứng và giữ vùng người khác. Mất camera đơn thuần không phải
bằng chứng đã rời. Reset bộ nhớ, rewind clock hoặc đổi geometry map xóa
ký ức cũ. Vùng nhớ chưa xác minh không tự hoàn tất lượt camera kiểm tra mới.

Smoke node ROS trong domain riêng với phép đo tổng hợp và map trống:

| Tình huống | Số vùng | Số ô keepout |
|---|---:|---:|
| Hai người đã xác nhận viewing | 2 | 832 |
| Không quan sát lại đến 200 s | 2 | 832 |
| Đo một người rời chỗ | 1 | 576 |

Timestamp bằng chứng vẫn 1,7 s, không được timer làm mới. Reset geometry
map và rewind clock xóa cache. Bộ đầy đủ trước chỉnh search cuối có 168
test qua (2 warning SciPy, 3 lint file không chạy); sau chỉnh cuối, toàn bộ
62 test social qua, gồm 7 ca mới cho bộ nhớ/kiểm tra lại.

Chưa replay Gazebo hay đo độ chính xác DNN/ID switch. Vùng nhớ chỉ là giả
thuyết bảo thủ trong phiên, có thể hạn chế đường nếu người đã rời ngoài tầm
camera; cần quan sát lại hoặc reset để giải quyết. Không lưu qua restart và
không được dùng làm chứng cứ người hiện đang xem TV.

Minh chứng: [social tests](docs/evidence/2026-10-28/persistent_viewing/social_tests.log),
[ROS tick và ô costmap](docs/evidence/2026-10-28/persistent_viewing/ros_tick_smoke.json),
[hồi quy trước chỉnh search cuối](docs/evidence/2026-10-28/persistent_viewing/regression_tests.log).

## 12. Leader phục hồi khi đã nằm trong phần dự phòng của track

**Hạn chế bản trước:** geometry đo gần leader có outer radius đã cộng dự
phòng phủ điểm đứng. MPC/A* đòi full swept clearance ngay bước đầu, nên
cả bước tăng khoảng cách cũng bị loại. Đây là một nguyên nhân tái hiện
được từ dữ liệu đo; không phải bằng chứng thân robot đã va chạm thực.

**Sửa ở bản sau:** tách body envelope ước lượng với dự phòng. LiDAR giữ
extent cụm đo, tối thiểu model 0,32 m; dự phòng hình dạng khuất 0,12 m và
dự phòng tuổi phép đo được tách riêng. Camera vẫn dùng model đầu vào,
không mặc định coi mọi điểm đo là người có kích thước chính xác.

Nhánh phục hồi chỉ dành cho track xác nhận và xe đã nằm trong buffer:
swept body gap ít nhất 0,03 m; outer gap không giảm trên đoạn, tăng ở
cuối bước. Đích cuối phải thoát cả buffer và giữ ngắn hợp lệ. Giữ kiểm
tra map vật lý, raw LiDAR, teammate, gia tốc và freshness. Điều hướng
thường vẫn dùng full buffer. Thêm diagnostics lý do dừng, không cần
suy từ marker đường đi để đoán controller đã chấp nhận quỹ đạo.

**Kiểm chứng:** test tái hiện no escape trước sửa đã có command sau sửa.
179 test chức năng qua, 56 ca safety/A*/camera qua; 2 warning SciPy,
3 lint file không chạy. Ca dựng geometry leader với map vật lý dự án và
feedback động học tăng khoảng cách track 0,563→0,803 m, body gap model
nhỏ nhất 0,085 m. Ca follower đã né trước đó vẫn qua, khoảng cách tâm
nhỏ nhất 0,687 m trong mô hình kiểm thử đó.

Node ROS riêng với camera pose/scan/map tổng hợp phát command né khi
outer gap âm nhưng body gap dương; stale scan làm watchdog dừng. Đây
không phải replay Gazebo hay phép đo contact thực. Chưa xác nhận mọi
deadlock được giải quyết, chưa có benchmark RTF cùng điều kiện.

**Đối chiếu Gazebo sau sửa, 01/11:** theo dõi 600 s thực, clock tiến
114,777 s (RTF toàn mẫu ~0,191). Nhánh uncertainty recovery có 5 transition
được ghi nhận, nhưng người dùng vẫn quan sát leader chưa né; không coi có
lệnh né hay tới gần goal là chứng minh tránh thành công. Leader có đoạn
gần như không đổi XY ~143,3 s; không có contact sensor để xác nhận an toàn.

Giới hạn lộ ra: reference rỗng ở 497/596 snapshot; log lặp chuẩn bị yield
và báo leader đã vượt follower. Predicate completion được tái hiện với
leader cách goal 0,0268 m (<0,05 m) trong khi target follower vẫn còn xa,
có thể kết thúc maneuver trước khi gửi rows rồi lập lại. Đây là reproduction
riêng, chưa đọc đầy đủ trạng thái nội bộ live. Đồng thời scan leader có
tuổi capture >0,3 s ở 122/596 snapshot, có receipt gap ~17,8 s thực khi
mô phỏng chậm. Bản phục hồi buffer chưa giải quyết các lớp điều phối/
freshness này. Đây là kết quả kiểm chứng giới hạn, chưa có bản sửa mới.
Minh chứng: [phân tích](docs/evidence/2026-11-01/audit_10min_115903/analysis.json),
[biểu đồ](docs/evidence/2026-11-01/audit_10min_115903/runtime_plot.png).

**Giới hạn và phối hợp ba phần:** body model/uncertainty chưa hiệu chuẩn
thống kê; camera và nhiều LiDAR vẫn có track riêng, chưa fusion identity
chung. Camera sweep nhường ưu tiên cho guard; vùng xã hội và map vật lý
có vai trò riêng; chỉ MPC phát command của từng robot ở backend baseline.
Các phần vẫn có thể chặn nhau qua ràng buộc và tranh CPU. Cần đo tuổi
dữ liệu, thời gian MPC và rejection trước khi tăng rate hoặc nới watchdog.
Luồng và các bước tối ưu chưa triển khai được tách rõ trong
[tài liệu camera–LiDAR–điều khiển](docs/LEADER_CAMERA_LIDAR_DIEU_HUONG.md).

Minh chứng: [hồi quy](docs/evidence/2026-10-28/leader_uncertainty_recovery/regression_tests.log),
[safety](docs/evidence/2026-10-28/leader_uncertainty_recovery/safety_tests.log),
[ROS smoke](docs/evidence/2026-10-28/leader_uncertainty_recovery/ros_smoke.json).


## 13. Kiểm tra loại ảnh hưởng RGB-D khỏi lượt thử né

**Hạn chế trước:** camera/DNN, vùng xã hội, LiDAR và controller cùng chạy,
khó tách tác động khi leader đứng yên. **Thay đổi:** profile chẩn đoán tắt
RGB-D/DNN/suy luận xã hội, giữ nguyên hình học robot và LiDAR đa tầng,
D* Lite cùng ba MPC. Profile thường vẫn bật camera.

**Kiểm chứng:** 4 test profile qua; 180 s thực trong Gazebo, cả ba robot
có dịch chuyển và trạng thái yield. Leader cuối mẫu cách goal ~0,119 m.
Vẫn có nhiều lần không tìm được quỹ đạo an toàn, reference rỗng và scan
quá tuổi. RTF mẫu ~0,2994; điều kiện khác lượt camera-on nên chưa kết luận
mức tăng do tắt camera. Không có contact measurement, chưa chứng minh né
thành công hay nguyên nhân duy nhất nằm ở camera.
[Minh chứng](docs/evidence/2026-11-01/lidar_only_trial/runtime_180s/analysis.json).

**Đọc tiếp phiên camera-off (01/11):** mẫu 120 s xác nhận leader có 10/120
snapshot bị chặn ngay MPC bước1 do track, dù có reference; ví dụ scan tuổi
0,190 s, track reject 11, các lý do map/lidar/peer bằng 0. Đồng thời có 20
snapshot scan leader quá 0,3 s và 33 reference rỗng. Có lệnh A* né nhưng chưa
đối chiếu contact hoặc danh tính track, không coi là tránh người thành công.
Lỗi vẫn mở, gồm cả peer spacing dưới footprint ở log tiếp theo.
[Minh chứng](docs/evidence/2026-11-01/leader_audit_encounter/analysis.json).

## 14. Tác nhân người có động học và hoạt ảnh đi bộ

**Chính sách hiện hành (NK-047):** người đi theo lịch sim time và không
nhường xe; robot phải tự né. Cơ chế người giảm tốc/dừng ở các đoạn dưới
là bước thử trước đó, đã được thay theo yêu cầu kiểm thử của người dùng.


**Hạn chế trước:** mesh cứng trượt theo tuyến tốc độ hằng, đổi tốc độ đột
ngột; lịch hoạt động vẫn tiến khi người gặp robot, không có phản ứng nhường.

**Thay đổi sau:** route tăng/giảm tốc .45 m/s², quay mượt tối đa .75 rad/s;
người dự báo vị trí tương đối 1,5 s để giảm tốc/dừng nhường ba robot. Đồng
hồ riêng của từng tác nhân giữ liên tục các giai đoạn khi dừng/chạy lại.
Skeleton walking có animation khớp; phase đi theo quãng đường, dừng chân
khi đứng chờ. Actor và proxy collision cùng vị trí; marker lấy pose thật.
Môi trường tĩnh và thuật toán điều hướng giữ nguyên. Đây là cải tiến độ
thực tế của môi trường, không phải bằng chứng cải tiến khả năng né robot.

**Kiểm chứng:** test C++ chạy plugin thật với ECM tổng hợp xác nhận dừng
trước robot, khoảng cách tâm ≥.55 m trong ca test, phase chân dừng, resume
không nhảy bù và reset. Ba test Python kiểm giới hạn động học, skin/root/
loop và ánh xạ collision. Tổng 186 test Python và 1 CTest C++ qua; 2 warning
SciPy, 3 file ament lint không chạy. Hồi quy đầy đủ lưu tại
[log test](docs/evidence/2026-11-01/realistic_people/regression_tests.log).
Gazebo smoke xác nhận pose vật lý người đi tuần/rời ghế và có actor trong
ảnh/ECM. Chưa kiểm đủ chu kỳ, contact hay độ trượt chân bằng video.

**Giới hạn:** vẫn là tác nhân kinematic; ngưỡng nhường và tốc độ clip chưa
hiệu chuẩn bằng dữ liệu người thật. Chưa né người–người hoặc tự đổi tuyến;
robot có thể đi vào người đã dừng. Đứng/ngồi là chuyển tư thế gần đúng,
uống nước chỉ là dừng ở bình. Cần kiểm thử lặp có contact/clearance, tách
người chủ động nhường khỏi hiệu quả leader tự né.
[ECM test](docs/evidence/2026-11-01/realistic_people/plugin_ecm_test.log).


**Đính chính kiểm chứng GUI và bản sửa đồng bộ:** bản trước đã xác nhận
pose vật lý và actor tồn tại, nhưng chưa chứng minh hình người di chuyển
trên GUI. Người dùng phát hiện GUI đứng yên; hai ảnh liên tiếp tái hiện lỗi
trong khi server pose đã đổi. Nguyên nhân được xử lý: setter actor Fortress
không tự đánh dấu Data() đã đổi để đồng bộ sang GUI.

Bản sau đánh dấu thay đổi TrajectoryPose và AnimationTime mỗi lần cập nhật.
CTest thêm kiểm tra change flags, giữ ca nhường từng robot; 1 CTest và 3
Python test mục tiêu qua. Sau restart, hai ảnh GUI xác nhận patrol áo xanh
lá/quần xanh đổi vị trí; proxy tương ứng dịch chuyển 1,254 m trong 3,143 s
mô phỏng. Đây là sửa hiển thị môi trường; chưa chứng minh độ tự nhiên của
gait, đầy đủ chu kỳ hay khả năng né leader.
[Hai ảnh và pose](docs/evidence/2026-11-01/actor_visibility/after/comparison.json).


**Sửa hướng bước đi sau đồng bộ GUI:** bản trước cộng góc 90° cố định,
trong khi walking asset có mũi chân và root locomotion hướng +X, gây trượt
ngang/lùi khi nhìn trong Gazebo. Bản sau đo hướng forward từ hai bàn chân
của asset và gửi hiệu chỉnh theo metadata; yaw render = yaw tuyến − yaw
forward mesh. Tốc độ clip cũng lấy từ quãng đường root/thời lượng clip.

Kiểm chứng: 187 test Python và 1 CTest qua; 2 warning SciPy, 3 lint file
không chạy. CTest kiểm 4.730 mẫu dịch chuyển trên hai chu kỳ tuyến trong
ECM tổng hợp, dot hướng render với vận tốc >.999, đồng thời giữ test nhường
ba robot. Hai ảnh/state Gazebo xác nhận patrol tiếp tục dịch chuyển, hướng
render đoạn +X đã bỏ lệch 90°. Chưa kiểm toàn chu kỳ Gazebo, độ trượt chân,
động tác quay bước hoặc mô hình người thực; không coi đây là sửa né leader.
[Kiểm thử](docs/evidence/2026-11-01/walk_heading/plugin_heading.log),
[minh chứng ảnh/state](docs/evidence/2026-11-01/walk_heading/comparison.json).


**Điều chỉnh kịch bản để kiểm tra robot tự né (NK-047):** trước đó người
chủ động dừng nhường robot, làm giảm mức thử thách và khó tách hiệu quả
né của robot. Bản sau bỏ dự báo/giảm tốc/dừng vì robot, chạy lịch trực tiếp
theo thời gian mô phỏng. Giữ các dừng theo hoạt động và quay ở góc; hoạt
ảnh, căn hướng và đồng bộ GUI không đổi.

Kiểm chứng: build, 187 test Python và 1 CTest qua; 2 warning SciPy, 3 file
ament lint không chạy. Test plugin đặt riêng từng robot1/2/3 trên tuyến:
người tiếp tục đi; đổi robot ra xa cho cùng pose và phase chân khi chạy
lại cùng sim time. Đây là ECM tổng hợp, chưa phải kiểm chứng physics/contact
trong Gazebo. Thay đổi làm kịch bản không nhường robot, không chứng minh
leader đã né tốt hơn; người kinematic vẫn có thể đi vào robot không né kịp.
[Minh chứng](docs/evidence/2026-11-01/pedestrians_no_yield/plugin_test.log).


## 15. Khôi phục kiểm thử follower và giảm tải luồng điều hướng

**Hạn chế trước:** NK-034 ghi nhận hai follower né được ở một lượt thử,
nhưng chưa có benchmark lặp. Các thay đổi tiếp theo vẫn có lúc cả ba dừng
khi track chắn route nhưng không đe dọa robot đứng yên. Runtime nhận cả
link transforms và clock tần số cao, gây tải executor/deserialize. Một
lượt kiểm tra còn chỉ có Gazebo, các node ROS đã mất nên không đo né được.

**Sửa sau:** giữ ca hồi quy follower và kiểm cả hai vai; thêm nhánh escape
khi confirmed track chặn rollout, duy trì có hạn khi reference rỗng. Thử
đích né thẳng an toàn trước A*, cùng predicates và budget. Thêm reserve
peer theo tuổi pose, phục hồi spacing sớm từ<.48 m hướng tới.56 m, giữ
footprint .32 m. Giữ đầy đủ kiểm tra map/raw scan/body/peer/freshness.

Luồng robot pose C++ chỉ có 3 model ở 20 Hz sim; clock 100 Hz sim riêng cho
planner, giữ clock đầy đủ cho điều khiển bánh xe. Timestamp theo capture,
scan cho phép 20 ms skew nhưng không tăng stale TTL. Actor update định kỳ,
GUI dynamic state 30 Hz wall. Không đổi physics step, LiDAR hay dùng human
ground truth làm đầu vào robot. Hai scene và hai backend paper được giữ.

**Kiểm chứng:** 199 test Python và CTest qua (2 warning SciPy, 3 lint file
không chạy). Ca dựng trước: cả 3 controller dừng ở step 6 do track; sau có
lệnh né ngang, vẫn dừng khi stale scan. Ca hình học follower cũ và hoán đổi
vai qua. Local search 50 lần cùng input: median edge checks 171→7, khoảng
1,13→0,040 ms; chỉ là microbenchmark local search, không phải RTF/MPC đầy đủ.

Profiler khoảng 20 s cho thấy coordinator tốn ~14,3 s ở nhận/deser message,
không chủ yếu ở planner; profiler có overhead. Sau dùng stream gọn, probe
đọc đúng≈100 clock và≈20 pose messages mỗi giây mô phỏng, pose chỉ có ba
robot. Mẫu CPU khác đoạn hoạt động cho thấy tải Python giảm, nhưng không
phải A/B kiểm soát và không quy mọi chênh lệch RTF cho một thay đổi.

**Giới hạn:** lượt Gazebo trung gian vẫn có cặp robot quá sát, là cơ sở thêm
reserve/recovery sớm; không xem đó là kiểm thử né thành công. Chưa có contact
sensor hoặc benchmark lặp cùng điều kiện để khẳng định follower/leader hết
va chạm, hoặc tốt hơn trạng thái quan sát ở NK-034. Cần controlled encounter
và đo đồng bộ clearance, tuổi dữ liệu, CPU/RTF ở cả ba robot.
[Hồi quy](docs/evidence/2026-11-01/avoidance_rework/regression_final.log),
[profiler](docs/evidence/2026-11-01/avoidance_rework/coordinator_profile.txt),
[benchmark cục bộ](docs/evidence/2026-11-01/avoidance_rework/escape_benchmark.json).


Bổ sung kiểm chứng cuối NK-048: dự phòng peer có xét vận tốc tương đối đo
được và quãng đường hãm (giả định deceleration .15 m/s², chưa hiệu chuẩn).
Test lag hai trục và hồi quy tổng199 ca qua. Mẫu Gazebo60 s cuối có khoảng
cách tâm nhỏ nhất lấy mẫu robot2/leader≈.427 m, RTF trung bình≈.39; không có
contact sensor và khác pha/goal so với lượt trước, không kết luận collision-free
hoặc mức tăng RTF nhân quả. [Phân tích](docs/evidence/2026-11-01/avoidance_rework/runtime_braking/analysis.json).


## 16. Xác nhận tiếp xúc bằng physics thay cho khoảng cách lấy mẫu

**Hạn chế trước:** chỉ có khoảng cách tâm theo snapshot và ảnh; không biết
contact giữa các mẫu, cặp model/part hay thời gian chạm. Người dùng vẫn
quan sát người đâm leader; min khoảng cách ở NK-048 không chứng minh hết lỗi.

**Thay đổi sau:** CollisionAudit đọc contact từ physics Gazebo, ghi begin/
update/end/reset theo cặp model, thời gian mô phỏng, collision và điểm chạm.
ROS monitor ghi JSONL và marker đỏ; status phân biệt thiếu coverage/chưa
lấy mẫu khi pause. Cả hai scene và profile camera-off đều có diagnostic.
Không thay collision geometry, luật né hoặc cấp ground truth vào perception.

**Kiểm chứng:** 208 test Python qua (2 warning SciPy, 3 lint file không
chạy). Physics fixture riêng cho robot1/2/3 đều có begin/end;
near-miss y1 m không có contact, không tính tiếp xúc sàn thường. Kiểm thử
kín physics→bridge→JSONL/marker qua: ghi begin/end thật, nhận điểm đỏ và xóa
khi tách. Đây là thân robot fixture đơn giản, không phải replay URDF leader
đầy đủ hay benchmark né người. [Physics](docs/evidence/2026-11-01/collision_audit/physics_validation.json),
[ROS/marker](docs/evidence/2026-11-01/collision_audit/wire_validation_verified.json).

**Giới hạn:** phiên chính không còn chạy khi thử gắn trực tiếp, chưa xác
nhận nạp sensor vào phiên đó; giữ yêu cầu không tự resume. Bộ đo sẽ bật ở
lượt launch tiếp theo. Chưa đo overhead, lực va chạm/độ xuyên hoặc contact
chỉ giữa robot rollers. Contact của proxy không đồng nghĩa mọi va quệt
visual mesh. Bổ sung phép đo không chứng minh đã sửa xong leader né người.


**Bổ sung kiểm chứng toàn scene (NK-051, 01/11/2026):** phiên LiDAR-only mới
đã nhận đủ contact coverage3 robot/14 proxy người. Physics ghi leader
`robot3` chạm `tv_viewer_a_walking` ở thân xe từ sim29.751 đến35.557 s
(5.806 s). Nhờ phép đo mới, xác nhận lỗi va chạm vẫn còn; không công bố đã
cải thiện né. Mẫu ROS sau contact15 s wall có RTF≈.246 (stats riêng≈.211),
leader cách goal≈.048 m, còn giữ dừng do escape không an toàn/dữ liệu quá tuổi;
robot2 có lệnh escape. Không thu đồng bộ trước contact nên chưa quy nguyên nhân,
không so hiệu năng với baseline khác điều kiện. Không thay thuật toán trong audit.
[Contact và phân tích](docs/evidence/2026-11-01/collision_live_audit_143718/analysis.json),
[mẫu ROS](docs/evidence/2026-11-01/collision_live_audit_143718/followup/summary.json).


## 17. Thoát vùng đệm map trong nhánh né khẩn cấp

**Hạn chế trước:** khi tracking đi vào đệm map nhưng thân xe còn an toàn,
kiểm sweep bắt buộc inflation ngay tại điểm xuất phát loại cả hướng đi ra
xa vật cản. Hàng đợi sensor còn giữ nhiều mẫu khi executor chậm.

**Sửa sau:** dùng cùng predicate cho search và rollout: chỉ phục hồi khi
clearance đầu>=bán kính xe+1cm, toàn sweep không giảm clearance và endpoint
tăng khoảng cách; đích dừng recovery phải ngoài đệm đầy đủ. Giữ kiểm tra
người, peer và freshness. Log thêm lý do loại ứng viên. Cloud projector và
scan subscriber MPC ưu tiên mẫu mới bằng BEST_EFFORT depth1. Cơ chế yêu cầu
replan về goal sau khi hết nguy cơ vốn đã có, không coi là chức năng mới.

**Kiểm chứng:** tình huống tổng hợp không reference ở goal, xe cách biên
map .17m trong đệm .18m, người tiến tới: predicate cũ fail cả3 vai, mới qua
cả3, giữ khoảng cách sweep người>.47m theo mô hình kinematic. Test loại
hướng sát tường hơn, đi song song trong đệm, thiếu reserve thân và xuyên ô
map. Tổng212 test Python qua, gồm2 hồi quy follower cũ;2 warning SciPy,
3 file lint không chạy. Build2 package qua.
[Hồi quy](docs/evidence/2026-11-01/escape_margin_fix/regression.log),
[đối chứng predicate](docs/evidence/2026-11-01/escape_margin_fix/predicate_ablation.json).

**Giới hạn:** chưa replay Gazebo ca contact NK-051, chưa quy lỗi map-buffer
là nguyên nhân của ca đó, chưa đo QoS có giảm latency/RTF hay không. Không
khẳng định đã hết va chạm. Process đang chạy chưa nạp bản sửa; không restart
trong tác vụ này. Reserve1cm chưa được hiệu chuẩn theo động học Gazebo.


**Bổ sung thực nghiệm NK-053:** phiên mới có log diagnostic mới của NK-052
nhưng physics vẫn ghi leader chạm người quay về TV sim106.239→108.617s
(2.378s). Mẫu15s sau contact có leader phát lệnh né, status rear/fallback,
nhưng nhiều lần64 ứng viên bị track loại và scan quá tuổi. Không quy lỗi
trước contact từ mẫu sau; nhãn rear chưa phân biệt direct shortcut với
lattice A*. Kết quả tổng hợp mục17 không đại diện thành công trong Gazebo.
[Contact](docs/evidence/2026-11-01/leader_contact_recheck/contacts.jsonl),
[mẫu ROS](docs/evidence/2026-11-01/leader_contact_recheck/summary.json).


## 18. Chia sẻ hướng né đã kiểm tra giữa follower và leader

**Hạn chế trước:** có trao đổi prediction để tránh nhau nhưng không tận dụng
hướng thoát của follower làm phương án ưu tiên cho leader.

**Sửa sau:** dùng prediction MPC kèm status checked-yield còn hạn của peer
để gợi ý hướng world. Leader tự tạo đích từ vị trí của mình và kiểm tra lại;
ưu tiên robot1→robot2→robot3 tránh vòng tham khảo. Rút gợi ý khi peer dừng,
dữ liệu cũ, lệch pose hoặc ở xa. Không bỏ ràng buộc đồng đội, không sao chép
lệnh/endpoint, không buộc robot đang bị đe dọa đứng chờ. Đây là phối hợp
hướng; chưa có scheduler với quyền đi độc quyền/ACK.

**Kiểm chứng:**12 test mới qua, gồm leader dùng hướng follower, thu hồi khi
hold, từ chối hướng bị xe thứ ba chắn và dữ liệu sai/cũ. Cùng tình huống
dựng, leader đổi hướng cmd_y từ+.07391 sang−.07391m/s khi có peer checked-yield;
không coi đây là số đo cải thiện tỷ lệ né. Hồi quy toàn bộ224 test Python
qua (2 warning SciPy,3 file ament lint không chạy). Build planner và import
module từ install qua.
[Hồi quy](docs/evidence/2026-11-01/cooperative_escape/regression.log).
[Tests](docs/evidence/2026-11-01/cooperative_escape/guidance_tests.log),
[đối chứng](docs/evidence/2026-11-01/cooperative_escape/direction_comparison.json).

**Giới hạn:** chưa replay Gazebo, chưa xác nhận sửa được contact NK-053 hoặc
cải thiện RTF. Dữ liệu track sai/stale vẫn có thể gây hold. Chưa có cam kết
hành lang dài hạn; hint không chứng minh peer sẽ thực hiện đúng dự đoán.


## 19. Phản ứng sớm và giảm chặn luồng nhận dữ liệu MPC

**Hạn chế trước:** vận tốc cần ba capture (5Hz tương ứng .4s giữa mẫu đầu
và mẫu thứ3); TTC xét robot đứng yên; nhận scan và tính MPC chung executor
một luồng; search/rollout chưa có ngân sách thời gian thực.

**Sửa sau:** hai mẫu nhất quán có provisional velocity, ba mẫu vẫn xác
nhận; TTC dùng vận tốc tương đối người–xe. Ingress callback group riêng
và executor2 threads chỉ lưu message mới nhất, control cập nhật state tuần
tự và giữ receipt time. Thêm deadline mềm control60ms/A*8ms, ưu tiên hướng
né phù hợp, chỉ phát candidate đã kiểm đầy đủ. Không bỏ freshness, body
clearance hay peer checks; budget hết chưa có đường đầy đủ thì dừng.

**Kiểm chứng:**234 test Python qua (2 warning SciPy,3 file lint không chạy),
gồm10 test mới về early motion, TTC, deadline và inbox; cả3 vai có lệnh
né ở mẫu thứ2 trong input dựng. Build qua. Kiểm riêng ROS domain99 trên
MPC thật nhận scan trong khi nhóm control bị giữ. Event probe nhả GIL,
không đo latency khi CPU bận. 5Hz cho khoảng capture hai mẫu .2s thay vì
.4s của ba mẫu; đây không phải số đo tăng tốc end-to-end.
[Hồi quy](docs/evidence/2026-11-01/early_reaction/regression.log),
[ROS](docs/evidence/2026-11-01/early_reaction/ingress_validation.json).

**Giới hạn:** chưa replay contact Gazebo hoặc benchmark RTF/latency, chưa
khẳng định hết va chạm. Deadline kiểm giữa các bước không ngắt một phép
geometry đang chạy và không loại bỏ Python GIL; không bảo đảm thời gian
thực tuyệt đối. Track sai/occlusion hoặc người đã quá sát vẫn có thể gây
hold. Hai mẫu provisional chưa thay thế chất lượng xác nhận ba mẫu.


## 20. Sửa hồi quy đứng im sau khi tách ingress và thêm budget

**Hạn chế NK-055:** inbox gộp theo topic làm mất một trong hai callback
planning/physical cùng `/map`. Sau sửa inbox, normal beam12 vẫn hết60ms
trước khi đủ horizon nên xe liên tục stop. Test inbox một consumer và
các ca không deadline trước đó chưa phát hiện hai lỗi vận hành này.

**Sửa:** gộp riêng theo (topic,callback); finite-budget normal pass giữ1
nhánh mỗi depth để kiểm xong cả horizon trước phát lệnh. Không bỏ kiểm
sweep, không phát quỹ đạo dở. Nhánh không deadline giữ beam12.

**Kiểm chứng:**25 test mục tiêu qua, gồm map nhiều consumer và cả3 vai
chạy normal MPC có60ms budget trong corridor trống. Mẫu live10s giữ nguyên
Gazebo/goal sau sửa: cả3 có lệnh khác0, dịch chuyển tâm≈.184/.161/.094m.
Đây là xác nhận thoát đứng im hoàn toàn, không phải benchmark né người.
[Tests](docs/evidence/2026-11-01/map_inbox_fix/tests_final.log),
[live](docs/evidence/2026-11-01/map_inbox_fix/runtime_summary.json).

**Giới hạn:** chưa chạy lại toàn bộ test, chưa chứng minh đạt goal/hết
contact. Leader/follower vẫn có hold do track và hết budget. Beam1 có thể
mất phương án cục bộ mà beam12 tìm được; chưa đo tradeoff chất lượng đường
đi hoặc RTF. Không dùng mẫu khác pha để kết luận cải thiện tỷ lệ né.


**Bổ sung NK-057:** mẫu10s tiếp theo có robot1/2/3 lần lượt2/28,6/27,2/31
lệnh khác0; leader vẫn đổi giữa track hold/hết budget, stale scan và escape.
Ngay finite beam1 vẫn có normal MPC timeout. Vì vậy mục20 chỉ xác nhận
thoát đứng im hoàn toàn, chưa khôi phục chuyển động liên tục. Count lệnh
không phải tỷ lệ thành công và mẫu khác pha không phải A/B. Chưa đo đồng
bộ reference để định lượng ảnh hưởng của coordinator xóa reference/replan.
[Runtime](docs/evidence/2026-11-01/stop_go_audit/runtime.json).


## 21. Ổn định chuyển bám đường–né–phục hồi và kiểm quỹ đạo trước branching

**Hạn chế trước:** safety message xóa đường/reference cả đội, hết nguy cơ
lại replan; guard còn phát normal trước biết MPC có lệnh. Ngay beam1 vẫn
có thể hết60ms trước khi duyệt đủ proposals/horizon.

**Sửa sau:** giữ route và cấp reference hợp lệ trong safety; xe active
nhận target giữ tại pose thực, xe khác chỉ kết thúc horizon cũ rồi giữ,
không ngoại suy/gia hạn cache. Sau hết nguy cơ .4s mới phục hồi/replan
một lần. Tách hazard_clear khỏi normal. Kiểm một rollout tracking đầy đủ
trước branching; finite escape chọn candidate hợp lệ đầu tiên. Không dùng
lệnh cũ hoặc quỹ đạo dở, vẫn kiểm map/LiDAR/track/peer và freshness.

**Kiểm chứng:**241 test Python qua,2 warning SciPy,3 file lint không chạy;
build qua. Test giữ route/cache, hysteresis và loại rollout bị raw scan/
peer chắn hoặc sensor quá tuổi. Live20s giữ Gazebo/goal: sampled travel
robot1/2/3≈.074/.321/.175m; cuối mẫu leader cách goal≈.039m, reference cuối
đủ27 pose. Status changes không có normal-MPC timeout, vẫn có hold và
budget hết ở nhánh escape. Không dùng số count message để kết luận tỷ lệ
né hoặc mức tăng hiệu năng so với mẫu khác pha.
[Hồi quy](docs/evidence/2026-11-01/stable_handoff/regression.log),
[live](docs/evidence/2026-11-01/stable_handoff/analysis.json).

**Giới hạn:** chưa benchmark lặp/kiểm hết contact; track quá sát và sensor
stale vẫn có thể dừng. Chọn candidate hợp lệ đầu tiên không bảo đảm tối
ưu chi phí trong toàn bộ tập ứng viên. Xe gần goal có thể đứng yên hợp lệ;
không đồng nhất mọi cmd0 với mất khả năng điều khiển.


**Đối chiếu bảo toàn kết quả mục9 (NK-059):** thành công follower người dùng
quan sát tại NK-034 vẫn được giữ nguyên. Các bản sửa leader tiếp theo thay
đổi cả controller/coordinator dùng chung3 xe; giữ test hình học follower
chưa bảo vệ đủ runtime. Hai hồi quy inbox/map và deadline NK-056 là bằng
chứng cụ thể. Chưa có replay cùng điều kiện và snapshot đầy đủ NK-034 nên
chưa xác nhận đã giữ hoặc khôi phục được hành vi follower cũ; không dùng
unit test qua để suy ra điều đó. Chưa quy toàn bộ lỗi hiện tại cho một
thay đổi riêng lẻ. Lượt đối chiếu này không thay thuật toán hoặc chạy test.


## Trạng thái khôi phục baseline tại NK-060

Theo yêu cầu người dùng, nguồn hiện hành trở về mã của lượt NK-032 được
xác nhận hai follower né tại NK-034 (mục9). Các sửa NK-033 chưa được nạp
vào lượt đó, nên không lấy timestamp mục nhật ký làm tên release giả.
Khôi phục controller, track/A*, perception/config/world và lịch người cũ;
đưa các thử nghiệm deadline/inbox/cooperative hint/compact clock và hành
vi/hoạt ảnh sau này ra khỏi baseline. Giữ hai paper và hai môi trường.

Candidate qua159 test Python,2 warning SciPy,3 lint file không chạy; build
sạch2 package và parse launch4 chế độ qua. Bốn module điều khiển chính khớp
candidate tái dựng. Đây không phải xác nhận mới về tỷ lệ né hoặc RTF.
Nguồn được dựng lại từ Git base và lịch sử edit; các paper untracked và
wiring tích hợp được giữ, không gọi toàn workspace là snapshot bit-for-bit
của NK-034. Chưa mở lại Gazebo sau khôi phục; leader vẫn có lỗi cũ đã biết.
[Phạm vi/provenance](docs/RESTORE_NK034.md),
[hồi quy](docs/evidence/2026-11-01/nk034_restore/regression.log),
[manifest](docs/evidence/2026-11-01/nk034_restore/restoration_manifest.json).


**Bổ sung kiểm chứng nguồn khôi phục (NK-062):** người dùng đã chạy camera
và báo leader né sai phía khi follower đang né. Dữ liệu có3đoạn leader
bodyvy âm đồng thời follower yielding; LiDAR vùng phải ghi min≈1.088/
1.422/1.086m, chưa gán được các return là người. Một đoạn observer không
nhận scan mới trong≈4.398s wall, không đủ chứng minh MPC dùng cùng frame.
Baseline đã được chạy thực tế sau khôi phục nhưng chưa replay có kiểm soát
hay chứng minh giữ được mọi hành vi follower; test159 ca không thay kết
luận đó. Phiên đã dừng theo yêu cầu, chưa sửa thuật toán trong audit này.
[Phân tích và giới hạn](docs/evidence/2026-11-01/right_escape_audit/analysis.json).


## Bổ sung công cụ kiểm chứng quỹ đạo — NK-063

**Hạn chế trước:** log cảm biến/lệnh cho biết robot nhận dữ liệu gì nhưng
thiếu pose thực của toàn bộ người và đồ vật, khó xác định hướng né và
chồng lấn từ ảnh Gazebo. Không thể phát lại chính xác session cũ chỉ bằng
lịch người đã định sẵn.

**Bổ sung sau:** plugin chỉ đọc ECM ghi pose model/actor20Hz; metadata hình
học cố định theo phiên. Trình phát lại nhìn từ trên xuống có timeline,
vệt người/xe, hướng thân và vận tốc đo, nhãn trái/phải/tiến/lùi theo thân,
PNG có thời điểm và HTML độc lập. Hình học có xét khoảng cao để đánh dấu
chồng lấn ước tính. Ground truth chỉ dùng đánh giá, không cấp cho điều hướng.

**Kiểm chứng:** build qua;164 test Python qua,2 warning SciPy,3 lint file
không chạy. World riêng ghi50 đối tượng; fixture thêm3 cylinder robot
scripted ghi53 đối tượng/90 frame, có pose thay đổi. Firefox kiểm nhãn
hướng, overlap/chiều cao và thao tác tua/bước/chạy qua. Bốn module điều
hướng và geometry hai world được giữ nguyên ngoài plugin recorder.
[Minh chứng](docs/evidence/2026-11-01/ground_truth_replay/),
[ảnh trình phát lại](docs/evidence/2026-11-01/ground_truth_replay/viewer.png),
[kết quả trình duyệt](docs/evidence/2026-11-01/ground_truth_replay/browser_validation.json).

**Giới hạn:** chưa kiểm thử phiên đầy đủ3 URDF/MPC với replay, chưa đo
RTF/overhead hoặc tỷ lệ tránh va chạm. Envelope robot tròn radius.15m,
z0..0.2m và primitive SDF là xấp xỉ, không contact physics; chưa mô tả đầy
đủ mast/bánh/mesh và root roll/pitch.20Hz có thể bỏ sót tiếp xúc giữa mẫu.
Đây là cải tiến khả năng quan sát/kiểm chứng, chưa là cải tiến thuật toán né.


## Xác nhận tiếp xúc bằng physics — NK-065

**Hạn chế trước:** viền đỏ NK-063 chỉ là envelope chồng lấn ước tính,
không đủ khẳng định robot đã tiếp xúc collision người/vật cản.

**Sửa sau:** khi chủ động ghi replay, yêu cầu ContactSensorData trên các
collision sẵn có của3 xe; đọc kết quả Physics từng bước, gom vào frame20Hz.
Viền đỏ nay dành cho contact engine ghi nhận, kèm cặp collision/thời điểm/
điểm tiếp xúc; cảnh báo geometry chuyển cam. Không có depth thì để null.
Không thay thuật toán né hoặc hình học vật lý; vẫn không ghi tự động khi
chạy thường.

**Kiểm chứng:** build qua,5 test replay qua; fixture physics riêng2500 bước,
50 frame ghi robot3↔person_contact, robot1↔nền; ca robot2 cách khối10mm
không contact, frame trước chạm cũng không contact. Điểm tiếp xúc có dữ
liệu, depth không được engine cung cấp. Firefox kiểm thông báo contact và
bản ghi thiếu dữ liệu. Bốn module core điều hướng giữ nguyên.
[Physics fixture](docs/evidence/2026-11-01/physical_contacts/validation.json),
[kiểm UI](docs/evidence/2026-11-01/physical_contacts/browser_validation.json).

**Giới hạn:** chưa thử lại full3 URDF/MPC/người đi hoặc benchmark overhead.
Xác nhận là với khối collision Gazebo (người dùng proxy), không mesh da/
quần áo. Engine/mask hoặc actor thiếu collision vẫn có thể bỏ sót; không
có contact ghi nhận không chứng minh tuyệt đối không va chạm. Thành công
công cụ xác nhận chưa chứng minh thuật toán né đã được cải thiện.


**Bổ sung kiểm chứng runtime NK-066:** bản ghi người dùng `thu_ne_01`
(1619 frame,0.001–80.901s sim) có contact physics giữa leader robot3 với
người xem TV đang đi tại29.701–32.268s và follower robot2 với người tuần
tra tại79.626–80.901s. Cơ chế NK-065 đã nhận contact trên robot đầy đủ trong
phiên người dùng, mở rộng bằng chứng fixture; chưa là benchmark lặp.
Leader/follower2 gần đứng yên khi người tiếp cận, nên chưa xác nhận khôi
phục baseline đã xử lý né ổn. Không thấy contact ngoài nền robot1 trong
đoạn ghi. Không có scan/camera/cmd/goal nên chưa quy nguyên nhân cho độ trễ
perception hoặc nhánh hold. Thuật toán chưa thay đổi trong audit này.
[Phân tích](docs/evidence/2026-11-01/latest_replay_audit/analysis.json),
[quỹ đạo đo](docs/evidence/2026-11-01/latest_replay_audit/trajectories.png).


## Khoanh vùng nguyên nhân xe đứng yên — NK-067

**Hạn chế trước:** replay NK-066 xác nhận contact và xe gần đứng yên,
nhưng thiếu sensor freshness, reference, command và nhánh quyết định nên
chưa phân biệt nhận diện muộn với điều khiển giữ xe hoặc lỗi thực thi lệnh.

**Bổ sung sau:** chẩn đoán bật thủ công ghi tại controller/coordinator,
không subscribe thêm toàn bộ sensor. Lưu cửa sổ trước/trong/sau dừng gồm
reason, command, pose đội, capture/receipt ages, tracks/tốc độ/TTC, reference/
goal/observation, A* và counters loại ứng viên bởi map/LiDAR/moving/peer.
Có trigger khi lệnh khác0 nhưng pose đội gần đứng yên; analyzer ghép với
contact và pose Gazebo. Chạy thường vẫn không ghi; không đổi cost/ngưỡng né.

**Kiểm chứng:** build qua;180 test Python qua,2 warning SciPy,3 lint file
không chạy. Tracking cả3 xe và ca escape cho command/rollout giống khi
tắt/bật capture; test window/reset/IO và map-reject/analyzer qua. ROS smoke
domain211 với timer thật ghi đúng lý do thiếu đầu vào ở controller và
coordinator; wrapper activation qua phép thử executable stub.
[Hồi quy](docs/evidence/2026-11-02/stop_diagnostics/regression.log),
[ROS smoke](docs/evidence/2026-11-02/stop_diagnostics/ros_smoke.json),
[hướng dẫn](docs/CHAN_DOAN_DUNG_XE.md).

**Giới hạn:** chưa chạy mode mới trong full Gazebo và chưa tìm nguyên nhân
contact thu_ne_01. Không lưu raw ảnh/full scan; chưa có benchmark overhead/
RTF. Các test command-equivalence là ca cụ thể, chưa chứng minh bảo toàn
mọi runtime follower. Đây là năng lực chẩn đoán, chưa sửa thuật toán né.


## Đối chiếu quỹ đạo với mục tiêu đã chọn — NK-068

**Hạn chế trước:** replay có quỹ đạo/contact nhưng thiếu dấu goal theo thời
điểm, khó đánh giá xe đang tiến tới đích nào khi người dùng đổi goal.

**Bổ sung sau:** RViz có marker tím GOAL; bản ghi tùy chọn thêm lịch sử goal,
viewer chọn goal theo timestamp/epoch, ghi nhãn và tọa độ trên bản đồ.
Tua, đổi goal, HTML và PNG giữ đúng thông tin mục tiêu; không đổi thuật toán.

**Kiểm chứng:**9 test mục tiêu/export/backup qua; ROS callback riêng xác
nhận goal và Marker cùng tọa độ; Firefox fixture hai goal tổng hợp kiểm
thời điểm/đổi goal/epoch và screenshot, HTTP feed qua; build planner qua.
[Kiểm ROS](docs/evidence/2026-11-02/goal_markers/ros_marker_validation.json),
[ảnh viewer](docs/evidence/2026-11-02/goal_markers/viewer.png).

**Giới hạn:** chưa thử marker mới trong full simulation; phiên đang chạy
của người dùng giữ nguyên, cần process mới để ghi goal. Goal được chọn
không chứng minh có đường hợp lệ hoặc xe đã tới đích. Bản ghi cũ thiếu
sự kiện goal không được tự dựng lại. Không kết luận cải thiện khả năng né.


**Kiểm chứng chẩn đoán runtime — NK-069:** session chan_doan_01 có1800 frame
đến89.951s, xác nhận patrol contact robot2/robot3 và TV-return contact robot2.
Chẩn đoán cho thấy leader bị chặn freshness dù có moving tracks; tại83.3s
state wall2.081s vượt giới hạn2s, observation camera không active. Robot2
78.9s bị loại64 rollout bởi moving buffer. Numerical probe xác minh gap
đệm start−.1833m và swept rule yêu cầu≥.03m khiến hướng ra cũng bị loại.
Escape75.3s tính≈3.628s wall, lệnh né đổi thành dừng≈.125s wall sau đó;
coordinator đồng thời giữ reference rỗng theo moving safety. Đây là bằng
chứng nhánh gây dừng, chưa phải bản sửa hoặc benchmark CPU/RTF.

Giới hạn:3 stream robot gần trần20MiB và hết trước replay, chưa đủ context
contact cuối86.305s. Không quy camera thiếu candidate thành nguyên nhân
CPU; không chứng minh mọi hướng vật lý đều không an toàn từ buffer rule.
Không sửa né trong audit. [Phân tích và mẫu thật](docs/evidence/2026-11-02/stop_diagnostics_audit/analysis.json).


## Né vật động bằng LiDAR2m cho cả3 xe — NK-071

**Hạn chế bản trước:** NK-069 có contact thật dù đã có track LiDAR. Khi
buffer dự báo overlap điểm đầu, mọi hướng thoát bị loại; tính toán dài làm
state/guard hết hạn, reference rỗng gián đoạn điều khiển. Capture-pose không
đồng bộ và track trùng nhiều nguồn làm sai hình học/vận tốc. Profile cũ
trộn camera/LiDAR nên khó thử riêng năng lực né vật động.

**Cải tiến bản sau:** sensor2m/10Hz/240tia, ba xe cùng nhánh né LiDAR không
cần nhận diện người. Profile động tắt camera/observation để kiểm riêng.
Chiếu scan theo pose capture-time, retry bounded khi pose trễ; gom spatial
components/fit cung, track local ưu tiên và nguồn đồng đội bổ sung. Giữ
ước lượng vận tốc ngắn khi dropout. Recovery từ buffer chỉ cho hướng giảm
nguy cơ có kiểm tra map/ray/moving/peer. Giới hạn tìm kiếm, kiểm lại dữ liệu
trước lệnh và giữ reference/goal qua né. Thêm kích hoạt nearby-approach và
giữ dừng ngắn trước quay về goal khi vật tạm dừng/rẽ. Normal MPC kiểm full
tracking rollout trước beam; không dùng quỹ đạo dở hoặc lệnh quá tuổi.

**Kiểm chứng:** build hai package qua;217 test qua,2 warning SciPy,3 file
ament lint không chạy. Ca kinematic raw-LiDAR cho mỗi xe ở tốc độ vật động
.15/.35/.8m/s, đội3xe và ca pause/rẽ qua; giới hạn command/rollout≤.28m/s.
ROS constructor cả3 xác nhận LiDAR2m,3 scan sources và không subscription
camera; resolved URDF2m/10Hz/240tia. Đây là kiểm thử số học và constructor,
không phải chứng minh an toàn thực tế.

Các lượt Gazebo trung gian vẫn có contact và được giữ nguyên minh chứng;
lượt03/07 lỗi startup không được tính là thành công. Lượt09 không có
contact ngoài nền ở hai follower trong90s nhưng leader contact patrol
83.901–86.051s khi quay về goal trong lúc người rẽ. Bản sau thêm guard góc
rẽ. Lượt10 cùng goal, server-only, camera tắt: không ghi contact ngoài nền
trong0.001–90.101s sim. Quãng đường root XY lấy mẫu3xe≈10.82/10.35/8.20m;
leader đã gần goal lúc74s rồi chủ động rời goal để né patrol đổi hướng.
Cuối lượt leader còn cách goal≈1.71m, follower đang pause-hold: chưa xác
nhận tái lập đội hình/đến lại goal hoặc toàn chu kỳ người quay về.
[Summary và contact](docs/evidence/2026-11-02/lidar_2m_avoidance/validation_summary.json),
[quỹ đạo lượt10](docs/evidence/2026-11-02/lidar_2m_avoidance/final_trajectories.png).
Đây là một lượt có giới hạn, không suy thành tỷ lệ thành công hoặc an
toàn tổng quát.
[Hồi quy](docs/evidence/2026-11-02/lidar_2m_avoidance/regression.log),
[cấu hình sensor](docs/evidence/2026-11-02/lidar_2m_avoidance/sensor_config.json),
[runbook](docs/LIDAR_2M_AVOIDANCE.md).

**Giới hạn:** chưa benchmark có lặp hoặc so baseline cùng điều kiện;
không so RTF giữa GUI/server hoặc DDS khác nhau. LiDAR không nhận dạng
chắc chắn người; track/footprint bảo thủ không phải collision mesh thật.
Recovery từ vùng quá sát không đảm bảo có lối an toàn. Còn cần kiểm che
khuất, nhiều vật đổi hướng, hành lang chật, goal khác và hồi phục đội hình.
Sensor chung đổi2m nên kết quả hai paper cũ không là benchmark mới.


**Kiểm chứng mở rộng trên bản ghi người dùng — NK-072:** cùng mã NK-071,
lidar_2m_01 có4943 frame0.001–247.101s; cả3 xe phát lệnh né nhưng physics
xác nhận8 cặp/9 đợt contact ngoài nền, gồm robot2↔TV32.117–32.638,
leader↔patrol84.382–86.557,robot1↔TV-return93.338–95.664 và robot1↔leader
147.650–147.658. Đợt cuối leader↔TV245.110 chưa kết thúc ở247.101s.
Kết quả90s trước vẫn là một lượt riêng, chưa chứng minh né ổn định.

Bằng chứng mới chỉ ra giới hạn còn lại: local velocity t30 của robot2
ngược người thật trong khi peer đo đúng nhưng bị local-priority suppress;
leader có đoạn lùi cùng chiều patrol rồi chuyển ngang muộn; goal A* là
proposal, MPC còn đổi hướng và estimate chậm ở góc rẽ. Robot1 command0 ở7
mẫu147–147.6 nhưng root đi≈.270m; dự báo stationary khi stop không khớp
chuyển động thực. Chưa xác định nguồn trôi vì thiếu wheel/effort và audit
mọi command publisher. Scan/state ở các checkpoint khoảng.1s tuổi, camera
không dùng; không đủ căn cứ quy toàn bộ contact cho tốc độ camera/RTF.

Audit không sửa thuật toán. Hướng tiếp: motion fusion có chất lượng,
điểm né ra khỏi corridor có kiểm thời gian tới/đổi hướng, giữ phía né khi
an toàn và dự báo phanh/peer theo vận tốc đo. Cần kiểm nhiều chu kỳ sau
sửa, chưa có benchmark lặp hoặc kết luận tối ưu.
[Phân tích](docs/evidence/2026-11-02/lidar_2m_01_audit/README.md),
[số liệu/hash](docs/evidence/2026-11-02/lidar_2m_01_audit/analysis.json),
[quỹ đạo contact](docs/evidence/2026-11-02/lidar_2m_01_audit/contact_trajectories.png).


## Hợp nhất vận tốc và ổn định điểm trú khi né — NK-073

**Hạn chế trước:** NK-072 xác nhận contact cả3 xe. Local velocity sai có
thể che dữ liệu peer đúng; điểm né thay đổi, dự báo vận tốc trễ ở góc rẽ,
xe quay về route hoặc bị dừng giữa các lần tìm. Command0 không phản ánh
robot đã dừng thực; endpoint của cruise cũng bị ép như một nơi đỗ.

**Thay đổi sau:** consensus theo nguồn độc lập/freshness giữ local geometry
nhưng sửa velocity bất đồng. Recent-turn update và pause reserve hữu hạn
tránh coi vật vừa dừng là đứng yên chắc chắn. Motion gate theo map tránh
forecast bề mặt tĩnh đã biết, giữ raw rays để kiểm collision. Connector
chấm theo flow/heading, warm direction được kiểm mới đầu budget. Refuge
world giữ qua nhiều tick và chờ flow đi qua; chỉ latch nơi holding-safe.
Cruise tiếp tục phải qua toàn horizon, có penalty khi chưa dừng được ở
endpoint; không ép nó đứng lại trước khi ra khỏi đội hình chật. Recovery
bổ sung floor khoảng cách tâm ước lượng khi đã overlap buffer.

Pose history đo velocity robot, stop prediction và peer checks xét thêm
coast/braking envelope thay vì stationary ngay khi Twist0. Đây là sửa dự
báo; chưa đo/calibrate hoặc chữa nguồn vật lý làm xe trôi. Goal người dùng
và collision mesh/timeline người giữ nguyên; camera không tham gia né.

**Kiểm chứng:**234 test qua,2 warning SciPy,3 ament lint file không chạy;
17 test mới gồm dữ liệu NK-072 t30, vote trùng/cũ, recent turn/pause expiry,
refuge/static map, budget/map đổi, world target/hold/release, recovery floor
và braking/peer. Hồi quy follower chật giữ nguyên assert>.47m; không giảm
ngưỡng để cho qua. ROS constructors3xe xác nhận2m/3 scan sources/cameraoff
và pause reserve. Các test kinematic không là chứng minh Gazebo an toàn.

Các prototype trong quá trình sửa vẫn có contact, được giữ riêng kèm
source provenance. Không tính chúng thành lượt thành công hoặc release
thuật toán. Lượt chốt0.001–247.951s không có contact ngoài nền trước193.260s,
robot2 không có contact trong toàn lượt; robot1/leader còn6 cặp/8 đợt
ở chu kỳ sau. Contact cuối245.868–247.951 còn active tại cuối record.
Do đó **chưa đạt cả3 né ổn định**. Có chuyển động thật, nhưng cuối lượt
còn cách goal và chưa xác nhận tái lập đội hình. Không suy tỷ lệ cải thiện
hoặc benchmark từ khác biệt GUI/DDS/thời gian chạy.
[Acceptance](docs/evidence/2026-11-02/nk073_motion_escape/acceptance.json),
[physics/source summary](docs/evidence/2026-11-02/nk073_motion_escape/validation_summary.json),
[quỹ đạo](docs/evidence/2026-11-02/nk073_motion_escape/final_trajectories.png).
[Hồi quy](docs/evidence/2026-11-02/nk073_motion_escape/regression.log),
[mô tả và lệnh kiểm](docs/evidence/2026-11-02/nk073_motion_escape/README.md).

**Giới hạn:** consensus/map gate/temporal reserve là heuristic, chưa đo
perception accuracy hoặc benchmark lặp. Vật sát tường, nhiều vật bị che,
đổi hướng đột ngột và actuator response vẫn cần kiểm. Cruise có an toàn
trong horizon dự báo không đồng nghĩa có nơi dừng an toàn mãi tại endpoint;
recovery từ quá sát không đảm bảo tránh contact. Probe drive trong lúc
sim chậm không đủ mẫu động để xác định nguyên nhân trôi.


## Đối chiếu vùng LiDAR và điểm né trong phát lại — NK-074

**Hạn chế trước:** replay có pose/contact/goal nhưng thiếu raw scan đồng
bộ theo capture; nhìn quỹ đạo chưa biết người đã vào tầm quét, có bị che,
hay A* đề xuất một phía còn MPC thực chọn phía khác.

**Thay đổi sau:** bản ghi thủ công thêm scan/TF/timestamp và đầu ra kế
hoạch cả3 xe. Viewer hiển thị tầm tối đa2m theo scan, điểm trả về hữu hạn,
khoảng thời gian vào vùng theo mẫu và đối chiếu tia gần footprint người.
Chiếu theo pose capture, tách receipt; không vẽ điểm khi thiếu TF/pose,
quá tuổi hoặc khác epoch. A*◇/path và MPC× tách riêng, theo hướng thân xe,
giữ trong PNG/HTML và dữ liệu đọc tăng dần. Đây là cải tiến quan sát và
chẩn đoán; policy né giữ nguyên.

**Kiểm chứng:**244 test qua,2 warning SciPy;3 ament lint không chạy.10 test
mới có kiểm command/rollout tương đương bật/tắt telemetry và lỗi publisher.
ROS kiểm soát cả3 nguồn/TF/capture-delay/clear/reset, installed observer
và Firefox qua. Trình duyệt phân biệt người trong2m nhưng bị che với tia
trả về gần người; kiểm A* khác MPC, entry interval, dữ liệu cũ, export và
HTTP tăng dần. [Minh chứng](docs/evidence/2026-11-02/replay_lidar_astar/README.md).

**Giới hạn:** fixture pose tổng hợp, chưa chạy toàn kịch bản Gazebo mới;
không suy thành cải thiện tỷ lệ né/contact hoặc RTF. Tia gần footprint
Gazebo chỉ là đối chiếu hình học, không chứng minh controller nhận dạng
người/đã nhận track. Stream có giới hạn và có thể thiếu mẫu; bản ghi cũ
không khôi phục raw scan đã mất. Các contact còn mở ở NK-073 giữ nguyên.


**Bằng chứng vận hành bổ sung — NK-075:** replay mới cho thấy robot3
không về goal chủ yếu do nhánh MPC vượt deadline100ms wall rồi phát
Twist0:173 mẫu trong106.025–126.025s sim. Frame126.301 còn cách goal
≈1.72m, camera tắt. Đã xác định lý do dừng trực tiếp, chưa profile để quy
nguồn chi phí hoặc chứng minh không có lối an toàn. Chưa sửa thuật toán;
bước tiếp đo thời gian rollout/beam/check và nguyên nhân loại candidate.
[Số liệu và hash](docs/evidence/2026-11-02/nk075_leader_timeout/analysis.json).


## Phục hồi đi về goal sau né — NK-076

**Hạn chế trước:** bản ghi người dùng lidar_vung_01 không ghi contact
ngoài nền trong0.001–165.201s, cả3 né tốt theo quan sát, nhưng robot3
mắc ở normal MPC quay về goal. Fallback beam12 hết ngân sách100ms trước
khi hoàn tất horizon, liên tục phát dừng dù nhánh chờ né đã thoát.
Không đồng nhất lỗi này với kết quả contact lượt NK-073 khác.

**Thay đổi sau:** giữ nhánh chọn điểm né/escape, đổi normal tracking sang
hoàn tất beam hẹp trước (1, ngõ cụt thì3/12) trong deadline cũ. Giữ đầy đủ
sweep map/LiDAR/moving/peer, acceleration/cost và freshness; không dùng
quỹ đạo dở hoặc nới khoảng cách an toàn để đi được. Normal command xóa
marker né cũ qua telemetry. Đánh đổi là nghiệm hợp lệ sớm có thể chưa
đạt chi phí của beam rộng khi có đủ thời gian.

**Kiểm chứng:**248 test qua,2 warning SciPy;3 ament lint không chạy.
4 test mới kiểm full horizon trong work budget, deadline, collision và
đi tiếp reference sau pause. AST nhánh escape và các helper kiểm an toàn
khớp backup. Đúng1 lượt Gazebo server-only/cameraoff/LiDAR2m cùng goal:
0.001–75.051s không contact ngoài nền ghi nhận. Leader đến gần goal lúc
12.151s, sau đó né ra xa>.5m lúc24.051s và trở lại cách goal<.15m lúc
58.501s, cuối lượt ở goal; cả3 status cuối normal. Leader không báo normal
MPC timeout trong lượt này, vẫn có1 escape timeout/1 beam empty.
[Minh chứng](docs/evidence/2026-11-02/nk076_resume_goal/README.md).

**Giới hạn:** chỉ1 lượt theo ràng buộc người dùng, không benchmark lặp
hoặc so RTF với GUI; chưa kiểm chu kỳ sau75s, nhiều goal/ngõ cụt hoặc
chứng minh luôn tái lập đội hình. Các contact lịch sử NK-073 vẫn mở ở
điều kiện/thời điểm tương ứng; không suy thành an toàn tổng quát.


## Chọn và đối chiếu nhiều bản ghi trong viewer — NK-077

**Hạn chế trước:** viewer gắn một --session, đổi bản ghi phải chạy lại
lệnh hoặc chọn từng file; import local trong trang HTTP có thể bị poll
server cũ ghi đè.

**Thay đổi sau:** danh sách bản ghi recordings/, refresh/mở trên giao
diện và nút chọn thư mục bất kỳ trên máy. Tải lại đồng bộ các stream
khi chuyển phiên, lựa chọn độc lập từng tab. Import local tắt poll và
đợi request cũ hoàn tất trước thay state; HTML độc lập hỗ trợ folder.

**Kiểm chứng:**20 test replay/scripts qua, HTTP thật kiểm các stream
cùng session, Unicode/tab độc lập/refresh và path không hợp lệ. Firefox
fixture kiểm nút chuyển bản ghi, local import không bị ghi đè và
standalone qua. [Minh chứng](docs/evidence/2026-11-02/nk077_recording_picker/README.md).

**Giới hạn:** thư mục mở trực tiếp là snapshot lúc đọc; thiếu dữ liệu
cũ không hồi điền. Không thay thuật toán điều hướng hoặc thử Gazebo;
đây là cải tiến công cụ phân tích, không là cải tiến tỷ lệ né.


## Kiểm chứng tích hợp camera/vùng xã hội120s — NK-078

**Giới hạn bản trước:** kết quả NK-076 chỉ một lượt75s, camera và nhận
diện xã hội tắt; chưa kiểm việc kết hợp vùng xã hội với né người và
quay lại goal ở chu kỳ dài hơn.

**Cấu hình được kiểm:** giữ mã né NK-076, bật camera/person/head/body,
social map/observation/auto-observe trong đúng1 lượt server-only120s.
Camera tạo vùng cho planning map D*/3MPC; né vật động vẫn LiDAR2m.
Không đổi goal, ngưỡng an toàn hoặc cấp ground truth vào control.

**Kết quả:**raw frames0.001–120.001s. Có vùng viewing_tv11 mẫu từ14.033
đến18.235s và facing_group/person; chưa có lying candidate/lying_person.
Chưa đo độ đúng nhận diện/persistence, không coi nhãn là hành vi thật.
Leader về gần goal20.801s, né ra xa và trở lại55.101s, cuối ở goal.
Tuy nhiên physics xác nhận patrol↔leader84.180–86.253s và patrol↔robot2
85.647–87.771s; robot1 không contact ngoài nền ghi nhận. **Chưa đạt cả3
né ổn với cấu hình tích hợp này.**

Sát contact các candidate bị moving checks loại, command0 trong khi
state/scan≈.1–.2s sim; ví dụ compute≈13–26ms. Không đủ cơ sở quy contact
chủ yếu cho camera chậm. Cần audit forecast/geometry/lối né/actuator.
[Minh chứng](docs/evidence/2026-11-02/nk078_social_camera_120s/README.md),
[số liệu](docs/evidence/2026-11-02/nk078_social_camera_120s/analysis.json).

**Giới hạn:**1 lượt theo yêu cầu, không benchmark lặp, không cameraoff
baseline cùng120s; contact xuất hiện sau mốc75s của lượt trước nên không
quy mức hồi quy cho camera. Harness bị SIGTERM trong cleanup, thiếu
live/samples cuối; completion dựa raw120s/events/params còn giữ, không
bịa service results. Không thay thuật toán sau test hoặc chạy lần2;
chưa chứng minh mọi vùng xã hội được duy trì/né hoặc đội hình luôn phục
hồi. Không so RTF giữa cấu hình khác nhau.


## Đồng bộ ảnh camera và vùng xã hội khi phát lại — NK-079

**Hạn chế trước:** viewer có pose/contact/LiDAR/điểm né nhưng không thấy
ảnh camera hoặc vùng xã hội. Dữ liệu NK-078 phải đọc riêng từ log và ảnh,
khó đối chiếu vùng xem TV với hướng xe tại một thời điểm.

**Thay đổi sau:** panel camera raw/nhận diện theo receipt/capture và lớp
contour vùng xã hội đã publish, tách khỏi ground truth/kịch bản. Không
hiện ảnh tương lai hoặc epoch khác, ghi rõ ảnh cũ/thưa, xóa/ẩn vùng cũ.
PNG ghép map/camera, HTML/folder/HTTP giữ dữ liệu cùng phiên. Recorder
opt-in thêm stream JPEG/social riêng có giới hạn, encode ngoài controller.
Đính kèm6 ảnh gốc+marker NK-078, không nội suy frame hoặc bịa capture.

**Kiểm chứng:**23 test scripts qua; ROS fixture read-only tạo JPEG từ2
nguồn, clear region/capture-vs-receipt và writer sạch qua. Firefox với
bản ghi NK-078 kiểm TV14.5s, không lấy ảnh84.704 ở84.5s, PNG camera,
HTML/TTL/reset/legacy qua. [Minh chứng](docs/evidence/2026-11-02/nk079_camera_social_replay/README.md).

**Giới hạn:** chưa thử Gazebo mới/benchmark overhead; các ảnh NK-078
rời rạc, thiếu capture stamp được ghi rõ. Region contour không là toàn
raster keepout sau carve lối thoát hoặc chứng minh nhận diện/né đúng.
Không thay thuật toán, kết quả contact NK-078 không đổi.


**Đối chiếu nguyên nhân NK-078 — NK-080 (không đổi thuật toán):** GT
patrol đi lại≈.404m/s, track robot3 t83 chỉ≈.14 nên forecast cho phép
lối né−Y cắt tuyến y=−2;83.1 đổi goal nhưng command còn hướng cũ do gia
tốc,83.3 không rollout nào được moving checks chấp nhận. Robot2 có các
mẫu track0 ở84.0/85.1 trong khi người thật vẫn đi, nhánh pause hold;
velocity phục hồi thì đã quá sát, candidate bị loại trước contact.
Gate risk speed<.05 và cách xử lý uncertain cần audit/sửa có kiểm chứng.
Scan/state mới và compute13–26ms ở mẫu sát contact không hỗ trợ kết luận
camera chậm là nguyên nhân trực tiếp. Root leader còn dịch5.94cm sau
command0, chưa xác định wheel/actuator/command-delay. Đề xuất xử lý
uncertainty/corridor/pause/braking chưa triển khai. Không chứng minh
lối thoát vật lý khả thi tại tick kẹt hoặc baseline cameraoff120s.
[Minh chứng](docs/evidence/2026-11-02/nk080_nk078_cause_audit/README.md).


## Dự báo khi mất fit và kiểm tra đường né cắt luồng người — NK-081

**Hạn chế trước:** NK-080 ghi nhận vận tốc track bằng0 dù người còn đi,
đường né cắt trước người, xe còn trôi sau command0. Risk dựa nominal có
thể bỏ sót threat; kiểm tra từ vận tốc lệnh0 chưa phản ánh chuyển động thật.

**Mã cuối:** giữ thêm giả thuyết vận tốc thực đo gần nhất tối đa0.8s khi mất
fit, bỏ khi đứng yên/expiry, không tự tăng tốc độ. A*/rollout kiểm tra cắt
phía trước luồng người; rollout xét vận tốc trôi và phanh nếu vượt giới hạn.
Giữ các kiểm tra an toàn và normal tracking NK-076.

**Kiểm chứng:**260 test qua/2 cảnh báo SciPy; build2package thành công,
ba ament lint chưa chạy. Đúng1 lượt Gazebo120s đã chạy với bản thử ban đầu
còn synthetic speed prior: leader chạm người rời ghế TV32.117–34.595s,
cuối cách goal4.222m; robot1/2 không contact ngoài nền ghi nhận. **Bản thử
không đạt.** Sau đó bỏ synthetic prior và thêm overspeed guard; mã cuối
chỉ qua kiểm thử số học/build, chưa Gazebo. Raw tail120.001–125.601s là
đóng phiên, không tính đánh giá.

**Giới hạn:** chưa chứng minh cải thiện so với NK-078 hoặc sửa hết va chạm/
phục hồi goal; quỹ đạo khác nên không lấy việc hết contact patrol làm bằng
chứng thành công. Chưa tách nhân quả từng thay đổi, không benchmark lặp.
[Minh chứng, bản thử và mã cuối](docs/evidence/2026-11-02/nk081_motion_uncertainty/README.md).


## Ưu tiên vùng xã hội khi chọn đường né — NK-082

**Trước:** nhánh né khẩn cấp chỉ kiểm bản đồ vật lý; điểm né tốt về hình học
có thể nằm trong vùng xã hội dù đã nhận diện.

**Sau:** A* tìm ngoài planning keepout trước, rồi mới xét lối vật lý khi
không tìm được trong ngân sách. MPC ưu tiên quỹ đạo ngoài vùng, tiếp theo
endpoint ngoài vùng và giảm số bước đi trong vùng, trước điểm tiện lợi cũ.
Giữ kiểm tra an toàn vật lý/người/xe khác; vẫn cho phép lối khẩn cấp.

**Kiểm chứng:**40 test qua gồm4 test mới về thứ tự ưu tiên, xuyên vùng,
thoát khỏi vùng và thời lượng xâm nhập. Chưa chạy Gazebo bản này.

**Giới hạn:** chỉ so các ứng viên tính được trong ngân sách, dùng planning
map sau carve; không bảo đảm không bao giờ vào contour xã hội. Chưa chứng
minh sửa va chạm hoặc luôn rời vùng sau né. Không thay kết quả NK-081.


## Kiểm chứng tích hợp NK-082 — NK-083

**Mục tiêu:** kiểm tra ưu tiên né ngoài vùng xã hội trong120s với camera và
social map bật, cùng goal cũ. Không đổi controller trong lượt này.

**Kết quả một lượt:** không đạt. Physics ghi nhận patrol–robot2
85.445–97.334s, robot2–leader88.111–89.318s, robot2–kệ TV88.218–90.460s
(mốc đầu/cuối, không khẳng định contact liên tục). Robot1 không contact
ngoài nền ghi nhận. Leader cuối cách goal0.963m, chưa về lại15cm sau khi
rời goal. Có marker viewing_tv14.067–76.434s, không chứng minh độ đúng hay
persistence toàn phiên.

**Giới hạn:** chưa quy nhân quả cho cơ chế ưu tiên xã hội/camera; chưa audit
mức xâm nhập planning keepout/carve hay benchmark lặp. Không tuyên bố tốt
hơn NK078/NK081 hoặc đã sửa va chạm. Nguồn giữ nguyên NK082, phiên đã dừng.
[Minh chứng](docs/evidence/2026-11-02/nk083_social_escape_120s/README.md).


## Ưu tiên điểm né phía sau thân xe — NK-084

**Trước:** chọn hướng chủ yếu theo thoát ngang luồng người và giữ hướng;
connector sau bị xét sau hai bên, dễ không được xét khi hết ngân sách.

**Sau:** xét sau trước trong A*, tăng ưu tiên endpoint sau; MPC xét hướng
lùi sớm, ưu tiên điểm sau đã qua kiểm tra giữ an toàn. Nón sau±45 độ theo
yaw xe; ưu tiên ngoài vùng xã hội và mọi hard checks được giữ. Có thể
chọn hai bên khi sau không an toàn; không ép lùi vào hướng người tới.

**Kiểm chứng:**44 test qua, gồm4 test mới về hướng quay/thông thoáng/
bị chặn/không an toàn để dừng phía sau. Chưa chạy Gazebo bản này;
không coi đây là bằng chứng xử lý xong contact và phục hồi goal NK083.


## Bổ sung10 phương pháp đối chiếu ba tầng — NK-087

**Trước:** hai backend paper và D* Lite/MPC; chưa có bộ10 phương pháp trong
hội thoại chia sẻ để lựa chọn trên cùng hạ tầng cảm biến/xã hội.

**Sau:** triển khai10 pipeline formation → trajectory → control riêng,
method01–10 tương ứng paper3–12; thêm adapter dùng chung map/LiDAR/peer/
moving/freshness/gia tốc và nhánh né khẩn cấp. D* vẫn cấp tham chiếu, tracking
bị loại thì dừng, không âm thầm dùng tracking MPC baseline. Launch chọn
đúng ba controller mới, giữ hai paper cũ. Bộ đối chiếu là kiến trúc lai.

**Kiểm chứng:** mới kiểm cấu trúc tĩnh nguồn/launch/shell/tài liệu. Đã viết
test numerical và adapter nhưng chưa chạy; chưa build/ROS/Gazebo, không có
số liệu tránh va chạm hoặc benchmark tăng hiệu năng. Các kết quả test của
hội thoại khác không là bằng chứng dự án này.

**Giới hạn:** prototype lấy từ bản ba tầng trong hội thoại, không mã tác giả
hoặc bản tái lập đã xác minh. CTC vận tốc, image-space dùng pose proxy, slip
xấp xỉ, car-like trên omni, DEFORM-inspired và một phương pháp tổ hợp nhiều
nghiên cứu. Chưa đối chiếu đầy đủ DOI/phương trình, chưa chứng minh tốt hơn
baseline/hai paper cũ. Shared safety không là bảo đảm tránh va chạm.
[Phạm vi và minh chứng](docs/evidence/2026-11-02/nk087_ten_comparison_methods/README.md).


## Đối chiếu lỗi không trở về goal sau né — NK-090 (chưa sửa thuật toán)

**Hạn chế xác nhận:** bản ghi người dùng `dynamic_20261102_173439_286642343`
đến106.245s có goal bị planner loại do clearance. Khi hết moving safety/
observation, coordinator vẫn reference_rows0/replan_requiredtrue; ba xe giữ
dừng. Leader cách goal2.047m. Scan/state mới, reference cũ; không quy trực
tiếp cho chậm camera hoặc thiếu phát hiện người.

**Bằng chứng:** cảnh báo Goal lacks obstacle clearance lặp trong log cùng
phiên. Map vật lý hiện hành có khoảng hở1.052m, contour xã hội cách goal
0.137–0.146m dưới margin0.18m, phù hợp social clearance chặn goal. Thiếu
raster planning/keepout sau carve nên chưa quy ô hoặc lớp duy nhất.

**Hướng xử lý chưa triển khai:** giữ goal người dùng, phân biệt goal bị
social layer chặn tạm với vật cản vật lý; chờ/tiếp cận ngoài vùng và replan
khi clear. Chưa có bằng chứng sửa được lỗi hoặc benchmark cải thiện.
[Minh chứng](docs/evidence/2026-11-02/nk090_goal_blocked_after_escape/README.md).


## Phục hồi tuyến khi goal bị chặn — NK-091 (đã viết, chưa thử runtime)

**Trước:** goal thiếu clearance làm planner trả về ngay, reference không
phục hồi sau né (bằng chứng NK090).

**Sau:** giữ goal gốc; tìm điểm tiếp cận ngoài vùng chặn với kiểm tra đường,
đưa điểm đó vào D*/formation; tự yêu cầu replan về goal khi nó clear. Có
trạng thái endpoint tạm trong diagnostics. Kiểm tra cấu hình giữ ít nhất
1cm ngoài robot_radius; mặc định3cm không đổi.

**Kiểm chứng:** AST và diff; đã viết3 test cô lập, chưa chạy pytest/build/
Gazebo. Chưa chứng minh sửa thành công bản ghi thực.

**Giới hạn:** tìm tối đa8 ứng viên trong1m, có thể không tìm được đường;
không xóa keepout để đạt goal. Chưa hỗ trợ tiếp xúc có kiểm soát vào chân
người. Map5cm và sai số động học không cho phép khẳng định khoảng hở thực1cm.


## Kiểm chứng thực tế bản NK091 — NK092

Bản người dùng mới vẫn có contact robot1–người tại first26.834,last28.738s.
Đã có phát hiện nguy cơ và lệnh né, nhưng ngắt bởi pause/budget và loại
mọi rollout dẫn đến cmd0 khi người đi tới. Chưa chứng minh né ổn định;
NK091 chỉ sửa tiếp cận goal, không sửa nhánh escape này.

Vùng TV xuất hiện13.061–trước16.247s rồi mất dù track màn hình còn. Chưa
xác định gate mất vùng vì thiếu debug từng viewer; có camera inference
stale trong trạng thái quan sát. Chưa sửa mới hoặc benchmark.
[Minh chứng](docs/evidence/2026-11-02/nk092_robot1_contact_tv/README.md).


## Né khi dự báo dài không tìm được đường và quan sát goal — NK093

**Hạn chế trước:** bản NK092 có lệnh né ngắt bởi pause/budget rồi mọi
rollout bị loại, robot dừng khi người tiếp tục tới; chưa có tự quay quanh goal.

**Sau:** sửa chờ refuge khi chưa tới; giữ hướng tiếp cận đo tối đa0.5s
qua dropout, kiểm lại escape; dự trữ thời gian tìm rollout ngắn0.6s nếu
không tìm được full3s, giữ các kiểm tra từng bước. Leader<=20cm từ goal
thử full scan, hoàn thành một vòng feedback rồi trở lại tuyến; bị ngắt
thì thử lại. Chưa sửa lỗi mất vùng TV.

**Kiểm chứng:** AST/diff; viết regression tests, chưa chạy pytest/build/
Gazebo. Chưa có bằng chứng giảm contact, không coi thay đổi này là thành công
thực nghiệm. Rollout ngắn có rủi ro thiếu lối thoát ở những tick sau;
không bảo đảm tránh mọi người tiếp tục đi tới. Camera phải bật và đủ mới;
quay đủ không đồng nghĩa nhận diện đúng mọi vùng xã hội.


## Bằng chứng duy trì vùng TV — NK094 (chưa sửa)

Bản người dùng sau NK093 vẫn mất vùng TV:2→1 tại77.834s,→0 tại80.612s;
track TV còn, camera có frame mới. Nguồn hiện hành hết hạn75s theo thành
phần bằng chứng cũ nhất; phù hợp mất vùng cuối nhưng chưa có gate/stamp
mỗi vùng để kết luận duy nhất. Chớp tắt ngắn trước đó còn có thể do invalidation.
Chưa sửa hoặc chứng minh cải thiện perception.
[Minh chứng](docs/evidence/2026-11-02/nk094_tv_region_expiry/README.md).


## Kiểm chứng có giới hạn nhánh né NK093 — NK095

Lượt người dùng130.801s không ghi contact robot với người/vật/robot khác;
stream contact nền vẫn có dữ liệu. Nhánh ngắn0.6s đã phát26/11/21lệnh cho
robot1/2/3. So với lượt NK092 có contact robot1, lượt mới chưa ghi contact,
nhưng không phải thử lặp cùng điều kiện nên chưa chứng minh tỷ lệ cải thiện.
Leader cuối cách goal0.455m, chưa scan hoàn tất; phục hồi goal và vùng TV
còn mở. [Bằng chứng](docs/evidence/2026-11-02/nk095_contact_free_checkpoint/README.md).
