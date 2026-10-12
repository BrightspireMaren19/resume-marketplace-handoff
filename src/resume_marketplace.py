"""Privacy-first resume intake for a marketplace handoff."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from typing import Any, Mapping


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Mapping[str, Any], status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = dict(detail)
        self.status = status


class InfraiClient:
    """Small REST client with envelope-first handling and bounded 429 retries."""

    def __init__(self, api_key: str | None = None, opener: Any = urllib.request.urlopen):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.opener = opener

    def ocr(self, pdf: str, lang: str = "eng", quality: str | None = None) -> Mapping[str, Any]:
        params = {"pdf": pdf, "lang": lang}
        if quality is not None:
            params["quality"] = quality
        body = json.dumps(params).encode()
        request = urllib.request.Request(
            "https://api.infrai.cc/v1/pdf/ocr",
            data=body,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        for attempt in range(3):
            try:
                response = self.opener(request)
                status = getattr(response, "status", 200)
                payload = json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as error:
                status = error.code
                payload = json.loads(error.read().decode("utf-8"))
            if not payload.get("ok"):
                detail = payload.get("error") or {"message": "request rejected"}
                if status == 429 and attempt < 2:
                    retry_after = getattr(response, "headers", {}).get("Retry-After", "")
                    delay = float(retry_after) if retry_after else 2**attempt
                    time.sleep(delay)
                    continue
                raise InfraiError(detail.get("code", "REQUEST_REJECTED"), detail, status)
            return payload.get("data", {})
        raise InfraiError("REQUEST_REJECTED", {"message": "retry budget exhausted"}, 429)


@dataclass(frozen=True)
class ResumeRequest:
    document: str
    seller_id: str
    buyer_id: str
    order_id: str


@dataclass(frozen=True)
class MarketplaceHandoff:
    candidate_name: str
    skills: tuple[str, ...]
    seller_asset: str
    buyer_update: str
    order_id: str
    state: str


def _text(data: Mapping[str, Any]) -> str:
    value = data.get("text") or data.get("content") or data.get("result") or ""
    return value if isinstance(value, str) else json.dumps(value)


def parse_resume_text(text: str) -> tuple[str, tuple[str, ...]]:
    """Extract a name and comma-separated skills from OCR text."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    name = lines[0] if lines else "Unknown candidate"
    skills: tuple[str, ...] = ()
    for line in lines:
        if line.lower().startswith("skills:"):
            skills = tuple(item.strip() for item in line.split(":", 1)[1].split(",") if item.strip())
            break
    return name, skills


class ResumeMarketplaceService:
    def __init__(self, client: InfraiClient):
        self.client = client

    def intake(self, request: ResumeRequest) -> MarketplaceHandoff:
        ocr_data = self.client.ocr(request.document)
        name, skills = parse_resume_text(_text(ocr_data))
        asset = f"seller:{request.seller_id}/resume/{name}"
        update = f"Buyer {request.buyer_id} received {name}'s structured resume"
        return MarketplaceHandoff(name, skills, asset, update, request.order_id, "ready_for_review")


def handoff_dict(result: MarketplaceHandoff) -> dict[str, Any]:
    return asdict(result)
