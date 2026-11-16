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

| Thông tin | Nguồn | Bắt buộc | Dùng cho |
|-----------|-------|----------|----------|
| Biển số xe (BKS) | Ô "Biển số xe" trên web, hoặc tham số `bks=` khi chạy script | ✅ | Bộ ảnh + Biên bản |
| Giám định viên | Ô "Giám định viên", hoặc `gdv=` | — | Bộ ảnh + Biên bản |
| Ngày giám định | Ô "Ngày giám định", hoặc `ngay=` | — | Bộ ảnh + Biên bản |
| **Ngày tổn thất** | Ô "Ngày tổn thất" (date picker) | — | Biên bản |
| **Địa điểm tổn thất** | Ô "Địa điểm tổn thất" | — | Biên bản |
| **Tên lái / chủ xe** | Ô "Tên lái / chủ xe" | — | Biên bản |
| **SĐT lái / chủ xe** | Ô "SĐT lái / chủ xe" | — | Biên bản |

BKS được chuẩn hoá bằng `normalize_bks()` (regex `\d{2}[A-Z]{1,2}-?\d{3,5}\.?\d*`),
dùng cho tiêu đề mỗi trang và tên file output `GiamDinh_GiayToXe_{BKS}.pdf`.

### 3. Thông tin thêm cho Biên bản giám định (khối gập trên web, đều không bắt buộc)

Số GPLX · SĐT giám định viên · Số hồ sơ ·
Gara / Địa điểm giám định · Phòng / Khu vực giám định · Ý kiến của các bên.

> Các trường này chỉ dùng cho **Biên bản giám định** (mục riêng bên dưới), không
> ảnh hưởng bộ ảnh giấy tờ.

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

