# CLAUDE.md — Ghép ảnh Giám định Giấy Tờ Xe (GTX) PTI

## Mục đích

Tạo bộ ảnh giám định giấy tờ xe ô tô PTI chuẩn định dạng từ ảnh giấy tờ, xuất file PDF.
Danh mục giấy tờ được **định nghĩa sẵn trong dự án** (file `doc_types.json`) — không cần
file Excel GTX nữa. Danh mục **bổ sung được**: sửa file JSON, hoặc thêm ngay trên giao diện web.

**Kích hoạt khi người dùng:**
- Upload ảnh giấy tờ xe và gõ "tạo ảnh GTX"
- Yêu cầu "ghép ảnh GTX", "tạo bản ảnh giấy tờ xe", "tạo ảnh giám định giấy tờ"
- Có các ảnh đặt tên theo tiền tố `1.1`, `1.2`, `2.1`, `3.1`, `4`, `5`… và yêu cầu tạo ảnh
- Đề cập đến "bản ảnh GTX", "ảnh giấy tờ xe PTI", "ghép ảnh GTX"

---

## Đầu vào

### 1. File ảnh / PDF — đặt tên theo tiền tố danh mục

Tên file bắt đầu bằng **tiền tố** khớp bảng danh mục: `{tiền tố}.jpg` / `{tiền tố}.pdf`
Ví dụ: `1.1.jpg`, `1.2.jpg`, `2.1.jpg`, `4.pdf`

File PDF tự động chuyển sang ảnh bằng PyMuPDF (`pip install PyMuPDF`), mỗi trang PDF thành 1 ảnh.

### 2. Thông tin giám định (nhập trực tiếp)

| Thông tin | Nguồn | Bắt buộc |
|-----------|-------|----------|
| Biển số xe (BKS) | Ô "Biển số xe" trên web, hoặc tham số `bks=` khi chạy script | ✅ |
| Giám định viên | Ô "Giám định viên", hoặc `gdv=` | — |
| Ngày giám định | Ô "Ngày giám định", hoặc `ngay=` | — |

BKS được chuẩn hoá bằng `normalize_bks()` (regex `\d{2}[A-Z]{1,2}-?\d{3,5}\.?\d*`),
dùng cho tiêu đề mỗi trang và tên file output `GiamDinh_GiayToXe_{BKS}.pdf`.

---

## Danh mục tiền tố

Caption lấy từ danh mục này. Có **3 lớp**, lớp sau ghi đè lớp trước khi trùng tiền tố:

| # | Nguồn | Phạm vi | Dùng khi |
|---|-------|---------|----------|
| 1 | `BUILTIN_DOC_TYPES` trong `gtx_gen.py` | Dự phòng | Chỉ dùng khi thiếu `doc_types.json` |
| 2 | **`doc_types.json`** | Toàn dự án, mọi người dùng | Bổ sung hạng mục chính thức, lâu dài |
| 3 | Ô **"Thêm hạng mục"** trên web | Riêng trình duyệt đang dùng | Hạng mục phát sinh, không cần deploy lại |

### Cách 1 — sửa `doc_types.json` (khuyến nghị cho hạng mục cố định)

```json
{
  "items": {
    "9": "Biên bản hiện trường",
    "3.7": "Xác minh bằng lái bổ sung"
  }
}
```

Thêm dòng vào mục `items`, lưu file, khởi động lại server (hoặc commit + push để Render
deploy lại). Khóa bắt đầu bằng `_` chỉ là ghi chú, chương trình bỏ qua.

### Cách 2 — thêm trên giao diện web (nhanh, không cần deploy)

Trong khối **"Danh mục tiền tố"**, nhập Tiền tố + Tên hạng mục rồi bấm **"+ Thêm hạng mục"**.
Hạng mục mới gắn nhãn *tự thêm*, có nút `×` để bỏ, được lưu trong `localStorage` của
trình duyệt đó và tự gửi kèm mỗi lần tạo PDF.

> Lưu ý: hạng mục thêm kiểu này **chỉ có trên máy/trình duyệt đó**, không chia sẻ cho
> đồng nghiệp và sẽ mất nếu xóa dữ liệu duyệt web. Muốn dùng chung thì đưa vào `doc_types.json`.

