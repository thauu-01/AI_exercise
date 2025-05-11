# AI_exercise

# Đồ án cá nhân: 8-Puzzle Solver

## 🎯 Mục tiêu
      
   Xây dựng một chương trình giải bài toán 8-Puzzle sử dụng nhiều thuật toán tìm kiếm trong lĩnh vực Trí tuệ nhân tạo (AI). Chương trình cung cấp giao diện đồ họa (GUI) trực quan để nhập trạng thái ban đầu, hiển thị quá trình giải và so sánh hiệu suất của các thuật toán. Các thuật toán được triển khai bao gồm tìm kiếm không có thông tin, tìm kiếm có thông tin, tìm kiếm ràng buộc, tìm kiếm cục bộ, tìm kiếm trong môi trường không xác định, tìm kiếm ràng buộc cùng với một số thuật toán đặc biệt.
     
---

## 🧠 Nội dung
### 📝✏️ Các thành phần của bài toán 8-Puzzle
- **State space**: Tập hợp các hoán vị của 9 ô (9!/2 trạng thái khả thi do kiểm tra tính khả thi).
- **Actions**: Di chuyển ô trống (lên, xuống, trái, phải).
- **Transition model**: Hoán đổi ô trống với ô lân cận, tạo trạng thái mới.
- **Goal test**: Trạng thái bằng `(1, 2, 3, 4, 5, 6, 7, 8, 0)`.
- **Path cost**: Mỗi bước di chuyển có chi phí 1.
- **Solution**: Đường đi từ trạng thái ban đầu đến trạng thái mục tiêu, biểu diễn bằng danh sách các trạng thái.
- **Heuristic** : Khoảng cách Manhattan + Linear Conflict để ước lượng chi phí .
  
### 2.1. Các thuật toán tìm kiếm không có thông tin
#### Thuật toán và mô tả

| Thuật Toán               | Mô Tả                                                                 | Minh Họa GIF                              |
|--------------------------|----------------------------------------------------------------------|-------------------------------------------|
| **Breadth-First Search (BFS)** | Tìm kiếm theo chiều rộng, sử dụng hàng đợi (queue) để khám phá tất cả các trạng thái ở mức hiện tại trước khi chuyển sang mức sâu hơn. Đảm bảo tìm được đường đi ngắn nhất nhưng tốn bộ nhớ khi không gian trạng thái lớn.    | ![BFS](gif/bfs.gif)                     |
| **Depth-First Search (DFS)**   | Tìm kiếm theo chiều sâu, sử dụng ngăn xếp (stack) để khám phá nhánh sâu nhất trước khi quay lại. Không đảm bảo đường đi ngắn nhất và có thể dẫn đến vòng lặp nếu không kiểm soát.             |          ![DFS](gif/dfs.gif)            |
| **Uniform Cost Search (UCS)**  | Tìm kiếm chi phí đồng nhất, sử dụng hàng đợi ưu tiên (priority queue) để ưu tiên trạng thái có chi phí đường đi từ gốc thấp nhất. Đảm bảo đường đi tối ưu khi chi phí di chuyển giữa các trạng thái bằng nhau.        |   ![UCS](gif/ucs.gif)                  |
| **Iterative Deepening DFS (IDDFS)** | Kết hợp ưu điểm của DFS và BFS, thực hiện DFS với giới hạn độ sâu tăng dần qua từng vòng lặp. Tiết kiệm bộ nhớ hơn BFS và đảm bảo đường đi ngắn nhất.            |   ![IDDFS](gif/iddfs.gif)              |


#### So sánh hiệu suất và nhận xét
1.	  DFS (Depth-First Search):
	  
•	Ưu điểm: Tiết kiệm bộ nhớ nhờ chỉ khám phá một nhánh tại một thời điểm (mở rộng 7298 trạng thái) và có thời gian thực thi nhanh (0.382s).

