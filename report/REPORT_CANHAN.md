# Báo Cáo Cá Nhân — Lab 7: Embedding & Vector Store

**Họ tên:** Nguyễn Bá Chinh
**MSSV:** 2A202602654
**Nhóm:** TDTU Library
**Ngày:** 19/09/2026

> **Nộp 1 bản / sinh viên.** Phần nhóm được trình bày trong `REPORT_NHOM.md`.

**Tổng điểm phần cá nhân: 60** = Khởi động (5) + Hướng tiếp cận (10) + Hoàn thiện code (30) + Dự đoán độ tương tự (5) + Kết quả truy xuất của tôi (10).

---

## 1. Khởi động (Warm-up) — Cá nhân (5 điểm)

### Độ tương tự Cosine (Cosine Similarity) (Bài tập 1.1)

**Độ tương tự cosine cao (High cosine similarity) nghĩa là gì?**

Cosine similarity cao nghĩa là hai vector embedding có hướng gần giống nhau. Với text embedding, điều này thường cho thấy hai đoạn văn bản có ý nghĩa hoặc nội dung tương tự nhau, ngay cả khi cách dùng từ không hoàn toàn giống nhau.

**Ví dụ có độ tương tự CAO:**

- Câu A: Students can borrow circulating materials for five days.
- Câu B: The loan period for circulating materials is five days.
- Tại sao tương đồng: Hai câu đều diễn đạt cùng một thông tin về thời gian mượn tài liệu.

**Ví dụ có độ tương tự THẤP:**

- Câu A: Students can renew library materials online.
- Câu B: The weather is sunny today.
- Tại sao khác: Hai câu nói về hai chủ đề hoàn toàn khác nhau.

**Tại sao cosine similarity được ưu tiên hơn Euclidean distance cho text embeddings?**

Cosine similarity tập trung vào hướng của vector thay vì độ lớn tuyệt đối của vector. Vì vậy nó phù hợp để so sánh mức độ tương đồng về ý nghĩa giữa các text embeddings.

### Bài toán tính toán Chunking (Bài tập 1.2)

**Tài liệu 10,000 ký tự, `chunk_size=500`, `overlap=50`. Bao nhiêu chunks?**

Công thức:

`ceil((document_length - overlap) / (chunk_size - overlap))`

Thay số:

`ceil((10000 - 50) / (500 - 50))`
`= ceil(9950 / 450)`
`= ceil(22.11...)`
`= 23`

**Đáp án: 23 chunks.**

**Nếu overlap tăng lên 100, số lượng chunk thay đổi thế nào? Tại sao muốn overlap nhiều hơn?**

`ceil((10000 - 100) / (500 - 100))`
`= ceil(9900 / 400)`
`= ceil(24.75)`
`= 25 chunks`

Khi overlap tăng từ 50 lên 100, số chunk tăng từ 23 lên 25. Overlap lớn hơn giúp giữ lại nhiều ngữ cảnh ở ranh giới giữa hai chunk và giảm nguy cơ thông tin quan trọng bị chia tách, nhưng đồng thời làm tăng số chunk và chi phí embedding.

---

## 2. Hướng tiếp cận của tôi (My Approach) — Cá nhân (10 điểm)

Giải thích cách tiếp cận khi triển khai các phần chính trong gói `src`.

### Các hàm chia nhỏ (Chunking Functions)

**`SentenceChunker.chunk` — hướng tiếp cận:**

Tôi sử dụng biểu thức chính quy:

`r"(?<=[.!?])\s+"`

để phát hiện ranh giới câu dựa trên các dấu kết thúc câu như `.`, `!` và `?`. Sau khi tách thành các câu riêng, các câu được gom lại thành chunk theo số lượng câu tối đa đã cấu hình. Với trường hợp input rỗng hoặc chỉ chứa khoảng trắng, hàm trả về danh sách rỗng để tránh tạo chunk không có nội dung.

**`RecursiveChunker.chunk` / `_split` — hướng tiếp cận:**

RecursiveChunker thử chia văn bản theo các separator từ lớn đến nhỏ theo thứ tự:

`["\n\n", "\n", ". ", " ", ""]`

Nếu đoạn văn bản hiện tại đã có độ dài nhỏ hơn hoặc bằng `chunk_size`, đoạn đó được trả về ngay và đây là base case của thuật toán. Nếu đoạn vẫn quá dài, thuật toán tiếp tục chia bằng separator nhỏ hơn. Trong trường hợp không thể chia thêm bằng separator, văn bản được cắt trực tiếp theo số ký tự để bảo đảm mỗi chunk không vượt quá giới hạn.

