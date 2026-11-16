"""
Dựng PDF **BIÊN BẢN GIÁM ĐỊNH THIỆT HẠI** theo mẫu PTI `BM.PTI.CG.02.08a`,
kèm khối ký tay (chữ ký PNG nền trong suốt) và dấu vết kiểm chứng.

Dùng ReportLab (platypus) nên chữ là vector: nét, chọn/copy/tìm được trong PDF.

Bố cục bám mẫu BM.PTI.CG.02.08a:
    [logo PTI + tên, địa chỉ, điện thoại tổng công ty]
    BIÊN BẢN GIÁM ĐỊNH THIỆT HẠI
    Hôm nay, ngày {ngay} tại : {dia_diem_gd}
    Chúng tôi gồm có:
      1/ {gdv}                GĐV {phong}, SĐT: {sdt_gdv}
      2 {chu_xe}              là Đại diện: Chủ xe/lái xe BKS : {bks} , SĐT {sdt_chu_xe}
    Giám định thiệt hại xe ô tô BKS {bks} bị tổn thất ngày : {ngay_ton_that}
    Tại : {dia_diem_ton_that}
    1. Thông tin tai nạn : Theo Thông báo tai nạn và yêu cầu bồi thường
    2. Hạng mục giám định : (Theo các phụ lục đính kèm)   → bảng 10 dòng
    3. Ý kiến của các bên tham gia giám định:
    4. Đơn vị sửa chữa: Gara {dia_diem_gd} / Đ/c ... SĐT liên hệ ...
    [2 đoạn in nghiêng] + LÁI XE/CHỦ XE | GIÁM ĐỊNH VIÊN PTI
    [DẤU VẾT KIỂM CHỨNG CHỮ KÝ ĐIỆN TỬ — chỉ in ở bản đã ký]

Sửa nội dung mẫu: xem hàm `body_flowables()`. Khung trang (logo, footer mã
biểu mẫu, watermark bản chưa ký), khối ký và dấu vết kiểm chứng nằm ở các hàm
riêng, không phụ thuộc nội dung.
"""
import base64
import hashlib
import io
import json
import os
import re
import unicodedata
from datetime import datetime, timedelta, timezone
from xml.sax.saxutils import escape as xml_escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image as RLImage, KeepTogether, PageTemplate,
    Paragraph, Spacer, Table, TableStyle,
)

BASE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR_WIN = r"C:\Windows\Fonts"
FONT_LOCAL = os.path.join(BASE, "fonts")

MA_BIEU_MAU = "BM.PTI.CG.02.08a"
QUY_TRINH = "Quy trình giám định bảo hiểm xe cơ giới"
CONG_TY = "TỔNG CÔNG TY CỔ PHẦN BẢO HIỂM BƯU ĐIỆN"
DIA_CHI = "Số 95, Trần Thái Tông, Cầu Giấy, Hà nội"
LIEN_HE = "Tel: 1900545475   Website : pti.com.vn"
PHONG_MAC_DINH = "Cứu hộ & Giám định khu vực Quảng Ninh"

NAVY = colors.Color(31 / 255, 59 / 255, 115 / 255)      # xanh logo PTI
GRAY_LINE = colors.Color(120 / 255, 120 / 255, 120 / 255)
GRAY_TEXT = colors.Color(90 / 255, 107 / 255, 123 / 255)
BOX_BG = colors.Color(244 / 255, 246 / 255, 249 / 255)

PAGE_W, PAGE_H = A4
MARGIN_X = 1.9 * cm
MARGIN_TOP = 1.4 * cm
MARGIN_BOTTOM = 1.8 * cm
TZ_VN = timezone(timedelta(hours=7))

# Giới hạn an toàn cho dữ liệu nhận từ trình duyệt
MAX_SIG_BYTES = 3 * 1024 * 1024      # 3 MB mỗi ảnh chữ ký
MAX_TEXT_LEN = 300                   # cắt mọi chuỗi hiển thị
SO_DONG_HANG_MUC = 10                # bảng hạng mục giám định của mẫu: 10 dòng

# ---------------------------------------------------------------------------
# Font — ưu tiên Times New Roman (giống mẫu Word) → Arial → Be Vietnam Pro → DejaVu
# ---------------------------------------------------------------------------
FONTS = {"reg": "Times-Roman", "bold": "Times-Bold", "italic": "Times-Italic",
         "bolditalic": "Times-BoldItalic"}
