# Dữ liệu hồi quy

`my_maze.pgm` giữ nguyên hình học map của ca kẹt đội hình đã ghi nhận.
`test_formation_recovery.py` và `test_mpc_formation_motion.py` cần nó để tái
hiện lỗi và kiểm tra phục hồi, không thay bằng map trống hoặc bỏ test.
Đây là fixture, không được cài vào package mô phỏng hoặc chọn làm world.
