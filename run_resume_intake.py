import base64
import json
import sys
from pathlib import Path

from src.resume_marketplace import InfraiClient, ResumeMarketplaceService, ResumeRequest, handoff_dict


def main() -> None:
    if len(sys.argv) != 5:
        raise SystemExit("usage: python run_resume_intake.py PDF_REFERENCE SELLER_ID BUYER_ID ORDER_ID")
    pdf = base64.b64encode(Path(sys.argv[1]).read_bytes()).decode("ascii")
    request = ResumeRequest(pdf, *sys.argv[2:])
    result = ResumeMarketplaceService(InfraiClient()).intake(request)
    print(json.dumps(handoff_dict(result), indent=2))


if __name__ == "__main__":
    main()
