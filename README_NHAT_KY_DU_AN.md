# Nhật ký trao đổi và chỉnh sửa — Three Robot Rescue

**Cập nhật:** 28/10/2026 — múi giờ Việt Nam (`Asia/Ho_Chi_Minh`).\
**Mốc chức năng hiện hành:** M6 — D* Lite + MPC, cảnh xã hội động và pipeline cảm biến đã sửa.\
**Báo cáo gửi giảng viên:** [README_BAO_CAO_TIEN_DO.md](README_BAO_CAO_TIEN_DO.md).

## 1. Phạm vi và cách đọc

Tài liệu ghi lại các nội dung trao đổi chính, quyết định và thay đổi dự án
có trong lịch sử làm việc hiện có; đây không phải bản chép nguyên văn từng
tin nhắn hoặc từng lần gọi công cụ. Nội dung trước lịch sử hội thoại này chỉ
được ghi khi có README hoặc Git làm căn cứ, không dựng lại các trao đổi chưa có.

Phần nhật ký giữ cả các hướng đã đề xuất nhưng chưa triển khai, các bản sửa
chưa đạt kết quả ở lần đầu và những kết luận đã được kiểm tra lại. Mỗi mục có
ID để các lần cập nhật sau dẫn chiếu hoặc đính chính.

Các mốc M0–M6 là nhãn mô tả tiến trình trong tài liệu, **không phải Git tag hoặc
phiên bản đã phát hành**. Nhiều thay đổi hiện còn trong working tree. Git HEAD
ghi nhận khi lập tài liệu là `5ac6982` (13/10/2026); không gán các sửa mới cho
commit này.

## 2. Nền dự án có trước các trao đổi gần đây

Các căn cứ từ Git:

| Commit | Ngày trong Git | Nội dung tiêu đề commit |
|---|---|---|
| `c74013a` | 04/10/2026 | Mô phỏng ba robot, D* Lite, MPC và đội hình thích nghi |
| `ff15d90` | 04/10/2026 | Snapshot workspace, gồm build/install/log và cấu hình làm việc |
| `5ac6982` | 13/10/2026 | RGB-D social navigation và people-aware planning |

Theo [hướng dẫn MPC/đội hình](social_navigation_sim/README_DSTAR_MPC.md), nền
hệ thống gồm ba robot omni `3w_v2`, mặc định `robot3` dẫn đầu, D* Lite tìm đường
trên occupancy grid và ba node MPC bám tham chiếu chung. Đội hình đổi giữa
tam giác và hàng dọc; có kiểm tra khoảng cách, vật cản và cơ chế phục hồi.

Camera RGB-D, LiDAR, suy luận hướng đầu/thân, nhóm trò chuyện, TV và vùng xã
hội đã có trước các sửa gần đây. README cũ cũng mô tả các lần chỉnh đội hình,
cảm biến và đồ họa; tài liệu này không nhận các phần đó là được tạo mới toàn
bộ trong hội thoại hiện tại.

## 3. Các mốc phát triển

| Mốc | Nội dung | Trạng thái/quan hệ với bản hiện hành |
|---|---|---|
| M0 | D* Lite + ba MPC, đội hình và cảm biến/vùng xã hội nền | Nền được tiếp tục sử dụng |
| M1 | Các nhánh Paper1 và Paper2 để tham khảo/thử thuật toán | Giữ source, không dùng làm backend hiện hành |
| M2 | Sửa hình học vùng người–TV và kiểm tra từng người | Có trong pipeline chung |
| M3 | Sửa xác nhận vùng TV theo quan sát nối tiếp, hướng người ngồi và mặt trước màn hình | Có trong pipeline chung |
| M4 | Thêm `social_dynamic`, người nằm và hai kiểu di chuyển | Chế độ riêng, giữ cảnh tĩnh để đối chiếu |
| M5 | Audit runtime và thử goal đi qua khu vực người nằm | Phát hiện hạn chế; tránh giường chưa chứng minh nhận diện người |
| M6 | Sửa ghép RGB-D, trùng track, cooldown, nhánh tư thế nằm và cấu hình DDS | Mốc chức năng hiện hành; còn cần benchmark đầy đủ |

## 4. Nhật ký chi tiết

### NK-001 — 27/10/2026 — So sánh Paper2 với D* Lite + MPC

**Yêu cầu:** xem thuật toán trong `paper2_social.launch.py` có tối ưu hơn
`dstar_mpc` hay không.

**Kết quả trao đổi:** file launch Paper2 chọn backend APF–MPC cho leader và
enhanced APF cho follower. Bản này dùng SLSQP, mặc định Np=16, Nc=5,
T=0,1 s; không dùng D* Lite tìm đường toàn cục hoặc đổi dạng đội hình.
Baseline có D* Lite, MPC cho từng robot và đội hình tam giác/hàng dọc.

Không có benchmark cùng điều kiện để kết luận Paper2 tốt hơn. Với cảnh có
phòng, tường và khe hẹp, baseline có các cơ chế cần thiết hơn để tìm đường vòng
và đổi đội hình. Đây là đánh giá cấu trúc code, không phải kết quả thống kê.
Giới hạn nhìn trước của Paper2 ở tốc độ 0,18 m/s và 1,6 s dự báo được phân tích
để giải thích vì sao tối ưu cục bộ không bảo đảm đường toàn cục tốt hơn.