### Cách 3 — tham số `--them` khi chạy script

```powershell
python gtx_gen.py --bks "14K-240.48" --them "9=Biên bản hiện trường" --them "3.7=Xác minh bằng lái"
```

### Quy tắc tiền tố

- Dạng số: `9` hoặc `3.7` (tối đa 3 chữ số mỗi phần)
- Chữ số đầu = nhóm, quyết định layout (xem bảng Layout bên dưới)
- Tiền tố mới thuộc nhóm có sẵn thì theo layout của nhóm đó; nhóm từ 4 trở lên luôn 1 ảnh/trang

### Bảng danh mục hiện tại

| Tiền tố | Tên hạng mục | Layout |
|---------|--------------|--------|
| `1.1` | Đăng ký xe mặt trước | 4 ảnh/trang · A4 ngang |
| `1.2` | Đăng ký xe mặt sau | 4 ảnh/trang · A4 ngang |
| `1.3` | Bằng lái mặt trước | 4 ảnh/trang · A4 ngang |
| `1.4` | Bằng lái mặt sau | 4 ảnh/trang · A4 ngang |
| `1.5` | Căn cước công dân lái xe | 4 ảnh/trang · A4 ngang |
| `1.6` | Căn cước công dân lái xe | 4 ảnh/trang · A4 ngang |
| `2.1` | Giấy chứng nhận đăng kiểm A5 mặt trước | 2 ảnh/trang · A4 dọc |
| `2.2` | Giấy chứng nhận đăng kiểm A5 mặt sau | 2 ảnh/trang · A4 dọc |
| `2.3` | Giấy chứng nhận bảo hiểm A5 mặt trước | 2 ảnh/trang · A4 dọc |
| `2.4` | Giấy chứng nhận bảo hiểm A5 mặt sau | 2 ảnh/trang · A4 dọc |
| `3.1` | Xác minh bằng lái | 4 ảnh/trang · A4 dọc |
| `3.2` | Xác minh bằng lái | 4 ảnh/trang · A4 dọc |
| `3.3` | Xác minh bằng lái | 4 ảnh/trang · A4 dọc |
| `3.4` | Xác minh bằng lái | 4 ảnh/trang · A4 dọc |
| `3.5` | Xác minh bằng lái | 4 ảnh/trang · A4 dọc |
| `3.6` | Xác minh bằng lái | 4 ảnh/trang · A4 dọc |
| `4` | Giấy chứng nhận bảo hiểm A4 | 1 ảnh/trang · A4 dọc |
| `5` | Xác minh thanh toán phí bảo hiểm | 1 ảnh/trang · A4 dọc |
| `6` | Giấy chứng nhận kiểm định XCG A4 | 1 ảnh/trang · A4 dọc |
| `7` | Biên bản bàn giao xe mới | 1 ảnh/trang · A4 dọc |
| `8` | Giấy xác nhận quyền thụ hưởng Ngân hàng | 1 ảnh/trang · A4 dọc |

Caption in trên ảnh = `{tiền tố}. {tên hạng mục}` — ví dụ `1.1. Đăng ký xe mặt trước`.

> **Tiền tố ngoài danh mục** (ví dụ `9.1.jpg` khi chưa khai báo): code lấy tên của mục gần
> nhất phía trước trong cùng nhóm; nếu không có thì fallback `"Hạng mục 9.1"`. Giao diện web
> đánh dấu đỏ "tiền tố không có trong danh mục" ngay khi chọn file.
> → Cách xử lý: bổ sung tiền tố theo một trong 3 cách ở trên.

---

## Layout tự động theo nhóm (số nguyên đầu của tiền tố)

