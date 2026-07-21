# CLAUDE.md — Ghép ảnh Giám định Giấy Tờ Xe (GTX) PTI

## Mục đích

Tạo bộ ảnh giám định giấy tờ xe ô tô PTI chuẩn định dạng từ ảnh giấy tờ và file GTX Excel (.xlsx), xuất file PDF.

**Kích hoạt khi người dùng:**
- Upload ảnh giấy tờ xe + file GTX Excel (.xlsx) và gõ "tạo ảnh GTX"
- Yêu cầu "ghép ảnh GTX", "tạo bản ảnh giấy tờ xe", "tạo ảnh giám định giấy tờ"
- Có file GTX.xlsx kèm các ảnh số thứ tự 1_, 2_, 3_, 4_, 5_ và yêu cầu tạo ảnh
- Đề cập đến "bản ảnh GTX", "ảnh giấy tờ xe PTI", "ghép ảnh GTX"

---

## Đầu vào

### File ảnh (phân loại theo số đầu tên file)

Tên file dùng dấu chấm để đánh số thứ tự ảnh trong cùng nhóm: `{nhóm}.{số thứ tự}.jpg`  
Ví dụ: `1.1.jpg`, `1.2.jpg`, `2.1.jpg`, `3.jpg`

| Tên file | Nhóm | Caption mặc định |
|----------|------|-----------------|
| `1.*.jpg` (1.1, 1.2, 1.3, 1.4...) | 1 | "1. Đăng ký xe" |
| `2.*.jpg` (2.1, 2.2...) | 2 | "2. Bằng lái người điều khiển phương tiện" |
| `3.*.jpg` (3.1, 3.2, 3.3, 3.4...) | 3 | "3. Giấy chứng nhận đăng kiểm XCG" |
| `4.jpg` hoặc `4.pdf` | 4 | "4. Xác minh bằng lái" |
| `5.jpg` hoặc `5.pdf` | 5 | "5. Giấy chứng nhận bảo hiểm XCG" |
| `6.jpg` hoặc `6.pdf` | 6 | "6. Giấy chứng nhận bảo hiểm VCX" |

File PDF tự động chuyển sang ảnh bằng PyMuPDF (`pip install PyMuPDF`).
Caption thực tế đọc từ file Excel GTX (cột STT + Tên giấy tờ).

> **Quan trọng — Excel phải có đủ dòng cho MỌI nhóm ảnh.**
> Code khớp caption theo **key STT** (ví dụ ảnh `3.1.jpg` → tìm dòng STT `3.1` trong Excel).
> Nếu Excel **thiếu** dòng của nhóm nào (ví dụ có ảnh `3.1`–`3.4` nhưng Excel không có STT `3.x`),
> caption sẽ bị fallback thành `"Hạng mục 3.1"...` — **không phải lỗi code**, mà do thiếu dữ liệu.
> → Cách xử lý: **bổ sung dòng STT tương ứng vào GTX.xlsx** (STT + Tên giấy tờ), rồi chạy lại.

### File Excel GTX (.xlsx)

```
Row 1: (None, "Giấy tờ xe 14K-240.48")   ← lấy biển số xe
Row 2: ("Stt", "Tên giấy tờ")
Row 3+: (1, "Đăng ký xe"), (2, "Bằng lái..."), ...
```

### Tên Giám định viên (GĐV)
Lấy từ lệnh người dùng sau "GĐV:". Nếu không có → bỏ trống.

---

## Layout tự động theo nhóm số đầu tên file

| Nhóm | Layout | Số ảnh/trang | Ghi chú |
|------|--------|--------------|---------|
| **1** | A4 NGANG | 4 ảnh (2 cột × 2 hàng) | Tất cả ảnh nhóm 1.x ghép vào 1 trang ngang |
| **2** | A4 DỌC | 2 ảnh (1 cột × 2 hàng) | Tất cả ảnh nhóm 2.x ghép vào 1 trang dọc |
| **3** | A4 DỌC | 4 ảnh (2 cột × 2 hàng) | Tất cả ảnh nhóm 3.x ghép vào 1 trang dọc |
| **Khác (4, 5, 6...)** | A4 DỌC | 1 ảnh/trang | Mỗi ảnh/trang riêng biệt |

