# Báo Cáo Nhóm — Lab 7: Embedding & Vector Store

**Nhóm:** TDTU Library

**Thành viên:** Nguyễn Bá Chinh (2A202602654) — R1; Trần Anh Vũ (2A202602570) — R2; Dương Thị Hồng Viên (2A202602385) — R3

**Ngày:** 19/09/2026

**Tổng điểm phần nhóm: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Tra cứu dịch vụ và quy định sử dụng Thư viện TDTU.

**Tại sao nhóm chọn chủ đề này?**

Nhóm chọn các dịch vụ và quy định của Thư viện TDTU vì đây là nguồn thông tin công khai, có cấu trúc rõ ràng và có nhiều tình huống truy vấn thực tế như mượn tài liệu, gia hạn, đặt phòng và tài khoản thư viện. Các tài liệu cũng có nhiều nhóm đối tượng như `student`, `staff` và `all`, phù hợp để thử nghiệm metadata filtering và so sánh các chiến lược chunking.

### Danh sách tài liệu (Data Inventory)

Số ký tự dưới đây tính trên phần nội dung Markdown sau khi bỏ YAML frontmatter.

| # | Tên tài liệu                                      | Nguồn (Source URL)                                                 | Ngày lấy / Phiên bản       | Số ký tự | Metadata đã gán                                                                 |
| - | ------------------------------------------------- | ------------------------------------------------------------------ | -------------------------- | -------: | ------------------------------------------------------------------------------- |
| 1 | Undergraduate Student - Circulation Service       | https://lib.tdtu.edu.vn/services/circulation/undergraduate-student | 2026-09-19 / not specified |     1240 | audience=student, department=library, category=circulation, language=en         |
| 2 | Library Card & Account                            | https://lib.tdtu.edu.vn/guides/essential/library-card-account      | 2026-09-19 / not specified |     1150 | audience=all, department=library, category=account, language=en                 |
| 3 | Renew Library Materials                           | https://lib.tdtu.edu.vn/guides/essential/renewal                   | 2026-09-19 / not specified |      663 | audience=all, department=library, category=renewal, language=en                 |
| 4 | Reserve a Room                                    | https://lib.tdtu.edu.vn/guides/essential/reserve-a-room            | 2026-09-19 / not specified |     1028 | audience=all, department=library, category=room_booking, language=en            |
| 5 | Services for TDTU Undergraduate Students          | https://lib.tdtu.edu.vn/user-group-services/undergraduate-student  | 2026-09-19 / not specified |      906 | audience=student, department=library, category=user_group_services, language=en |
| 6 | Services for TDTU Academic and Professional Staff | https://lib.tdtu.edu.vn/user-group-services/professional-staff     | 2026-09-19 / not specified |     1007 | audience=staff, department=library, category=user_group_services, language=en   |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**