### Lớp EmbeddingStore

**`add_documents` + `search` — hướng tiếp cận:**

Khi thêm document vào store, nội dung của mỗi document được chuyển thành embedding và lưu cùng với `id`, `content` và `metadata`. Metadata được giữ lại để có thể truy vết tài liệu gốc và phục vụ các thao tác lọc sau này.

Khi search, câu query cũng được chuyển thành embedding bằng cùng embedding function. Hệ thống tính độ tương tự giữa query embedding và từng document embedding bằng dot product, sau đó sắp xếp kết quả theo score giảm dần và trả về `top_k` kết quả có độ tương tự cao nhất.

**`search_with_filter` + `delete_document` — hướng tiếp cận:**

`search_with_filter` lọc các record theo metadata trước khi tính similarity. Cách làm này giúp loại bỏ sớm các document không phù hợp, ví dụ chỉ giữ các tài liệu có `audience=student` trước khi xếp hạng kết quả.

`delete_document` xóa tất cả các chunk có cùng `doc_id` trong metadata. Sau khi xóa, hệ thống kiểm tra kích thước store để xác định document có thực sự được xóa hay không.

### Tác tử KnowledgeBaseAgent

**`answer` — hướng tiếp cận:**

KnowledgeBaseAgent trước tiên truy xuất các chunk liên quan nhất với câu hỏi. Nếu có `metadata_filter`, agent gọi `search_with_filter`; nếu không, agent dùng `search`. Các chunk được ghép thành context có đánh số nguồn rồi đưa vào prompt cùng với câu hỏi.

Prompt yêu cầu mô hình chỉ trả lời dựa trên context được cung cấp, trích dẫn nguồn bằng `[1]`, `[2]`, và nói rõ khi context chưa đủ thông tin thay vì tự suy đoán.

---

## 3. Hoàn thiện code (Core Implementation) — Cá nhân (30 điểm)

Vượt qua bộ kiểm thử là điều kiện tính điểm phần này.

### Kết Quả Kiểm Thử (Test Results)

Lệnh kiểm thử:

```bash
pytest tests/ -v
```

Kết quả gần nhất:

```text
============================= 42 passed in 0.09s ==============================
```

**Số lượng bài test vượt qua (pass): 42 / 42**

> Trước khi commit cuối, chạy lại `pytest tests/ -v` để xác nhận kết quả vẫn là 42/42 sau các thay đổi benchmark/agent.

---

## 4. Dự đoán độ tương tự (Similarity Predictions) — Cá nhân (5 điểm)

Tôi đưa ra dự đoán trước khi chạy `compute_similarity()` với LocalEmbedder.

| Cặp | Câu A | Câu B | Dự đoán | Điểm thực tế | Đúng? |
|---|---|---|---|---:|---|
| 1 | Students can borrow circulating materials for five days. | The loan period for circulating materials is five days. | Cao | 0.8253 | Có |
| 2 | Renewal is not allowed for overdue materials. | Overdue library items cannot be renewed. | Cao | 0.6344 | Có |
| 3 | Users can reserve a library room. | The weather is sunny today. | Thấp | 0.0446 | Có |
| 4 | Students use portal credentials to access the library. | Library access uses credentials from the student portal. | Cao | 0.9175 | Có |
| 5 | Course readings are available for students. | Staff can request materials for purchase. | Thấp | 0.2551 | Có |

**Kết quả nào bất ngờ nhất? Điều này nói gì về cách embeddings biểu diễn ý nghĩa?**

Kết quả làm tôi chú ý nhất là cặp 2 chỉ đạt 0.6344 mặc dù hai câu gần như diễn đạt cùng một ý về việc tài liệu quá hạn không thể được gia hạn. Trong khi đó, cặp 4 đạt tới 0.9175 vì hai câu có cả ngữ nghĩa và nhiều khái niệm quan trọng tương đồng như `credentials`, `library` và `portal`.

Điều này cho thấy embedding không chỉ kiểm tra các từ giống nhau mà biểu diễn tổng thể ngữ nghĩa và ngữ cảnh của câu. Hai câu thuộc chủ đề khác nhau vẫn có thể có một mức similarity nhỏ nếu chúng chia sẻ một số khái niệm liên quan.

