#!/usr/bin/env python3
"""LocalSift backend — lightweight local text-extraction server.
Standard library only (pypdf just for PDF). Serves the UI and the
POST /upload endpoint on http://127.0.0.1:8200 — everything stays local.
"""
import io
import json
import os
import sys
import zipfile
import socketserver
import http.server
from email.parser import BytesParser
from email.policy import default as email_policy
from xml.etree import ElementTree as ET

HOST = "127.0.0.1"
PORT = 8200

# extensions -> extraction strategy
TEXT_EXTS = {".txt", ".md", ".csv"}
SUPPORTED_EXTS = TEXT_EXTS | {".odt", ".docx", ".pdf"}


def local_name(tag):
    """Strip the XML namespace: '{urn:...}p' -> 'p'."""
    return tag.rsplit("}", 1)[-1]


def extract_from_zip_xml(data, inner_path, paragraph_tags):
    """ODT/DOCX are ZIP archives containing XML: open inner_path and
    join the text of the paragraph-like elements with blank lines."""
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        xml_bytes = zf.read(inner_path)
    root = ET.fromstring(xml_bytes)
    lines = []
    for el in root.iter():
        if local_name(el.tag) in paragraph_tags:
            text = "".join(el.itertext()).strip()
            if text:
                lines.append(text)
    return "\n\n".join(lines)


def extract_text(filename, data):
    """Return (ok, text_or_error). No file is ever written to disk."""
    ext = os.path.splitext(filename)[1].lower()
    if ext in TEXT_EXTS:
        return True, data.decode("utf-8", errors="replace")
    if ext == ".odt":
        return True, extract_from_zip_xml(data, "content.xml", {"p", "h", "span"})
    if ext == ".docx":
        return True, extract_from_zip_xml(data, "word/document.xml", {"p", "t"})
    if ext == ".pdf":
        try:
            from pypdf import PdfReader  # imported lazily: only needed for PDFs
        except ImportError:
            return False, "PDF support requires the 'pypdf' package (pip install pypdf)"
        try:
            reader = PdfReader(io.BytesIO(data))
            pages = [page.extract_text() or "" for page in reader.pages]
            return True, "\n\n".join(pages)
        except Exception as exc:
            return False, f"Could not parse PDF: {exc}"
    return False, f"Unsupported file type '{ext}'. Supported: {', '.join(sorted(SUPPORTED_EXTS))}"


def parse_multipart(ctype, body):
    """Parse multipart/form-data using only the standard library
    (the old cgi module was removed in Python 3.13)."""
    header = b"Content-Type: " + ctype.encode("utf-8", errors="replace") + b"\r\nMIME-Version: 1.0\r\n\r\n"
    message = BytesParser(policy=email_policy).parsebytes(header + body)
    for part in message.iter_parts():
        filename = part.get_filename()
        if filename:
            payload = part.get_payload(decode=True) or b""
            yield os.path.basename(filename), payload


class LocalSiftHandler(http.server.SimpleHTTPRequestHandler):
    """Serves static files (GET) and the text-extraction endpoint (POST /upload)."""

    def log_message(self, fmt, *args):
        print(f"[server] {self.address_string()} {fmt % args}")

    # ---- POST /upload: multipart file -> extracted text as JSON ----
    def do_POST(self):
        if self.path != "/upload":
            self._json(404, {"ok": False, "error": "Not found"})
            return
        try:
            ctype = self.headers.get("Content-Type", "")
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            for filename, payload in parse_multipart(ctype, body):
                ok, result = extract_text(filename, payload)
                if not ok:
                    print(f"[upload] rejected {filename}: {result}")
                    self._json(422, {"ok": False, "error": result})
                    return
                print(f"[upload] {filename}: {len(payload)} bytes -> {len(result)} chars")
                self._json(200, {
                    "ok": True,
                    "filename": filename,
                    "size": len(payload),
                    "chars": len(result),
                    "text": result,
                })
                return
            self._json(400, {"ok": False, "error": "No file found in the request"})
        except Exception as exc:  # never leak a stack trace to the client
            print(f"[upload] error: {exc}")
            self._json(500, {"ok": False, "error": f"Upload failed: {exc}"})

    def _json(self, code, obj):
        payload = json.dumps(obj).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


class LocalSiftServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = LocalSiftServer((HOST, PORT), LocalSiftHandler)
    print(f"[server] LocalSift running at http://{HOST}:{PORT}/index.html")
    print(f"[server] supported formats: {', '.join(sorted(SUPPORTED_EXTS))}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[server] stopped")


if __name__ == "__main__":
    main()
