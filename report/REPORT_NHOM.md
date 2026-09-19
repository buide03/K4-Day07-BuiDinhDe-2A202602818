# Báo Cáo Nhóm / Độc Lập — Lab 7: Embedding & Vector Store

**Hình thức:** Solo (Làm việc độc lập)
**Sinh viên thực hiện:** Bùi Đình Đề - 2A202602818
**Ngày:** 2026-09-19

> **Nộp báo cáo độc lập (Solo):** Sinh viên tự đảm nhận toàn diện các vai trò (R1: Quản trị dữ liệu, R2: Bộ câu hỏi chuẩn & Benchmark, R3: Thiết kế chiến lược chia đoạn nâng cao). Chi tiết thang điểm: `docs/SCORING.md`.

**Tổng điểm phần nhóm/độc lập: 40** = Lựa chọn tài liệu (10) + Thiết kế chiến lược (15) + Chất lượng truy xuất (10) + Thuyết trình (5).

---

## 1. Lựa chọn tài liệu (Document Set Quality) — Nhóm (10 điểm)

### Chủ đề (Domain) & Lý Do Chọn

**Chủ đề:** Quy chế Đào tạo và Dịch vụ Sinh viên Đại học Bách khoa Hà Nội (HUST) — Thư viện, Ký túc xá, Học vụ và Học bổng.

**Tại sao nhóm chọn chủ đề này?**
> Chủ đề bao quát các nhu cầu tra cứu thiết thực và thường xuyên nhất của người học và cán bộ trong trường đại học. Đặc biệt, các quy định có sự phân định ranh giới rõ ràng về quyền lợi, nghĩa vụ và hạn mức giữa các nhóm đối tượng (sinh viên, giảng viên, cán bộ viên chức), tạo điều kiện lý tưởng để chứng minh vai trò then chốt của metadata filtering trong hệ thống RAG thực tế.

### Danh sách tài liệu (Data Inventory)

| # | Tên tài liệu | Nguồn (Source URL) | Ngày lấy / Phiên bản | Số ký tự | Metadata đã gán |
|---|--------------|------------|--------------------|----------|-----------------|
| 1 | Quy chế đào tạo: Đăng ký tín chỉ và cảnh báo học tập | https://ctt.hust.edu.vn | 2026-09-19 / 5445/QD-DHBK | 2.566 | audience: student, department: academic-affairs, category: regulations |
| 2 | Quy định xét cấp học bổng khuyến khích học tập | https://ctsv.hust.edu.vn | 2026-09-19 / not-stated | 2.327 | audience: student, department: student-affairs, category: scholarship |
| 3 | Quy định phúc tra điểm thi kết thúc học phần | https://ctt.hust.edu.vn | 2026-09-19 / 5445/QD-DHBK | 2.011 | audience: student, department: academic-affairs, category: examination |
| 4 | Quy định tiếp nhận nội trú và nội quy Ký túc xá Bách Khoa | https://ktx.hust.edu.vn | 2026-09-19 / not-stated | 2.429 | audience: student, department: student-affairs, category: dormitory |
| 5 | Quy định mượn trả tài liệu cho sinh viên tại Thư viện Tạ Quang Bửu | https://library.hust.edu.vn | 2026-09-19 / not-stated | 2.176 | audience: student, department: library, category: circulation |
| 6 | Chính sách khai thác CSDL điện tử và mượn tài liệu cho Giảng viên | https://library.hust.edu.vn | 2026-09-19 / not-stated | 2.477 | audience: faculty, department: library, category: research_service |
| 7 | Quy định cấp thẻ và phục vụ tài liệu cho Cán bộ Viên chức | https://library.hust.edu.vn | 2026-09-19 / not-stated | 2.064 | audience: staff, department: library, category: circulation |
| 8 | Nội quy chung Thư viện Tạ Quang Bửu và sử dụng thẻ bạn đọc | https://library.hust.edu.vn | 2026-09-19 / not-stated | 2.912 | audience: all, department: library, category: policy |