---

## 5. Kết quả truy xuất của tôi (Competition Results) — Cá nhân (10 điểm)

Tôi sử dụng chiến lược:

`FixedSizeChunker(chunk_size=500, overlap=50)`

và LocalEmbedder để chạy cùng 5 benchmark queries của nhóm.

| # | Câu hỏi (Query) | Top-1 Chunk truy xuất được (tóm tắt) | Điểm Score | Có liên quan không? | Câu trả lời của Agent (tóm tắt) |
|---|---|---|---:|---|---|
| 1 | For undergraduate students, how long is the loan period for circulating materials, and how many renewals are allowed? | `student-borrowing-policy` — loan period và renewal | 0.783883 | Có | 5 ngày; được gia hạn một lần thêm 5 ngày. |
| 2 | Under what conditions is renewal not allowed? | `renewal-guide` — điều kiện không được renewal | 0.664599 | Có | Không được gia hạn khi tài liệu đã quá hạn hoặc có người khác đặt giữ; Agent cũng nêu tài liệu non-circulating không được gia hạn. |
| 3 | How can a user cancel a library room booking? | `reserve-a-room` — Booking and Cancellation | 0.852233 | Có | Có thể hủy qua điện thoại, email, Facebook hoặc liên hệ nhân viên tại Service Desk/Information Desk. |
| 4 | Which credentials are used to sign in to the Library Portal? | `library-card-account`, nhưng chunk chứa đáp án chuẩn không nằm trong top-3 | 0.580207 | Không theo content-level evaluation | Agent báo ngữ cảnh chưa đủ thông tin để xác định credentials. |
| 5 | What course-related support resources are available? | `undergraduate-student-services` — Learning Support | 0.667969 | Có | Course readings, subject guides và required reading lists by course. |

**Bao nhiêu câu hỏi trả về chunk có liên quan trong top-3?** 4 / 5

**Kết quả đánh giá:** 8 / 10.

### Phân tích kết quả Agent

Agent trả lời chính xác Query 1, 2, 3 và 5 dựa trên các chunk được truy xuất. Query 4 là failure case của chiến lược FixedSize: mặc dù top-1 đến từ `library-card-account`, chunk thực tế được truy xuất không chứa phần thông tin cần thiết về credentials. Vì vậy Agent không tự suy đoán mà trả lời rằng ngữ cảnh chưa đủ thông tin.

Kết quả này cho thấy chỉ kiểm tra `doc_id` của tài liệu là chưa đủ; cần đánh giá nội dung của chunk thực tế được retrieval. Nó cũng cho thấy cơ chế grounding của Agent hoạt động hợp lý vì khi thiếu bằng chứng, Agent không tự tạo ra câu trả lời.

### Tác dụng của metadata filtering

Query 5 sử dụng:

`metadata_filter={"audience": "student"}`

Khi có filter, `undergraduate-student-services` được đưa lên top-1 với score `0.667969`.

Khi bỏ metadata filter, `professional-staff-services` có `audience=staff` đứng ở top-1 với score `0.688083`, còn tài liệu dành cho sinh viên tụt xuống top-2.

Điều này cho thấy metadata filtering giúp giới hạn candidate theo đúng đối tượng người dùng và tránh trường hợp hệ thống lấy tài liệu đúng chủ đề nhưng sai audience.

**Điều hay nhất tôi học được từ thành viên khác / nhóm khác:**

Qua việc so sánh với RecursiveChunker và Heading/Section Chunker, tôi nhận thấy chiến lược chunking ảnh hưởng trực tiếp tới ranking retrieval, không chỉ ảnh hưởng số lượng chunk. Heading/Section Chunker hoạt động đặc biệt tốt với corpus có cấu trúc heading rõ ràng, trong khi RecursiveChunker giữ được các ranh giới ngữ nghĩa tự nhiên tốt hơn FixedSize trong một số trường hợp.

---

## Tự Đánh Giá (Phần Cá Nhân)

| Tiêu chí | Điểm tự đánh giá |
|---|---:|
| Khởi động (Warm-up) | 5/5 |
| Hướng tiếp cận của tôi (My Approach) | 10/10 |
| Hoàn thiện code (Core Implementation — tests) | 30/30 |
| Dự đoán độ tương tự (Similarity Predictions) | 5/5 |
| Kết quả truy xuất của tôi (Competition Results) | 8/10 |
| **Tổng phần cá nhân** | **58/60** |
