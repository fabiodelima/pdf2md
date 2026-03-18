import os
import uuid
import json
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, render_template

app = Flask(__name__)

UPLOAD_FOLDER = Path("uploads")
OUTPUT_FOLDER = Path("output")
UPLOAD_FOLDER.mkdir(exist_ok=True)
OUTPUT_FOLDER.mkdir(exist_ok=True)

def check_opendataloader():
    try:
        import opendataloader_pdf
        return True, None
    except ImportError:
        return False, "opendataloader-pdf não está instalado. Execute: pip install opendataloader-pdf"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/health")
def health():
    ok, err = check_opendataloader()
    return jsonify({"ok": ok, "error": err})

@app.route("/api/convert", methods=["POST"])
def convert():
    import opendataloader_pdf

    if "file" not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400

    file = request.files["file"]
    if not file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "Apenas arquivos PDF são suportados"}), 400

    mode = request.form.get("mode", "local")  # "local" ou "hybrid"

    job_id = str(uuid.uuid4())[:8]
    input_path = UPLOAD_FOLDER / f"{job_id}.pdf"
    output_dir = OUTPUT_FOLDER / job_id
    output_dir.mkdir(exist_ok=True)

    file.save(input_path)

    try:
        convert_kwargs = {
            "input_path": [str(input_path)],
            "output_dir": str(output_dir),
            "format": ["markdown"],
        }

        if mode == "hybrid":
            convert_kwargs["hybrid"] = "docling-fast"

        opendataloader_pdf.convert(**convert_kwargs)

        md_files = list(output_dir.glob("*.md"))
        if not md_files:
            md_files = list(output_dir.rglob("*.md"))

        if not md_files:
            return jsonify({"error": "Conversão concluída mas nenhum arquivo .md foi gerado"}), 500

        content = md_files[0].read_text(encoding="utf-8")
        word_count = len(content.split())
        line_count = content.count("\n")

        return jsonify({
            "ok": True,
            "markdown": content,
            "stats": {
                "words": word_count,
                "lines": line_count,
                "filename": file.filename,
                "mode": mode,
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if input_path.exists():
            input_path.unlink()

@app.route("/output/<path:filename>")
def serve_output(filename):
    return send_from_directory(OUTPUT_FOLDER, filename)

if __name__ == "__main__":
    ok, err = check_opendataloader()
    if not ok:
        print(f"\n⚠️  AVISO: {err}\n")
    else:
        print("\n✅ opendataloader-pdf detectado\n")
    port = int(os.environ.get("PORT", 5000))
    print(f"🚀 Rodando em http://0.0.0.0:{port}\n")
    app.run(debug=False, host="0.0.0.0", port=port)
