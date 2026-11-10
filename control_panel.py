"""Bilingual, read-only Streamlit control panel for reserve evidence and health reports."""
from __future__ import annotations
import json
from decimal import Decimal
from pathlib import Path
import streamlit as st

st.set_page_config(page_title="Handasa Onchain OS | هانداسا", layout="wide")
lang = st.sidebar.radio("Language / اللغة", ["العربية", "English"], index=0)
ar = lang == "العربية"
T = {
    "title": "محمد الهندسة — مراقبة الأصول على الشبكة" if ar else "Mohamed Al-Handasa — Onchain Observability",
    "caption": "لوحة قراءة فقط؛ لا توجد صلاحية توقيع أو نقل أصول" if ar else "Read-only panel; no signing or asset-transfer authority",
    "missing": "لم يتم إنشاء تقرير أرصدة بعد." if ar else "No reserve report has been generated yet.",
    "value": "القيمة المرصودة USD" if ar else "Observed value USD",
    "block": "الكتلة" if ar else "Block",
    "ownership": "الملكية متحققة" if ar else "Ownership verified",
    "assets": "الأرصدة المرصودة" if ar else "Observed assets",
    "source": "مصدر السعر" if ar else "Price source",
    "proof": "نوع الدليل" if ar else "Proof type",
}
st.title(T["title"])
st.caption(T["caption"])
report_path = Path("reports/reserves-latest.json")
if not report_path.exists():
    st.info(T["missing"])
else:
    report = json.loads(report_path.read_text())
    first, second, third = st.columns(3)
    first.metric(T["value"], f"{Decimal(report['total_value_usd']):,.2f}")
    second.metric(T["block"], f"{report['block']:,}")
    third.metric(T["ownership"], "لا" if ar else "No")
    st.subheader(T["assets"])
    st.dataframe(report["assets"], use_container_width=True)
    st.caption(f"{T['source']}: {report['price_source']} | {T['proof']}: {report['proof_type']}")