**Quy tắc phân trang:**
- Nhóm 1: tối đa 4 ảnh/trang A4 ngang (2 cột × 2 hàng); nếu >4 ảnh thì tạo thêm trang
- Nhóm 2: tối đa 2 ảnh/trang A4 dọc (1 cột × 2 hàng); nếu >2 ảnh thì tạo thêm trang
- Nhóm 3: tối đa 4 ảnh/trang A4 dọc (2 cột × 2 hàng); nếu >4 ảnh thì tạo thêm trang
- Nhóm khác (4, 5, 6...): mỗi ảnh 1 trang A4 dọc riêng biệt

---

## Thiết kế trang

### Header
- Nền blue `(0, 112, 192)` — xanh blue tiêu chuẩn (đã đổi từ navy `(0,32,96)`)
- Logo PTI SOS góc trái (107px = 89×1.2, nền trong suốt)
- Tiêu đề: `Giám định Giấy tờ xe xe ô tô biển kiểm soát: {BKS}` — 16pt bold trắng, **căn giữa** vùng text
- GĐV: `Giám định viên: {tên}` — 12pt trắng, **căn giữa** vùng text

### Caption
- Nền: **TRẮNG** `(255, 255, 255)`
- Chữ: **ĐEN** `(0, 0, 0)`, 11pt, căn giữa
- Đường kẻ xám `(200, 200, 200)` phân tách ảnh và caption

### Footer
- Nền trắng
- Trái: `Phòng Giám định và Cứu hộ tại Quảng Ninh` — 10pt xám
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
FONT_DIR = r"C:\Windows\Fonts"   # Windows — dùng arial.ttf / arialbd.ttf / ariali.ttf
```

---

## Thứ tự thực hiện (Windows)

1. Cài thư viện: `pip install Pillow openpyxl reportlab numpy PyMuPDF -q`
2. Đặt dữ liệu vào thư mục `input\` (ảnh JPG/PNG + PDF + GTX.xlsx + logo-ptisos.png)
3. Chỉnh `gdv=` và đường dẫn trong `gtx_gen.py`
4. Chạy: `python gtx_gen.py`
5. Output PDF xuất ra thư mục `output\`

---

## Code hoàn chỉnh (`/tmp/gtx_gen.py`)

```python
import openpyxl, re, os, io
from PIL import Image, ImageDraw, ImageFont
import numpy as np

DPI=150; PORTRAIT_W,PORTRAIT_H=1240,1753; LANDSCAPE_W,LANDSCAPE_H=1753,1240
MARGIN=30; LOGO_PX=89; HEADER_H=130; FOOTER_H=50; CAPTION_H=38
BLUE=(0,32,96); WHITE=(255,255,255); BLACK=(0,0,0); GRAY=(200,200,200)

def pt2px(pt): return int(pt*DPI/72)

def get_font(bold=False, italic=False, pt=12):
    px = pt2px(pt)
    paths = (['/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf',
               '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'] if bold else
              ['/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf',
               '/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf'] if italic else
              ['/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf',
               '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'])
    for p in paths:
        if os.path.exists(p):
            try: return ImageFont.truetype(p, px)
            except: pass
    return ImageFont.load_default()

def process_logo(logo_path, size_px):
    logo = Image.open(logo_path).convert('RGBA')
    data = np.array(logo)
    r,g,b,a = data[:,:,0],data[:,:,1],data[:,:,2],data[:,:,3]
    is_dark = (r<80)&(g<80)&(b<80)
    data[is_dark] = [0,0,0,0]
    is_blue = (r<60)&(g<60)&(b>100)&(~is_dark)
    data[is_blue] = [255,255,255,255]
    return Image.fromarray(data).resize((size_px,size_px), Image.LANCZOS)

def read_gtx_excel(path):
    wb = openpyxl.load_workbook(path); ws = wb.active; bks=""
    for row in ws.iter_rows(min_row=1,max_row=5,values_only=True):
        for cell in row:
            if cell and isinstance(cell,str) and 'Giấy tờ xe' in cell:
                parts=cell.strip().split(); bks=parts[-1] if parts else ""; break
        if bks: break
    items={}
    for row in ws.iter_rows(values_only=True):
        c0=row[0]; c1=row[1] if len(row)>1 else None
        if isinstance(c0,int) and c0>0 and c1 and isinstance(c1,str):
            items[c0]=str(c1).strip()
    return bks,items

