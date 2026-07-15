# SKILL.md — Kỹ năng tạo ảnh GTX (Giám định Giấy Tờ Xe) PTI

## Mô tả

Script `gtx_gen.py` tạo PDF giám định giấy tờ xe PTI từ ảnh JPG/PNG và file PDF giấy tờ, đọc thông tin từ file GTX Excel.

---

## Cài đặt (Windows)

```powershell
pip install Pillow openpyxl reportlab numpy PyMuPDF -q
```

---

## Cấu trúc thư mục

```
anh-giay-to-xe\
  input\
    1.1.jpg, 1.2.jpg     # STT 1 - Dang ky xe
    2.1.jpg, 2.2.jpg     # STT 2 - Bang lai
    3.1.jpg, 3.2.jpg     # STT 3 - Dang kiem
    4.jpg                # STT 4 - Xac minh bang lai
    5.pdf                # STT 5 - Bao hiem XCG
    6.pdf                # STT 6 - Bao hiem VCX
    GTX.xlsx             # File Excel thong tin giam dinh
    logo-ptisos.png      # Logo PTI SOS
  output\
    GiamDinh_GiayToXe_{BKS}.pdf   # Output
  gtx_gen.py            # Script chinh
```

---

## Chay script

```powershell
cd "d:\MCP\Claude Code\anh-giay-to-xe"
python gtx_gen.py
```

De thay doi GDV hoac duong dan, sua phan `if __name__ == "__main__":` trong `gtx_gen.py`.

---

## Hang muc thay doi

| Hang muc | Gia tri cu | Gia tri moi | Ngay |
|----------|-----------|------------|------|
| Mau BLUE header | `(0, 32, 96)` navy | `(0, 112, 192)` blue | 2026-05-28 |
| LOGO_PX | 89px | 107px (+20%) | 2026-05-28 |
| Ho tro PDF | Khong | Co (PyMuPDF) | 2026-05-28 |
| STT 6 | Khong xu ly | Portrait 1 anh/trang | 2026-05-28 |
| Font | Linux paths | Windows `C:\Windows\Fonts\` | 2026-05-28 |
| Thu muc du lieu | `/mnt/user-data/uploads` | `input\` | 2026-05-28 |
| So trang footer | Can giua | Ngoai cung ben PHAI | 2026-06-09 |

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

## Layout

| STT | Layout | So anh/trang |
|-----|--------|-------------|
| 1, 2 | A4 NGANG | 4 anh (2 cot x 2 hang) |
| 3, 4 (gop chung) | A4 DOC | 3 anh (1 cot x 3 hang) |
| 5, 6 | A4 DOC | 1 anh/trang |

---

## Xu ly dac biet

- **PDF -> anh**: Dung `fitz.open()` (PyMuPDF), render 150 DPI, luu JPG tam
- **Bien so xe**: Doc bang regex `\d+[A-Z]-\d+[\.\d]*` tu Excel
- **Logo**: Pixel den -> alpha=0; pixel blue -> trang, de trong suot tren nen xanh
- **Caption**: Nen TRANG, chu DEN, khong dung mau blue