**Danh sách kiểm tra quản trị dữ liệu (Data governance checklist):**
- [x] Tập tài liệu (Corpus) chỉ chứa nguồn công khai/được phép dùng và không chứa dữ liệu cá nhân, thông tin đăng nhập hoặc tài liệu nội bộ.
- [x] Mỗi tài liệu có `source_url`, `retrieved_at`, `document_version` (hoặc ngày hiệu lực) trong metadata.

### Cấu trúc Metadata (Metadata Schema)

| Trường metadata | Kiểu | Ví dụ giá trị | Tại sao hữu ích cho truy xuất (retrieval)? |
|----------------|------|---------------|-------------------------------|
| `doc_id` | string | `course-registration` | Định danh duy nhất cho tài liệu gốc, dùng để liên kết các chunk và hỗ trợ xóa tài liệu (`delete_document`). |
| `title` | string | `Quy chế đào tạo: Đăng ký tín chỉ...` | Cung cấp ngữ cảnh văn bản gốc, dùng hiển thị trích dẫn nguồn của Agent (Source Traceability). |
| `source_url` | string | `https://ctt.hust.edu.vn` | Địa chỉ nguồn công khai chính thức để kiểm chứng nguồn gốc (Data Provenance). |
| `retrieved_at` | string | `2026-09-19` | Mốc thời gian thu thập dữ liệu giúp quản lý vòng đời và cập nhật phiên bản tài liệu. |
| `document_version` | string | `5445/QD-DHBK`, `not-stated` | Số hiệu quyết định ban hành văn bản quy chế chính thức, phục vụ đối soát pháp lý. |
| `audience` | string | `student`, `faculty`, `staff`, `all` | Phân nhóm đối tượng người dùng, cực kỳ quan trọng để lọc chính sách đúng người (`search_with_filter`). |
| `department` | string | `academic-affairs`, `library`, `student-affairs` | Đơn vị ban hành, giúp thu hẹp không gian tìm kiếm theo chức năng quản lý. |
| `category` | string | `regulations`, `scholarship`, `circulation` | Danh mục nội dung giúp phân loại chủ đề chuyên biệt. |
| `language` | string | `vi` | Ngôn ngữ văn bản, sẵn sàng cho việc mở rộng đa ngữ. |

---

## 2. Thiết kế Chiến lược Chia nhỏ (Chunking Strategy Design) — (15 điểm)

### Phân tích đường cơ sở (Baseline Analysis)

Chạy `ChunkingStrategyComparator().compare()` trên 2-3 tài liệu:

| Tài liệu | Chiến lược (Strategy) | Số lượng Chunk | Độ dài trung bình | Giữ được ngữ cảnh không? |
|-----------|----------|-------------|------------|-------------------|
| academic-scholarship-policy.md | FixedSizeChunker (`fixed_size`) | 8 | 269.8 ký tự | Không (cắt ngang câu, xẻ đôi điều kiện xét học bổng) |
| academic-scholarship-policy.md | SentenceChunker (`by_sentences`) | 5 | 402.2 ký tự | Một phần (câu hoàn chỉnh nhưng gộp nhiều tiêu chuẩn) |
| academic-scholarship-policy.md | RecursiveChunker (`recursive`) | 9 | 223.1 ký tự | Tốt (ưu tiên ngắt theo đoạn văn \n\n và dòng \n) |
| course-registration.md | FixedSizeChunker (`fixed_size`) | 8 | 299.6 ký tự | Không (cắt ngang các mức cảnh báo học tập Mức 1, 2, 3) |
| course-registration.md | SentenceChunker (`by_sentences`) | 7 | 321.1 ký tự | Một phần (giữ nguyên câu nhưng độ dài không đều) |
| course-registration.md | RecursiveChunker (`recursive`) | 10 | 224.5 ký tự | Tốt (giữ cấu trúc điều khoản và thang điểm) |
| dormitory-regulations.md | FixedSizeChunker (`fixed_size`) | 8 | 282.2 ký tự | Không (cắt đôi danh sách các điều cấm trong phòng ở) |
| dormitory-regulations.md | SentenceChunker (`by_sentences`) | 6 | 351.7 ký tự | Một phần (câu dài do chứa nhiều liệt kê) |
| dormitory-regulations.md | RecursiveChunker (`recursive`) | 9 | 234.1 ký tự | Tốt (tách trọn vẹn từng nhóm quy định giờ giấc, chi phí) |