def classify_images(image_paths,items):
    classified={}
    for path in image_paths:
        fname=os.path.basename(path); name_no_ext=os.path.splitext(fname)[0]
        m=re.match(r'^(\d+)',name_no_ext)
        if m:
            stt=int(m.group(1)); caption=f"{stt}. {items.get(stt,f'Hạng mục {stt}')}"
            if stt not in classified: classified[stt]=[]
            classified[stt].append((path,caption,name_no_ext))
    for stt in classified: classified[stt].sort(key=lambda x:x[2])
    return classified

def wrap_text(draw,text,font,max_w):
    words=text.split(); lines=[]; cur=""
    for w in words:
        test=(cur+" "+w).strip()
        bb=draw.textbbox((0,0),test,font=font)
        if bb[2]-bb[0]<=max_w: cur=test
        else:
            if cur: lines.append(cur)
            cur=w
    if cur: lines.append(cur)
    return lines

def draw_header(page,draw,W,HEADER_H,MARGIN,logo_px,logo_img,bks,gdv):
    draw.rectangle([0,0,W,HEADER_H],fill=BLUE)
    logo_y=(HEADER_H-logo_px)//2
    page.paste(logo_img,(MARGIN,logo_y),logo_img)
    text_x=MARGIN+logo_px+10; text_w=W-text_x-MARGIN
    font_title=get_font(bold=True,pt=16); font_gdv=get_font(bold=False,pt=12)
    title_lines=wrap_text(draw,f"Giám định Giấy tờ xe xe ô tô biển kiểm soát: {bks}",font_title,text_w)
    tlh=pt2px(16)+4; total_th=len(title_lines)*tlh
    gdv_h=pt2px(12)+4 if gdv else 0
    cur_y=(HEADER_H-total_th-gdv_h)//2
    for line in title_lines:
        bb=draw.textbbox((0,0),line,font=font_title)
        x=text_x+(text_w-(bb[2]-bb[0]))//2
        draw.text((x,cur_y),line,font=font_title,fill=WHITE); cur_y+=tlh
    if gdv:
        gdv_text=f"Giám định viên: {gdv}"
        bb=draw.textbbox((0,0),gdv_text,font=font_gdv)
        x=text_x+(text_w-(bb[2]-bb[0]))//2
        draw.text((x,cur_y),gdv_text,font=font_gdv,fill=WHITE)

