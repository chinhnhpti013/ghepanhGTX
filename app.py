"""
Web server cho công cụ Ghép ảnh Giám định Giấy tờ xe (GTX) — PTI SOS.

Chạy:  python app.py
Mở:    http://127.0.0.1:5000
"""
import io
import os
import re
import shutil
import tempfile

from flask import Flask, request, send_file, jsonify, send_from_directory

import gtx_gen

BASE = os.path.dirname(os.path.abspath(__file__))
LOGO_PATH = os.path.join(BASE, "assets", "logo-ptisos.png")

app = Flask(__name__, static_folder=None)

# Phần mở rộng hợp lệ
ALLOWED_IMG = {".jpg", ".jpeg", ".png"}
ALLOWED_DOC = {".pdf"}
ALLOWED_XLS = {".xlsx"}


def safe_name(filename):
    """Giữ lại tiền tố số (1.1, 2.3, 4...) và phần mở rộng, loại bỏ đường dẫn."""
    filename = os.path.basename(filename or "")
    # Chỉ giữ ký tự an toàn, giữ nguyên dấu chấm để phân loại nhóm
    filename = re.sub(r"[^A-Za-z0-9._-]", "_", filename)
    return filename or "file"


@app.route("/")
def index():
    return send_from_directory(BASE, "index.html")


@app.route("/generate", methods=["POST"])
def generate():
    images = request.files.getlist("images")
    excel = request.files.get("excel")
    gdv = (request.form.get("gdv") or "").strip()
    ngay = (request.form.get("ngay") or "").strip()

    if not excel:
        return jsonify({"error": "Thiếu file Excel GTX (.xlsx)."}), 400
    if not images:
        return jsonify({"error": "Chưa chọn ảnh hoặc file PDF giấy tờ nào."}), 400

    ext = os.path.splitext(excel.filename)[1].lower()
    if ext not in ALLOWED_XLS:
        return jsonify({"error": "File Excel phải có định dạng .xlsx."}), 400

    work = tempfile.mkdtemp(prefix="gtx_")
    in_dir = os.path.join(work, "input")
    out_dir = os.path.join(work, "output")
    os.makedirs(in_dir, exist_ok=True)
    os.makedirs(out_dir, exist_ok=True)

    try:
        # Lưu Excel
        excel_path = os.path.join(in_dir, "GTX.xlsx")
        excel.save(excel_path)

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
            excel_path=excel_path,
            logo_path=LOGO_PATH,
            image_dir=in_dir,
            output_path=output_path,
            gdv=gdv,
            ngay=ngay,
        )

        if not result or not os.path.exists(result):
            return jsonify({"error": "Không tạo được PDF — kiểm tra lại tên file ảnh và nội dung Excel."}), 500

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
        return jsonify({"error": f"Lỗi xử lý: {e}"}), 500
    finally:
        # Dọn thư mục tạm sau khi gửi file (send_file đã đọc xong vào bộ nhớ)
        shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    print("Mở trình duyệt: http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