_FONTS_READY = False

_FONT_CANDIDATES = {
    "reg": ("GTXBB", ["times.ttf", "arial.ttf"], "BeVietnamPro-Regular.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),
    "bold": ("GTXBB-Bold", ["timesbd.ttf", "arialbd.ttf"], "BeVietnamPro-Bold.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"),
    "italic": ("GTXBB-Italic", ["timesi.ttf", "ariali.ttf"], "BeVietnamPro-Regular.ttf",
               "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"),
    "bolditalic": ("GTXBB-BoldItalic", ["timesbi.ttf", "arialbi.ttf"],
                   "BeVietnamPro-Bold.ttf",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSerif-BoldItalic.ttf"),
}


def register_fonts():
    """Đăng ký font Unicode cho ReportLab (chỉ chạy một lần mỗi tiến trình)."""
    global _FONTS_READY
    if _FONTS_READY:
        return FONTS
    for slot, (name, win_files, local_file, linux_path) in _FONT_CANDIDATES.items():
        paths = [os.path.join(FONT_DIR_WIN, f) for f in win_files]
        paths.append(os.path.join(FONT_LOCAL, local_file))
        paths.append(linux_path)
        for p in paths:
            if not os.path.exists(p):
                continue
            try:
                pdfmetrics.registerFont(TTFont(name, p))
                FONTS[slot] = name
                break
            except Exception:
                continue
    try:
        pdfmetrics.registerFontFamily(
            FONTS["reg"], normal=FONTS["reg"], bold=FONTS["bold"],
            italic=FONTS["italic"], boldItalic=FONTS["bolditalic"],
        )
    except Exception:
        pass
    _FONTS_READY = True
    return FONTS


def styles():
    """Bộ style của biên bản (gọi sau register_fonts())."""
    f = register_fonts()
    s = {}
    s["company"] = ParagraphStyle(
        "company", fontName=f["bold"], fontSize=10.5, leading=13.5, textColor=NAVY)
    s["company_sub"] = ParagraphStyle(
        "company_sub", fontName=f["reg"], fontSize=9, leading=12, textColor=NAVY)
    s["title"] = ParagraphStyle(
        "title", fontName=f["bold"], fontSize=15, leading=20, alignment=TA_CENTER)
    s["body"] = ParagraphStyle(
        "body", fontName=f["reg"], fontSize=11, leading=15.5)
    s["body_b"] = ParagraphStyle(
        "body_b", fontName=f["bold"], fontSize=11, leading=15.5)
    s["body_i"] = ParagraphStyle(
        "body_i", fontName=f["italic"], fontSize=11, leading=16, alignment=TA_JUSTIFY)
    s["dots"] = ParagraphStyle(
        "dots", fontName=f["reg"], fontSize=11, leading=16, textColor=colors.black)
    s["th"] = ParagraphStyle(
        "th", fontName=f["bold"], fontSize=10.5, leading=13, alignment=TA_CENTER)
    s["td"] = ParagraphStyle(
        "td", fontName=f["reg"], fontSize=10.5, leading=13, alignment=TA_CENTER)
    s["sign_head"] = ParagraphStyle(
        "sign_head", fontName=f["bold"], fontSize=11, leading=14, alignment=TA_CENTER)
    s["sign_name"] = ParagraphStyle(
        "sign_name", fontName=f["bold"], fontSize=10.5, leading=13, alignment=TA_CENTER)
    s["sign_note"] = ParagraphStyle(
        "sign_note", fontName=f["italic"], fontSize=8.5, leading=11,
        alignment=TA_CENTER, textColor=GRAY_TEXT)
    s["audit_h"] = ParagraphStyle(
        "audit_h", fontName=f["bold"], fontSize=10, leading=13, textColor=NAVY,
        spaceBefore=6, spaceAfter=3)
    s["audit_k"] = ParagraphStyle("audit_k", fontName=f["bold"], fontSize=8.5, leading=11.5)
    s["audit_v"] = ParagraphStyle("audit_v", fontName=f["reg"], fontSize=8.5, leading=11.5)
    s["mono"] = ParagraphStyle("mono", fontName=f["reg"], fontSize=7.8, leading=10.5)
    s["small"] = ParagraphStyle(
        "small", fontName=f["italic"], fontSize=8.5, leading=11.5, textColor=GRAY_TEXT,
        alignment=TA_JUSTIFY)
    return s


# ---------------------------------------------------------------------------
# Tiện ích làm sạch dữ liệu
# ---------------------------------------------------------------------------
def clean_text(value, limit=MAX_TEXT_LEN):
    """Chuẩn hoá chuỗi nhận từ web: bỏ ký tự điều khiển, gộp khoảng trắng, cắt dài."""
    if value is None:
        return ""
    s = str(value)
    s = "".join(ch for ch in s if unicodedata.category(ch)[0] != "C")
    s = " ".join(s.split())
    return s[:limit]


def esc(value, dots=0):
    """Escape cho Paragraph của ReportLab; rỗng thì trả về dấu chấm lửng như mẫu."""
    s = clean_text(value)
    if not s:
        return "." * dots if dots else ""
    return xml_escape(s)


def ten_gara(value):
    """Mục 4 của mẫu in "Gara {tên}" — bỏ tiền tố nếu người dùng đã gõ sẵn."""
    v = clean_text(value)
    if not v:
        return "Gara " + "." * 34
    return v if v.lower().startswith("gara") else f"Gara {xml_escape(v)}"


def now_vn():
    return datetime.now(TZ_VN)


def sha256_hex(data):
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def group_hex(hex_str, size=8):
    """Chia mã băm thành nhóm cho dễ đối chiếu bằng mắt."""
    return " ".join(hex_str[i:i + size] for i in range(0, len(hex_str), size))


def decode_signature(data_url):
    """Giải mã dataURL PNG của signature pad → bytes PNG.

    Chỉ nhận PNG (chữ ký xuất từ canvas, nền trong suốt). Trả về None nếu
    không hợp lệ — biên bản khi đó để ô ký trống.
    """
    if not data_url or not isinstance(data_url, str):
        return None
    m = re.match(r"^data:image/png;base64,([A-Za-z0-9+/=\s]+)$", data_url.strip())
    if not m:
        return None
    try:
        raw = base64.b64decode(re.sub(r"\s+", "", m.group(1)))
    except Exception:
        return None
    if not raw or len(raw) > MAX_SIG_BYTES:
        return None
    if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        return None
    return raw


# ---------------------------------------------------------------------------
# Logo PTI cho nền trắng
# ---------------------------------------------------------------------------
_logo_cache = {}


def logo_png(logo_path):
    """Logo PTI SOS chuyển sang bản dùng được trên nền trắng (trả về bytes PNG).

    File assets/logo-ptisos.png có chữ "pti" màu trắng (thiết kế để đặt trên
    dải xanh của bộ ảnh giám định) nên sẽ biến mất trên nền giấy. Ở đây đổi các
    pixel sáng thành xanh navy của thương hiệu PTI, giữ nguyên phần cam và độ
    trong suốt.
    """
    if not logo_path or not os.path.exists(logo_path):
        return None
    if logo_path in _logo_cache:
        return _logo_cache[logo_path]
    data = None
    try:
        import numpy as np
        from PIL import Image

        img = Image.open(logo_path).convert("RGBA")
        # Logo in ở ~2,5 cm nên 300 px là quá đủ; thu nhỏ để PDF nhẹ hơn nhiều
        if max(img.size) > 300:
            img.thumbnail((300, 300), Image.LANCZOS)
        a = np.array(img)
        r, g, b, al = a[:, :, 0], a[:, :, 1], a[:, :, 2], a[:, :, 3]
        light = (r > 200) & (g > 200) & (b > 200) & (al > 0)
        a[light, 0], a[light, 1], a[light, 2] = 31, 59, 115
        dark = (r < 80) & (g < 80) & (b < 80) & (al > 0)
        a[dark] = [0, 0, 0, 0]
        buf = io.BytesIO()
        Image.fromarray(a).save(buf, format="PNG")
        data = buf.getvalue()
    except Exception:
        data = None
    _logo_cache[logo_path] = data
    return data


# ---------------------------------------------------------------------------
# Khung trang: footer mã biểu mẫu + watermark khi chưa ký
# ---------------------------------------------------------------------------
def make_page_decorator(draft):
    """Trả về hàm onPage vẽ footer (và watermark nếu là bản chưa ký)."""
    f = register_fonts()

    def decorate(canvas, doc):
        canvas.saveState()
        canvas.setFillColor(colors.black)
        canvas.setFont(f["italic"], 9)
        canvas.drawString(MARGIN_X, 1.0 * cm, f"{QUY_TRINH} – {MA_BIEU_MAU}")
        canvas.setFont(f["italic"], 9)
        canvas.drawRightString(PAGE_W - MARGIN_X, 1.0 * cm, f"Trang {doc.page}")

        if draft:
            canvas.saveState()
            canvas.translate(PAGE_W / 2, PAGE_H / 2)
            canvas.rotate(38)
            canvas.setFont(f["bold"], 42)
            canvas.setFillColor(colors.Color(0, 0, 0, alpha=0.07))
            canvas.drawCentredString(0, 0, "BẢN XEM TRƯỚC — CHƯA KÝ")
            canvas.restoreState()
        canvas.restoreState()

    return decorate


def letterhead(logo_path, s):
    """Khối tiêu đề thư: logo trái + tên/địa chỉ/liên hệ tổng công ty."""
    png = logo_png(logo_path)
    left = (fit_image(png, 2.5 * cm, 2.5 * cm, align="LEFT") if png
            else Paragraph("", s["company_sub"]))
    right = [
        Paragraph(CONG_TY, s["company"]),
        Paragraph(DIA_CHI, s["company_sub"]),
        Paragraph(LIEN_HE, s["company_sub"]),
    ]
    tbl = Table([[left, right]], colWidths=[3.0 * cm, None], hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, 0), 0),
        ("LEFTPADDING", (1, 0), (1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return tbl


def fit_image(png_bytes, max_w, max_h, align="CENTER"):
    """Flowable ảnh PNG (giữ tỉ lệ, giữ nền trong suốt) vừa trong khung cho trước."""
    reader = ImageReader(io.BytesIO(png_bytes))
    iw, ih = reader.getSize()
    scale = min(max_w / iw, max_h / ih)
    img = RLImage(io.BytesIO(png_bytes), width=iw * scale, height=ih * scale)
    img.hAlign = align
    return img


# ---------------------------------------------------------------------------
# NỘI DUNG BIÊN BẢN — mẫu BM.PTI.CG.02.08a
# ---------------------------------------------------------------------------
def body_flowables(info, s, logo_path):
    out = [letterhead(logo_path, s), Spacer(1, 10)]

    out.append(Paragraph("BIÊN BẢN GIÁM ĐỊNH THIỆT HẠI", s["title"]))
    out.append(Spacer(1, 10))

    ngay = esc(info.get("ngay"), 14)
    dia_diem_gd = esc(info.get("dia_diem_gd"), 34)
    bks = esc(info.get("bks"), 14)

    out.append(Paragraph(f"Hôm nay, ngày {ngay} tại : {dia_diem_gd}", s["body"]))
    out.append(Paragraph("Chúng tôi gồm có:", s["body_b"]))

    # Hai dòng thành phần tham gia — canh cột như mẫu
    tp = Table(
        [
            [Paragraph(f"1/ {esc(info.get('gdv'), 24)}", s["body"]),
             Paragraph(
                 f"GĐV {esc(info.get('phong') or PHONG_MAC_DINH, 24)}, "
                 f"SĐT: {esc(info.get('sdt_gdv'), 14)}", s["body"])],
            [Paragraph(f"2 {esc(info.get('chu_xe'), 24)}", s["body"]),
             Paragraph(
                 f"là Đại diện: Chủ xe/lái xe BKS : {bks} , "
                 f"SĐT {esc(info.get('sdt_chu_xe'), 14)}", s["body"])],
        ],
        colWidths=[6.2 * cm, None], hAlign="LEFT",
    )
    tp.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    out.append(tp)
    out.append(Spacer(1, 4))

    out.append(Paragraph(
        f"Giám định thiệt hại xe ô tô BKS {bks} bị tổn thất ngày : "
        f"{esc(info.get('ngay_ton_that'), 14)}", s["body"]))
    out.append(Paragraph(
        f"Tại : {esc(info.get('dia_diem_ton_that'), 50)}", s["body"]))
    out.append(Spacer(1, 6))

    out.append(Paragraph(
        "<b>1. Thông tin tai nạn :</b> Theo Thông báo tai nạn và yêu cầu bồi thường",
        s["body_b"]))
    out.append(Spacer(1, 4))
    out.append(Paragraph(
        "<b>2. Hạng mục giám định :</b> <i>( Theo các phụ lục đính kèm )</i>",
        s["body_b"]))
    out.append(Spacer(1, 5))
    out.append(hang_muc_table(info, s))
    out.append(Spacer(1, 10))

    out.append(Paragraph("3. Ý kiến của các bên tham gia giám định:", s["body_b"]))
    y_kien = clean_text(info.get("y_kien"), 600)
    if y_kien:
        out.append(Paragraph(xml_escape(y_kien), s["body"]))
    else:
        for _ in range(2):
            out.append(Paragraph("." * 112, s["dots"]))
    out.append(Spacer(1, 4))

    out.append(Paragraph(
        f"<b>4. Đơn vị sửa chữa:</b> {ten_gara(info.get('dia_diem_gd'))}",
        s["body_b"]))
    out.append(Paragraph(
        f"Đ/c : {esc(info.get('dia_chi_gara'), 48)}"
        f"SĐT liên hệ{esc(info.get('sdt_gara'), 22)}", s["body"]))
    out.append(Spacer(1, 10))

    out.append(Paragraph(
        "Biên bản này được lập với sự xác nhận của các bên liên quan cùng tham gia "
        f"giám định bao gồm {esc(info.get('so_phu_luc'), 10)} phụ lục đính kèm làm "
        "cơ sở xây dựng Báo giá sửa chữa", s["body_i"]))
    out.append(Spacer(1, 4))
    out.append(Paragraph(
        "Đại diện chủ xe/ lái xe giữ bản sao/chụp ảnh làm cơ sở theo dõi nội dung "
        "sửa chữa", s["body_i"]))
    return out


def hang_muc_table(info, s):
    """Bảng '2. Hạng mục giám định' — 2 tầng tiêu đề, 10 dòng như mẫu."""
    head = [
        [Paragraph("STT", s["th"]), Paragraph("Chi tiết thiệt hại", s["th"]),
         Paragraph("Phương án giải quyết", s["th"]), "",
         Paragraph("Hiện vật thu hồi", s["th"]), ""],
        ["", "",
         Paragraph("Sửa chữa", s["th"]), Paragraph("Thay thế", s["th"]),
         Paragraph("Có", s["th"]), Paragraph("Không", s["th"])],
    ]
    # Hạng mục nhập sẵn (nếu có) — mỗi phần tử là một dòng "tên thiệt hại"
    ds = [clean_text(x, 120) for x in (info.get("hang_muc") or []) if clean_text(x)]
    rows = []
    for i in range(max(SO_DONG_HANG_MUC, len(ds))):
        ten = xml_escape(ds[i]) if i < len(ds) else ""
        rows.append([
            Paragraph(str(i + 1), s["td"]),
            Paragraph(ten, ParagraphStyle("t", parent=s["td"], alignment=TA_LEFT)),
            "", "", "", "",
        ])

    tbl = Table(head + rows,
                colWidths=[1.2 * cm, 6.4 * cm, 2.5 * cm, 2.5 * cm, 1.9 * cm, 2.2 * cm],
                rowHeights=[None, None] + [0.55 * cm] * len(rows),
                hAlign="CENTER", repeatRows=2)
    tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.6, colors.black),
        ("SPAN", (0, 0), (0, 1)),       # STT
        ("SPAN", (1, 0), (1, 1)),       # Chi tiết thiệt hại
        ("SPAN", (2, 0), (3, 0)),       # Phương án giải quyết
        ("SPAN", (4, 0), (5, 0)),       # Hiện vật thu hồi
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, 1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, 1), 4),
        ("TOPPADDING", (0, 2), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 2), (-1, -1), 2),
    ]))
    return tbl


