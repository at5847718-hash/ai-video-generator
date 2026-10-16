import os
from flask import Flask, render_template_string, request, jsonify
from google import genai

app = Flask(__name__)

# إعداد مفتاح API الخاص بـ Gemini 3.8 Flash
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>مولد سيناريو الفيديو بالذكاء الاصطناعي</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body { background-color: #0f172a; color: #f8fafc; font-family: system-ui, -apple-system, sans-serif; }
        .card { background-color: #1e293b; border: 1px solid #334155; border-radius: 12px; }
        .btn-primary { background-color: #6366f1; border: none; }
        .btn-primary:hover { background-color: #4f46e5; }
        .btn-success { background-color: #10b981; border: none; }
        .plan-card { border: 2px solid #334155; border-radius: 12px; padding: 20px; text-align: center; }
        .plan-card.featured { border-color: #6366f1; background-color: #1e1b4b; }
        footer { border-top: 1px solid #334155; margin-top: 50px; padding: 20px 0; }
    </style>
</head>
<body class="py-5">
    <div class="container">
        <div class="text-center mb-5">
            <h1 class="fw-bold text-light">🎬 صانع سيناريو الفيديو بالذكاء الاصطناعي</h1>
            <p class="text-secondary">أنشئ سيناريوهات فيديو احترافية باللهجات العربية المحلية وفصحى خلال ثوانٍ</p>
        </div>

        <div class="row g-4">
            <div class="col-md-7">
                <div class="card p-4 shadow">
                    <h4 class="mb-3">إنشاء سيناريو جديد</h4>
                    <form id="scriptForm">
                        <div class="mb-3">
                            <label class="form-label">عنوان الفيديو أو الفكرة الأساسية</label>
                            <input type="text" id="topic" class="form-control bg-dark text-light border-secondary" placeholder="مثال: أهم 5 نصائح للتداول الآمن" required>
                        </div>
                        <div class="mb-3">
                            <label class="form-label">اللهجة المطلوبة</label>
                            <select id="dialect" class="form-select bg-dark text-light border-secondary">
                                <option value="المصرية">اللهجة المصرية</option>
                                <option value="السودانية">اللهجة السودانية</option>
                                <option value="العربية الفصحى">العربية الفصحى</option>
                            </select>
                        </div>
                        <button type="submit" class="btn btn-primary w-100 py-2 fs-5">إنشاء السيناريو ✨</button>
                    </form>
                    <div id="result" class="mt-4 p-3 bg-dark border border-secondary rounded d-none">
                        <h5>السيناريو المقترح:</h5>
                        <pre id="scriptText" class="text-light style-pre" style="white-space: pre-wrap;"></pre>
                    </div>
                </div>
            </div>

            <div class="col-md-5">
                <div class="card p-4 shadow mb-4">
                    <h4 class="mb-3 text-center">ترقية الحساب 🚀</h4>
                    <div class="plan-card featured mb-3">
                        <h5>الخطة الشهرية</h5>
                        <h2 class="my-2">$15 <small class="fs-6 text-secondary">/ شهرياً</small></h2>
                        <p class="text-secondary small">إنشاء بلا حدود + دعم جميع اللهجات</p>
                        <a href="https://pay.binance.com" target="_blank" class="btn btn-success w-100">الدفع عبر Binance Pay</a>
                    </div>
                    <div class="plan-card">
                        <h5>الخطة السنوية (خصم مميز)</h5>
                        <h2 class="my-2">$120 <small class="fs-6 text-secondary">/ سنوياً</small></h2>
                        <p class="text-secondary small">وفر 33% مع الوصول الشامل لكافة الميزات</p>
                        <a href="https://pay.binance.com" target="_blank" class="btn btn-outline-light w-100">الدفع عبر Binance Pay</a>
                    </div>
                </div>
            </div>
        </div>

        <footer class="text-center text-secondary">
            <p class="mb-0">تم التطوير بواسطة ⚡ <strong>Abu Shukri Saadan</strong> | جميع الحقوق محفوظة © 2026</p>
        </footer>
    </div>

    <script>
        document.getElementById('scriptForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            const topic = document.getElementById('topic').value;
            const dialect = document.getElementById('dialect').value;
            const resultDiv = document.getElementById('result');
            const scriptText = document.getElementById('scriptText');
            
            scriptText.innerText = 'جاري كتابة السيناريو بالذكاء الاصطناعي... ⏳';
            resultDiv.classList.remove('d-none');

            try {
                const response = await fetch('/generate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ topic, dialect })
                });
                const data = await response.json();
                scriptText.innerText = data.script || data.error;
            } catch (err) {
                scriptText.innerText = 'حدث خطأ أثناء الاتصال بالخادم.';
            }
        });
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    topic = data.get("topic", "")
    dialect = data.get("dialect", "العربية الفصحى")

    if not topic:
        return jsonify({"error": "يرجى إدخال الموضوع"}), 400

    if not GEMINI_API_KEY:
        return jsonify({"error": "مفتاح API غير مضبوط في السيرفر"}), 500

    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
        prompt = f"اكتب سيناريو فيديو قصير احترافي وجذاب ومناسب لمنصات التيك توك والريلز بخصوص: '{topic}'. اتبع اللهجة {dialect}. قسم السيناريو إلى (المقدمة / محتوى الفيديو / الخاتمة والداعي للمتابعة)."
        
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
        )
        return jsonify({"script": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
