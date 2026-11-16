"""
Web server cho công cụ Ghép ảnh Giám định Giấy tờ xe (GTX) — PTI SOS.

Chạy:  python app.py
Mở:    http://127.0.0.1:5000
"""
import base64
import io
import json
import os
import re
import shutil
import tempfile
import traceback

from flask import Flask, request, send_file, jsonify, send_from_directory

import bien_ban
import gtx_gen

BASE = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE, "assets", "logo-ptisos.png")

app = Flask(__name__, static_folder=None)

# Phần mở rộng hợp lệ
ALLOWED_IMG = {".jpg", ".jpeg", ".png"}
ALLOWED_DOC = {".pdf"}


def safe_name(filename):
    """Giữ lại tiền tố số (1.1, 2.3, 4...) và phần mở rộng, loại bỏ đường dẫn."""
    filename = os.path.basename(filename or "")
    # Chỉ giữ ký tự an toàn, giữ nguyên dấu chấm để phân loại nhóm
    filename = re.sub(r"[^A-Za-z0-9._-]", "_", filename)
    return filename or "file"


@app.route("/")
def index():
    return send_from_directory(BASE, "index.html")


@app.route("/health")
def health():
    """Điểm kiểm tra để giao diện xác nhận đang chạy qua server Flask."""
    return jsonify({"ok": True, "app": "gtx"})


@app.route("/doc-types")
def doc_types():
    """Danh mục giấy tờ (tiền tố → tên hạng mục) cho giao diện.

    Nguồn: BUILTIN_DOC_TYPES trong gtx_gen.py, ghi đè bởi doc_types.json.
    Hạng mục người dùng tự thêm trên web KHÔNG nằm ở đây — chúng được lưu tại
    trình duyệt và gửi kèm mỗi lần tạo PDF qua trường "extra".
    """
    items = gtx_gen.DOC_TYPES
    return jsonify({
        "items": [
            {"key": k, "name": items[k], "group": int(float(k))}
            for k in gtx_gen.sort_keys(items)
        ]
    })


@app.route("/generate", methods=["POST"])
def generate():
    images = request.files.getlist("images")
    bks = (request.form.get("bks") or "").strip()
    extra_raw = (request.form.get("extra") or "").strip()
    gdv = (request.form.get("gdv") or "").strip()
    ngay = (request.form.get("ngay") or "").strip()

    if not bks:
        return jsonify({"error": "Thiếu biển số xe."}), 400
    if not images:
        return jsonify({"error": "Chưa chọn ảnh hoặc file PDF giấy tờ nào."}), 400

    # Hạng mục người dùng tự thêm trên giao diện (JSON {"tiền tố": "tên"}).
    # gtx_gen.clean_doc_types() sẽ lọc lại lần nữa, đây chỉ là bước parse.
    extra_doc_types = {}
    if extra_raw:
        try:
            parsed = json.loads(extra_raw)
            if isinstance(parsed, dict):
                extra_doc_types = parsed
        except ValueError:
            return jsonify({"error": "Danh sách hạng mục bổ sung không hợp lệ."}), 400

    work = tempfile.mkdtemp(prefix="gtx_")
    in_dir = os.path.join(work, "input")
    out_dir = os.path.join(work, "output")
    os.makedirs(in_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)

    try:
        # Lưu ảnh + PDF, giữ nguyên tên để phân loại nhóm
        saved = 0
        for f in images:
            if not f or not f.filename:
                continue
            fx = os.path.splitext(f.filename)[1].lower()
            if fx not in ALLOWED_IMG and fx not in ALLOWED_DOC:
                continue
            f.save(os.path.join(in_dir, safe_name(f.filename)))
            saved += 1

        if saved == 0:
            return jsonify({"error": "Không có ảnh/PDF hợp lệ (chỉ nhận .jpg, .png, .pdf)."}), 400

        output_path = os.path.join(out_dir, "GiamDinh_GiayToXe.pdf")
        result = gtx_gen.main(
            logo_path=LOGO_PATH,
            image_dir=in_dir,
            output_path=output_path,
            bks=bks,
            gdv=gdv,
            ngay=ngay,
            extra_doc_types=extra_doc_types,
        )

        if not result or not os.path.exists(result):
            return jsonify({"error": "Không tạo được PDF — kiểm tra lại tên file ảnh (phải bắt đầu bằng tiền tố số, VD 1.1.jpg)."}), 500

        # Đọc PDF vào bộ nhớ để có thể xóa thư mục tạm an toàn trước khi stream
        download_name = os.path.basename(result)
        with open(result, "rb") as fh:
            pdf_bytes = fh.read()
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype="application/pdf",
            as_attachment=False,
            download_name=download_name,
        )
    except Exception as e:
        # In traceback đầy đủ ra terminal để chẩn đoán
        print("=" * 60)
        print("LỖI khi tạo PDF:")
        traceback.print_exc()
        print("=" * 60)
        return jsonify({"error": f"Lỗi xử lý: {type(e).__name__}: {e}"}), 500
    finally:
        # Dọn thư mục tạm sau khi gửi file (send_file đã đọc xong vào bộ nhớ)
        shutil.rmtree(work, ignore_errors=True)