# ---------------------------------------------------------------------------
# Khối ký — placeholder sẵn trong mẫu, chèn ảnh PNG khi đã ký
# ---------------------------------------------------------------------------
SIGN_BOX_H = 3.0 * cm        # ô ký khi đã có chữ ký
SIGN_BOX_H_EMPTY = 1.6 * cm  # ô ký để trống (bản chưa ký, in ra ký tay)


def _sig_cell(png_bytes, box_w, box_h):
    """Nội dung một ô ký: ảnh chữ ký nếu có, ngược lại chừa khoảng trống."""
    if not png_bytes:
        return Spacer(1, box_h)
    try:
        return fit_image(png_bytes, box_w - 0.8 * cm, box_h - 0.2 * cm)
    except Exception:
        return Spacer(1, box_h)


def signature_flowables(info, signatures, s):
    """Hai ô ký của mẫu: LÁI XE/CHỦ XE và GIÁM ĐỊNH VIÊN PTI."""
    signatures = signatures or {}
    col_w = (PAGE_W - 2 * MARGIN_X) / 2
    ten_khach = clean_text(info.get("chu_xe"))
    ten_gdv = clean_text(info.get("gdv"))
    t_khach = clean_text(signatures.get("khach_at"))
    t_gdv = clean_text(signatures.get("gdv_at"))

    signed = bool(signatures.get("khach") or signatures.get("gdv"))
    box_h = SIGN_BOX_H if signed else SIGN_BOX_H_EMPTY
    data = [
        [Paragraph("LÁI XE/CHỦ XE", s["sign_head"]),
         Paragraph("GIÁM ĐỊNH VIÊN PTI", s["sign_head"])],
        [Paragraph("(ký, ghi rõ họ tên)", s["sign_note"]),
         Paragraph("(ký, ghi rõ họ tên)", s["sign_note"])],
        [_sig_cell(signatures.get("khach"), col_w, box_h),
         _sig_cell(signatures.get("gdv"), col_w, box_h)],
        [Paragraph(esc(ten_khach), s["sign_name"]),
         Paragraph(esc(ten_gdv), s["sign_name"])],
    ]
    # Dòng thời điểm ký chỉ xuất hiện ở bản đã ký
    if t_khach or t_gdv:
        data.append([
            Paragraph(f"Ký lúc: {esc(t_khach)}" if t_khach else "", s["sign_note"]),
            Paragraph(f"Ký lúc: {esc(t_gdv)}" if t_gdv else "", s["sign_note"]),
        ])
    tbl = Table(data, colWidths=[col_w, col_w], hAlign="CENTER")
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 2), (-1, 2), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    # Giữ trọn khối ký trong một trang, không để tiêu đề và chữ ký tách rời
    return [Spacer(1, 8), KeepTogether(tbl)]