•	Nhược điểm: Không đảm bảo đường đi ngắn nhất (7112 bước), dễ bị kẹt trong nhánh sâu hoặc vòng lặp nếu không kiểm soát độ sâu.

2.	 BFS (Breadth-First Search):

•	Ưu điểm: Đảm bảo đường đi ngắn nhất (24 bước), phù hợp với bài toán cần giải pháp tối ưu về số bước.

•	Nhược điểm: Tốn nhiều bộ nhớ do mở rộng 118151 trạng thái và thời gian thực thi hơi cao (0.402s).

3.	  UCS (Uniform Cost Search):
 
•	Ưu điểm: Đảm bảo đường đi ngắn nhất (24 bước) và tối ưu về chi phí khi chi phí di chuyển bằng nhau.

•	Nhược điểm: Mở rộng nhiều trạng thái hơn BFS (140087) và thời gian thực thi cao hơn (0.577s) do quản lý hàng đợi ưu tiên.

4.	  IDDFS (Iterative Deepening Depth-First Search):
	 
•	Ưu điểm: Đảm bảo đường đi ngắn nhất (24 bước) và kết hợp ưu điểm của BFS (tối ưu về số bước) với DFS (tiết kiệm bộ nhớ tương đối).

•	Nhược điểm: Mở rộng rất nhiều trạng thái (429283) và thời gian thực thi dài (9.995s) do lặp lại tìm kiếm với các giới hạn độ sâu.

#### Nhận xét

•      Hiệu suất tối ưu về số bước: BFS, UCS, và IDDFS đều tìm được đường đi ngắn nhất (24 bước), trong khi DFS với đường đi rất dài (7112 bước). 

•      Hiệu suất về bộ nhớ và tốc độ: DFS là lựa chọn tốt nhất khi bộ nhớ hạn chế và thời gian thực thi quan trọng (0.382s, 7298 trạng thái). BFS và UCS cân bằng giữa số bước tối ưu và thời gian thực thi hợp lý, nhưng UCS mở rộng nhiều trạng thái hơn một chút. IDDFS, mặc dù đảm bảo giải pháp tối ưu, lại tiêu tốn nhiều tài nguyên nhất (9.995s, 429283 trạng thái).

### 2.2. Các thuật toán tìm kiếm có thông tin
#### Thuật toán và mô tả

| Thuật Toán               | Mô Tả                                                                 | Minh Họa GIF                              |
|--------------------------|----------------------------------------------------------------------|-------------------------------------------|
| **Greedy Search**   | Tìm kiếm tham lam, sử dụng hàng đợi ưu tiên để chọn trạng thái có giá trị heuristic (khoảng cách Manhattan) nhỏ nhất mà không xét chi phí từ gốc. Nhanh nhưng không đảm bảo tối ưu.          | ![Greedy](gif/greedy.gif)               |
| **A* Search**                 | Tìm kiếm tối ưu, kết hợp chi phí từ gốc (g) và giá trị heuristic (h = Manhattan + Linear Conflict). Đảm bảo đường đi ngắn nhất nếu heuristic thỏa mãn tính chất đơn điệu (monotonic).       | ![A*](gif/a_star.gif)                |
| **IDA* Search**               | Biến thể của A*, sử dụng tìm kiếm theo chiều sâu với ngưỡng heuristic tăng dần. Tiết kiệm bộ nhớ hơn A* nhưng có thể lặp lại việc khám phá trạng thái.               | ![IDA*](gif/ida_star.gif)               |

#### So sánh hiệu suất và nhận xét
1.	Greedy Best-First Search:
	
•	Ưu điểm: Rất nhanh (0.001s) và mở rộng ít trạng thái nhất (33), nhờ chỉ tập trung vào trạng thái có giá trị heuristic thấp nhất tại mỗi bước(24 bước).

•	Nhược điểm: Không đảm bảo tính tối ưu trong mọi tình huống, vì chỉ dựa vào heuristic (h) mà không tính chi phí đường đi (g). 