# ---------------------------------------------------------------------------
# BIÊN BẢN GIÁM ĐỊNH (mẫu BM.PTI.CG.02.08a) — xem trước và ký tay
# ---------------------------------------------------------------------------
# Các trường của biên bản nhận từ form; mọi trường đều không bắt buộc trừ BKS.
BB_FIELDS = (
    "bks", "gdv", "ngay", "phong", "sdt_gdv", "chu_xe", "sdt_chu_xe", "gplx",
    "dia_diem_gd", "ngay_ton_that", "dia_diem_ton_that", "dia_chi_gara",
    "sdt_gara", "so_phu_luc", "y_kien", "so_ho_so",
)


def bb_info_from_form(form):
    """Gom thông tin biên bản từ form, đã làm sạch chuỗi."""
    info = {k: bien_ban.clean_text(form.get(k) or "") for k in BB_FIELDS}
    info["y_kien"] = bien_ban.clean_text(form.get("y_kien") or "", 600)
    return info


def pdf_pages_png(pdf_path, dpi=110):
    """Render các trang PDF thành PNG base64 để hiển thị bằng thẻ <img>.

    Trình duyệt điện thoại (iOS Safari, Chrome Android) thường không hiển thị
    được PDF trong <iframe>, trong khi biên bản lại hay được ký ngay tại hiện
    trường bằng điện thoại — nên bản xem trước dùng ảnh thay vì nhúng PDF.
    """
    import fitz

    pages = []
    doc = fitz.open(pdf_path)
    try:
        mat = fitz.Matrix(dpi / 72, dpi / 72)
        for page in doc:
            pix = page.get_pixmap(matrix=mat)
            pages.append(base64.b64encode(pix.tobytes("png")).decode("ascii"))
    finally:
        doc.close()
    return pages


def client_ip():
    """IP của phiên ký — tính cả khi chạy sau proxy (Render)."""
    fwd = request.headers.get("X-Forwarded-For", "")
    if fwd:
        return bien_ban.clean_text(fwd.split(",")[0], 60)
    return bien_ban.clean_text(request.remote_addr or "", 60)


@app.route("/bien-ban", methods=["POST"])
def bien_ban_preview():
    """Dựng bản XEM TRƯỚC của biên bản (có watermark 'chưa ký').

    Trả JSON gồm PDF (base64, để tải về) và ảnh từng trang (để hiển thị).
    """
    info = bb_info_from_form(request.form)
    if not info.get("bks"):
        return jsonify({"error": "Thiếu biển số xe."}), 400

    work = tempfile.mkdtemp(prefix="gtx_bb_")
    try:
        name = bien_ban.output_name(info["bks"])
        out = os.path.join(work, name)
        path, _, file_hash = bien_ban.build(out, info, logo_path=LOGO_PATH)
        with open(path, "rb") as fh:
            pdf_bytes = fh.read()
        return jsonify({
            "name": name,
            "pdf": base64.b64encode(pdf_bytes).decode("ascii"),
            "pages": pdf_pages_png(path),
            "file_hash": file_hash,
        })
    except Exception as e:
        print("=" * 60)
        print("LỖI khi dựng biên bản:")
        traceback.print_exc()
        print("=" * 60)
        return jsonify({"error": f"Lỗi dựng biên bản: {type(e).__name__}: {e}"}), 500
    finally:
        shutil.rmtree(work, ignore_errors=True)