**Căn cứ:** [README_PAPER2.md](README_PAPER2_APF_MPC.md),
[paper2_core.py](social_navigation_planner/social_navigation_planner/paper2_apf_mpc_core.py),
[three_robot_dstar_mpc.py](social_navigation_planner/social_navigation_planner/dstar_mpc_controller.py).

### NK-002 — 27/10/2026 — Đề xuất thuật toán vùng xã hội

**Yêu cầu:** một thuật toán xác định vùng xã hội tốt hơn phương pháp hiện tại.

Đã xem quy tắc ghép quan hệ theo cặp, thành phần liên thông và bao lồi. Điểm
yếu được nêu: quan hệ A–B và B–C có thể ghép cả A–B–C dù không có không gian
tương tác chung; nhìn thoáng qua có thể bị hiểu thành trò chuyện; bao lồi có
thể chặn dư diện tích.

Đề xuất GCFF (Graph-Cuts for F-formation), với lọc thời gian và độ bất định,
cho nhóm trò chuyện. **GCFF chỉ được đề xuất, chưa triển khai trong repo.**
Người dùng sau đó xác định ưu tiên là vùng xem TV, nên không chuyển toàn bộ
pipeline sang GCFF.

Tham khảo đã trao đổi: [GCFF, PLOS ONE 2015](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0123783).

### NK-003 — 27/10/2026 — Chốt phạm vi vùng xem TV

**Yêu cầu:** “tôi muốn tối ưu cái vùng xem tivi ấy”.

Phương pháp cũ cho phép hướng lệch tới 60°, yêu cầu người xem có hướng gần
song song và dựng bề ngang màn hình giả định 1,1 m. Đề xuất chuyển sang quan
hệ từng người–màn hình, xác nhận qua thời gian và hợp các vùng nhìn riêng.

Giữ phân biệt hướng đầu/thân với hướng mắt thực sự. Phần mở rộng dựa trên
hình học RGB-D là thiết kế kỹ thuật cho repo, không được gọi là tái lập đầy
đủ một thuật toán nghiên cứu hoặc mô hình gaze đã hiệu chuẩn.

### NK-004 — 27/10/2026 — Sửa code vùng xem TV lần đầu

**Yêu cầu:** “sửa code đi”.

Đã thêm đo đoạn màn hình từ depth trong box TV, topic
`/leader/people/tv_screens`, kiểm tra hướng từng người và polygon riêng cho
từng người–màn hình. Map hợp các polygon để giảm việc lấp khoảng trống giữa
người xem bằng bao lồi cả nhóm. TV chỉ có tâm vẫn dùng bề ngang ước lượng và
ghi rõ nguồn; không gọi đó là kích thước đo được.

Thêm xác nhận qua capture khác nhau, tối thiểu ba quan sát trải dài 0,6 s;
timer lặp hoặc timestamp lặp không tăng bằng chứng. Các kiểm tra đầu gồm
hình học màn hình xiên, hướng người, vùng nhìn, thiếu depth và hồi quy LiDAR.

**Kiểm chứng tại mốc này:** 20 kiểm tra qua; build package thành công. Chưa
đánh giá chuyển động Gazebo tại chính bước sửa đầu. Điều kiện xác nhận này
còn lỗi đối với camera quan sát nối tiếp, được sửa ở NK-006.

### NK-005 — 27/10/2026 — Quay lại dự án D* Lite + MPC

**Yêu cầu:** không chạy các nhánh Paper nữa, chạy dự án D* + MPC với vùng xã
hội đã sửa.

Đã chọn `navigation_backend:=baseline` qua `three_robot_social.launch.py`,
khởi động Gazebo, RViz, bộ điều phối và ba node MPC. Camera/LiDAR và map xã
hội được giữ. Source Paper1/Paper2 còn để tham khảo, không bị xóa.

### NK-006 — 27/10/2026 — Vùng xem TV vẫn chưa được nhận diện

**Phản hồi:** “nhận diện vùng xem tivi vẫn chưa được”.

Đọc tiếp phiên chạy cho thấy có TV và hướng người nhưng `tv_regions` vẫn
bằng 0. Phát hiện và sửa các điểm sau:

- Xác nhận ba mẫu chỉ bắt đầu sau khi thấy TV làm mất lịch sử hướng người
  đã quan sát trước đó. Giữ số mẫu và cửa sổ hướng ổn định từ tracker nguồn.
- Bộ nhớ vùng TV 8 s quá ngắn cho camera cố định quay lần lượt giữa người và
  màn hình. Đổi về 75 s cho bằng chứng nối tiếp, giữ riêng timestamp nguồn;
  quan sát mới về di chuyển/hướng đối lập vẫn phải thu hồi vùng cũ.
- Người ngồi thường thiếu hông hoặc không có mặt chính diện, nên hướng là
  `null`. Bổ sung tín hiệu mũi–mắt–tai RGB-D và kiểm tra hướng vai.
- Lượt quay bị hủy sau 8 giây thực trong khi Gazebo chậm hơn thời gian thực.
  Tách watchdog thực `observation_wall_timeout` mặc định 60 s khỏi deadline
  mô phỏng của lượt quan sát.
- Người phía sau màn hình cũng có thể hướng về tâm TV. Bổ sung mặt trước
  từ hình học màn hình và phía camera đã quan sát bề mặt đó.