2.	A Search*:
   
•	Ưu điểm: Đảm bảo đường đi tối ưu (24 bước) nhờ kết hợp chi phí đường đi (g) và heuristic (h). Heuristic đơn điệu (Manhattan + Linear Conflict) giúp A* định hướng tốt.

•	Nhược điểm: Tốn nhiều bộ nhớ và thời gian hơn (0.013s, 1560 trạng thái) do phải quản lý hàng đợi ưu tiên và mở rộng nhiều trạng thái để đảm bảo tính tối ưu.

3.	IDA Search*:
   
•	Ưu điểm: Đảm bảo đường đi tối ưu (24 bước) với số trạng thái mở rộng thấp hơn A* (167) và thời gian nhanh (0.002s). IDA* tiết kiệm bộ nhớ bằng cách sử dụng chiến lược lặp sâu với ngưỡng chi phí.

•	Nhược điểm: Có thể lặp lại việc khám phá một số trạng thái, làm tăng chi phí tính toán trong các trường hợp phức tạp hơn.

#### Nhận xét

•      Hiệu suất tối ưu về số bước: Cả Greedy, A*, và IDA* đều tìm được đường đi tối ưu (24 bước) trong trường hợp này. Tuy nhiên, A* và IDA* đảm bảo tính tối ưu trong mọi trường hợp nhờ sử dụng f = g + h, trong khi Greedy chỉ đạt được nhờ heuristic hiệu quả. ớc). 

•      Hiệu suất về bộ nhớ và tốc độ: 

	•	Greedy vượt trội về tốc độ (0.001s) và số trạng thái mở rộng (33), nhưng không đáng tin cậy về tính tối ưu trong các trường hợp phức tạp.
	•	IDA* cân bằng tốt giữa tốc độ (0.002s), số trạng thái mở rộng (167), và tính tối ưu, là lựa chọn hiệu quả khi bộ nhớ hạn chế.
	•	A* tốn nhiều tài nguyên hơn (0.013s, 1560 trạng thái) nhưng đảm bảo giải pháp tối ưu, phù hợp khi tài nguyên không bị giới hạn.


### 2.3. Các thuật toán tìm kiếm cục bộ
#### Thuật toán và mô tả


| Thuật Toán               | Mô Tả                                                                 | Minh Họa GIF                              |
|--------------------------|----------------------------------------------------------------------|-------------------------------------------|
| **Simple Hill Climbing**       | Tìm kiếm leo đồi đơn giản, chọn trạng thái láng giềng ngẫu nhiên tốt hơn trạng thái hiện tại dựa trên heuristic (Manhattan + Linear Conflict). Dễ bị kẹt ở cực trị cục bộ.                    |     |
| **Steepest Hill Climbing**     | Tìm kiếm leo đồi dốc nhất, xem xét tất cả trạng thái láng giềng và chọn trạng thái có heuristic tốt nhất. Vẫn có nguy cơ kẹt ở cực trị cục bộ nhưng cải thiện hơn Simple Hill Climbing.    |![Steepest Hill](gif/steepest_hill.gif)  |
| **Stochastic Hill Climbing**   | Tìm kiếm leo đồi ngẫu nhiên, chọn trạng thái láng giềng ngẫu nhiên nhưng ưu tiên trạng thái tốt hơn dựa trên xác suất. Giúp thoát khỏi cực trị cục bộ nhờ yếu tố ngẫu nhiên.           | ![Stochastic Hill](gif/stochastic_hill.gif) |
| **Simulated Annealing**        | Mô phỏng ủ nhiệt, chấp nhận cả trạng thái xấu hơn với xác suất giảm dần theo "nhiệt độ". Nhiệt độ giảm theo thời gian (cooling rate), giúp thoát khỏi cực trị cục bộ và tìm giải pháp toàn cục.    | ![Simulated Annealing](gif/simulated_annealing.gif)   |
| **Beam Search**                | Tìm kiếm chùm, giữ một số lượng trạng thái giới hạn (beam width) ở mỗi mức, kết hợp giữa BFS và tính tham lam. Có thể bỏ sót giải pháp tối ưu nếu beam width nhỏ.   | ![Beam Search](gif/beam.gif)     |
| **Genetic Algorithm**                | Thuật toán di truyền, sử dụng quần thể các trạng thái, thực hiện các phép lai ghép (crossover) và đột biến (mutation) để tiến hóa đến trạng thái mục tiêu. Phù hợp với không gian trạng thái phức tạp.   | ![Genetic Algorithm](gif/genetic.gif)     |