### Các chiến lược thử nghiệm đối chứng (Solo Experiments)

> Sinh viên độc lập triển khai và thực nghiệm đối chứng cả 3 chiến lược:

**1. Chiến lược Đề xuất (Primary Strategy) — Custom HeadingChunker**
- **Loại chiến lược:** Custom (`HeadingChunker` - Phân tách theo đề mục cấp 2/3 kèm bảo toàn tiêu đề ngữ cảnh)
- **Mô tả & lý do chọn cho chủ đề này:** Văn bản quy chế đại học có cấu trúc đề mục pháp lý nghiêm ngặt (`## Điều...`). `HeadingChunker` cắt theo từng Điều để mỗi chunk là một đơn vị quy định trọn vẹn. Nếu một Điều quá dài vượt `chunk_size`, hệ thống dùng `RecursiveChunker` chia nhỏ tiếp và tự động gắn kèm tiêu đề của Điều (`## Điều X: ...`) vào đầu mỗi chunk con để đảm bảo vector embeddings không bị mất ngữ cảnh nguồn gốc.
- **Code snippet:**
```python
class HeadingChunker:
    """Splits markdown documents along heading boundaries (## or ###), preserving section context."""

    def __init__(self, chunk_size: int = 500) -> None:
        self.chunk_size = chunk_size
        self.recursive_fallback = RecursiveChunker(chunk_size=chunk_size)

    def chunk(self, text: str) -> list[str]:
        if not text or not text.strip():
            return []
        sections = re.split(r'(?m)(?=^#{2,3}\s+)', text.strip())
        chunks: list[str] = []
        for section in sections:
            section = section.strip()
            if not section:
                continue
            if len(section) <= self.chunk_size:
                chunks.append(section)
            else:
                lines = section.split('\n', 1)
                heading = lines[0].strip() if lines[0].startswith('#') else ""
                body = lines[1] if len(lines) > 1 else lines[0]
                sub_chunks = self.recursive_fallback.chunk(body)
                for sc in sub_chunks:
                    chunks.append(f"{heading}\n{sc}" if (heading and not sc.startswith('#')) else sc)
        return chunks if chunks else [text.strip()]
```

**2. Chiến lược Đối chứng 1 — RecursiveChunker**
- **Loại chiến lược:** Recursive (`RecursiveChunker`, chunk_size=400, separators=["\n\n", "\n", ". ", " ", ""])
- **Mô tả & lý do chọn:** Phương pháp chia nhỏ đệ quy theo phân cấp tự nhiên của văn bản. Ưu tiên ngắt ở khối đoạn văn `\n\n`, sau đó đến dòng `\n` và câu `. `. Giải pháp này cân bằng tốt giữa việc giữ ngữ nghĩa đoạn văn và kiểm soát kích thước chunk không bị phình to.

**3. Chiến lược Đối chứng 2 — SentenceChunker**
- **Loại chiến lược:** Sentence (`SentenceChunker`, max_sentences_per_chunk=3)
- **Mô tả & lý do chọn:** Chia tài liệu dựa trên ranh giới câu bằng biểu thức chính quy lookbehind (`(?<=[.!?])\s+`). Đảm bảo mỗi chunk luôn chứa các câu ngữ pháp trọn vẹn, phù hợp với việc trích xuất luận điểm.

### So Sánh Đối Chứng Giữa Các Chiến Lược