@app.route("/bien-ban/ky", methods=["POST"])
def bien_ban_ky():
    """Chèn chữ ký tay vào biên bản và ghi dấu vết kiểm chứng.

    Nhận thêm:
      sig_khach / sig_gdv — ảnh chữ ký dataURL PNG nền trong suốt
      dong_y              — "1" khi khách đã tích ô xác nhận đã đọc biên bản
      audit               — JSON {client_time, gps, device} do trình duyệt gửi
    Trả JSON gồm PDF (base64) và toàn bộ thông tin kiểm chứng để hiển thị/lưu.
    """
    info = bb_info_from_form(request.form)
    if not info.get("bks"):
        return jsonify({"error": "Thiếu biển số xe."}), 400

    sig_khach = bien_ban.decode_signature(request.form.get("sig_khach"))
    sig_gdv = bien_ban.decode_signature(request.form.get("sig_gdv"))
    if not sig_khach and not sig_gdv:
        return jsonify({"error": "Chưa có chữ ký nào hợp lệ. Vui lòng ký vào ô ký tay."}), 400
    if request.form.get("dong_y") != "1":
        return jsonify({"error": "Khách hàng chưa tích ô xác nhận đã đọc và đồng ý nội dung biên bản."}), 400

    try:
        raw_audit = json.loads(request.form.get("audit") or "{}")
        if not isinstance(raw_audit, dict):
            raw_audit = {}
    except ValueError:
        raw_audit = {}

    now = bien_ban.now_vn()
    ky_luc = now.strftime("%d/%m/%Y %H:%M")
    audit = {
        "so_ho_so": info.get("so_ho_so") or "—",
        "signed_at_vn": now.strftime("%d/%m/%Y %H:%M:%S (GMT+7)"),
        "signed_at_utc": now.astimezone(bien_ban.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "client_time": bien_ban.clean_text(raw_audit.get("client_time"), 60),
        "gps": bien_ban.clean_text(raw_audit.get("gps"), 120),
        "device": bien_ban.clean_text(raw_audit.get("device"), 220),
        "ip": client_ip(),
        "consent": "Có — khách hàng tích xác nhận đã đọc và đồng ý nội dung biên bản",
    }
    signatures = {
        "khach": sig_khach, "gdv": sig_gdv,
        "khach_at": ky_luc if sig_khach else "",
        "gdv_at": ky_luc if sig_gdv else "",
    }

    work = tempfile.mkdtemp(prefix="gtx_bbky_")
    try:
        name = bien_ban.output_name(info["bks"], signed=True)
        out = os.path.join(work, name)
        path, payload_hash, file_hash = bien_ban.build(
            out, info, signatures=signatures, audit=audit, logo_path=LOGO_PATH,
        )
        with open(path, "rb") as fh:
            pdf_bytes = fh.read()
        audit["payload_hash"] = payload_hash
        audit["file_hash"] = file_hash
        return jsonify({
            "name": name,
            "pdf": base64.b64encode(pdf_bytes).decode("ascii"),
            "pages": pdf_pages_png(path),
            "audit": audit,
        })
    except Exception as e:
        print("=" * 60)
        print("LỖI khi ký biên bản:")
        traceback.print_exc()
        print("=" * 60)
        return jsonify({"error": f"Lỗi khi ký biên bản: {type(e).__name__}: {e}"}), 500
    finally:
        shutil.rmtree(work, ignore_errors=True)


@app.errorhandler(Exception)
def handle_any_error(e):
    """Đảm bảo MỌI lỗi đều trả về JSON (không phải trang HTML 500),
    để giao diện luôn hiển thị được lý do thật."""
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException):
        return jsonify({"error": f"{e.code} {e.name}: {e.description}"}), e.code
    traceback.print_exc()
    return jsonify({"error": f"Lỗi máy chủ: {type(e).__name__}: {e}"}), 500


if __name__ == "__main__":
    print("Mở trình duyệt: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
