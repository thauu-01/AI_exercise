# AI_exercise

# Đồ án cá nhân: 8-Puzzle Solver

## 🎯 Mục tiêu
Xây dựng một chương trình giải bài toán **8-Puzzle** sử dụng nhiều thuật toán tìm kiếm khác nhau trong lĩnh vực Trí tuệ nhân tạo.

---

## 🧠 Các thuật toán được triển khai

| Thuật Toán               | Mô Tả                                                                 | Minh Họa GIF                              |
|--------------------------|----------------------------------------------------------------------|-------------------------------------------|
| **Breadth-First Search (BFS)** | Tìm kiếm theo chiều rộng, khám phá tất cả trạng thái ở mức hiện tại trước khi đi sâu hơn, dùng hàng đợi (queue). Đảm bảo đường đi ngắn nhất.    | ![BFS](gifs/bfs.gif)                     |
| **Depth-First Search (DFS)**   | Tìm kiếm theo chiều sâu, khám phá nhánh sâu nhất trước, dùng ngăn xếp (stack). Có thể không tối ưu do không kiểm tra chi phí.             |                    |
| **Uniform Cost Search (UCS)**  | Tìm kiếm chi phí đồng nhất, ưu tiên trạng thái có tổng chi phí thấp nhất từ gốc, dùng hàng đợi ưu tiên (priority queue).        |                     |
| **Iterative Deepening DFS (IDDFS)** | Kết hợp DFS với giới hạn độ sâu tăng dần, lặp lại cho đến khi tìm ra giải pháp, tiết kiệm bộ nhớ hơn DFS.               |                 |
| **Greedy Best-First Search**   | Tìm kiếm tham lam, chọn trạng thái có giá trị heuristic (khoảng cách Manhattan) nhỏ nhất mà không xét chi phí từ gốc.           | ![Greedy](gifs/greedy.gif)               |
| **A* Search**                 | Tìm kiếm tối ưu, kết hợp chi phí từ gốc (g) và heuristic (h = Manhattan + Linear Conflict), đảm bảo đường đi ngắn nhất nếu heuristic thỏa mãn tính chất tam giác.       |                 |
| **IDA* Search**               | Kết hợp A* với giới hạn ngưỡng heuristic tăng dần, tiết kiệm bộ nhớ hơn A*.                   | ![IDA*](gifs/ida.gif)               |
| **Simple Hill Climbing**       | Leo đồi đơn giản, chọn trạng thái láng giềng tốt hơn hiện tại dựa trên heuristic, dễ bị kẹt ở cực trị cục bộ.                     |     |
| **Steepest Hill Climbing**     | Leo đồi dốc nhất, chọn trạng thái láng giềng tốt nhất dựa trên heuristic trong tất cả các láng giềng, vẫn có thể kẹt ở cực trị cục bộ.     |  |
| **Stochastic Hill Climbing**   | Leo đồi ngẫu nhiên, chọn trạng thái láng giềng ngẫu nhiên nhưng ưu tiên trạng thái tốt hơn, giúp thoát cực trị cục bộ.            |  |
| **Simulated Annealing**        | Mô phỏng ủ nhiệt, chấp nhận cả trạng thái xấu hơn với xác suất giảm dần theo "nhiệt độ", giúp thoát cực trị cục bộ.    |  |
| **Beam Search**                | Tìm kiếm chùm, giữ số lượng trạng thái giới hạn (beam width) ở mỗi mức, kết hợp giữa BFS và tính tham lam.   | ![Beam Search](gifs/beam_search.gif)     |

## 👨‍💻 Tác giả

**Nguyễn Trung Hậu**  
MSSV: `23110212`  
Môn: `Trí Tuệ Nhân Tạo`  
Giáo viên hướng dẫn: `Phan Thị Huyền Trang` 