#### So sánh hiệu suất 
1.	Simple Hill Climbing: 

•	Ưu điểm: Rất nhanh (~0.001s) và mở rộng ít trạng thái (10) nhờ chiến lược đơn giản.

•	Nhược điểm: Dễ bị kẹt ở cực trị cục bộ, không tìm thấy giải pháp trong trường hợp này.

2.	Steepest Ascent Hill Climbing: 

•	Ưu điểm: Nhanh (0.003s) và mở rộng ít (40), tìm được giải pháp (40 bước) nhờ chọn trạng thái tốt nhất.

•	Nhược điểm: Giải pháp không tối ưu và vẫn có nguy cơ kẹt ở cực trị.

3.	Stochastic Hill Climbing: 

•	Ưu điểm: Tìm được giải pháp (568 bước) nhờ yếu tố ngẫu nhiên giúp thoát cực trị cục bộ.

•	Nhược điểm: Số bước và thời gian dài (0.035s, 568 trạng thái), không hiệu quả về tối ưu.

4.	Simulated Annealing: 

•	Ưu điểm: Tìm được giải pháp (460 bước) với thời gian hợp lý (0.010s), khả năng thoát cực trị nhờ cơ chế làm nguội.

•	Nhược điểm: Giải pháp dài  và mở rộng nhiều (461) hơn Steepest Ascent.

5.	Beam Search: 

•	Ưu điểm: Tìm được giải pháp (1264 bước) với beam width = 3, duy trì khám phá đa dạng.

•	Nhược điểm: Số bước và thời gian dài (0.063s, 3302 trạng thái), không tối ưu.

6.	Genetic Algorithm: 

•	Ưu điểm: Khả năng khám phá không gian lớn (1471208 trạng thái), lý tưởng cho bài toán phức tạp.

•	Nhược điểm: Không tìm thấy giải pháp trong giới hạn ít thế hệ, tốn nhiều thời gian (~0.1s+).



#### Nhận xét

•      Hiệu suất về giải pháp: Chỉ Steepest Ascent Hill Climbing, Stochastic Hill Climbing, Simulated Annealing, và Beam Search tìm được giải pháp. Simple Hill Climbing và Genetic Algorithm thất bại trong nhiều trường hợp, phản ánh hạn chế của tìm kiếm cục bộ. 

•      Hiệu suất về bộ nhớ và tốc độ: 

	•	Simple Hill Climbing và Steepest Ascent Hill Climbing tiết kiệm tài nguyên nhất (10-40 trạng thái, 0.001-0.003s), nhưng không ổn định.
	•	Simulated Annealing cân bằng tốt giữa thời gian (0.010s) và số lần mở rộng (461).
	•	Beam Search và Genetic Algorithm tốn nhiều tài nguyên nhất (3302 và 1471208 trạng thái), nhưng chỉ Beam Search thành công.



### 2.4. Các thuật toán tìm kiếm trong môi trường không xác định
#### Thuật toán và mô tả

