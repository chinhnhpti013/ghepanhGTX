"""
Web server cho công cụ Ghép ảnh Giám định Giấy tờ xe (GTX) — PTI SOS.

Chạy:  python app.py
Mở:    http://127.0.0.1:5000
"""
import io
import json
import os
import re
import shutil
import tempfile
import traceback

from flask import Flask, request, send_file, jsonify, send_from_directory

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
