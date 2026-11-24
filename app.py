import os, base64, requests
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
HF_TOKEN = os.environ.get("HF_TOKEN", "").strip()
CF_ACC = os.environ.get("CF_ACCOUNT_ID", "").strip()
CF_TOK = os.environ.get("CF_API_TOKEN", "").strip()
GROQ_KEY = os.environ.get("GROQ_API_KEY", "").strip()
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
OR_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()

S = chr(47)
HF_CHAT = "https:" + S + S + "router.huggingface.co" + S + "v1" + S + "chat" + S + "completions"
HF_INF = "https:" + S + S + "router.huggingface.co" + S + "hf-inference" + S + "models" + S

def cors():
    return {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type,Authorization", "Access-Control-Allow-Methods": "GET,POST,OPTIONS"}

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ONLINE",
        "version": "MASTER-SITE-BRAIN-v36",
        "brains": {"groq": bool(GROQ_KEY), "gemini": bool(GEMINI_KEY), "openrouter": bool(OR_KEY), "hf": bool(HF_TOKEN)},
        "image_engines": {"cloudflare": bool(CF_ACC and CF_TOK), "hf_flux": bool(HF_TOKEN)}
    }), 200, cors()

def master_site_brain(system_role, user_text, max_tok=800, tout=12):
    i0 = int("0")
    # 1. Groq (Llama-3.3-70B) - استجابة فورية
    if GROQ_KEY:
        try:
            u = "https:" + S + S + "://groq.com" + S + "openai" + S + "v1" + S + "chat" + S + "completions"
            r = requests.post(u, headers={"Authorization": "Bearer " + GROQ_KEY, "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": system_role}, {"role": "user", "content": user_text}], "max_tokens": max_tok}, timeout=tout)
            if r.status_code == 200:
                t = r.json()["choices"][i0]["message"]["content"].strip()
                if t: return t
        except Exception: pass

    # 2. Google Gemini (Gemini 2.5 Flash) - فهم عميق لكل اللهجات واللغات
    if GEMINI_KEY:
        try:
            gu = "https:" + S + S + "://googleapis.com" + S + "v1beta" + S + "models" + S + "gemini-2.5-flash:generateContent?key=" + GEMINI_KEY
            r = requests.post(gu, headers={"Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": system_role + "\n\nUser request:\n" + user_text}]}]}, timeout=tout)
            if r.status_code == 200:
                t = r.json()["candidates"][i0]["content"]["parts"][i0]["text"].strip()
                if t: return t
        except Exception: pass

    # 3. OpenRouter - بوابة النماذج العالمية المتعددة
    if OR_KEY:
        try:
            ou = "https:" + S + S + "openrouter.ai" + S + "api" + S + "v1" + S + "chat" + S + "completions"
            r = requests.post(ou, headers={"Authorization": "Bearer " + OR_KEY, "Content-Type": "application/json"},
                json={"model": "google/gemini-2.0-flash-001", "messages": [{"role": "system", "content": system_role}, {"role": "user", "content": user_text}], "max_tokens": max_tok}, timeout=tout)
            if r.status_code == 200:
                t = r.json()["choices"][i0]["message"]["content"].strip()
                if t: return t
        except Exception: pass

    # 4. Hugging Face (Qwen-2.5-72B) - خط الأمان الدائم
    try:
        r = requests.post(HF_CHAT, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"},
            json={"model": "Qwen/Qwen2.5-72B-Instruct", "messages": [{"role": "system", "content": system_role}, {"role": "user", "content": user_text}], "max_tokens": max_tok}, timeout=18)
        if r.status_code == 200:
            t = r.json()["choices"][i0]["message"]["content"].strip()
            if t: return t
    except Exception: pass
    return None

def build_visual_prompt(q):
    clean = q.replace("صمم", "").replace("صورة", "").replace("صور", "").replace("ارسم", "").strip()
    if len(clean) < 2:
        return "black Mercedes AMG GT sports car speeding on coastal highway at golden sunset, shot on ARRI Alexa 65, 85mm f/1.4 lens, sharp focus, 8k raw photograph"
    sys_vis = "You are the visual director brain of DARK HORIZON FILMS. Understand any language or dialect (including Algerian Darja) and expand the request into a hyper-realistic 8K RAW camera photograph prompt in English. Include ARRI Alexa 65, 85mm f/1.4 lens, natural lighting, no watermarks. Output ONLY the English prompt."
    res = master_site_brain(sys_vis, clean, max_tok=100, tout=7)
    return res if res else ("RAW candid photograph of " + clean + ", ARRI Alexa 65, 85mm f/1.4 lens, golden hour lighting, sharp details, 8k")

@app.route("/api/image", methods=["POST", "OPTIONS"])
def api_image():
    if request.method == "OPTIONS": return ("", 204, cors())
    en_p = build_visual_prompt((request.get_json(silent=True) or {}).get("prompt", ""))
    if CF_ACC and CF_TOK:
        try:
            u = "https:" + S + S + "://cloudflare.com" + S + "client" + S + "v4" + S + "accounts" + S + CF_ACC + S + "ai" + S + "run" + S + "@cf" + S + "black-forest-labs" + S + "flux-1-schnell"
            r = requests.post(u, headers={"Authorization": "Bearer " + CF_TOK, "Content-Type": "application/json"}, json={"prompt": en_p}, timeout=18)
            if r.status_code == 200:
                b64 = r.json().get("result", {}).get("image")
                if b64: return Response(base64.b64decode(b64), mimetype="image/png", headers=cors())
        except Exception: pass
    for m in ["black-forest-labs/FLUX.1-schnell", "black-forest-labs/FLUX.1-dev", "stabilityai/stable-diffusion-xl-base-1.0"]:
        try:
            r = requests.post(HF_INF + m, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"}, json={"inputs": en_p}, timeout=20)
            if r.status_code == 200 and len(r.content) > 8000:
                return Response(r.content, mimetype="image/png", headers=cors())
        except Exception: continue
    return jsonify({"error": "busy"}), 503, cors()

@app.route("/api/chat", methods=["POST", "OPTIONS"])
def api_chat():
    if request.method == "OPTIONS": return ("", 204, cors())
    msg = (request.get_json(silent=True) or {}).get("message", "مرحبا")
    sys_core = "أنت العقل المركزي الذكي لاستوديو DARK HORIZON FILMS. تفهم كل لغات واللهجات العالمية (بما فيها الدارجة الجزائرية)، وتكتب أكواداً نظيفة متكاملة، وتولّد أفكاراً إبداعية مذهلة."
    reply = master_site_brain(sys_core, msg, max_tok=900, tout=16)
    return jsonify({"reply": reply or "⚡ عقل الموقع متصل وجاهز!"}), 200, cors()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