| Thuật Toán               | Mô Tả                                                                 | Minh Họa GIF                              |
|--------------------------|----------------------------------------------------------------------|-------------------------------------------|
| **AO Search***                | Được thiết kế để xử lý các bài toán tìm kiếm trong môi trường không xác định (non-deterministic), nơi mỗi hành động có thể dẫn đến nhiều kết quả khác nhau.   |      |
| **Trust-Based Search**                | Thuật toán này hoạt động trong môi trường không có quan sát (non-observable), dựa trên niềm tin (belief state) và sử dụng yếu tố tin cậy (trust) để định hướng tìm kiếm.   | ![Trust-Based Search](gif/trust_search.gif)      |
| **Trust-Based Search (Partial)**                | Thuật toán này xử lý bài toán với quan sát từng phần (partial observability), sử dụng belief state và cập nhật dựa trên các quan sát (percepts).   |  ![Trust-Based Search (Partial)](gif/trust_partial.gif)     |


#### So sánh hiệu suất 
1.	AND-OR Search: 

•	Ưu điểm: Xử lý tốt môi trường không xác định, xây dựng kế hoạch điều kiện khả thi cho mọi trường hợp. 

•	Nhược điểm: Khó tìm ra đường đi thành công

2.	Trust No Observation: 

•	Ưu điểm: Hiệu quả về mặt mở rộng trạng thái nhờ không phải xử lý quan sát. Yếu tố tin cậy giúp định hướng tìm kiếm.

•	Nhược điểm: Đường đi dài do thiếu thông tin, không đảm bảo tối ưu. Belief state có thể lớn nếu không có cách thu hẹp.

3.	Trust Partial Observation: 

•	Ưu điểm: Tận dụng quan sát để thu hẹp belief state, dẫn đến đường đi ngắn hơn . Kế hoạch điều kiện đảm bảo tính khả thi, phù hợp với thông tin hạn ché.

•	Nhược điểm: Số trạng thái mở rộng lớn  và thời gian chậm do chi phí tính toán belief state và cập nhật từ quan sát.



📝✏️ Tóm tắt các thành phần của bài toán Sudoku 6x6

• State space: Tập hợp các gán giá trị 1-6 cho 36 ô, thỏa mãn ràng buộc Alldiff (hàng, cột, vùng 2x3), ước lượng 10⁶-10⁸ trạng thái khả thi.

• Actions: Gán giá trị 1-6 cho ô trống, tuân theo ràng buộc không trùng lặp.

• Transition model: Cập nhật trạng thái bằng cách gán giá trị, kiểm tra tính hợp lệ, từ chối nếu có xung đột.

• Goal test: Bảng 6x6 hoàn chỉnh, mỗi hàng, cột, vùng 2x3 chứa duy nhất 1-6.

• Path cost: Mỗi gán giá trị hợp lệ có chi phí 1, tổng bằng số ô trống.

• Solution: Đường đi từ trạng thái ban đầu đến bảng hoàn chỉnh, biểu diễn bằng các bước gán giá trị.

• Heuristic: MRV (ưu tiên ô ít giá trị), LCV (giá trị ít ràng buộc), AC-3 (tính nhất quán cung).

### 2.5. Các thuật toán tìm kiếm có ràng buộc
#### Thuật toán và mô tả


| Thuật Toán               | Mô Tả                                                                 | Minh Họa GIF                              |
|--------------------------|----------------------------------------------------------------------|-------------------------------------------|
| **AC-3**                |Là thuật toán đảm bảo tính nhất quán cung (arc consistency) trong bài toán CSP. Nó xử lý từng cung (arc) trong danh sách các ràng buộc bằng cách loại bỏ các giá trị không thể thỏa mãn từ miền giá trị (domains) của các biến. Thuật toán sử dụng một hàng đợi (queue) để xử lý các cung và lặp lại cho đến khi không còn cung nào cần sửa đổi hoặc phát hiện không có giải pháp nào.   |   ![AC-3](gif/backtracking.gif)     |
| **Min-Conflicts**                | Là thuật toán tìm kiếm cục bộ dựa trên việc giảm thiểu xung đột (conflicts) trong bài toán CSP. Nó bắt đầu với một trạng thái ngẫu nhiên hoặc nhập liệu và lặp lại các bước thay đổi giá trị của các biến có xung đột để đạt được trạng thái không xung đột. Thuật toán chọn ngẫu nhiên một biến có xung đột và gán giá trị làm giảm số xung đột tối đa.   |   ![Min-Conflicts](gif/backtracking.gif)     |
| **Backtracking CSP**                | Kết hợp với AC-3 để giải bài toán CSP. Backtracking khám phá không gian trạng thái theo cách đệ quy, gán giá trị cho các biến và quay lui khi phát hiện xung đột. AC-3 được sử dụng như một bước tiền xử lý để giảm miền giá trị, và trong quá trình tìm kiếm, nó thực hiện suy luận để cập nhật miền.   |   ![Backtracking CSP](gif/backtracking.gif)     |


