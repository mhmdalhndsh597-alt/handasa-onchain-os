# Handasa Onchain OS
## نظام هانداسا لمراقبة الأصول على الشبكة
لوحة قراءة فقط لمراقبة الأصول العامة وصحة نقاط RPC دون توقيع أو نقل أصول.

نظام ملاحظة وتحليل موحد للأصول العامة وصحة RPC. هذا المستودع **قراءة فقط**: لا يوقّع أو يرسل أو ينقل أصولًا، ولا يثبت ملكية العناوين أو الملاءة القانونية.

## المكونات

- `asset_consolidator.py`: يقرأ أرصدة EVM العامة عند كتلة محددة ويحسب قيمة USD باستخدام أسعار يمررها المشغل ويحدد مصدرها.
- `system_guard.py`: يفحص RPC الأساسي والبدائل ويخرج حالة فشل واضحة. لا يعيد تشغيل خدمة دائمة لأن GitHub Actions بيئة مؤقتة.
- `control_panel.py`: لوحة Streamlit للعرض فقط.
- `social_summary.py`: مسودات عربية وإنكليزية للمراجعة، دون نشر تلقائي.
- `.github/workflows/onchain-observability.yml`: فحص دوري كل 5 دقائق ورفع Artifacts.

## المتغيرات

### Secrets

- `NETWORK_RPC_URL` — RPC قراءة فقط.
- `NETWORK_RPC_URLS` — اختياري؛ RPCs مفصولة بفواصل لفحص الصحة.

### Actions Variables

- `CHAIN_ID`
- `WATCHED_ADDRESSES` — عناوين عامة مفصولة بفواصل.
- `NATIVE_SYMBOL` — مثل `ETH`.
- `ASSET_PRICES_USD` — JSON مثل `{"ETH":2500}` مع مصدر موثق.
- `PRICE_SOURCE` — وصف مصدر الأسعار ووقت اللقطة.

## التشغيل المحلي

```bash
export NETWORK_RPC_URL="https://read-only-rpc.example"
export WATCHED_ADDRESSES="0x..."
export NATIVE_SYMBOL="ETH"
export ASSET_PRICES_USD='{"ETH":2500}'
python asset_consolidator.py
```

للوحة:

```bash
pip install -r requirements-dashboard.txt
streamlit run control_panel.py
```

## حدود الإثبات

التقرير هو **ملاحظة أرصدة عامة** عند رقم كتلة، وليس Proof of Reserves قانونيًا أو إثبات ملكية أو إثبات ملاءة. لا تُستنتج منه “أرباح ملايين” أو سيطرة على شبكة دون مصادر وعقود وصلاحيات قابلة للتحقق.

## التشغيل المستمر

GitHub Actions لا يضمن عملية 24/7 ولا يعيد تشغيل daemon مستمرًا. الجدولة كل 5 دقائق مناسبة للفحص الدوري وقد تتأخر بسبب ازدحام GitHub. للاستمرارية الصارمة يلزم مشغل خدمة دائم مع ضوابط منفصلة، وليس صلاحية توقيع أو نقل.