- Ưu tiên TV có hình học đo được so với mục tiêu màu gần trùng.

Thêm `/social_navigation/attention_debug` để xem góc lệch, tầm nhìn, tuổi
quan sát, số mẫu hướng, trạng thái xác nhận và hình học màn hình.

**Kiểm chứng:** tại mốc cuối đợt này 29 kiểm tra qua; đã thấy `tv_regions > 0`
và `completed: social evidence acquired` trong Gazebo. Số vùng lúc đó **không
được coi là số người xem duy nhất**: audit sau phát hiện trùng track ở NK-008.

Trong các lần restart có lỗi DDS/shared memory. Đã có lúc chuyển ROS domain
từ 30 sang 31 để tiếp tục kiểm tra; sửa transport riêng cho launch được bổ
sung ở NK-011. Lỗi shader RViz lúc mở vẫn được ghi nhận, chưa xử lý dứt điểm.

### NK-007 — 27/10/2026 — Thêm ba tình huống xã hội động

**Yêu cầu:** thêm người nằm ngủ, người rời TV đi uống nước và người đi bộ
khắp map. Người dùng chọn **triển khai chế độ động riêng và giữ chế độ hiện
tại để đối chiếu**, thay vì chỉ thiết kế thuật toán.

Đã tạo `social_dynamic`, `dynamic_social.launch.py`, generator world/map/
manifest/bridge, plugin C++ `SocialScenarioMotion` và marker kịch bản có cập
nhật vị trí. Các world `people` và `rooms` được giữ.

| Tình huống | Triển khai hiện tại |
|---|---|
| Người nằm | Mesh nằm trên giường, không di chuyển; nhãn ngủ chỉ là mô tả kịch bản |
| Người rời TV | Xem 12 s mô phỏng; đổi tư thế trong 2 s; đi 0,35 m/s tới bình nước; dừng 6 s; trở lại ghế |
| Người đi bộ | Đi theo tuyến tuần tra 0,4 m/s, vòng khoảng 107,2 s mô phỏng |
| Người còn lại tại TV | `tv_viewer_b` tiếp tục ngồi xem |

Chu kỳ rời TV–quay lại khoảng 106,7 s. Chuyển động là kinematic, có thân va
chạm đi cùng mesh; chưa có hoạt ảnh chân bước, tay nâng cốc hoặc ngồi–đứng
hoàn chỉnh. Người theo lịch chưa chủ động nhường robot.

Map tĩnh chỉ thêm đồ đạc như giường/bình nước, không chứa người hoặc tuyến
của họ. Lịch, tên người và marker scenario không được dùng để gán kết quả
nhận diện. Pose robot từ Gazebo là một giả thiết có sẵn của nền mô phỏng.

Thêm ứng viên tư thế nằm từ khớp RGB-D và xử lý thu hồi vùng TV khi camera
đo được người đi khỏi vị trí cũ, kể cả khi ra ngoài bán kính ghép vị trí.

**Kiểm chứng:** 37 kiểm tra Python qua. Một world tạm headless chạy nhanh
112 giây mô phỏng đi qua đầy đủ các giai đoạn; plugin kiểm tra pose mô hình
trong physics khớp lệnh. Bản test nhanh dùng bước 0,01 s và RTF mục tiêu 100,
khác world chính 0,001 s/RTF mục tiêu 1: đây là kiểm tra lịch/pose, không phải
benchmark tránh va chạm của toàn hệ ba robot.

### NK-008 — 27/10/2026 — Audit mô phỏng đang chạy

**Yêu cầu:** “xem trình mô phỏng hiện tại đang có vấn đề gì không”.

Theo dõi log và lấy mẫu topic 22 s, không gửi lệnh điều khiển trong audit.
Các lỗi/hiện tượng được xác định:

| Hiện tượng | Bằng chứng/giới hạn kết luận |
|---|---|
| Chạy chậm | RTF khoảng 0,160; 22 giây thực tương ứng khoảng 3,53 giây mô phỏng |
| RGB–depth không đều | Bộ audit nhận 28 RGB, 20 depth, 20 timestamp trùng; log có `RGB only` |
| Trùng người xem TV | Hai track 16/17 ở gần nhau khoảng 11 cm, cùng vùng người còn ngồi |
| Tách track TV | Nhiều ID tâm/mép của một màn hình |
| D* Lite từng không có đường | Cảnh báo lặp ở giai đoạn trước; sau đó đã có đường 144 điểm và robot di chuyển |
| Shader RViz | Lỗi `active samplers with a different type...` lúc khởi động |

Không kết luận mất chính xác 28% dữ liệu toàn hệ chỉ từ mẫu nhận tại một
subscriber. Không kết luận robot đang kẹt vĩnh viễn khi log sau cho thấy
đã phục hồi đường. Việc nhận diện người nằm chưa được chứng minh ở audit này.

### NK-009 — 27/10/2026 — Theo dõi goal đi qua người nằm

**Yêu cầu:** người dùng đặt goal qua khu vực người nằm và yêu cầu đọc tiếp.

Goal quan sát được xấp xỉ `(-3,01456; 4,91303)`. Robot đi hàng dọc vòng phía
tây giường. Đọc tiếp đến khi cả ba đã đi qua giường; có các khoảng dừng quay
quan sát rồi tiếp tục đi.