#### So sánh hiệu suất 
1.	AC-3: 

•	Ưu điểm: Rất nhanh hiệu quả trong việc giảm miền giá trị, giúp cải thiện hiệu suất của các thuật toán tìm kiếm sau đó. Mở rộng ít trạng thái.

•	Nhược điểm: Không tìm được giải pháp hoàn chỉnh, chỉ là bước tiền xử lý.

2.	Min-Conflicts: 

•	Ưu điểm: Tìm giải pháp nhanh  với ít trạng thái mở rộng nếu khởi tạo tốt. 

•	Nhược điểm: Không đảm bảo tìm được giải pháp tối ưu, phụ thuộc vào ngẫu nhiên. Có thể thất bại nếu không gian trạng thái phức tạp.

3.	Backtracking: 

•	Ưu điểm: Đảm bảo tìm được giải pháp tối ưu nhờ heuristic, kết hợp AC-3 để giảm quay lui. 

•	Nhược điểm: Chậm hơn và mở rộng nhiều trạng thái  do khám phá toàn bộ không gian.

### 2.6. Thuật toán học tăng cường
#### Thuật toán và mô tả

| Thuật Toán               | Mô Tả                                                                 | Minh Họa GIF                              |
|--------------------------|----------------------------------------------------------------------|-------------------------------------------|
| **Q-Learning**                | Là thuật toán học tăng cường không mô hình (model-free) thuộc nhóm học giá trị (value-based), được sử dụng để tìm chính sách tối ưu trong môi trường rời rạc. Thuật toán học cách tối ưu hóa hành vi của tác nhân (agent) thông qua việc thử và sai (trial-and-error), dựa trên phần thưởng nhận được từ môi trường.   |   ![Q-Learning](gif/backtracking.gif)     |

## Cơ chế chính của Q-Learning trong code:

1.	Khởi tạo: 

•	Bảng Q (q_table) được khởi tạo với giá trị 0 cho mỗi cặp (trạng thái, hành động). Trạng thái là các ô trên lưới 3x3 (STATES = [(i, j) for i in range(3) for j in range(3)]), và hành động là các hướng di chuyển (ACTIONS = ['up', 'down', 'left', 'right']).

•	Các tham số học: alpha = 0.1 (tốc độ học), gamma = 0.9 (hệ số chiết khấu).

2.	Cập nhật Q-Table: 

•	Trong mỗi bước (step), tác nhân chọn một hành động ngẫu nhiên (random exploration).

•	Trạng thái tiếp theo (next_state) được tính dựa trên hành động hiện tại (get_next_state).

•	Phần thưởng (reward) được lấy từ môi trường (get_reward): +10 tại ô (2,2), -1 nếu ra ngoài lưới, 0 hoặc giá trị ngẫu nhiên từ lưới (self.grid).

