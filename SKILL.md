# SKILL.md — Kỹ năng tạo ảnh GTX (Giám định Giấy Tờ Xe) PTI

## Mô tả

Script `gtx_gen.py` tạo PDF giám định giấy tờ xe PTI từ ảnh JPG/PNG và file PDF giấy tờ.
Caption lấy từ bảng danh mục `DOC_TYPES` định nghĩa sẵn trong script (không dùng file Excel).
Biển số xe, giám định viên, ngày giám định do người dùng nhập.

---

## Cài đặt (Windows)

```powershell
pip install Pillow reportlab numpy PyMuPDF Flask -q
```

---

## Cấu trúc thư mục

```
anh-giay-to-xe\
  input\
    1.1.jpg, 1.2.jpg     # Dang ky xe mat truoc / mat sau
    1.3.jpg, 1.4.jpg     # Bang lai mat truoc / mat sau
    1.5.jpg, 1.6.jpg     # Can cuoc cong dan lai xe
    2.1.jpg, 2.2.jpg     # Dang kiem A5 mat truoc / mat sau
    2.3.jpg, 2.4.jpg     # Bao hiem A5 mat truoc / mat sau
    3.1.jpg ... 3.6.jpg  # Xac minh bang lai
    4.pdf                # Giay chung nhan bao hiem A4
    5.jpg                # Xac minh thanh toan phi bao hiem
    6.jpg                # Giay chung nhan kiem dinh XCG A4
    7.jpg                # Bien ban ban giao xe moi
    8.jpg                # Giay xac nhan quyen thu huong Ngan hang
  assets\
    logo-ptisos.png      # Logo PTI SOS
  fonts\                 # Be Vietnam Pro (du phong cho Linux/hosting)
  output\
    GiamDinh_GiayToXe_{BKS}.pdf   # Output
  gtx_gen.py            # Script chinh
  app.py                # Web server Flask
  index.html            # Giao dien web
```

---

## Chay

### Web (khuyen nghi)

```powershell
cd "d:\MCP\Claude Code\anh-giay-to-xe"
python app.py
```

Mo http://127.0.0.1:5000 → chon anh/PDF → nhap **Bien so xe** (bat buoc), GDV, ngay → Tao PDF.

### Script truc tiep

```powershell
cd "d:\MCP\Claude Code\anh-giay-to-xe"
python gtx_gen.py --bks "14K-240.48" --gdv "Nguyen Van Huong" --ngay "14/11/2026"
```

