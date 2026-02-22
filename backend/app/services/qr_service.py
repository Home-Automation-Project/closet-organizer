"""
QR code generation for basket scan pages.
"""
import io
import os

import qrcode
import qrcode.image.svg


def generate_basket_qr_png(qr_token: str) -> bytes:
    """Return PNG bytes for a QR code pointing to /scan/{qr_token}."""
    app_host = os.environ.get("APP_HOST", "http://localhost").rstrip("/")
    url = f"{app_host}/scan/{qr_token}"
    img = qrcode.make(url)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def generate_basket_qr_svg(qr_token: str) -> str:
    """Return SVG string for inline embedding."""
    app_host = os.environ.get("APP_HOST", "http://localhost").rstrip("/")
    url = f"{app_host}/scan/{qr_token}"
    factory = qrcode.image.svg.SvgPathImage
    img = qrcode.make(url, image_factory=factory)
    buf = io.BytesIO()
    img.save(buf)
    return buf.getvalue().decode("utf-8")
