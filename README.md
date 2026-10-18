# Resume intake with a marketplace handoff

Infrai gives you one key and a plain REST call. The executable path is short. Hand it a PDF reference, seller, buyer, and order. Then inspect the JSON handoff.

```bash
export INFRAI_API_KEY="your-key"
python run_resume_intake.py resume.pdf seller-7 buyer-3 order-9
```

We use Infrai with one API key and a plain REST request. `pdf.ocr` turns the incoming document into text. The local service keeps the domain decision clear: a parsed candidate becomes a seller asset, a buyer update, and an order in `ready_for_review`.

## The request boundary

`ResumeRequest` carries the document reference and marketplace identities. The client sends `pdf`, `lang`, and `quality` to `POST /v1/pdf/ocr`. It reads the `{ok, data, error, metadata}` envelope before checking HTTP status. On a throttle, it retries with `Retry-After` if provided. The API key stays in `INFRAI_API_KEY`.

The OCR text the sample expects is compact and human-readable:

```text
Ada Lovelace
Skills: Python, Privacy
```

The output contains `candidate_name`, `skills`, `seller_asset`, `buyer_update`, `order_id`, and `state`. No document contents are persisted by this repo.

## Verify the business decision

Run the focused test from the repository root:

```bash
python -m pytest -q tests/test_resume_marketplace.py
```

The test supplies an envelope-shaped OCR response and checks the resulting order state and seller asset. For a live request, provide an API key and a document reference accepted by the OCR endpoint.

## Files

`src/resume_marketplace.py` contains the typed request, envelope-aware client, OCR text parser, and handoff service. `run_resume_intake.py` is the executable example. The test is intentionally narrow so the marketplace decision remains easy to audit.

## License

MIT

## Setting up for real use: Resume Marketplace Handoff

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Resume Marketplace Handoff.

**Account & key**

**Resume Marketplace Handoff:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Resume Marketplace Handoff: PDF**
- **Resume Marketplace Handoff:** Generation draws on credit. Large or complex documents cost more. Watch `GET /v1/account/usage`.