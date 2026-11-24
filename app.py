import os, time, random, base64, threading, urllib.parse, requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
HF_TOKEN = os.environ.get("HF_TOKEN", "").strip()
CF_ACC = os.environ.get("CF_ACCOUNT_ID", "").strip()
CF_TOK = os.environ.get("CF_API_TOKEN", "").strip()

S = chr(47)
HF_CHAT = "https:" + S + S + "router.huggingface.co" + S + "v1" + S + "chat" + S + "completions"
HF_INF = "https:" + S + S + "router.huggingface.co" + S + "hf-inference" + S + "models" + S

AI_WORLD_ARCHIVE = """
[مكتبة وأرشيف الذكاء الاصطناعي العالمي المدمج في DARK HORIZON FILMS]:
1. التصوير والصور السينمائية (مستلهم من Midjourney v6 & FLUX.1 Pro): استخدام عدسات 85mm f/1.4، إضاءة الساعة الذهبية (Golden Hour / Rim Lighting)، وتفاصيل 8K RAW.
2. الإخراج والفيديو (مستلهم من Sora & Kling AI & Runway Gen-3): حركات الكاميرا الناعمة (Dolly Zoom, Drone Pan, 60FPS).
3. البرمجة والهندسة (مستلهم من DeepSeek-R1 & Qwen-72B): كتابة أكواد نظيفة كاملة قابلة للتشغيل الفوري بدون أخطاء.
"""

def keep_alive():
    u = "https:" + S + S + "://onrender.com" + S
    while True:
        time.sleep(600)
        try: requests.get(u, timeout=10)
        except Exception: pass

threading.Thread(target=keep_alive, daemon=True).start()

def cors():
    return {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type,Authorization", "Access-Control-Allow-Methods": "GET,POST,OPTIONS"}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ONLINE_24_7", "brain": "OMNI-BRAIN-WORLD-ARCHIVE-v29", "hf": bool(HF_TOKEN)}), 200, cors()

def web_live_search(query):
    try:
        q_enc = urllib.parse.quote(query)
        w_url = f"https:{S}{S}ar.wikipedia.org{S}w{S}api.php?action=query&list=search&srsearch={q_enc}&format=json&utf8=1"
        res = requests.get(w_url, headers={"User-Agent": "DarkHorizonBot/1.0"}, timeout=6).json()
        hits = res.get("query", {}).get("search", [])
        if hits:
            snippets = [h["title"] + ": " + h["snippet"].replace("<span class=\"searchmatch\">", "").replace("</span>", "") for h in hits[:3]]
            return "\n".join(snippets)
    except Exception: pass
    return ""

def smart_prompt(q):
    clean = q.replace("صمم", "").replace("صورة", "").replace("صور", "").replace("ارسم", "").strip()
    if len(clean) < 2:
        return "black Mercedes AMG GT sports car speeding on coastal highway at golden sunset, 8k automotive photography"
    try:
        r = requests.post(HF_CHAT, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"},
            json={"model": "Qwen/Qwen2.5-72B-Instruct", "messages": [
                {"role": "system", "content": "You are a master visual director inspired by Midjourney v6 and FLUX.1 Pro. Understand ANY language or dialect (including Algerian Darja) and expand even a single word into a rich, hyper-realistic 8K English photography prompt. Output ONLY the English prompt."},
                {"role": "user", "content": clean}
            ], "max_tokens": 110}, timeout=8)
        if r.status_code == 200:
            t = r.json()["choices"][0]["message"]["content"].strip()
            if t: return t
    except Exception: pass
    return "cinematic ultra-photorealistic shot of " + clean + ", golden hour rim lighting, 85mm f/1.4 lens, sharp focus, 8k"

def call_hf(mdl, en_p):
    try:
        r = requests.post(HF_INF + mdl, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"}, json={"inputs": en_p}, timeout=22)
        return r.content if (r.status_code == 200 and len(r.content) > 6000) else None
    except Exception: return None

def call_horde(en_p):
    try:
        u_a = "https:" + S + S + "stablehorde.net" + S + "api" + S + "v2" + S + "generate" + S + "async"
        r = requests.post(u_a, headers={"Content-Type": "application/json", "apikey": "0000000000"},
            json={"prompt": en_p + " ### blurry, low quality, distorted", "params": {"width": 512, "height": 512, "steps": 16, "n": 1}}, timeout=10)
        hid = r.json().get("id")
        if not hid: return None
        u_s = "https:" + S + S + "stablehorde.net" + S + "api" + S + "v2" + S + "generate" + S + "status" + S + hid
        for _ in range(18):
            time.sleep(1.5)
            st = requests.get(u_s, timeout=8).json()
            gens = st.get("generations") or []
            if st.get("done") and gens and gens[0].get("img"):
                iu = gens[0].get("img")
                return requests.get(iu, timeout=12).content if iu.startswith("http") else base64.b64decode(iu)
    except Exception: pass
    return None

@app.route("/api/image", methods=["POST", "OPTIONS"])
def api_image():
    if request.method == "OPTIONS": return ("", 204, cors())
    en_p = smart_prompt((request.get_json(silent=True) or {}).get("prompt", ""))
    models = ["black-forest-labs/FLUX.1-schnell", "stabilityai/stable-diffusion-3.5-large-turbo", "Qwen/Qwen-Image", "stabilityai/stable-diffusion-xl-base-1.0"]
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = [ex.submit(call_hf, m, en_p) for m in models] + [ex.submit(call_horde, en_p)]
        for fut in as_completed(futs):
            img = fut.result()
            if img: return Response(img, mimetype="image/png", headers=cors())
    return jsonify({"error": "busy"}), 503, cors()

@app.route("/api/chat", methods=["POST", "OPTIONS"])
def api_chat():
    if request.method == "OPTIONS": return ("", 204, cors())
    msg = (request.get_json(silent=True) or {}).get("message", "مرحبا")
    search_ctx = web_live_search(msg) if any(k in msg for k in ["بحث", "ابحث", "ما هو", "من هو", "مقال", "معلومات", "تاريخ"]) else ""
    sys_prompt = f"""أنت العقل الخارق لاستوديو DARK HORIZON FILMS.
- تفهم جميع لغات واللهجات العالمية (بما فيها الدارجة الجزائرية) وتجيب بنفس أسلوب المستخدم.
- خبير في كل لغات البرمجة وتكتب أكواداً كاملة نظيفة بدون أخطاء.
- تستلهم أفكارك من مكتبتك العالمية المدمجة: {AI_WORLD_ARCHIVE}
- إذا أعطاك المستخدم كلمة واحدة فقط (مثل: فكرة، مشروع، فيلم، تطبيق)، قم بتوليد خطة إبداعية متكاملة ومبتكرة فوراً.
{('نتائج البحث الحي من الموسوعة العالمية:\n' + search_ctx) if search_ctx else ''}"""

    for llm in ["Qwen/Qwen2.5-72B-Instruct", "meta-llama/Llama-3.3-70B-Instruct"]:
        try:
            r = requests.post(HF_CHAT, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"},
                json={"model": llm, "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": msg}], "max_tokens": 900}, timeout=22)
            if r.status_code == 200:
                return jsonify({"reply": r.json()["choices"][0]["message"]["content"]}), 200, cors()
        except Exception: continue
    return jsonify({"reply": "⚡ العقل السحابي متصل وجاهز!"}, 200, cors()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