| Nhóm | Layout | Số ảnh/trang | Ghi chú |
|------|--------|--------------|---------|
| **1** | A4 NGANG | 4 ảnh (2 cột × 2 hàng) | Tất cả ảnh nhóm 1.x ghép vào 1 trang ngang |
| **2** | A4 DỌC | 2 ảnh (1 cột × 2 hàng) | Tất cả ảnh nhóm 2.x ghép vào 1 trang dọc |
| **3** | A4 DỌC | 4 ảnh (2 cột × 2 hàng) | Tất cả ảnh nhóm 3.x ghép vào 1 trang dọc |
| **≥ 4 (4, 5, 6, 7, 8…)** | A4 DỌC | 1 ảnh/trang | Mỗi ảnh/trang riêng biệt |

**Quy tắc phân trang:**
- Nhóm 1: tối đa 4 ảnh/trang A4 ngang (2 cột × 2 hàng); nếu >4 ảnh thì tạo thêm trang
- Nhóm 2: tối đa 2 ảnh/trang A4 dọc (1 cột × 2 hàng); nếu >2 ảnh thì tạo thêm trang
- Nhóm 3: tối đa 4 ảnh/trang A4 dọc (2 cột × 2 hàng); nếu >4 ảnh thì tạo thêm trang
- Nhóm ≥ 4: mỗi ảnh 1 trang A4 dọc riêng biệt (kể cả từng trang của file PDF nhiều trang)

---

## Thiết kế trang

### Header
- Nền blue `(0, 112, 192)` — xanh blue tiêu chuẩn (đã đổi từ navy `(0,32,96)`)
- Logo PTI SOS góc trái (107px = 89×1.2, nền trong suốt)
- Tiêu đề: `Giám định Giấy tờ xe ô tô biển kiểm soát: {BKS}` — 16pt bold trắng, **căn giữa** vùng text
- GĐV: `Giám định viên: {tên} - Ngày: {ngày}` — 12pt trắng, **căn giữa** vùng text

### Caption
- Nền: **TRẮNG** `(255, 255, 255)`
- Chữ: **ĐEN** `(0, 0, 0)`, 11pt, căn giữa
- Đường kẻ xám `(200, 200, 200)` phân tách ảnh và caption

### Footer
- Nền trắng
- Trái: `Phòng Cứu hộ & Giám định tại khu vực Quảng Ninh` — 10pt xám
- Phải: `Trang X/Y` — 10pt italic đen, căn sát mép phải (cách MARGIN)

---

## Thông số kỹ thuật

```python
DPI = 150
PORTRAIT_W, PORTRAIT_H   = 1240, 1753   # A4 dọc
LANDSCAPE_W, LANDSCAPE_H = 1753, 1240   # A4 ngang
MARGIN    = 30
LOGO_PX   = 107          # 89 * 1.2 (tăng 20%)
HEADER_H  = 130
FOOTER_H  = 50
CAPTION_H = 38
BLUE  = (0, 112, 192)   # blue tiêu chuẩn (đổi từ navy (0,32,96))
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (200, 200, 200)
FONT_DIR   = r"C:\Windows\Fonts"   # Windows — arial.ttf / arialbd.ttf / ariali.ttf
FONT_LOCAL = "fonts/"              # Be Vietnam Pro kèm repo (Linux/hosting)
```

---

## Cách dùng

### A. Giao diện web (khuyến nghị)

```powershell
cd "d:\MCP\Claude Code\anh-giay-to-xe"
pip install -r requirements.txt
python app.py
```

Mở http://127.0.0.1:5000 → (1) chọn ảnh/PDF, (2) nhập biển số xe + GĐV + ngày,
(3) bấm **Tạo PDF giám định** → xem trước và tải về.

Giao diện tự nạp danh mục từ endpoint `/doc-types` (trả về `BUILTIN_DOC_TYPES` đã ghi đè
bởi `doc_types.json`), nên bảng danh mục và nhãn hạng mục trên từng file luôn khớp server.
Hạng mục tự thêm nằm ở `localStorage` và gửi kèm request qua trường `extra`.

### B. Chạy script trực tiếp