- Khoảng hở tới mép giường ước tính nhỏ nhất: robot1 0,061 m, robot2 0,062 m,
  robot3 0,054 m, theo bán kính robot cấu hình 0,15 m.
- Không xuất hiện `lying_person` hoặc nhãn tư thế nằm trong mẫu theo dõi;
  các khung camera lấy ở đoạn sau hướng về nhóm người đứng/trò chuyện.
- Mẫu cuối leader còn cách goal khoảng 3,19 m. Không ghi nhận ca này là đã
  hoàn thành goal chỉ vì các robot đã đi qua giường.

**Kết luận:** đã quan sát hành vi tránh giường vốn có trên map; chưa chứng
minh nhận diện người nằm hoặc giữ khoảng cách xã hội với người đó. Các số
khoảng hở trên không phải phép đo contact hoặc khoảng cách tới thân người.

### NK-010 — 27/10/2026 — Sửa theo các lỗi quan sát được

**Yêu cầu:** “dựa trên những lỗi bạn vừa thấy, hãy sửa lại cho tối ưu hơn”.

Các thay đổi chính của M6:

1. Chọn cặp RGB-D còn mới và khớp frame/kích thước/timestamp trước DNN;
   dùng depth đã ghép suốt lượt suy luận; tránh xử lý lại capture đã dùng.
2. Ghép điểm người theo khoảng cách dự báo có giới hạn, giữ ID qua mất dấu
   ngắn, loại điểm trùng dưới 0,25 m và hợp mảnh bộ nhớ gần trùng dưới 0,28 m.
3. Hợp tâm/mép TV theo đoạn bề mặt đo được và alias ID, giữ timestamp nguồn;
   thu hồi vùng gắn ID đã bỏ. Phân biệt số track đã hợp và số track đầu vào.
4. Cooldown dùng chung cho các kiểu tìm kiếm/kiểm tra; lượt kiểm tra vật cản
   không bị yêu cầu tìm TV thay thế ngay.
5. Cho phép một lượt camera nhìn vật cản hình học lớn sát tuyến sắp đi,
   mặc định bật ở chế độ động. Điểm nhìn lấy từ map và path, không từ nhãn
   người/giường của scenario. Đề xuất nhìn không tự tạo vùng người.
6. Thử ảnh/crop xoay theo tần suất giới hạn; ưu tiên crop nằm ngang, giữ
   kiểm tra khớp ở tọa độ ảnh gốc trước khi dùng depth.
7. Vì YOLO-tiny vẫn bỏ sót người nằm trong ảnh rõ, bổ sung đề xuất bề mặt
   thấp từ RGB-D, rồi xác minh khớp thân/hông/chân và hình học 3D. Thiếu mũi
   có thể dùng hai vai tin cậy cùng chân xa phù hợp; không gán ngủ.
8. Tránh hai lượt detector toàn ảnh xoay dư khi đã có crop hình học; giảm tải
   profile động xuống camera 6 Hz, tối đa hai crop thường 224 px, OpenCV một
   thread, DNN tối đa 2 Hz thực. Crop nằm ngang giữ 256 px.

Các file mới đáng chú ý: `rgbd_pairing.py`, `vision_regions.py`,
`posture_proposals.py`, `route_inspection.py` và `test_perception_pipeline.py`.
Các sửa khác nằm trong detector, tracking, suy luận xã hội, search, launch
và bộ điều phối lượt quan sát. Không thay D* Lite/MPC bằng backend Paper.

### NK-011 — 27/10/2026 — Kiểm chứng tối ưu và sửa khởi động DDS

**Đối chứng nhận diện:** camera Gazebo riêng nhìn rõ giường. Chạy qua các
hàm xử lý/xuất dữ liệu của node: mẫu có người nằm tạo một ứng viên; mẫu cùng
giường bỏ người không tạo ứng viên. Thời gian suy luận hai mẫu lưu được lần
lượt khoảng 776 ms và 833 ms; không coi là latency trung bình của toàn hệ.

Đây là đối chứng hai ca, không phải thống kê precision/recall hay chứng minh
mọi góc nhìn. Hiệu chuẩn camera kiểm thử là đầu vào phép chiếu; không đưa nhãn
người hoặc tọa độ scenario vào bộ nhận diện.

**Kiểm tra:** 55 kiểm tra pipeline và 50 kiểm tra điều khiển qua; lần chạy bộ
điều khiển báo 1 skipped và 2 cảnh báo SciPy clipping. Ba kiểm tra lint mẫu
`copyright`, `flake8`, `pep257` không nằm trong lệnh xác nhận vì môi trường
thiếu các gói ament tương ứng. Không gọi đó là toàn bộ kiểm tra chất lượng đã qua.

**Khởi động:** một lượt restart không có camera/pose và controller không tìm
được dịch vụ, nên không coi lượt đó là kiểm chứng thành công. Thêm profile
UDPv4 riêng `fastdds_udp.xml` cho launch động, tùy chọn `dds_udp_only`.
Không xóa `/dev/shm` hay sửa cấu hình ROS toàn máy. Lượt sau khởi động đủ
controller/camera; dùng ROS domain 31. Goal cuối được khôi phục có điều kiện,
không ghi đè nếu người dùng đã chọn goal mới.

