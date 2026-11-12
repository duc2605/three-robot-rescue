# NK119 — Paper2 mất pose/TF, biểu hiện như lỗi bản đồ RViz

Ảnh người dùng có map hiển thị, Global Status: Error và marker spawn estimate. Không có chi tiết status mở rộng nên chưa xác nhận riêng thông báo RViz.
Log lượt paper2_20261103_141539_026331080: controller PID79905 thoát code1 tại1793690144.8838272, sau log robot1: using Gazebo world pose in map. Trích log giữ trong launch_excerpt.txt. Không lưu được traceback gốc trong ROS log đọc được.

Lỗi xác định bằng mã: ThreeRobotDStarMPC.world_pose_callback gọi self.record_pose(index,x,y,yaw,stamp), trong khi Paper2Controller override chỉ nhận index,x,y,yaw. Python phát TypeError khi dispatch callback này; lỗi xảy ra ngoài try/except tick, khiến node thoát. Node này cấp TF map/odom và pose dùng chung; mất node giải thích robot không định vị trong RViz dù map server có dữ liệu. Đây là suy luận nhân quả từ call signature và thời điểm log, không trích traceback chưa có.

Sửa adapter Paper2 nhận stamp=None, chuyển tiếp nguyên stamp tới lớp nền và dùng measurement timestamp cho dt ước lượng vận tốc. Giữ call không timestamp cho odom fallback. Không đổi map/world, APF/MPC, baseline hay camera.

Thêm regression trong test_paper2_apf_mpc.py: stamped callback không lỗi, timestamp được chuyển tiếp, vận tốc tính theo measurement time khi receipt time giống nhau; callback thiếu stamp dùng clock hiện tại. Test được viết, CHƯA CHẠY. Chỉ kiểm AST và git diff --check. Chưa build/Gazebo, chưa xác nhận runtime sau sửa. Lệnh tự chạy có trong README Paper2.

Backup: backups/20261103_141814_707453_nk119_fix_paper2_timestamp_pose_callback; script verify archive từng file/SHA so nguồn và manifest verified_against_source=true trước sửa.