* [x] Corpus chỉ sử dụng các trang công khai chính thức của TDTU Library và không chứa dữ liệu đăng nhập hoặc tài liệu nội bộ.
* [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` cùng các metadata phục vụ truy xuất.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata    | Kiểu        | Ví dụ giá trị              | Tại sao hữu ích cho retrieval?                 |
| ------------------ | ----------- | -------------------------- | ---------------------------------------------- |
| `doc_id`           | string      | `student-borrowing-policy` | Nhận diện tài liệu nguồn của mỗi chunk         |
| `title`            | string      | `Library Card & Account`   | Giúp mô tả nội dung tài liệu                   |
| `audience`         | string      | `student`                  | Cho phép lọc kết quả theo đúng nhóm người dùng |
| `department`       | string      | `library`                  | Cho phép giới hạn retrieval theo đơn vị        |
| `category`         | string      | `circulation`              | Phân biệt loại dịch vụ/quy định                |
| `language`         | string      | `en`                       | Hỗ trợ lọc theo ngôn ngữ                       |
| `source_url`       | string      | URL TDTU Library           | Truy xuất nguồn gốc và kiểm chứng thông tin    |
| `retrieved_at`     | string/date | `2026-09-19`               | Theo dõi thời điểm thu thập dữ liệu            |
| `document_version` | string      | `not specified`            | Theo dõi phiên bản tài liệu nếu có             |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

Mỗi thành viên sử dụng một chiến lược chunking khác nhau trên cùng 6 tài liệu và cùng 5 benchmark queries.

### Phân tích đường cơ sở (Baseline Analysis)

Nhóm chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu sau khi loại bỏ YAML frontmatter.

| Tài liệu                          | Chiến lược       | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không?            |
| --------------------------------- | ---------------- | -------------: | ----------------: | ----------------------------------- |
| student-borrowing-policy.md       | FixedSizeChunker |              3 |            447.00 | Khá, nhưng có thể cắt giữa section  |
| student-borrowing-policy.md       | SentenceChunker  |              5 |            246.20 | Tốt ở mức câu nhưng chunk nhỏ hơn   |
| student-borrowing-policy.md       | RecursiveChunker |              3 |            413.67 | Tốt, ưu tiên các ranh giới tự nhiên |
| reserve-a-room.md                 | FixedSizeChunker |              3 |            376.33 | Khá                                 |
| reserve-a-room.md                 | SentenceChunker  |              3 |            340.33 | Tốt                                 |
| reserve-a-room.md                 | RecursiveChunker |              3 |            343.00 | Tốt                                 |
| undergraduate-student-services.md | FixedSizeChunker |              2 |            478.50 | Khá                                 |
| undergraduate-student-services.md | SentenceChunker  |              3 |            299.67 | Tốt ở mức câu                       |
| undergraduate-student-services.md | RecursiveChunker |              2 |            453.50 | Tốt                                 |

### Chiến lược của từng thành viên

**Thành viên 1 — Nguyễn Bá Chinh (R1)**

* **Loại chiến lược:** `FixedSizeChunker(chunk_size=500, overlap=50)`
* **Mô tả & lý do chọn:** Fixed-size chunking đơn giản, dễ kiểm soát kích thước đầu vào cho embedding và tạo một baseline rõ ràng. Overlap 50 ký tự giúp giảm khả năng mất thông tin nằm ngay tại ranh giới giữa hai chunk.
* **Code snippet:** Sử dụng implementation `FixedSizeChunker` trong `src/chunking.py`.

**Thành viên 2 — Trần Anh Vũ (R2)**

* **Loại chiến lược:** `RecursiveChunker(chunk_size=500)`
* **Mô tả & lý do chọn:** Recursive chunking ưu tiên tách theo đoạn văn, dòng và câu trước khi phải cắt theo ký tự. Cách này giúp chunk giữ được cấu trúc ngữ nghĩa tự nhiên hơn so với cắt cứng theo số ký tự.
* **Code snippet:** Sử dụng `RecursiveChunker` trong `src/chunking.py`.

**Thành viên 3 — Dương Thị Hồng Viên (R3)**

* **Loại chiến lược:** Heading/Section Chunking, `chunk_size=500`
* **Mô tả & lý do chọn:** Các tài liệu thư viện được tổ chức theo các heading như `Loan Periods`, `Renewal`, `Learning Support` và `Booking and Cancellation`, do đó mỗi section có thể xem là một đơn vị ngữ nghĩa. Khi section quá dài, nhóm sử dụng `RecursiveChunker` để chia tiếp nhưng vẫn gắn lại heading vào từng chunk con.

**Code snippet:**

```python
sections = re.split(
    r"(?=^#{1,6}\s+)",
    text.strip(),
    flags=re.MULTILINE,
)

if len(section) > self.chunk_size:
    fallback = RecursiveChunker(
        chunk_size=available_size
    )

    for subchunk in fallback.chunk(body):
        chunks.append(
            f"{heading}\n{subchunk}".strip()
        )
```

### So Sánh Giữa Các Thành Viên

Kết quả dưới đây là kết quả retrieval-only khi sử dụng LocalEmbedder trên cùng bộ 6 tài liệu và cùng 5 benchmark queries.

| Thành viên               | Chiến lược (Strategy)    |                                                                   Kết quả retrieval | Điểm mạnh                                                                         | Điểm yếu                                                                                 |
| ------------------------ | ------------------------ | ----------------------------------------------------------------------------------: | --------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| Nguyễn Bá Chinh (R1)     | FixedSizeChunker         |                                             4/5 query có relevant chunk trong top-3 | Đơn giản, dễ kiểm soát, có overlap để giảm mất ngữ cảnh ở biên chunk              | Có thể cắt giữa section; Query 4 không retrieve được chunk chứa đáp án chuẩn trong top-3 |
| Trần Anh Vũ (R2)         | RecursiveChunker         |                                             5/5 query có relevant chunk trong top-3 | Giữ các ranh giới tự nhiên tốt hơn, retrieve được relevant chunk cho cả 5 query   | Một số relevant chunk không đứng ở top-1                                                 |
| Dương Thị Hồng Viên (R3) | Heading/Section Chunking | 5/5 query có relevant chunk trong top-3, các relevant section được xếp hạng rất tốt | Phù hợp với tài liệu Markdown có heading rõ ràng và giữ ngữ cảnh theo section tốt | Phụ thuộc vào tài liệu có cấu trúc heading rõ ràng                                       |

Trong benchmark hiện tại, Heading/Section Chunking cho kết quả retrieval tốt nhất trên corpus TDTU Library. Điều này phù hợp với đặc điểm dữ liệu vì các tài liệu được tổ chức thành các section mang ý nghĩa riêng như `Loan Periods`, `Renewal`, `Library Portal Account`, `Learning Support` và `Booking and Cancellation`.

RecursiveChunker cũng hoạt động tốt vì ưu tiên các ranh giới tự nhiên của văn bản thay vì cắt cứng theo số ký tự. FixedSizeChunker vẫn là một baseline đơn giản và hiệu quả, nhưng có nguy cơ cắt một section thành nhiều phần khiến đoạn chứa đáp án không được xếp hạng cao.

Kết quả trên phản ánh bộ dữ liệu và benchmark hiện tại; không có nghĩa một chiến lược luôn tốt hơn trong mọi loại tài liệu.

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn

Nhóm sử dụng đúng 5 benchmark queries giống nhau cho cả ba thành viên.

| # | Câu hỏi (Query)                                                                                                       | Câu trả lời chuẩn (Gold Answer)                                                                | Chunk nào chứa thông tin?                                         |
| - | --------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| 1 | For undergraduate students, how long is the loan period for circulating materials, and how many renewals are allowed? | 5 days; one renewal for an additional 5 days.                                                  | `student-borrowing-policy` → Loan Periods → Circulating Materials |
| 2 | Under what conditions is renewal not allowed?                                                                         | Renewal is not allowed when the material is overdue or another user has placed a hold request. | `renewal-guide` → When Renewal Is Not Allowed                     |
| 3 | How can a user cancel a library room booking?                                                                         | By phone, email, Facebook, or by contacting staff at a Service Desk or Information Desk.       | `reserve-a-room` → Booking and Cancellation                       |
| 4 | Which credentials are used to sign in to the Library Portal?                                                          | The same credentials as the Student Information Portal or Lecturer/Staff Information Portal.   | `library-card-account` → Library Portal Account                   |
| 5 | What course-related support resources are available?                                                                  | For students: course readings, subject guides, and required reading lists by course.           | `undergraduate-student-services` → Learning Support               |

Query 5 sử dụng metadata filter:

```python
metadata_filter={"audience": "student"}
```

Đây là query được thiết kế để kiểm tra yêu cầu riêng của biến thể L3A: hệ thống cần giới hạn retrieval vào các tài liệu dành cho sinh viên thay vì chỉ dựa vào semantic similarity.

### Kết quả retrieval theo từng chiến lược

| Query                           | FixedSize                                 | Recursive            | Heading/Section      |
| ------------------------------- | ----------------------------------------- | -------------------- | -------------------- |
| Q1 — Loan period & renewal      | Relevant trong Top-3                      | Relevant trong Top-3 | Relevant trong Top-3 |
| Q2 — Renewal conditions         | Relevant trong Top-3                      | Relevant trong Top-3 | Relevant trong Top-3 |
| Q3 — Cancel room booking        | Relevant trong Top-3                      | Relevant trong Top-3 | Relevant trong Top-3 |
| Q4 — Library Portal credentials | Không tìm thấy relevant chunk trong Top-3 | Relevant trong Top-3 | Relevant ở Top-1     |
| Q5 — Course-related resources   | Relevant ở Top-1                          | Relevant ở Top-1     | Relevant ở Top-1     |
| **Tổng**                        | **4/5**                                   | **5/5**              | **5/5**              |

### Phân tích Query 4

Query 4 là trường hợp thể hiện rõ tác động của chunking strategy.

Câu hỏi:

> Which credentials are used to sign in to the Library Portal?

Gold answer nằm trong section:

`Library Card & Account → Library Portal Account`

với nội dung:

`The Library Portal uses the same credentials as the Student Information Portal or Lecturer/Staff Information Portal.`

Với FixedSizeChunker, hệ thống retrieve được các chunk thuộc đúng tài liệu `library-card-account`, nhưng đoạn thực sự chứa câu trả lời không nằm trong Top-3. Điều này cho thấy chỉ kiểm tra `doc_id` là chưa đủ; cần kiểm tra nội dung thực tế của chunk được retrieve.

Heading/Section Chunking giữ nguyên section `Library Portal Account` thành một đơn vị ngữ nghĩa rõ ràng. Vì vậy đoạn chứa đáp án được xếp ở Top-1.

---

## 4. Thử nghiệm Metadata Filtering

Query 5:

> What course-related support resources are available?

được chạy với:

```python
metadata_filter={"audience": "student"}
```

### Khi có metadata filter

Với FixedSizeChunker, kết quả Top-1 là:

* `doc_id`: `undergraduate-student-services`
* `audience`: `student`
* score: khoảng `0.667969`

Chunk chứa:

* course readings
* subject guides
* required reading lists by course

Đây chính là nội dung của gold answer.

### Khi bỏ metadata filter

Kết quả Top-1 trở thành:

* `doc_id`: `professional-staff-services`
* `audience`: `staff`
* score: khoảng `0.688083`

Trong khi tài liệu dành cho sinh viên `undergraduate-student-services` chỉ đứng Top-2.

### Nhận xét

Đây là ví dụ cho thấy semantic similarity cao chưa chắc đồng nghĩa với kết quả phù hợp với người dùng.

Cả tài liệu dành cho staff và sinh viên đều chứa nội dung liên quan đến hỗ trợ học tập hoặc giảng dạy nên embedding của chúng tương đối gần với query. Tuy nhiên, người dùng trong benchmark cần thông tin dành cho sinh viên.

Metadata filter giúp giới hạn candidate documents trước khi ranking:

```text
All documents
      ↓
filter audience=student
      ↓
Student documents only
      ↓
Similarity ranking
      ↓
Top-k results
```

Do đó metadata không chỉ có vai trò mô tả tài liệu mà còn có thể trực tiếp cải thiện độ chính xác của retrieval.

---

## 5. Kiểm tra câu trả lời của Agent

Nhóm sử dụng `KnowledgeBaseAgent` để tạo câu trả lời dựa trên các chunk được retrieval.

Agent được thiết kế theo pipeline:

```text
Question
   ↓
Embedding / Retrieval
   ↓
Top-k chunks
   ↓
Context
   ↓
Prompt
   ↓
LLM
   ↓
Grounded Answer
```

Prompt yêu cầu Agent:

* chỉ sử dụng thông tin trong context;
* không tự suy đoán khi context không đủ;
* trích dẫn các nguồn bằng `[1]`, `[2]`, ...;
* không thực hiện các chỉ dẫn nằm bên trong tài liệu retrieval.

### Kết quả Agent với FixedSizeChunker

| Query | Kết quả                                                                                                                              |
| ----- | ------------------------------------------------------------------------------------------------------------------------------------ |
| Q1    | Trả lời đúng: 5 ngày, gia hạn một lần thêm 5 ngày                                                                                    |
| Q2    | Trả lời đúng các điều kiện overdue và hold request; đồng thời bổ sung thông tin được grounding từ corpus về non-circulating material |
| Q3    | Trả lời đúng các cách hủy booking: phone, email, Facebook hoặc Service/Information Desk                                              |
| Q4    | Không có chunk chứa đáp án trong retrieved context nên Agent thông báo context chưa đủ                                               |
| Q5    | Trả lời đúng course readings, subject guides và required reading lists                                                               |

Điểm đáng chú ý nhất là Query 4.

Agent không có đủ bằng chứng trong retrieved context nhưng cũng **không tự bịa câu trả lời**. Thay vào đó Agent nói rõ rằng ngữ cảnh chưa đủ để xác định credentials.

Điều này cho thấy một RAG system tốt không chỉ cần trả lời nhiều câu hỏi mà còn cần biết khi nào evidence chưa đủ.

---

## 6. Failure Analysis

### Failure Case: Query 4 với FixedSizeChunker

**Query:**

`Which credentials are used to sign in to the Library Portal?`

**Gold answer:**

`The same credentials as the Student Information Portal or Lecturer/Staff Information Portal.`

### Điều gì xảy ra?

FixedSizeChunker chia văn bản theo số ký tự cố định:

```python
chunk_size=500
overlap=50
```

Cách chia này không quan tâm đến cấu trúc Markdown hay heading.

Vì vậy section `Library Portal Account`, nơi chứa gold answer, có thể nằm ở vị trí không thuận lợi trong các chunk. Hệ thống vẫn retrieve các đoạn thuộc tài liệu `library-card-account`, nhưng chunk chứa chính xác câu trả lời không xuất hiện trong Top-3.

### Nguyên nhân

Failure không phải do:

* corpus thiếu thông tin;
* gold answer sai;
* metadata sai.

Thông tin cần thiết thực sự tồn tại trong corpus.

Nguyên nhân chủ yếu là **chunk boundary** và **retrieval ranking**.

Fixed-size chunking có thể gom nhiều chủ đề khác nhau vào cùng chunk hoặc chia một section ngữ nghĩa thành nhiều phần. Khi đó embedding của chunk không còn tập trung mạnh vào nội dung `Library Portal credentials`.

### So sánh với Heading Chunking

Heading Chunker tạo riêng section:

```text
## Library Portal Account

The Library Portal uses the same credentials as the Student Information
Portal or Lecturer/Staff Information Portal.
```

Chunk này tập trung gần như hoàn toàn vào nội dung được hỏi nên similarity với Query 4 cao hơn và được đưa lên Top-1.

### Cách cải thiện

Có thể cải thiện FixedSize strategy bằng một số cách:

1. Giảm `chunk_size` để chunk tập trung hơn vào một chủ đề.
2. Điều chỉnh `overlap` để giảm mất context tại ranh giới.
3. Dùng RecursiveChunker để ưu tiên paragraph/section boundary.
4. Dùng Heading/Section Chunker cho tài liệu Markdown có cấu trúc.
5. Kết hợp heading vào metadata hoặc nội dung chunk.
6. Sử dụng reranking sau bước vector search nếu hệ thống thực tế yêu cầu độ chính xác cao hơn.

---

## 7. Những gì nhóm học được

### 7.1 Chunking ảnh hưởng trực tiếp đến retrieval

Ban đầu chunking có thể được xem đơn giản là bước chia một tài liệu dài thành các đoạn nhỏ hơn.

Qua benchmark, nhóm nhận thấy chunking ảnh hưởng trực tiếp đến embedding và ranking.

Nếu một chunk chứa nhiều nội dung không liên quan:

```text
Embedding(chunk)
```

sẽ biểu diễn nhiều ý cùng lúc.

Điều này có thể khiến similarity với một query cụ thể giảm xuống.

Ngược lại, một chunk tập trung vào đúng một section sẽ có representation phù hợp hơn với query liên quan đến section đó.

### 7.2 Không nên chỉ kiểm tra đúng document

Một retrieval result có thể có:

```text
doc_id = library-card-account
```

nhưng chunk được retrieve lại không chứa câu trả lời.

Do đó đánh giá retrieval phải ở **chunk-level**, không chỉ document-level.

### 7.3 Metadata và embeddings giải quyết hai vấn đề khác nhau

Embedding trả lời câu hỏi:

> Nội dung nào có ý nghĩa gần với query?

Metadata filter trả lời:

> Trong những tài liệu nào hệ thống được phép hoặc nên tìm kiếm?

Kết hợp hai cơ chế giúp retrieval chính xác hơn:

```text
Metadata filtering
        ↓
Semantic retrieval
        ↓
Relevant context
```

### 7.4 Strategy cần phù hợp với cấu trúc dữ liệu

Không có một chunking strategy tốt nhất cho mọi loại corpus.

* FixedSize phù hợp khi cần implementation đơn giản và kích thước chunk ổn định.
* Recursive phù hợp với văn bản tự nhiên có paragraph và sentence boundary.
* Heading/Section phù hợp với Markdown, documentation, policy, FAQ hoặc tài liệu có cấu trúc rõ ràng.

Đối với TDTU Library corpus, heading mang nhiều thông tin semantic nên Heading/Section Chunking phù hợp đặc biệt tốt.

### 7.5 Grounding quan trọng hơn việc luôn đưa ra câu trả lời

Query 4 của FixedSize strategy cho thấy một hành vi tốt của Agent.

Khi retrieval không cung cấp đủ evidence, Agent không suy đoán credentials mà thông báo context chưa đủ.

Trong hệ thống RAG thực tế, đây là hành vi an toàn hơn so với tạo ra câu trả lời không có căn cứ.

---

## 8. Demo / Thuyết trình

Trong phần demo, nhóm trình bày hệ thống theo quy trình sau:

### Bước 1 — Giới thiệu corpus

Nhóm giới thiệu 6 tài liệu công khai từ TDTU Library và metadata của chúng:

```text
source_url
retrieved_at
document_version
audience
department
category
language
```

### Bước 2 — Trình bày ba chiến lược

Ba thành viên trình bày:

```text
R1 → FixedSizeChunker
R2 → RecursiveChunker
R3 → Heading/Section Chunker
```

và giải thích lý do lựa chọn.

### Bước 3 — Chạy benchmark

Nhóm chạy cùng 5 queries trên ba chiến lược và quan sát Top-3 chunks.

Đặc biệt tập trung vào:

* Query 4 để thể hiện ảnh hưởng của chunking.
* Query 5 để thể hiện ảnh hưởng của metadata filtering.

### Bước 4 — Demo Query 5 có và không có filter

Không filter:

```text
Query
  ↓
professional-staff-services → Top-1
undergraduate-student-services → Top-2
```

Có:

```python
metadata_filter={"audience": "student"}
```

kết quả:

```text
undergraduate-student-services → Top-1
```

Qua đó nhóm minh họa trực tiếp giá trị của metadata.

### Bước 5 — Demo Agent

Nhóm cho Agent trả lời một query có context đầy đủ và Query 4 của FixedSize strategy.

Hai trường hợp cho thấy Agent:

* trả lời khi có evidence;
* từ chối suy đoán khi retrieved context không đủ.

---

## 9. Kết luận

Qua Lab 7, nhóm xây dựng một pipeline retrieval cơ bản từ đầu:

```text
Raw Documents
      ↓
Metadata
      ↓
Chunking
      ↓
Embedding
      ↓
Vector Store
      ↓
Retrieval
      ↓
Metadata Filtering
      ↓
RAG Agent
```

Kết quả benchmark cho thấy chất lượng của hệ thống RAG không chỉ phụ thuộc vào embedding model hoặc LLM. Cách tổ chức dữ liệu trước retrieval có ảnh hưởng lớn đến kết quả cuối cùng.

Trên corpus TDTU Library:

* FixedSizeChunker tạo baseline đơn giản nhưng gặp failure ở Query 4.
* RecursiveChunker giữ các ranh giới tự nhiên tốt hơn và retrieve được relevant chunk cho cả 5 query.
* Heading/Section Chunking đặc biệt phù hợp với cấu trúc Markdown của corpus và đưa section cần thiết lên vị trí cao.
* Metadata filtering giúp phân biệt tài liệu dành cho sinh viên và nhân viên dù cả hai có semantic similarity cao với query.
* Agent có thể tạo câu trả lời grounded khi retrieval cung cấp đủ evidence và tránh suy đoán khi context thiếu thông tin.

Bài học quan trọng nhất của nhóm là:

> **Chất lượng RAG bắt đầu từ chất lượng dữ liệu và chiến lược retrieval, không chỉ từ LLM.**

---

## 10. Checklist hoàn thành

* [x] Thu thập 5–10 tài liệu công khai.
* [x] Corpus có `source_url`, `retrieved_at`, `document_version`.
* [x] Mỗi tài liệu có metadata `audience`.
* [x] Có thêm metadata hữu ích như `department`, `category`, `language`.
* [x] Xây dựng đúng 5 benchmark queries và gold answers.
* [x] Có ít nhất một query sử dụng `metadata_filter={"audience": "student"}`.
* [x] Ba thành viên thử các chunking strategies khác nhau.
* [x] Có thành viên thử Heading/Section Chunking.
* [x] Chạy baseline comparison trên nhiều tài liệu.
* [x] Chạy retrieval benchmark cho ba strategies.
* [x] So sánh metadata filtering với unfiltered retrieval.
* [x] Có failure analysis.
* [x] Có Agent grounded trên retrieved context.
* [x] Hoàn thành báo cáo nhóm.