**Lấy mẫu sau sửa:** khoảng 22 s, RTF 0,200; subscriber audit nhận 17 RGB,
22 depth và 15 timestamp trùng. Điều kiện khác lượt trước (trạng thái robot,
camera và transport), nên không tuyên bố mức tăng RTF do thuật toán hay mọi
ảnh đã hết mất đồng bộ. Bộ nhận diện chủ động chờ cặp hợp lệ thay vì suy luận
khung RGB không có depth tương ứng. Shader RViz lúc mở vẫn còn.

### NK-012 — 28/10/2026 — Dừng mô phỏng theo yêu cầu

**Yêu cầu:** “tắt các mô phỏng đang chạy”.

Đã kiểm tra tiến trình, dừng launch động và cây tiến trình con Gazebo, RViz,
MPC, cảm biến. Cho kết thúc mềm trước, xử lý tiến trình còn lại nếu cần.
Kiểm tra cuối không còn tiến trình hoạt động trong cây mô phỏng đó.

**Trạng thái vận hành cuối đã xác minh:** mô phỏng đã dừng. Không tự khởi
động lại chỉ để lập hai README.

### NK-013 — 28/10/2026 — Thiết lập nhật ký và báo cáo được duy trì cùng dự án

**Yêu cầu:** tạo hai README — một ghi trao đổi/chỉnh sửa, một báo cáo tiến độ
và thay đổi giữa các phiên bản để gửi thầy cô; cập nhật cả hai mỗi khi cập nhật dự án.

Đã tạo tài liệu này và `README_BAO_CAO_TIEN_DO.md`, thêm liên kết ở README
gốc, và đặt quy trình trong `AGENTS.md`. Giữ ảnh/JSON/log minh chứng vào
`docs/evidence/2026-10-27/` thay vì phụ thuộc duy nhất file tạm.

Đợt này chỉ bổ sung hồ sơ và quy trình, không đổi mốc chức năng M6. Kiểm tra
liên kết nội bộ, ảnh/JSON minh chứng và tính nhất quán hai tài liệu. Không
chạy lại mô phỏng hoặc ghi các kết quả test cũ thành test mới của ngày 28/10.

### NK-014 — 28/10/2026 — Rà soát phần không dùng trong cấu hình hiện tại

**Yêu cầu:** xác định các phần dự án không dùng đến.

Đã đọc chuỗi launch `dynamic_social` → `three_robot_social` →
`three_robot_dstar_mpc` → `three_robot_gazebo`, kiểm tra entry point, import,
CMake và tham chiếu trong mã nguồn. Kết luận là phạm vi sử dụng theo cấu
hình D* Lite + MPC động, không phải chứng minh mọi nhánh khác không thể chạy.

- Paper1/Paper2, hai package `multi_robot_formation` và
  `virtual_structure_3robot`, A* độc lập, Nav2/SLAM và các mẫu robot khác
  không được chuỗi launch hiện tại gọi. Giữ riêng nhánh đối chiếu nếu cần.
- `astar_node` và `pid_follower` vẫn được khai báo trong
  `astar_planner/setup.py` nhưng hai module nguồn tương ứng không tồn tại;
  đây là entry point tồn dư, không ảnh hưởng đường khởi động baseline đang chọn.
- `test_cpp_publisher`, `test_subscriber.py`, `test_run_motor.py` là demo
  không được launch hiện tại gọi; không đồng nhất với các bộ test hồi quy.
- `social_protect_uncertain` và `social_inferred_focus` là tùy chọn legacy:
  backend cảnh báo, không tạo vùng theo luật cũ. `provisional_memory` được
  khai báo nhưng không tìm thấy chỗ đọc để xử lý trong script hiện hành.
- `log/`, cache Python và backup không thuộc thuật toán runtime. `build/`
  là sản phẩm build; `install/` vẫn cần cho cách chạy ROS hiện tại, chỉ tái
  tạo sau khi build chứ không xóa tùy tiện.
- Cảnh `people`/`rooms` không được chọn trong launch động nhưng phải giữ
  để đối chiếu theo yêu cầu trước. Các generator world/model vẫn là công
  cụ tái tạo tài nguyên. `_graphics_backend.py`, `kinematics.cpp`, helper
  đội hình và mô hình perception còn được dùng trực tiếp hoặc gián tiếp.

**Kiểm tra:** rà soát tĩnh và xác nhận hai file nguồn entry point không tồn
tại; chưa chạy ROS hoặc thử gỡ thành phần. Không xóa file hay sửa thuật toán.
Cập nhật kết quả vào mục 11 của báo cáo, giữ mốc M6 và trạng thái mô phỏng dừng.

### NK-015 — 28/10/2026 — Tinh gọn dự án, giữ ba backend và hai môi trường

**Yêu cầu:** giữ thuật toán D* Lite + MPC của dự án, cả hai bài báo đã kiểm
thử, môi trường tĩnh/động; xóa file cũ mà không làm hỏng phần được giữ.

**Phạm vi chốt:** tĩnh là `social_people`, động là `social_dynamic`. Giữ
Paper1/Paper2, toàn bộ test tương ứng, perception và vùng xã hội đã sửa,
MPC/đội hình, model/trọng số và công cụ tái tạo asset. Mốc thuật toán vẫn M6.