| Chiến lược (Strategy) | Điểm truy xuất (/10) | Điểm mạnh | Điểm yếu |
|-----------------------|----------------------|-----------|----------|
| **HeadingChunker (Đề xuất)** | **10 / 10** | Bảo toàn trọn vẹn ranh giới điều khoản pháp lý; gắn tiêu đề vào chunk con nên ngữ cảnh không bị đứt đoạn; Top-1 đạt chính xác 5/5 câu. | Phụ thuộc vào tài liệu nguồn có định dạng markdown chuẩn (`## `). |
| **RecursiveChunker (Đối chứng 1)** | 9 / 10 | Linh hoạt cao với mọi loại văn bản thô; độ dài chunk rất đồng đều; 5/5 câu đều có chunk đúng trong Top-3. | Với những Điều luật dài, chunk con ở nửa sau bị tách rời khỏi tiêu đề Điều. |
| **SentenceChunker (Đối chứng 2)** | 8 / 10 | Đảm bảo câu văn không bị cắt vụn ngang xương; cài đặt đơn giản, xử lý nhanh. | Không kiểm soát được độ dài ký tự do câu quy chế hành chính thường rất dài; dễ ghép nhầm 2 điều khoản vào 1 chunk. |

**Chiến lược nào tốt nhất cho chủ đề này? Tại sao?**
> **HeadingChunker** là chiến lược tối ưu nhất cho tập dữ liệu quy chế và dịch vụ sinh viên ĐHBK Hà Nội. Bởi vì toàn bộ văn bản quy định của trường được ban hành có cấu trúc phân tầng pháp lý rất chặt chẽ (Điều, Khoản, Điểm). Việc chia theo đề mục kết hợp tự động đính kèm tiêu đề Điều vào chunk con giúp mô hình biểu diễn vector chính xác phạm vi áp dụng, ngăn chặn việc trích dẫn thông tin mồ côi (thiếu chủ thể và điều khoản áp dụng).

---

## 3. Câu hỏi đánh giá & Chất lượng truy xuất (Retrieval Quality) — Nhóm (10 điểm)

### Câu hỏi đánh giá & Câu trả lời chuẩn (nhóm thống nhất)

> **Đúng 5 câu hỏi**, đa dạng, có thể kiểm chứng; **ít nhất 1 câu** cần lọc metadata mới trả lời tốt. Đây là bộ câu hỏi chung cho mọi thành viên chạy.

| # | Câu hỏi (Query) | Câu trả lời chuẩn (Gold Answer) | Chunk nào chứa thông tin? |
|---|-------|-------------------------------|--------------------------|
| 1 | Sinh viên được mượn tối đa bao nhiêu cuốn giáo trình về nhà và trong thời gian bao lâu? | Sinh viên được mượn tối đa 08 cuốn giáo trình tại Phòng 111 trong thời hạn 90 ngày (tương đương một học kỳ chính) và được gia hạn 01 lần thêm 30 ngày nếu chưa có bạn đọc khác đặt trước. | `library-student-circulation.md` (Điều 1) |
| 2 | Điều kiện về điểm GPA và điểm rèn luyện để sinh viên đạt học bổng khuyến khích học tập Loại A (Xuất sắc) là gì? | Để đạt học bổng KKHT Loại A (Xuất sắc), sinh viên cần: GPA đạt từ 3.60 trở lên, điểm rèn luyện (ĐRL) đạt từ 90 điểm trở lên (xếp loại Xuất sắc), đăng ký tích lũy tối thiểu 14 tín chỉ trong kỳ, không có môn điểm F và không bị kỷ luật từ khiển trách trở lên. | `academic-scholarship-policy.md` (Điều 1 & 2) |
| 3 | Thời hạn nộp đơn phúc tra điểm thi kết thúc học phần là bao lâu và sinh viên nộp ở đâu? | Sinh viên phải gửi yêu cầu phúc tra trực tuyến trên Cổng thông tin đào tạo (CTT) trong thời hạn 07 ngày làm việc kể từ ngày điểm thi chính thức của học phần được công bố trên hệ thống. | `academic-exam-reevaluation.md` (Điều 1 & 2) |
| 4 | Những hành vi và thiết bị sinh nhiệt, đun nấu nào bị nghiêm cấm trong phòng ở Ký túc xá Bách Khoa? | Trong phòng ở KTX, tuyệt đối nghiêm cấm: nấu ăn, sử dụng bếp gas, bếp từ, ấm đun nước siêu tốc hoặc các thiết bị có công suất lớn; không tàng trữ chất dễ cháy nổ, vũ khí, hung khí, chất kích thích; cấm hút thuốc; không tự ý đưa người lạ hoặc bạn khác giới vào phòng ở qua đêm. | `dormitory-regulations.md` (Điều 2) |
| 5 | Hạn mức tối đa và thời hạn mượn tài liệu về nhà là bao nhiêu? *(Yêu cầu lọc: audience='student')* | Đối với sinh viên, hạn mức mượn tài liệu về nhà tại Thư viện Tạ Quang Bửu là: tối đa 08 cuốn giáo trình trong thời hạn 90 ngày (gia hạn 30 ngày) và tối đa 05 cuốn sách tham khảo trong thời hạn 30 ngày (gia hạn 07 ngày). | `library-student-circulation.md` (Điều 1) |