•	Cập nhật giá trị Q theo công thức: ![image](https://github.com/user-attachments/assets/75a448b3-55e8-4c08-a754-39318afe0027)

3.	Lặp lại: 

	Thuật toán chạy qua 10 episode, mỗi episode bắt đầu từ trạng thái (0,0) và kết thúc khi đạt ô (2,2) hoặc trạng thái không hợp lệ.

•	Mỗi bước được ghi lại và hiển thị trên giao diện (nhưng không hiển thị chi tiết từng bước trong giao diện, chỉ cập nhật bảng Q).

4.	Kết thúc:

•	Thuật toán giả định hội tụ sau 10 episode và trả về kết quả "Optimal Policy Found!".

## 🌟 Các tính năng của chương trình
Giao diện đồ họa (GUI): Sử dụng thư viện pygame để tạo giao diện trực quan, cho phép người dùng: 

      •	Nhập trạng thái ban đầu bằng cách chọn ô và nhập số (0-8).
      
      •	Tạo trạng thái ban đầu ngẫu nhiên (đảm bảo khả thi).
      
      •	Chọn thuật toán để giải và theo dõi quá trình giải từng bước.
      
      •	Điều chỉnh tốc độ hiển thị bước giải (1x, 2x, 5x, 10x).
      
      •	Tăng/giảm độ rộng chùm (beam width) cho Beam Search.
      
      •	Hiển thị số bước, số trạng thái mở rộng, và thời gian thực thi.
      
•  Kiểm tra tính khả thi: Hàm is_solvable kiểm tra trạng thái ban đầu có thể đạt được trạng thái mục tiêu hay không dựa trên số lần đảo ngược (inversions).

•  Heuristic cải tiến: 

      •	Khoảng cách Manhattan: Tính tổng khoảng cách các ô từ vị trí hiện tại đến vị trí mục tiêu.
      
      •	Linear Conflict: Bổ sung chi phí khi hai ô trong cùng hàng/cột cần hoán đổi vị trí, cải thiện độ chính xác của heuristic.
      
•  Hỗ trợ nhiều thuật toán: Cho phép so sánh hiệu suất giữa các thuật toán dựa trên số bước, số trạng thái mở rộng, và thời gian chạy. 

•  Xử lý lỗi: Hiển thị thông báo khi trạng thái ban đầu không khả thi hoặc thuật toán không tìm được giải pháp.



## 🚀 Hướng dẫn chạy chương trình
      
•  Hướng dẫn sử dụng GUI: 

      •	Nhập trạng thái ban đầu: Click vào ô trên bảng "Trạng thái đầu", nhập số từ 0-8 (0 là ô trống).
      
      •	Tạo trạng thái ngẫu nhiên: Nhấn nút "Random" hoặc tạo trạng thái tùy thích.
      
      •	Chọn thuật toán: Nhấn nút tương ứng với thuật toán (DFS, BFS, A*, v.v.).
      
      •	Điều chỉnh tốc độ: Chọn tốc độ từ ComboBox (1x, 2x, 5x, 10x).
      
      •	Beam Search: Sử dụng nút "Beam Width +" hoặc "Beam Width -" để điều chỉnh độ rộng chùm.
      
      •	Dừng/tiếp tục: Nhấn "Stop" để dừng, "Continue" để tiếp tục quá trình giải.
      
      •	Reset: Nhấn "Reset" để đưa chương trình về trạng thái ban đầu.




## 🔍 Kết luận
Chương trình cung cấp một nền tảng toàn diện để so sánh các thuật toán AI trong bài toán 8-Puzzle. Giao diện trực quan và hỗ trợ nhiều thuật toán giúp người dùng thấy các thuật toán hoạt động. Các thuật toán như A*, IDA*, và Simulated Annealing nổi bật về hiệu suất và khả năng xử lý các trạng thái phức tạp, trong khi các phương pháp như Trust-Based Search và Backtracking CSP mang lại góc nhìn mới về cách tiếp cận bài toán.


## 👨‍💻 Tác giả

**Nguyễn Trung Hậu**  
MSSV: `23110212`  
Môn: `Trí Tuệ Nhân Tạo`  
Giáo viên hướng dẫn: `Phan Thị Huyền Trang` 