Đã xóa hai package điều khiển cũ, demo A*/PID và pub/sub/motor, launch một
robot/Nav2/SLAM, URDF/mesh robot khác, GIF cũ, installer Jazzy/Harmonic,
scene `maze1`/`maze2`/`my_maze`/`social_rescue` và cấu hình đi kèm. Bỏ lựa
chọn `rooms`; mặc định hai launch nền chuyển sang `social_people`.
Gỡ entry point trỏ tới module đã mất và target CMake `test_cpp_publisher`.

**Đính chính NK-014:** tuy cả model URDF `3w_v2` không được spawn, file
roller của nó được `3w_v2_multi/omni_wheel.urdf.xacro` include gián tiếp.
Đã chuyển nguyên file roller sang `3w_v2_multi` trước khi gỡ URDF cũ;
mesh `meshes/3w_v2` vẫn giữ vì robot hiện tại cần. Tách nguyên hàm SDF/map
còn được dùng từ generator cũ thành `scene_geometry.py` và `map_geometry.py`;
gỡ phần sinh môi trường cũ. Không thay luật D*/MPC/paper/perception.

Đã dọn build/install/log cũ, cache và backup trong repo; build lại chỉ hai
package hiện hành. Thêm `.gitignore` cho output/cache/backup sinh ra. Các
file đã được Git theo dõi từ snapshot cũ vẫn có diff; không sửa Git index
hay commit thay người dùng. Cập nhật README chính/package, hướng dẫn MPC,
cảnh tĩnh/động và hai paper để không gọi file đã gỡ hoặc installer cũ.

**Kiểm tra và xử lý hồi quy:**

- Build sạch hai package thành công với `BUILD_TESTING=OFF` do máy thiếu
  bộ ament lint. Regression Python chạy riêng; không coi tắt lint là bỏ test.
- Lượt test đầu sau dọn phát hiện bốn ca còn dùng map mê cung cũ. Chuyển
  đúng ảnh map sang `astar_planner/test/fixtures/my_maze.pgm` và đổi đường
  đọc, giữ nguyên tình huống/assertion; không cài fixture làm world.
- Sau khi có fixture, một test lộ mock coordinator thiếu `follower_speed`
  và `narrow_follower_speed`; bổ sung hai giá trị mặc định production đã có
  là 0,22/0,12 m/s trong test, không thay controller.
- Lượt cuối toàn bộ test chức năng: **115 passed**, hai warning clipping
  bounds của SciPy trong Paper2. Ba file lint không chạy.
- So sánh generator trước/sau trong thư mục tạm: **12 file giống từng byte**.
- Bốn launch chính đọc được `--show-args`; sáu tổ hợp hai scene × ba backend
  resolve đúng world/map/bridge/RViz. Kiểm tra Xacro leader có camera và
  follower không camera; 31 tham chiếu tài nguyên robot/world hợp lệ.
- Lượt đọc launch đầu bị sandbox chặn ghi `~/.ros/log`; đã chuyển riêng
  `ROS_LOG_DIR` kiểm tra sang `/tmp`, không đổi quyền hay cấu hình máy.

**Giới hạn:** không chạy lại Gazebo hoặc kiểm thử goal trong đợt dọn này.
Kiểm tra build, test và cấu hình không thay thế kiểm thử runtime đầy đủ.
Danh mục xóa: [manifest](docs/cleanup_2026-10-28.json). Minh chứng mới:
[test log](docs/evidence/2026-10-28/cleanup_tests.log),
[validation](docs/evidence/2026-10-28/cleanup_validation.json).
Bản khôi phục trước dọn lưu tạm tại
`/tmp/three-robot-rescue-before-cleanup-20261028.tar.gz`; không coi `/tmp`
là lưu trữ lâu dài. Hai README đã cập nhật cùng thay đổi.

### NK-016 — 28/10/2026 — Chuẩn hóa tên file theo cấu trúc dự án hiện hành

**Yêu cầu:** đổi tên file cho phù hợp dự án sau khi tinh gọn.

Đã đổi **31 file**, thêm launch riêng `social_static.launch.py`. Quy ước:
tên Python/config theo snake_case, launch theo chức năng/backend, README
theo chủ đề. Hai môi trường dùng tên `social_static` và `social_dynamic`;
giá trị launch `social_scene` là `static` hoặc `dynamic`. Đổi tên world tĩnh
và topic bridge của world tương ứng, không thay hình học hoặc lịch người.

| Nhóm | Tên hiện hành |
|---|---|
| Khởi động tĩnh/động | `social_static.launch.py`, `social_dynamic.launch.py` |
| Launch chung/nền | `social_navigation.launch.py`, `dstar_mpc.launch.py`, `three_robot_sim.launch.py` |
| Hai paper | `paper1_gwo_woa.launch.py`, `paper2_apf_mpc.launch.py`; module/test có cùng tiền tố thuật toán |
| Điều phối D*/MPC | `astar_planner/astar_planner/dstar_mpc_controller.py` |
| Tạo map xã hội | `ros2_omni_robot_sim/scripts/social_costmap.py` |
| Cảnh tĩnh | `social_static.sdf`, `.yaml`, `.pgm`, `_scene.json`, `_layout.svg` và generator tương ứng |
| Bridge | `social_static_bridge.yaml`, `social_dynamic_bridge.yaml` |
| Robot | `omni_kinematics.cpp`, `three_robot_controllers.yaml` |
| Tài liệu | `README_DSTAR_MPC.md`, `README_SOCIAL_STATIC.md`, `README_SOCIAL_DYNAMIC.md`, README hai paper có tên thuật toán |