# ---------------------------------------------------------------------------
# Dấu vết kiểm chứng
# ---------------------------------------------------------------------------
def audit_flowables(audit, s):
    """Khối thông tin kiểm chứng in ở cuối biên bản đã ký."""
    if not audit:
        return []
    pairs = [
        ("Mã hồ sơ", audit.get("so_ho_so") or "—"),
        ("Thời điểm ký (giờ VN)", audit.get("signed_at_vn") or "—"),
        ("Thời điểm ký (UTC)", audit.get("signed_at_utc") or "—"),
        ("Giờ trên thiết bị người ký", audit.get("client_time") or "—"),
        ("Toạ độ GPS", audit.get("gps") or "không được cấp quyền"),
        ("Thiết bị / trình duyệt", audit.get("device") or "—"),
        ("Địa chỉ IP phiên ký", audit.get("ip") or "—"),
        ("Xác nhận đã đọc biên bản", audit.get("consent") or "—"),
    ]
    rows = [[Paragraph(esc(k), s["audit_k"]), Paragraph(esc(v, 220), s["audit_v"])]
            for k, v in pairs]
    rows.append([
        Paragraph("Mã kiểm chứng (SHA-256)", s["audit_k"]),
        Paragraph(esc(group_hex(audit.get("payload_hash", "")), 200), s["mono"]),
    ])
    tbl = Table(rows, colWidths=[5.4 * cm, None], hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.4, GRAY_LINE),
        ("BACKGROUND", (0, 0), (0, -1), BOX_BG),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5),
    ]))
    return [
        Spacer(1, 16),
        Paragraph("DẤU VẾT KIỂM CHỨNG CHỮ KÝ ĐIỆN TỬ", s["audit_h"]),
        Paragraph(
            "Khối thông tin dưới đây do hệ thống ghi tự động tại thời điểm các bên ký "
            "trên thiết bị. Mã kiểm chứng là giá trị băm SHA-256 của toàn bộ dữ liệu ký "
            "(nội dung biên bản, hai ảnh chữ ký và các thông tin kiểm chứng); mọi thay "
            "đổi sau khi ký đều làm mã này sai lệch.", s["small"]),
        Spacer(1, 5),
        tbl,
    ]