Tham so: `--images` (mac dinh `input\`), `--logo` (mac dinh `assets\logo-ptisos.png`),
`--out` (mac dinh `output\GiamDinh_GiayToXe.pdf`), `--bks`, `--gdv`, `--ngay`.
Xem day du: `python gtx_gen.py --help`.

---

## Danh muc tien to mac dinh (`DOC_TYPES`)

| Tien to | Ten hang muc | Layout |
|---------|--------------|--------|
| 1.1 | Dang ky xe mat truoc | 4 anh/trang · A4 ngang |
| 1.2 | Dang ky xe mat sau | 4 anh/trang · A4 ngang |
| 1.3 | Bang lai mat truoc | 4 anh/trang · A4 ngang |
| 1.4 | Bang lai mat sau | 4 anh/trang · A4 ngang |
| 1.5 | Can cuoc cong dan lai xe | 4 anh/trang · A4 ngang |
| 1.6 | Can cuoc cong dan lai xe | 4 anh/trang · A4 ngang |
| 2.1 | Giay chung nhan dang kiem A5 mat truoc | 2 anh/trang · A4 doc |
| 2.2 | Giay chung nhan dang kiem A5 mat sau | 2 anh/trang · A4 doc |
| 2.3 | Giay chung nhan bao hiem A5 mat truoc | 2 anh/trang · A4 doc |
| 2.4 | Giay chung nhan bao hiem A5 mat sau | 2 anh/trang · A4 doc |
| 3.1 – 3.6 | Xac minh bang lai | 4 anh/trang · A4 doc |
| 4 | Giay chung nhan bao hiem A4 | 1 anh/trang · A4 doc |
| 5 | Xac minh thanh toan phi bao hiem | 1 anh/trang · A4 doc |
| 6 | Giay chung nhan kiem dinh XCG A4 | 1 anh/trang · A4 doc |
| 7 | Bien ban ban giao xe moi | 1 anh/trang · A4 doc |
| 8 | Giay xac nhan quyen thu huong Ngan hang | 1 anh/trang · A4 doc |

Them/sua hang muc: chinh `DOC_TYPES` trong `gtx_gen.py` (va `DOC_TYPES_FALLBACK` trong `index.html`).

---

## Hang muc thay doi

| Hang muc | Gia tri cu | Gia tri moi | Ngay |
|----------|-----------|------------|------|
| Mau BLUE header | `(0, 32, 96)` navy | `(0, 112, 192)` blue | 2026-05-28 |
| LOGO_PX | 89px | 107px (+20%) | 2026-05-28 |
| Ho tro PDF | Khong | Co (PyMuPDF) | 2026-05-28 |
| Font | Linux paths | Windows `C:\Windows\Fonts\` + fonts/ repo | 2026-05-28 |
| Thu muc du lieu | `/mnt/user-data/uploads` | `input\` | 2026-05-28 |
| So trang footer | Can giua | Ngoai cung ben PHAI | 2026-06-09 |
| Layout nhom 3 | A4 doc, 2 anh (1x2) | A4 doc, 4 anh (2x2) | 2026-07-17 |
| Nguon danh muc | File `GTX.xlsx` (openpyxl) | Bang `DOC_TYPES` trong code | 2026-11-14 |
| Bien so xe | Doc tu Excel | Nguoi dung nhap (`--bks` / o tren web) | 2026-11-14 |
| CLI | Sua tay block `__main__` | Tham so `--images/--logo/--out/--bks/--gdv/--ngay` | 2026-11-14 |
| Goi skill `.skill` | Code dan inline trong SKILL.md | Bundle `scripts/gtx_gen.py` + `fonts/` | 2026-11-14 |

---

## Thong so ky thuat

```python
DPI = 150
PORTRAIT_W, PORTRAIT_H   = 1240, 1753   # A4 doc
LANDSCAPE_W, LANDSCAPE_H = 1753, 1240   # A4 ngang
MARGIN    = 30
LOGO_PX   = 107          # 89 * 1.2
HEADER_H  = 130
FOOTER_H  = 50
CAPTION_H = 38
BLUE  = (0, 112, 192)    # blue tieu chuan
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (200, 200, 200)
FONT_DIR = r"C:\Windows\Fonts"
```

---

## Layout theo nhom

| Nhom | Layout | So anh/trang |
|------|--------|-------------|
| 1 | A4 NGANG | 4 anh (2 cot x 2 hang) |
| 2 | A4 DOC | 2 anh (1 cot x 2 hang) |
| 3 | A4 DOC | 4 anh (2 cot x 2 hang) |
| >= 4 | A4 DOC | 1 anh/trang |

---

## Xu ly dac biet

- **PDF -> anh**: Dung `fitz.open()` (PyMuPDF), render 150 DPI, luu JPG tam
- **Bien so xe**: `normalize_bks()` loc bang regex `\d{2}[A-Z]{1,2}-?\d{3,5}\.?\d*` tu chuoi nhap
- **Logo**: Pixel den -> alpha=0; pixel blue -> trang, de trong suot tren nen xanh
- **Caption**: Nen TRANG, chu DEN, khong dung mau blue
- **Tien to la**: Lay ten muc gan nhat phia truoc cung nhom, neu khong co thi `"Hang muc {key}"`
- **Endpoint `/doc-types`**: Tra ve `DOC_TYPES` cho giao dien web dong bo voi code