Giữ tên package ROS, console executable, node/topic điều khiển và hai README
nhật ký/báo cáo. Tên world tĩnh và đường dẫn launch cũ không còn dùng;
cập nhật launch/include, Python import, setup entry point, CMake, Xacro,
RViz, generator, test và tài liệu hướng dẫn. Giữ nguyên nội dung lịch sử
trước mục này và raw evidence; chỉ sửa đích liên kết để vẫn mở được file.

Build/install cũ được xóa và tạo lại để không còn launch/module đã đổi tên
trong bản cài. Không tạo wrapper mang tên cũ. Các tên chuẩn của ROS/build
như `package.xml`, `CMakeLists.txt`, `setup.py`, `AGENTS.md` giữ nguyên.

**Kiểm chứng:** build sạch hai package thành công (`BUILD_TESTING=OFF`);
toàn bộ **115 test chức năng qua**, hai warning SciPy ở Paper2, ba lint file
không chạy. So sánh generator trước/sau sau khi chuẩn hóa tên world/path:
12 file tương đương; 31 tham chiếu robot/world hợp lệ. Đọc tham số cả bảy
launch, resolve sáu tổ hợp scene/backend, kiểm tra Xacro leader/follower,
import module từ bản cài và xác nhận đường dẫn asset cũ không còn.

Mốc thuật toán vẫn M6. Không chạy Gazebo/goal trong đợt đổi tên.
Danh sách đầy đủ: [bảng đổi tên](docs/rename_2026-10-28.json).
Lệnh chạy hiện hành xem [README chính](README.md). Có bản khôi phục tạm
`/tmp/three-robot-rescue-before-rename-20261028.tar.gz`; minh chứng kiểm
tra được lưu vào `docs/evidence/2026-10-28/rename_*` trong repo.

### NK-017 — 28/10/2026 — Đổi tên package và làm sạch bản nguồn GitHub

**Yêu cầu:** đổi cả tên `astar_planner`, làm sạch toàn bộ dự án để người
dùng đưa lên GitHub. Điều chỉnh phạm vi so với NK-016 vốn giữ tên package.

Đổi package `astar_planner` → `social_navigation_planner`, gồm thư mục
nguồn, namespace Python, marker ament, `setup.py`, `setup.cfg`, manifest,
import và mọi launch sử dụng. Đổi `ros2_omni_robot_sim` →
`social_navigation_sim`, gồm tên project CMake, manifest, đường dẫn
package URI/Xacro, package share, launch, perception, test và hướng dẫn.
Giữ console executable, node/topic điều khiển, ba backend và hai cảnh.
Danh mục: [manifest](docs/github_cleanup_2026-10-28.json).

Đã xóa cấu hình VS Code có đường dẫn máy cũ; mở rộng `.gitignore` cho
editor, tài khoản/agent, `.env`, private key, cache, egg-info và output.
Thư mục `.agents`, `.codex`, `.aws` do môi trường mount chỉ đọc được giữ
cục bộ; không đọc nội dung, không đưa vào Git hoặc ZIP. Dọn build/install/log
sau khi kiểm chứng. Không xóa Git history/remote và không commit/push.

Thêm `scripts/prepare_github.py` kiểm tra và đóng gói theo danh sách nguồn
cho phép, không sao chép `.git` hoặc thư mục cục bộ. Thêm
[hướng dẫn GitHub](docs/GITHUB_PREPARATION.md) và [giấy phép](LICENSES.md).
Giữ MIT/attribution của simulator và model; planner trước đây chưa khai báo
giấy phép nên dùng `LicenseRef-Not-Specified`, không tự cấp lại giấy phép.
Điền mô tả package đúng chức năng, bổ sung buildtool `ament_python` và
phụ thuộc runtime simulator → planner. Không tự thay danh tính maintainer.

**Kiểm chứng:** build sạch hai package tên mới thành công; 115 test qua,
hai warning clipping của SciPy ở Paper2, ba lint file không chạy. Bảy launch
đọc tham số, sáu tổ hợp scene/backend resolve đúng asset; namespace planner
và ba module backend import từ bản cài được. Xacro leader/follower hợp lệ,
31 tham chiếu robot/world đúng. Kiểm tra bản nguồn không có file >=100 MiB
và không khớp các mẫu private key/AWS/GitHub token đã kiểm tra; đây không
phải kiểm toán bí mật đầy đủ. Minh chứng build/test lưu trong
`docs/evidence/2026-10-28/github_*`.

Mốc chức năng vẫn M6; chưa chạy Gazebo/goal sau đổi tên package. Nguồn cần
build lại trước khi chạy vì đã dọn output cuối. ZIP nguồn được tạo tại
`/tmp/three-robot-rescue-github.zip`; có thể tái tạo bằng script trong repo.
Bản khôi phục trước đổi package lưu tạm tại
`/tmp/three-robot-rescue-before-package-rename-20261028.tar.gz`.

### NK-018 — 28/10/2026 — Cập nhật repository GitHub của người dùng

**Yêu cầu:** đưa bản dự án đã làm sạch lên
`https://github.com/duc2605/three-robot-rescue`, nhánh `main`.