def payload_hash(info, audit, signatures):
    """SHA-256 của toàn bộ dữ liệu ký — in lên biên bản làm mã kiểm chứng."""
    payload = {
        "info": {k: (clean_text(v) if not isinstance(v, (list, tuple))
                     else [clean_text(x) for x in v])
                 for k, v in sorted((info or {}).items())},
        "audit": {k: clean_text(v, 220) for k, v in sorted((audit or {}).items())
                  if k != "payload_hash"},
        "sig_khach": sha256_hex((signatures or {}).get("khach") or b""),
        "sig_gdv": sha256_hex((signatures or {}).get("gdv") or b""),
    }
    blob = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256_hex(blob)


# ---------------------------------------------------------------------------
# Dựng PDF
# ---------------------------------------------------------------------------
def build(output_path, info, signatures=None, audit=None, logo_path=None):
    """Tạo PDF biên bản giám định thiệt hại theo mẫu BM.PTI.CG.02.08a.

    info        — dict: bks, gdv, phong, sdt_gdv, chu_xe, sdt_chu_xe, ngay,
                  dia_diem_gd, ngay_ton_that, dia_diem_ton_that, dia_chi_gara,
                  sdt_gara, so_phu_luc, y_kien, hang_muc (list), so_ho_so
    signatures  — dict {'khach': bytes PNG, 'gdv': bytes PNG,
                        'khach_at': str, 'gdv_at': str}; None/rỗng = bản chưa ký
    audit       — dict dấu vết kiểm chứng; chỉ in ở bản đã ký
    Trả về (output_path, payload_hash, file_hash).
    """
    import gtx_gen

    info = dict(info or {})
    info["bks"] = gtx_gen.normalize_bks(info.get("bks", ""))
    signatures = dict(signatures or {})
    signed = bool(signatures.get("khach") or signatures.get("gdv"))

    s = styles()
    audit = dict(audit or {})
    ph = ""
    if signed:
        ph = payload_hash(info, audit, signatures)
        audit["payload_hash"] = ph

    story = body_flowables(info, s, logo_path)
    story += signature_flowables(info, signatures, s)
    if signed:
        story += audit_flowables(audit, s)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
    doc = BaseDocTemplate(
        output_path, pagesize=A4,
        leftMargin=MARGIN_X, rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM,
        title=f"Bien ban giam dinh thiet hai {info.get('bks', '')}".strip(),
        author="PTI", subject=f"{QUY_TRINH} - {MA_BIEU_MAU}",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
                  id="main", leftPadding=0, rightPadding=0,
                  topPadding=0, bottomPadding=0)
    doc.addPageTemplates([PageTemplate(
        id="bb", frames=[frame], onPage=make_page_decorator(draft=not signed))])
    doc.build(story)

    with open(output_path, "rb") as fh:
        file_hash = sha256_hex(fh.read())
    return output_path, ph, file_hash