def draw_footer(page,draw,W,H,FOOTER_H,MARGIN,page_num,total_pages):
    fy=H-FOOTER_H; draw.rectangle([0,fy,W,H],fill=WHITE)
    draw.line([0,fy,W,fy],fill=GRAY,width=1)
    font_f=get_font(bold=False,pt=10); font_fi=get_font(italic=True,pt=10)
    ty=fy+(FOOTER_H-pt2px(10))//2
    draw.text((MARGIN,ty),"Phòng Giám định và Cứu hộ tại Quảng Ninh",font=font_f,fill=(128,128,128))
    pt=f"Trang {page_num}/{total_pages}"
    bb=draw.textbbox((0,0),pt,font=font_fi)
    draw.text(((W-(bb[2]-bb[0]))//2,ty),pt,font=font_fi,fill=BLACK)

def draw_caption(page,draw,caption,cx,cy,cell_w,cell_h,CAPTION_H):
    cap_y=cy+cell_h-CAPTION_H
    draw.rectangle([cx,cap_y,cx+cell_w,cy+cell_h],fill=WHITE)
    draw.line([cx,cap_y,cx+cell_w,cap_y],fill=GRAY,width=1)
    font_cap=get_font(bold=False,pt=11)
    bb=draw.textbbox((0,0),caption,font=font_cap)
    draw.text((cx+(cell_w-(bb[2]-bb[0]))//2, cap_y+(CAPTION_H-(bb[3]-bb[1]))//2),
              caption,font=font_cap,fill=BLACK)

def paste_image_in_cell(page,img_path,cx,cy,cell_w,img_area_h):
    try:
        img=Image.open(img_path).convert('RGB'); iw,ih=img.size
        scale=min(cell_w/iw,img_area_h/ih); nw,nh=int(iw*scale),int(ih*scale)
        img_r=img.resize((nw,nh),Image.LANCZOS)
        page.paste(img_r,(cx+(cell_w-nw)//2, cy+(img_area_h-nh)//2))
    except Exception as e: print(f"Lỗi ảnh {img_path}: {e}")

def create_landscape_page(imgs,page_num,total,hinfo,logo_img):
    W,H=LANDSCAPE_W,LANDSCAPE_H; COLS,ROWS=2,2
    page=Image.new('RGB',(W,H),WHITE); draw=ImageDraw.Draw(page)
    draw_header(page,draw,W,HEADER_H,MARGIN,LOGO_PX,logo_img,hinfo['bks'],hinfo.get('gdv',''))
    draw_footer(page,draw,W,H,FOOTER_H,MARGIN,page_num,total)
    draw.rectangle([0,0,W-1,H-1],outline=GRAY,width=1)
    cw=(W-2*MARGIN)//COLS; ch=(H-HEADER_H-FOOTER_H)//ROWS; iah=ch-CAPTION_H
    for idx,(ip,cap) in enumerate(imgs[:COLS*ROWS]):
        col,row=idx%COLS,idx//COLS; cx=MARGIN+col*cw; cy=HEADER_H+row*ch
        draw.rectangle([cx,cy,cx+cw,cy+ch],outline=GRAY,width=1)
        paste_image_in_cell(page,ip,cx,cy,cw,iah)
        draw_caption(page,draw,cap,cx,cy,cw,ch,CAPTION_H)
    for idx in range(len(imgs),COLS*ROWS):
        col,row=idx%COLS,idx//COLS; cx=MARGIN+col*cw; cy=HEADER_H+row*ch
        draw.rectangle([cx,cy,cx+cw,cy+ch],outline=GRAY,width=1)
    return page

def create_portrait_page_3(imgs,page_num,total,hinfo,logo_img):
    W,H=PORTRAIT_W,PORTRAIT_H; COLS,ROWS=1,3
    page=Image.new('RGB',(W,H),WHITE); draw=ImageDraw.Draw(page)
    draw_header(page,draw,W,HEADER_H,MARGIN,LOGO_PX,logo_img,hinfo['bks'],hinfo.get('gdv',''))
    draw_footer(page,draw,W,H,FOOTER_H,MARGIN,page_num,total)
    draw.rectangle([0,0,W-1,H-1],outline=GRAY,width=1)
    cw=W-2*MARGIN; ch=(H-HEADER_H-FOOTER_H)//ROWS; iah=ch-CAPTION_H
    for idx,(ip,cap) in enumerate(imgs[:ROWS]):
        cx=MARGIN; cy=HEADER_H+idx*ch
        draw.rectangle([cx,cy,cx+cw,cy+ch],outline=GRAY,width=1)
        paste_image_in_cell(page,ip,cx,cy,cw,iah)
        draw_caption(page,draw,cap,cx,cy,cw,ch,CAPTION_H)
    for idx in range(len(imgs),ROWS):
        cx=MARGIN; cy=HEADER_H+idx*ch
        draw.rectangle([cx,cy,cx+cw,cy+ch],outline=GRAY,width=1)
    return page

def create_portrait_page_1(ip,cap,page_num,total,hinfo,logo_img):
    W,H=PORTRAIT_W,PORTRAIT_H
    page=Image.new('RGB',(W,H),WHITE); draw=ImageDraw.Draw(page)
    draw_header(page,draw,W,HEADER_H,MARGIN,LOGO_PX,logo_img,hinfo['bks'],hinfo.get('gdv',''))
    draw_footer(page,draw,W,H,FOOTER_H,MARGIN,page_num,total)
    draw.rectangle([0,0,W-1,H-1],outline=GRAY,width=1)
    cx=MARGIN; cy=HEADER_H; cw=W-2*MARGIN; ch=H-HEADER_H-FOOTER_H; iah=ch-CAPTION_H
    draw.rectangle([cx,cy,cx+cw,cy+ch],outline=GRAY,width=1)
    paste_image_in_cell(page,ip,cx,cy,cw,iah)
    draw_caption(page,draw,cap,cx,cy,cw,ch,CAPTION_H)
    return page

def main(excel_path, logo_path, image_dir, output_path, gdv=''):
    bks,items = read_gtx_excel(excel_path)
    image_paths = [os.path.join(image_dir,f) for f in os.listdir(image_dir)
                   if f.lower().endswith(('.jpg','.jpeg','.png')) and 'logo' not in f.lower()]
    classified = classify_images(image_paths, items)
    logo_img = process_logo(logo_path, LOGO_PX)
    hinfo = {'bks': bks, 'gdv': gdv}
    pages_info = []
    imgs_12 = []
    for stt in [1,2]:
        if stt in classified: imgs_12.extend(classified[stt])
    for i in range(0,max(len(imgs_12),1),4):
        chunk=imgs_12[i:i+4]
        if chunk: pages_info.append(('landscape',chunk))
    imgs_34 = []
    for stt in [3,4]:
        if stt in classified: imgs_34.extend(classified[stt])
    for i in range(0,max(len(imgs_34),1),3):
        chunk=imgs_34[i:i+3]
        if chunk: pages_info.append(('portrait3',chunk))
    if 5 in classified:
        for item in classified[5]: pages_info.append(('portrait1',[item]))
    total=len(pages_info)
    from reportlab.pdfgen import canvas as rlc
    from reportlab.lib.units import cm
    from reportlab.lib.utils import ImageReader
    c=rlc.Canvas(output_path)
    for p_idx,(ptype,data) in enumerate(pages_info,1):
        if ptype=='landscape':
            pg=create_landscape_page([(d[0],d[1]) for d in data],p_idx,total,hinfo,logo_img); pw,ph=29.7*cm,21*cm
        elif ptype=='portrait3':
            pg=create_portrait_page_3([(d[0],d[1]) for d in data],p_idx,total,hinfo,logo_img); pw,ph=21*cm,29.7*cm
        else:
            d=data[0]; pg=create_portrait_page_1(d[0],d[1],p_idx,total,hinfo,logo_img); pw,ph=21*cm,29.7*cm
        c.setPageSize((pw,ph))
        buf=io.BytesIO(); pg.save(buf,format='JPEG',quality=92); buf.seek(0)
        c.drawImage(ImageReader(buf),0,0,pw,ph); c.showPage()
    c.save()
    print(f"✅ Xuất: {output_path}")

if __name__=='__main__':
    gdv='Nguyễn Văn Hướng'  # cập nhật từ lệnh người dùng
    main(
        excel_path='/mnt/user-data/uploads/GTX.xlsx',
        logo_path='/mnt/user-data/uploads/logo-ptisos.png',
        image_dir='/mnt/user-data/uploads',
        output_path='/mnt/user-data/outputs/GiamDinh_GiayToXe_14K-240.48.pdf',
        gdv=gdv
    )
```

---

## Lưu ý quan trọng

- **Caption**: Nền TRẮNG, chữ ĐEN (không dùng màu blue)
- **GĐV dòng 2**: Căn GIỮA theo vùng text (không căn trái)
- **STT 3 và 4**: Luôn GỘP CHUNG vào 1 mảng `imgs_34`, phân trang 3 ảnh/trang, layout 1 cột × 3 hàng
- **STT 5, 6**: Mỗi ảnh/trang PDF 1 cột (kể cả các trang PDF nhiều trang)
- **PDF**: Chuyển sang ảnh bằng PyMuPDF (`fitz`) trước khi xử lý
- **Logo**: Xử lý nền trong suốt (pixel đen → alpha=0) trước khi paste lên header
- **Tên file output**: `GiamDinh_GiayToXe_{BKS}.pdf`
- **Logo file**: `logo-ptisos.png` nằm trong thư mục `input\`
- **Font Windows**: `C:\Windows\Fonts\arial.ttf`, `arialbd.ttf`, `ariali.ttf`
- **Màu BLUE header**: `(0, 112, 192)` — KHÔNG dùng navy `(0, 32, 96)`
- **LOGO_PX**: 107 (= 89 × 1.2)