Đã đối chiếu remote: commit nền là
`115f150c4fd6c8660ec798838c5638e452ec5e93`, lịch sử độc lập với snapshot
Git cũ trong workspace. Chuẩn bị bản đồng bộ trong clone tạm để tạo commit
nối tiếp remote, không force-push hoặc đưa lịch sử build/log của snapshot
cũ lên repository đích. Giữ danh tính tác giả đã có trong commit remote.

Nội dung đồng bộ gồm hai package tên mới, ba backend, hai môi trường,
test/tài nguyên/tài liệu và script đóng gói. Loại các package/tài nguyên cũ
trên remote theo phạm vi tinh gọn đã được người dùng cho phép. Thư mục
Git, tài khoản/agent, build/install/log/cache không nằm trong bản nguồn.
README chính ghi đúng repository đích. Thông tin kiểm thử vẫn là kết quả
NK-017: 115 test qua và build hai package; không ghi thành lượt test mới.

Kiểm tra bộ nguồn, diff và staged paths trước commit; xác nhận remote HEAD
sau push. Trạng thái và liên kết commit được báo sau thao tác Git, không tự
ghi trước mã commit chưa được tạo. Mốc thuật toán vẫn M6, không chạy Gazebo.

**Kết quả trong phiên này:** đã tạo commit cập nhật trong clone tạm
`/tmp/three-robot-rescue-github-publish-20261028`. Push HTTPS chưa thành công:
Git không có credential helper/token và báo không đọc được username khi
terminal prompt bị tắt. SSH agent không có identity. Plugin GitHub có sẵn
để kết nối nhưng chưa được kết nối; cần người dùng đăng nhập GitHub hoặc
kết nối plugin trước khi hoàn tất. Chưa có thay đổi nào được đẩy lên remote.

### NK-019 — 28/10/2026 — Đăng nhập và đẩy bản nguồn lên GitHub thành công

Người dùng hoàn tất đăng nhập GitHub bằng tài khoản `duc2605`. Đã xác
nhận bằng `gh auth status`, cấu hình credential helper qua
`gh auth setup-git --hostname github.com` và push nối tiếp nhánh `main`.
Git xác nhận remote chuyển từ `115f150` sang commit **`d1f6b96`**:
[bản cập nhật nguồn](https://github.com/duc2605/three-robot-rescue/commit/d1f6b96).

Như vậy lỗi xác thực ở NK-018 đã được xử lý. Hai package hiện hành, hai
paper, hai môi trường, test và tài liệu đã được đưa lên repository được
chỉ định. Không force-push; không chạy lại Gazebo hoặc ghi kết quả 115 test
cũ thành lượt kiểm thử mới. Cập nhật hai README để ghi nhận kết quả đồng bộ.

## 5. Minh chứng đã lưu trong repository

| File | Ý nghĩa | Giới hạn |
|---|---|---|
| [Ảnh có người nằm](docs/evidence/2026-10-27/posture_with_person.png) | Ảnh xuất từ pipeline kiểm thử, có nhãn ứng viên | Một góc camera |
| [Ảnh giường trống](docs/evidence/2026-10-27/posture_empty_bed.png) | Đối chứng không sinh ứng viên người nằm | Một ca âm tính |
| [Kết quả pose](docs/evidence/2026-10-27/posture_validation.json) | Số ứng viên, vị trí đo, latency hai ca | Không phải bộ dữ liệu đánh giá |
| [Mẫu runtime trước](docs/evidence/2026-10-27/runtime_before.json) | Clock, topic, lệnh, trạng thái và dữ liệu audit | Khoảng 22 s, tình huống cụ thể |
| [Mẫu runtime sau](docs/evidence/2026-10-27/runtime_after.json) | Mẫu sau cấu hình mới và UDP | Điều kiện khác, không phải A/B kiểm soát |
| [Log lịch người](docs/evidence/2026-10-27/scenario_motion_validation.log) | Trích log giai đoạn và xác minh pose physics | World tạm chạy nhanh, không phải toàn bộ stack robot |

Các file trên được sao lưu từ minh chứng của phiên làm việc trước khi viết
README; không phải kết quả được chạy mới ngày 28/10/2026.

## 6. Cách cập nhật từ các lần sau

Thực hiện theo [AGENTS.md](AGENTS.md). Thêm mục `NK-020` tiếp theo; không viết
đè nhật ký cũ. Sau mỗi thay đổi code/world/config/test hoặc kết luận thực nghiệm:

1. Ghi yêu cầu và lý do đổi.
2. Liệt kê phần nguồn bị tác động và hành vi trước/sau.
3. Ghi đúng kiểm tra đã chạy, kết quả, điều kiện và việc chưa kiểm tra.
4. Cập nhật đồng thời trạng thái, bảng phiên bản và hạn chế trong báo cáo.
5. Giữ minh chứng cần thiết trong repo và kiểm tra liên kết.

Mẫu mục mới:

```markdown
### NK-XXX — DD/MM/YYYY — Tên cập nhật

Yêu cầu/bối cảnh:
Thay đổi và lý do:
File liên quan:
Kiểm tra đã chạy và kết quả:
Giới hạn/việc còn lại:
Ảnh hưởng tới báo cáo tiến độ:
```

Quy trình áp dụng cho các tác vụ làm việc trong repo. Không có dịch vụ nền
tự đọc ý định của mọi sửa đổi ngoài Codex; người sửa bằng công cụ khác cũng
cần cập nhật hai file trong cùng thay đổi.
