"""Streamlit read-only control panel for reserve evidence and health reports."""
from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import streamlit as st

st.set_page_config(page_title="Handasa Onchain OS", layout="wide")
st.title("محمد الهندسة — Onchain Observability")
st.caption("لوحة قراءة فقط؛ لا توجد صلاحية توقيع أو نقل أصول")

report_path = Path("reports/reserves-latest.json")
if not report_path.exists():
    st.info("لم يتم إنشاء تقرير أرصدة بعد.")
else:
    report = json.loads(report_path.read_text())
    first, second, third = st.columns(3)
    first.metric("القيمة المرصودة USD", f"{Decimal(report['total_value_usd']):,.2f}")
    second.metric("الكتلة", f"{report['block']:,}")
    third.metric("Ownership verified", "No")
    st.subheader("الأرصدة المرصودة")
    st.dataframe(report["assets"], use_container_width=True)
    st.caption(f"مصدر السعر: {report['price_source']} | نوع الدليل: {report['proof_type']}")