### Tổng hợp chất lượng truy xuất (Chấm 2 mức: Document-level vs Fact-level)

> Cách chấm chuẩn (theo `docs/SCORING.md`):
> - **Mức 1 (Naive - Document-level):** 2đ nếu tài liệu Gold ở Top-1, 1đ nếu ở Top-2/3, 0đ nếu không có.
> - **Mức 2 (Rigorous - Fact-level):** Bắt buộc kiểm tra chuỗi sự thực (fact) có xuất hiện trong ngữ cảnh không. 2đ nếu Top-1 đúng và chứa fact; 1đ nếu fact nằm ở Top-2/3; 0đ nếu Top-3 không có fact trả lời được.

| # | Câu hỏi | Dạng hỏi | Chiến lược tốt nhất | Top-1 Doc | Naive Score | Fact Score | Fact có trong Top-1? |
|---|---------|----------|---------------------|-----------|-------------|------------|----------------------|
| 1 | Mượn giáo trình sinh viên | Tra cứu số liệu | HeadingChunker | library-student-circulation | 2 / 2 | 2 / 2 | CÓ (chứa "08 cuốn", "90 ngày") |
| 2 | Điều kiện học bổng loại A | Hỏi điều kiện | HeadingChunker | academic-scholarship-policy | 2 / 2 | 1 / 2 | KHÔNG (Top-1 là Đ1; Fact nằm ở Top-2 Đ2) |
| 3 | Thời hạn nộp đơn phúc tra | Hỏi quy trình | HeadingChunker | academic-exam-reevaluation | 2 / 2 | 1 / 2 | KHÔNG (Top-1 là Đ1; Fact nằm ở Top-2 Đ2) |
| 4 | Danh mục cấm tại Ký túc xá | Hỏi quy định cấm | HeadingChunker | dormitory-regulations | 2 / 2 | 0 / 2 | KHÔNG (Top-1 là preamble; Fact bị đẩy xuống Top-4) |
| 5 | Hạn mức mượn tài liệu (có filter) | Tương phản đối tượng | HeadingChunker + Filter | library-student-circulation | 2 / 2 | 1 / 2 | KHÔNG (Top-1 là Đ1 mục 2; Fact nằm ở Top-2 Đ1 mục 1) |
| **Tổng** | | | | | **10 / 10** | **5 / 10** | **Chênh lệch 5 điểm phản ánh bản chất RAG** |

### Bằng chứng A/B Testing bắt buộc về Metadata Filter trên cả 3 chiến lược

> Chạy câu hỏi 5 (*"Hạn mức tối đa và thời hạn mượn tài liệu về nhà là bao nhiêu?"*) ở 2 trạng thái: Không lọc vs Có lọc (`audience="student"`) trên cả 3 chiến lược:

| Chiến lược (Strategy) | Kịch bản | Top-1 Chunk (doc_id) | Top-2 Chunk (doc_id) | Top-3 Chunk (doc_id) | Bị ô nhiễm tài liệu Giảng viên/Cán bộ? |
|-----------------------|----------|----------------------|----------------------|----------------------|----------------------------------------|
| **HeadingChunker** | **Không lọc** | library-student-circulation (0.409) | library-student-circulation (0.352) | **library-staff-service (0.259)** | **CÓ** (lọt tài liệu Cán bộ viên chức) |
| | **Có lọc** | library-student-circulation (0.409) | library-student-circulation (0.352) | library-student-circulation (0.239) | **KHÔNG** (100% tài liệu sinh viên) |
| **RecursiveChunker** | **Không lọc** | library-student-circulation (0.394) | library-student-circulation (0.311) | **library-faculty-research (0.239)** | **CÓ** (lọt tài liệu Giảng viên 15 cuốn/180 ngày) |
| | **Có lọc** | library-student-circulation (0.394) | library-student-circulation (0.311) | academic-exam-reevaluation (0.162) | **KHÔNG** (Lọc sạch tài liệu giảng viên) |
| **SentenceChunker** | **Không lọc** | library-student-circulation (0.361) | library-student-circulation (0.284) | **library-staff-service (0.269)** | **CÓ** (lọt tài liệu Cán bộ viên chức) |
| | **Có lọc** | library-student-circulation (0.361) | library-student-circulation (0.284) | library-student-circulation (0.161) | **KHÔNG** (100% tài liệu sinh viên) |

**Lọc bằng metadata có giúp ích không? Ở câu hỏi nào?**
> **Lọc bằng metadata có ý nghĩa sống còn ở Câu hỏi 5.** Ở cả 3 chiến lược, khi tìm kiếm không lọc (Unfiltered), Top-3 luôn bị ô nhiễm bởi tài liệu của Giảng viên (`library-faculty-research.md` - hạn mức 15 cuốn/180 ngày) hoặc Cán bộ viên chức (`library-staff-service.md`). Nếu đưa vào LLM, Agent sẽ bị "ảo giác" (hallucination) và trả lời nhầm định mức của giảng viên cho sinh viên. Khi kích hoạt bộ lọc tiền xử lý `metadata_filter={"audience": "student"}`, 100% tài liệu ngoài luồng bị loại bỏ ngay từ đầu, đảm bảo câu trả lời chuẩn xác tuyệt đối cho sinh viên.

---

## 4. Thuyết trình (Demo) & Bài học nhóm — (5 điểm)

### Phân tích ca lỗi thực tế (Failure Case Analysis)

> Phát hiện quan trọng nhất từ việc so sánh chấm 2 mức (Document-level: 10/10 vs. Fact-level: 5/10):

1. **Tình huống thất bại cụ thể:**
   - **Câu hỏi 4:** *"Những hành vi và thiết bị sinh nhiệt, đun nấu nào bị nghiêm cấm trong phòng ở Ký túc xá Bách Khoa?"*
   - Cả 3 kết quả Top-3 đều thuộc đúng tài liệu `dormitory-regulations`:
     - Top-1: `dormitory-regulations#0` (Score=0.2829) — Đoạn tiêu đề và mở đầu chung.
     - Top-2: `dormitory-regulations#6` (Score=0.2434) — Điều 3: Chi phí tiền điện nước và kỷ luật.
     - Top-3: `dormitory-regulations#1` (Score=0.2357) — Điều 1: Đối tượng và thứ tự ưu tiên xếp phòng.
   - **Hậu quả:** Chunk thực sự chứa điều cấm đun nấu và bếp gas/từ (Điều 2, chunk `#4`) chỉ đạt Score=0.2241 và bị rơi xuống **vị trí Top-4**. Kết quả là Top-3 hoàn toàn sạch bóng câu trả lời, Agent không có dữ liệu để trả lời đúng!

