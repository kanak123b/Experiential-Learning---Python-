
from flask import Flask, render_template, request, send_file
import qrcode
import cv2
import numpy as np
from io import BytesIO

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024


@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    error = None
    qr_image = None

    if request.method == "POST":
        action = request.form.get("action")

        if action == "encode":
            text = request.form.get("text", "").strip()

            if not text:
                error = "Please enter text or a URL."
            else:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4
                )
                qr.add_data(text)
                qr.make(fit=True)

                image = qr.make_image(
                    fill_color="black",
                    back_color="white"
                )

                buffer = BytesIO()
                image.save(buffer, format="PNG")
                qr_image = buffer.getvalue()

                return send_file(
                    BytesIO(qr_image),
                    mimetype="image/png",
                    as_attachment=True,
                    download_name="myqr.png"
                )

        elif action == "decode":
            file = request.files.get("qrfile")

            if not file or not file.filename:
                error = "Please select a QR image."
            else:
                raw = file.read()

                if not raw:
                    error = "The uploaded file is empty."
                else:
                    image = cv2.imdecode(
                        np.frombuffer(raw, np.uint8),
                        cv2.IMREAD_COLOR
                    )

                    if image is None:
                        error = "Unable to read this image."
                    else:
                        detector = cv2.QRCodeDetector()
                        data, points, _ = detector.detectAndDecode(image)

                        if data:
                            result = data
                        else:
                            error = "No readable QR code was found."

    return render_template(
        "index.html",
        result=result,
        error=error
    )


@app.errorhandler(413)
def file_too_large(error):
    return render_template(
        "index.html",
        error="File is too large. Maximum size is 5 MB.",
        result=None
    ), 413


if __name__ == "__main__":
    app.run(debug=True)
