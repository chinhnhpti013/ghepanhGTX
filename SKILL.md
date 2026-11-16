# SKILL.md — Kỹ năng tạo ảnh GTX (Giám định Giấy Tờ Xe) PTI

## Mô tả

Script `gtx_gen.py` tạo PDF giám định giấy tờ xe PTI từ ảnh JPG/PNG và file PDF giấy tờ.
Caption lấy từ danh mục `doc_types.json` (không dùng file Excel). Danh mục bổ sung được
bằng 3 cách: sửa `doc_types.json`, ô "Thêm hạng mục" trên web, hoặc tham số `--them`.
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
  gtx_gen.py            # Script chinh (bo anh giay to)
  bien_ban.py           # Bien ban giam dinh BM.PTI.CG.02.08a (PDF + ky tay)
  doc_types.json        # Danh muc tien to -> ten hang muc (sua de bo sung)
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

Mo http://127.0.0.1:5000:

- **Man hinh 1** — chon anh/PDF, nhap **Bien so xe** (bat buoc), GDV, ngay giam dinh,
  **Ngay ton that**, **Dia diem ton that**, va khoi "Thong tin them cho Bien ban giam dinh"
  (lai xe/chu xe, SDT, so GPLX, so ho so, gara, phong, y kien) → bam **Tao PDF giam dinh**.
- **Man hinh 2** — 2 tab:
  - *Ban anh giay to*: PDF bo anh, xem truoc va tai ve.
  - *Bien ban giam dinh*: bien ban mau `BM.PTI.CG.02.08a`, xem truoc bang anh tung trang,
    xac nhan thong tin, ky tay 2 o (lai xe/chu xe + GDV), tai ve PDF da ky va file
    kiem chung `.json`.

### Script truc tiep

```powershell
cd "d:\MCP\Claude Code\anh-giay-to-xe"
python gtx_gen.py --bks "14K-240.48" --gdv "Nguyen Van Huong" --ngay "14/11/2026"
```

Tham so: `--images` (mac dinh `input\`), `--logo` (mac dinh `assets\logo-ptisos.png`),
`--out` (mac dinh `output\GiamDinh_GiayToXe.pdf`), `--bks`, `--gdv`, `--ngay`,
`--them TIENTO=TEN` (bo sung hang muc, lap lai duoc).
Xem day du: `python gtx_gen.py --help`.

---

## Bien ban giam dinh (`bien_ban.py`)

Dung PDF theo dung mau PTI **BM.PTI.CG.02.08a** (Quy trinh giam dinh bao hiem xe co gioi):
letterhead PTI, "BIEN BAN GIAM DINH THIET HAI", thanh phan tham gia, thong tin ton that,
bang 10 dong hang muc giam dinh, y kien cac ben, don vi sua chua, 2 o ky.

- Ban chua ky: watermark cheo "BAN XEM TRUOC — CHUA KY".
- Ky tay: HTML5 Canvas + Pointer Events (ngon tay / but / chuot), moi o co nut *Xoa / Ky lai*,
  net ky luu theo toa do nen khong mat khi xoay may; xuat PNG nen trong suot da cat sat net.
- Bat buoc truoc khi ky: du 2 chu ky + tich o "Toi da doc va dong y noi dung bien ban".
- Dau vet kiem chung in cuoi bien ban da ky: ma ho so, thoi diem ky (gio VN/UTC), gio thiet bi,
  toa do GPS, thiet bi/trinh duyet, IP, ma bam SHA-256 cua du lieu ky. Tai duoc file
  `*_kiemchung.json` kem ma bam cua chinh file PDF.

Dung thu bo cuc: `python bien_ban.py` → `output\BienBan_Thu.pdf`.

Endpoint: `POST /bien-ban` (ban chua ky), `POST /bien-ban/ky` (ban da ky) — deu tra JSON
`{name, pdf(base64), pages[PNG base64], ...}`.

> Sua noi dung mau: chi sua ham `body_flowables()` trong `bien_ban.py`.

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

### Bo sung hang muc — 3 cach

| Cach | Pham vi | Lam the nao |
|------|---------|-------------|
| `doc_types.json` | Toan du an | Them dong vao muc `items`, restart server |
| O "Them hang muc" tren web | Rieng trinh duyet do | Nhap Tien to + Ten, bam "+ Them hang muc" (luu localStorage) |
| `--them` khi chay script | Mot lan chay | `--them "9=Bien ban hien truong"` (lap lai duoc) |

Tien to hop le: `9` hoac `3.7`. Chu so dau = nhom, quyet dinh layout.
Trung tien to co san -> ten moi ghi de ten cu.

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
| Ngay / dia diem ton that | Khong co | O nhap tren man hinh 1 (khong bat buoc) | 2026-11-16 |
| Bien ban giam dinh | Khong co | Tab moi o man hinh 2: mau BM.PTI.CG.02.08a + ky tay + dau vet kiem chung | 2026-11-16 |
| CLI | Sua tay block `__main__` | Tham so `--images/--logo/--out/--bks/--gdv/--ngay` | 2026-11-14 |
| Goi skill `.skill` | Code dan inline trong SKILL.md | Bundle `scripts/gtx_gen.py` + `fonts/` | 2026-11-14 |
| O Ngay giam dinh | `<input type=text>` | `<input type=date>` + nut "Hom nay" | 2026-11-14 |
| Danh muc tien to | Hard-code trong `gtx_gen.py` | `doc_types.json` + them tren web + `--them` | 2026-11-14 |

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