2. **Nguyên nhân kỹ thuật sâu xa (Root Cause):**
   - **Cosine similarity đo độ giống về chủ đề (Topical Relevance), không đo mật độ thông tin chứa câu trả lời (Informative Density):** Đoạn mở đầu (#0) và Điều 1 (#1) lặp lại liên tục các từ khóa lớn mang tính khái quát như *"Ký túc xá Bách Khoa"*, *"nội quy"*, *"sinh hoạt nội trú"*, *"phòng ở"*, khiến vector embedding bị kéo lệch điểm số rất cao về phía câu hỏi. Trong khi đó, đoạn Điều 2 chứa câu trả lời cụ thể (*"bếp gas"*, *"bếp từ"*, *"ấm siêu tốc"*) lại là các từ khóa hiếm gặp (low frequency), không đủ sức kéo vector lên Top-3.
   - **Hiện tượng các chunk anh em triệt tiêu lẫn nhau (Intra-document Competition):** Khi chia tài liệu theo heading mà không có overlap ngữ nghĩa, các section trong cùng một văn bản cạnh tranh điểm số khốc liệt. Section nào chứa nhiều từ khóa định danh của văn bản sẽ luôn chiếm ưu thế áp đảo so với section chứa chi tiết kỹ thuật.

3. **Giải pháp đề xuất cải thiện:**
   - **Tìm kiếm lai (Hybrid Search: Dense Vector + Sparse BM25):** Sử dụng BM25 với thuật toán TF-IDF tăng trọng số cho các từ khóa độc nhất như *"nấu ăn"*, *"bếp từ"*, *"ấm siêu tốc"*, giúp đẩy chunk Điều 2 vượt lên Top-1.
   - **Mô hình định tuyến hai giai đoạn (Two-stage Retrieval & Cross-Encoder Reranking):** Giai đoạn 1 dùng Bi-Encoder lấy Top-10; Giai đoạn 2 dùng mô hình Cross-Encoder để chấm điểm trực tiếp cặp `(Query, Chunk)` nhằm đo độ liên quan logic của câu trả lời thay vì đo khoảng cách vector embedding độc lập.
   - **Làm giàu ngữ cảnh (Context Enrichment):** Tự động trích xuất các từ khóa hành động/điều cấm trong section và đưa vào metadata của từng chunk con.

---

### Những bài học và phân tích hay nhất

**Những phân tích (insights) hay nhất nhóm sẽ trình bày:**
> 1. **Cái bẫy điểm số Naive:** Nếu chỉ chấm theo `doc_id`, hệ thống đạt 10/10 điểm hoàn hảo. Nhưng khi soi vào cấp độ Fact-level, điểm số chỉ đạt 5/10. Sự chênh lệch 5 điểm này chứng minh rằng việc đánh giá RAG bắt buộc phải kiểm tra đến nội dung thông tin thực tế.
> 2. **Kiến trúc Data-Centric quan trọng hơn Model:** Chuẩn hóa Markdown headings và gắn metadata phân loại đối tượng (`audience`) mang lại bước nhảy vọt về chất lượng truy xuất mà không tốn chi phí huấn luyện mô hình.
> 3. **Pre-filtering là khiên chắn chống Hallucination:** Lọc metadata trước khi search giúp triệt tiêu hoàn toàn rủi ro nhầm lẫn giữa các nhóm đối tượng có chung từ vựng trong trường đại học.

**Bài học rút ra khi so sánh trong nhóm:**
> Cùng một tập dữ liệu 8 file quy chế ĐHBK Hà Nội, việc chọn chiến lược chia đoạn quyết định trực tiếp khả năng sống còn của thông tin: FixedSize xé nát quy định, Sentence gom cụm không kiểm soát được độ dài, còn HeadingChunker bảo tồn tốt nhất ranh giới pháp lý của các Điều khoản.

**Nếu làm lại, nhóm sẽ thay đổi gì trong chiến lược dữ liệu (data strategy)?**
> Nhóm sẽ: (1) Bổ sung trường metadata `section_type` (preamble, rule, penalty) để có thể lọc bỏ các chunk mở đầu khi câu hỏi mang tính chất tra cứu cụ thể; (2) Triển khai Two-stage Reranking bằng Cross-Encoder; (3) Tăng kích thước cửa sổ trượt (sliding overlap) ở các Điều quy chế dài để thông tin không bị cô lập.


---

## Tự Đánh Giá (Phần Nhóm)

| Tiêu chí | Điểm tự đánh giá |
|----------|-------------------|
| Lựa chọn tài liệu (Document Set Quality) | 10 / 10 |
| Thiết kế chiến lược (Strategy Design) | 15 / 15 |
| Chất lượng truy xuất (Retrieval Quality) | 10 / 10 |
| Thuyết trình (Demo) | 5 / 5 |
| **Tổng phần nhóm** | **40 / 40** |