**Màn hình 1 — nhập liệu:** mở http://127.0.0.1:5000 → (1) chọn ảnh/PDF, (2) nhập biển số
xe + GĐV + ngày giám định + ngày/địa điểm tổn thất (và khối "Thông tin thêm cho Biên bản
giám định" nếu cần), (3) bấm **Tạo PDF giám định**.

**Màn hình 2 — kết quả, 2 tab:**
- **Bản ảnh giấy tờ** — PDF bộ ảnh như trước, xem trước và tải về.
- **Biên bản giám định** — biên bản mẫu `BM.PTI.CG.02.08a`, xem trước, ký tay và tải về
  (xem mục "Biên bản giám định" bên dưới).

Biên bản được dựng sẵn ngay khi tạo xong bộ ảnh, nên bấm sang tab là thấy luôn; trang
cũng tự cuộn tới vùng xem trước. Chạm vào ảnh từng trang để mở cỡ lớn.

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

## Biên bản giám định (mẫu `BM.PTI.CG.02.08a`)

Màn hình 2, tab **Biên bản giám định** dựng bản PDF theo đúng mẫu PTI
*Quy trình giám định bảo hiểm xe cơ giới – BM.PTI.CG.02.08a*:

```
[logo PTI] TỔNG CÔNG TY CỔ PHẦN BẢO HIỂM BƯU ĐIỆN / Số 95, Trần Thái Tông… / Tel: 1900545475
                       BIÊN BẢN GIÁM ĐỊNH THIỆT HẠI
Hôm nay, ngày {ngay} tại : {dia_diem_gd}
Chúng tôi gồm có:
  1/ {gdv}        GĐV {phong}, SĐT: {sdt_gdv}
  2 {chu_xe}      là Đại diện: Chủ xe/lái xe BKS : {bks} , SĐT {sdt_chu_xe}
Giám định thiệt hại xe ô tô BKS {bks} bị tổn thất ngày : {ngay_ton_that}
Tại : {dia_diem_ton_that}
1. Thông tin tai nạn : Theo Thông báo tai nạn và yêu cầu bồi thường
2. Hạng mục giám định : (Theo các phụ lục đính kèm)   → bảng 10 dòng để trống
3. Ý kiến của các bên tham gia giám định:  {y_kien} hoặc dòng kẻ chấm
4. Đơn vị sửa chữa: Gara {dia_diem_gd} / Đ/c … SĐT liên hệ …
        LÁI XE/CHỦ XE                GIÁM ĐỊNH VIÊN PTI     ← vị trí chèn chữ ký
[DẤU VẾT KIỂM CHỨNG CHỮ KÝ ĐIỆN TỬ]                        ← chỉ có ở bản đã ký
```

Bản chưa ký có watermark chéo **"BẢN XEM TRƯỚC — CHƯA KÝ"**; bản đã ký bỏ watermark.
Xem trước hiển thị bằng **ảnh từng trang** (không dùng `<iframe>` PDF) để chạy được cả
trên trình duyệt điện thoại — nơi biên bản thường được ký tại hiện trường.

### Ký tay (signature pad)

- Hai ô ký riêng: **Lái xe/Chủ xe** và **Giám định viên PTI**, mỗi ô có nút *Xoá / Ký lại*.
- HTML5 Canvas + Pointer Events (ngón tay, bút cảm ứng, chuột), `touch-action: none`.
- Nét ký được lưu theo toạ độ nên vẫn còn khi xoay máy / bật bàn phím ảo (canvas vẽ lại).
- Xuất **PNG nền trong suốt**, đã cắt sát nét ký, rồi chèn đúng vị trí ô ký của mẫu.
- Trước khi ký: khối **"Xác nhận thông tin trước khi ký"** hiện lại BKS, họ tên, số GPLX,
  ngày/địa điểm tổn thất… và ô tích bắt buộc *"Tôi đã đọc và đồng ý nội dung biên bản"*.

### Dấu vết kiểm chứng

In ở cuối biên bản đã ký và tải về được dưới dạng `*_kiemchung.json`:

| Mục | Nguồn |
|-----|-------|
| Mã hồ sơ | ô "Số hồ sơ" |
| Thời điểm ký (giờ VN / UTC) | đồng hồ máy chủ |
| Giờ trên thiết bị người ký | trình duyệt |
| Toạ độ GPS | `navigator.geolocation` (từ chối vẫn ký được, ghi rõ lý do) |
| Thiết bị / trình duyệt | User-Agent + nền tảng + độ phân giải |
| Địa chỉ IP phiên ký | `X-Forwarded-For` hoặc `remote_addr` |
| Mã kiểm chứng (SHA-256) | băm toàn bộ dữ liệu ký — in lên biên bản |
| Mã băm file PDF đã ký | SHA-256 của file trả về — chỉ có trong JSON/giao diện |

### Endpoint

| Endpoint | Vào | Ra |
|----------|-----|-----|
| `POST /bien-ban` | các trường biên bản | JSON `{name, pdf(base64), pages[PNG base64], file_hash}` — bản chưa ký |
| `POST /bien-ban/ky` | thêm `sig_khach`, `sig_gdv` (dataURL PNG), `dong_y=1`, `audit` (JSON) | JSON `{name, pdf, pages, audit}` — bản đã ký |

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

## Cấu trúc code (`bien_ban.py`)

| Thành phần | Vai trò |
|-----------|---------|
| `register_fonts()` / `styles()` | Font Times New Roman → Arial → Be Vietnam Pro → DejaVu; bộ style của biên bản |
| `clean_text` / `esc` / `ten_gara` | Làm sạch, escape chuỗi nhận từ web; tránh in "Gara Gara…" |
| `decode_signature(data_url)` | Giải mã dataURL chữ ký, chỉ nhận PNG hợp lệ ≤ 3 MB |
| `logo_png(path)` | Đổi chữ "pti" trắng của logo sang navy để dùng trên nền giấy |
| `make_page_decorator(draft)` | Footer mã biểu mẫu + watermark "BẢN XEM TRƯỚC — CHƯA KÝ" |
| `letterhead` / `body_flowables` | **Nội dung mẫu BM.PTI.CG.02.08a — sửa ở đây khi mẫu thay đổi** |
| `hang_muc_table` | Bảng "2. Hạng mục giám định" 2 tầng tiêu đề, 10 dòng |
| `signature_flowables` | Hai ô ký, chèn ảnh PNG chữ ký khi đã ký |
| `audit_flowables` / `payload_hash` | Khối dấu vết kiểm chứng và mã băm SHA-256 của dữ liệu ký |
| `build(...)` | Dựng PDF, trả `(đường dẫn, payload_hash, file_hash)` |

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

### Riêng Biên bản giám định (`bien_ban.py`)

- **Mẫu chuẩn**: `BM.PTI.CG.02.08a` — sửa nội dung ở `body_flowables()`, không sửa chỗ khác
- **Bản chưa ký** luôn có watermark "BẢN XEM TRƯỚC — CHƯA KÝ"; ký xong watermark biến mất
- **Chữ ký**: PNG nền trong suốt, đã cắt sát nét; server chỉ nhận PNG hợp lệ ≤ 3 MB
- **Bắt buộc khi ký**: đủ 2 chữ ký + ô tích "đã đọc và đồng ý", thiếu một thứ là từ chối
- **Xem trước bằng ảnh PNG** chứ không nhúng `<iframe>` PDF — để chạy trên điện thoại
- **Mã kiểm chứng in trên biên bản** = SHA-256 của dữ liệu ký; **mã băm file PDF** nằm ở
  JSON kiểm chứng (không in lên PDF vì sẽ tự thay đổi chính nó)
- **Font biên bản**: Times New Roman cho giống mẫu Word, thiếu thì lùi về Arial/Be Vietnam Pro
- **Logo trên biên bản**: đổi chữ "pti" trắng sang navy `(31, 59, 115)` để thấy trên nền giấy
