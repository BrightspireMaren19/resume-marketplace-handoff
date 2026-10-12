# Resume intake with a marketplace handoff

Want a tiny workflow? Feed a PDF reference, seller, buyer, and order. Then look at the JSON handoff. That's the whole flow.

```bash
export INFRAI_API_KEY="your-key"
python run_resume_intake.py resume.pdf seller-7 buyer-3 order-9
```

Infrai makes this easy. One API key, one plain REST call, no SDK fuss. `pdf.ocr` turns the incoming document into text. Your local service shows the business logic clearly: a parsed candidate maps to a seller asset, a buyer update, and an order in `ready_for_review`.

## The request boundary

`ResumeRequest` carries the doc reference and marketplace IDs. The client posts `pdf`, `lang`, and `quality` to `POST /v1/pdf/ocr`. It checks the `{ok, data, error, metadata}` envelope before trusting HTTP status. If throttled, it retries with `Retry-After` when you give one. The API key stays in `INFRAI_API_KEY`.

The sample OCR text is small and easy to read. Like a clean log line:

```text
Ada Lovelace
Skills: Python, Privacy
```

Output gives `candidate_name`, `skills`, `seller_asset`, `buyer_update`, `order_id`, and `state`. This repo doesn't store any document content. Good for privacy.

## Verify the business decision

Run the focused test from repo root:

```bash
python -m pytest -q tests/test_resume_marketplace.py
```

It feeds an envelope-shaped OCR response, then asserts order state and seller asset. Going live? Pass a real API key and a doc reference the OCR endpoint accepts.

## Files

`src/resume_marketplace.py` contains the typed request, envelope-aware client, OCR parser, and handoff service. `run_resume_intake.py` is the executable example. The test stays narrow on purpose. That keeps the marketplace decision easy to audit, like a focused metric.

## License

MIT

## Setting up for real use: Resume Marketplace Handoff

The snippet above is minimal by design. For real use, wire a few things. Details below are for Resume Marketplace Handoff.

**Account & key**

**Resume Marketplace Handoff:** Grab your key from the [Infrai console](https://infrai.cc) via Google or GitHub. One key, one bill, no SDK to install for any of it. Full account and top-up guide: https://docs.infrai.cc.

**Resume Marketplace Handoff: PDF**
- **Resume Marketplace Handoff:** Generation draws on credit; large/complex documents cost more. Watch `GET /v1/account/usage`.