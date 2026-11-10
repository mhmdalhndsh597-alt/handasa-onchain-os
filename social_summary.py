"""Create review-only Arabic/English social drafts from an observation report."""
from __future__ import annotations

import json
from pathlib import Path


def build_summary(report: dict) -> dict[str, str]:
    value = report.get("total_value_usd", "0")
    block = report.get("block", "unknown")
    ar = f"تقرير رصد الأصول: القيمة المرصودة ${value} عند الكتلة {block}. هذا دليل أرصدة عام للقراءة فقط ولا يثبت الملكية أو الملاءة."
    en = f"Asset observation: ${value} observed at block {block}. Public read-only evidence; it does not prove ownership or solvency."
    return {"arabic": ar, "english": en, "hashtags": "#Blockchain #ProofOfReserves #Onchain #ReadOnly"}


if __name__ == "__main__":
    report = json.loads(Path("reports/reserves-latest.json").read_text())
    print(json.dumps(build_summary(report), ensure_ascii=False, indent=2))