def output_name(bks, signed=False):
    """Tên file PDF biên bản theo biển số."""
    import gtx_gen
    safe = re.sub(r'[\\/:*?"<>|]', "_", gtx_gen.normalize_bks(bks) or "KhongBKS")
    return f"BienBan_GiamDinh_{safe}{'_DaKy' if signed else ''}.pdf"


if __name__ == "__main__":
    # Dựng thử để xem bố cục:  python bien_ban.py
    out = os.path.join(BASE, "output", "BienBan_Thu.pdf")
    build(
        out,
        {
            "bks": "14K-240.48", "gdv": "Nguyễn Văn Hướng",
            "phong": "Cứu hộ & Giám định khu vực Quảng Ninh",
            "sdt_gdv": "0912 345 678", "chu_xe": "Trần Văn Bình",
            "sdt_chu_xe": "0987 654 321", "ngay": "16/11/2026",
            "dia_diem_gd": "Gara Thành Đạt, TP Hạ Long",
            "ngay_ton_that": "10/11/2026",
            "dia_diem_ton_that": "QL18, phường Hà Khẩu, TP Hạ Long, Quảng Ninh",
            "so_ho_so": "XCG.2026.00123",
        },
        logo_path=os.path.join(BASE, "assets", "logo-ptisos.png"),
    )
    print("Da tao:", out)
