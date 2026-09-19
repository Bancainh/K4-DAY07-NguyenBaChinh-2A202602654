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

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|---|---|---|---:|---|
| 1 | Undergraduate Student - Circulation Service | https://lib.tdtu.edu.vn/services/circulation/undergraduate-student | 2026-09-19 / not specified | 1240 | audience=student, department=library, category=circulation, language=en |
| 2 | Library Card & Account | https://lib.tdtu.edu.vn/guides/essential/library-card-account | 2026-09-19 / not specified | 1150 | audience=all, department=library, category=account, language=en |
| 3 | Renew Library Materials | https://lib.tdtu.edu.vn/guides/essential/renewal | 2026-09-19 / not specified | 663 | audience=all, department=library, category=renewal, language=en |
| 4 | Reserve a Room | https://lib.tdtu.edu.vn/guides/essential/reserve-a-room | 2026-09-19 / not specified | 1028 | audience=all, department=library, category=room_booking, language=en |
| 5 | Services for TDTU Undergraduate Students | https://lib.tdtu.edu.vn/user-group-services/undergraduate-student | 2026-09-19 / not specified | 906 | audience=student, department=library, category=user_group_services, language=en |
| 6 | Services for TDTU Academic and Professional Staff | https://lib.tdtu.edu.vn/user-group-services/professional-staff | 2026-09-19 / not specified | 1007 | audience=staff, department=library, category=user_group_services, language=en |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**

- [x] Corpus chỉ sử dụng các trang công khai chính thức của TDTU Library và không chứa dữ liệu đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` cùng các metadata phục vụ truy xuất.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho retrieval? |
|---|---|---|---|
| `doc_id` | string | `student-borrowing-policy` | Nhận diện tài liệu nguồn của mỗi chunk |
| `title` | string | `Library Card & Account` | Giúp mô tả nội dung tài liệu |
| `audience` | string | `student` | Cho phép lọc kết quả theo đúng nhóm người dùng |
| `department` | string | `library` | Cho phép giới hạn retrieval theo đơn vị |
| `category` | string | `circulation` | Phân biệt loại dịch vụ/quy định |
| `language` | string | `en` | Hỗ trợ lọc theo ngôn ngữ |
| `source_url` | string | URL TDTU Library | Truy xuất nguồn gốc và kiểm chứng thông tin |
| `retrieved_at` | string/date | `2026-09-19` | Theo dõi thời điểm thu thập dữ liệu |
| `document_version` | string | `not specified` | Theo dõi phiên bản tài liệu nếu có |

---

## 2. Thiết kế chiến lược (Strategy Design) — Nhóm (15 điểm)

Mỗi thành viên sử dụng một chiến lược chunking khác nhau trên cùng 6 tài liệu và cùng 5 benchmark queries.

### Phân tích đường cơ sở (Baseline Analysis)

Nhóm chạy `ChunkingStrategyComparator().compare()` trên 3 tài liệu sau khi loại bỏ YAML frontmatter.

| Tài liệu | Chiến lược | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|---|---|---:|---:|---|
| student-borrowing-policy.md | FixedSizeChunker | 3 | 447.00 | Khá, nhưng có thể cắt giữa section |
| student-borrowing-policy.md | SentenceChunker | 5 | 246.20 | Tốt ở mức câu nhưng chunk nhỏ hơn |
| student-borrowing-policy.md | RecursiveChunker | 3 | 413.67 | Tốt, ưu tiên các ranh giới tự nhiên |
| reserve-a-room.md | FixedSizeChunker | 3 | 376.33 | Khá |
| reserve-a-room.md | SentenceChunker | 3 | 340.33 | Tốt |
| reserve-a-room.md | RecursiveChunker | 3 | 343.00 | Tốt |
| undergraduate-student-services.md | FixedSizeChunker | 2 | 478.50 | Khá |
| undergraduate-student-services.md | SentenceChunker | 3 | 299.67 | Tốt ở mức câu |
| undergraduate-student-services.md | RecursiveChunker | 2 | 453.50 | Tốt |

### Chiến lược của từng thành viên

**Thành viên 1 — Nguyễn Bá Chinh (R1)**

- **Loại chiến lược:** `FixedSizeChunker(chunk_size=500, overlap=50)`
- **Mô tả & lý do chọn:** Fixed-size chunking đơn giản, dễ kiểm soát kích thước đầu vào cho embedding và tạo một baseline rõ ràng. Overlap 50 ký tự giúp giảm khả năng mất thông tin nằm ngay tại ranh giới giữa hai chunk.
- **Code snippet:** Sử dụng implementation `FixedSizeChunker` trong `src/chunking.py`.

**Thành viên 2 — Trần Anh Vũ (R2)**

- **Loại chiến lược:** `RecursiveChunker(chunk_size=500)`
- **Mô tả & lý do chọn:** Recursive chunking ưu tiên tách theo đoạn văn, dòng và câu trước khi phải cắt theo ký tự. Cách này giúp chunk giữ được cấu trúc ngữ nghĩa tự nhiên hơn so với cắt cứng theo số ký tự.
- **Code snippet:** Sử dụng `RecursiveChunker` trong `src/chunking.py`.

**Thành viên 3 — Dương Thị Hồng Viên (R3)**

- **Loại chiến lược:** Heading/Section Chunking, `chunk_size=500`
- **Mô tả & lý do chọn:** Các tài liệu thư viện được tổ chức theo các heading như `Loan Periods`, `Renewal`, `Learning Support` và `Booking and Cancellation`, do đó mỗi section có thể xem là một đơn vị ngữ nghĩa. Khi section quá dài, nhóm sử dụng `RecursiveChunker` để chia tiếp nhưng vẫn gắn lại heading vào từng chunk con.

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