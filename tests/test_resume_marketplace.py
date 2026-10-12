import base64
import json
import sys

import run_resume_intake
from src.resume_marketplace import InfraiClient, ResumeMarketplaceService, ResumeRequest


class FakeResponse:
    status = 200

    def read(self):
        return b'{"ok": true, "data": {"text": "Ada Lovelace\\nSkills: Python, Privacy"}}'


def test_intake_marks_order_ready_and_keeps_seller_asset():
    client = InfraiClient(api_key="test-key", opener=lambda request: FakeResponse())
    result = ResumeMarketplaceService(client).intake(
        ResumeRequest("resume.pdf", "seller-7", "buyer-3", "order-9")
    )
    assert result.candidate_name == "Ada Lovelace"
    assert result.skills == ("Python", "Privacy")
    assert result.state == "ready_for_review"
    assert result.seller_asset == "seller:seller-7/resume/Ada Lovelace"
    assert result.order_id == "order-9"


def test_ocr_omits_default_quality_but_accepts_explicit_quality():
    bodies = []

    def open_request(request):
        bodies.append(json.loads(request.data))
        return FakeResponse()

    client = InfraiClient(api_key="test-key", opener=open_request)
    client.ocr("encoded-pdf")
    client.ocr("encoded-pdf", quality="high")
    assert bodies == [
        {"pdf": "encoded-pdf", "lang": "eng"},
        {"pdf": "encoded-pdf", "lang": "eng", "quality": "high"},
    ]


def test_documented_cli_encodes_local_pdf(tmp_path, monkeypatch, capsys):
    pdf = tmp_path / "resume.pdf"
    pdf.write_bytes(b"%PDF-1.4\nexample")
    received = []

    def open_request(request):
        received.append(json.loads(request.data))
        return FakeResponse()

    monkeypatch.setattr(run_resume_intake, "InfraiClient", lambda: InfraiClient("test-key", open_request))
    monkeypatch.setattr(sys, "argv", ["run_resume_intake.py", str(pdf), "seller-7", "buyer-3", "order-9"])
    run_resume_intake.main()
    assert received[0]["pdf"] == base64.b64encode(pdf.read_bytes()).decode("ascii")
    assert json.loads(capsys.readouterr().out)["state"] == "ready_for_review"