1. Cài thư viện: `pip install Pillow reportlab numpy PyMuPDF -q`
2. Đặt ảnh JPG/PNG + PDF vào thư mục `input\` (logo ở `assets\logo-ptisos.png`)
3. Chạy với tham số dòng lệnh:

```powershell
python gtx_gen.py --bks "14K-240.48" --gdv "Nguyễn Văn Hướng" --ngay "14/11/2026"
```

| Tham số | Mặc định | Ý nghĩa |
|---------|----------|---------|
| `--images` | `input\` | Thư mục ảnh JPG/PNG + PDF |
| `--logo` | `assets\logo-ptisos.png` | Logo PTI SOS |
| `--out` | `output\GiamDinh_GiayToXe.pdf` | File PDF xuất ra (tự chèn BKS vào tên) |
| `--bks` | *(trống)* | Biển số xe |
| `--gdv` | *(trống)* | Giám định viên |
| `--ngay` | *(trống)* | Ngày giám định |
| `--them` | — | Bổ sung hạng mục, lặp lại được: `--them "9=Biên bản hiện trường"` |

4. Output PDF xuất ra thư mục `output\`

---

## Cấu trúc code (`gtx_gen.py`)

| Thành phần | Vai trò |
|-----------|---------|
| `BUILTIN_DOC_TYPES` | Bảng tiền tố → tên hạng mục, bản dự phòng trong code |
| `load_doc_types(path)` | Nạp `doc_types.json` ghi đè lên bảng dự phòng → `DOC_TYPES` |
| `clean_doc_types(raw)` | Lọc tiền tố/tên hợp lệ, dùng cho cả JSON lẫn dữ liệu từ web |
| `sort_keys(keys)` | Sắp xếp tiền tố theo số (1.1 < 1.2 < 1.10 < 2 < 10) |
| `normalize_bks(text)` | Chuẩn hoá biển số xe người dùng nhập |
| `classify_images(paths, items=None)` | Gom ảnh theo nhóm, gán caption từ `DOC_TYPES` |
| `get_font(bold, italic, pt)` | Nạp font (có `lru_cache`), ưu tiên Arial → Be Vietnam Pro → DejaVu |
| `process_logo(path, px)` | Khử nền logo (pixel đen → alpha 0, pixel blue → trắng) |
| `draw_header` / `draw_footer` / `draw_caption` | Vẽ các thành phần cố định của trang |
| `paste_image_in_cell` | Resize (có `draft()` tăng tốc JPEG) + dán ảnh vào ô |
| `create_landscape_page` | Trang A4 ngang 2×2 (nhóm 1) |
| `create_portrait_page_2` | Trang A4 dọc 1×2 (nhóm 2) |
| `create_portrait_page_4` | Trang A4 dọc 2×2 (nhóm 3) |
| `create_portrait_page_1` | Trang A4 dọc 1 ảnh (nhóm ≥ 4) |
| `pdf_to_images` | PyMuPDF render PDF → JPG tạm ở 150 DPI |
| `main(..., extra_doc_types=None)` | Điều phối toàn bộ, xuất PDF; `extra_doc_types` là hạng mục thêm tại chỗ |

---

## Lưu ý quan trọng

- **Không dùng file Excel GTX nữa** — danh mục nằm trong `doc_types.json`
- **Bổ sung hạng mục**: sửa `doc_types.json` (dùng chung) hoặc ô "Thêm hạng mục" trên web (riêng máy)
- **Biển số xe là bắt buộc**, nhập thủ công (web) hoặc qua tham số `bks=` (script)
- **Caption**: Nền TRẮNG, chữ ĐEN (không dùng màu blue)
- **GĐV dòng 2**: Căn GIỮA theo vùng text (không căn trái)
- **Nhóm ≥ 4**: mỗi ảnh/trang PDF 1 trang riêng (kể cả PDF nhiều trang)
- **PDF**: Chuyển sang ảnh bằng PyMuPDF (`fitz`) trước khi xử lý
- **Logo**: Xử lý nền trong suốt (pixel đen → alpha=0) trước khi paste lên header
- **Tên file output**: `GiamDinh_GiayToXe_{BKS}.pdf`
- **Logo file**: `logo-ptisos.png` nằm trong thư mục `assets\`
- **Màu BLUE header**: `(0, 112, 192)` — KHÔNG dùng navy `(0, 32, 96)`
- **LOGO_PX**: 107 (= 89 × 1.2)
