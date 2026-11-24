import os, time, base64, requests
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
HF_TOKEN = os.environ.get("HF_TOKEN", "").strip()
CF_ACC = os.environ.get("CF_ACCOUNT_ID", "").strip()
CF_TOK = os.environ.get("CF_API_TOKEN", "").strip()
GROQ_KEY = os.environ.get("GROQ_API_KEY", "").strip()

S = chr(47)
HF_CHAT = "https:" + S + S + "router.huggingface.co" + S + "v1" + S + "chat" + S + "completions"
HF_INF = "https:" + S + S + "router.huggingface.co" + S + "hf-inference" + S + "models" + S

def cors():
    return {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type,Authorization", "Access-Control-Allow-Methods": "GET,POST,OPTIONS"}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ONLINE", "version": "STABLE-LIGHT-v35", "cf": bool(CF_ACC and CF_TOK), "hf": bool(HF_TOKEN)}), 200, cors()

def fast_prompt(q):
    clean = q.replace("صمم", "").replace("صورة", "").replace("صور", "").replace("ارسم", "").strip()
    if len(clean) < 2:
        return "black Mercedes AMG GT sports car speeding on coastal highway at golden sunset, 8k raw photograph"
    if GROQ_KEY:
        try:
            gu = "https:" + S + S + "://groq.com" + S + "openai" + S + "v1" + S + "chat" + S + "completions"
            r = requests.post(gu, headers={"Authorization": "Bearer " + GROQ_KEY, "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": [
                    {"role": "system", "content": "Translate into a hyper-realistic 8K RAW camera photograph prompt in English. No watermarks. Output ONLY the English prompt."},
                    {"role": "user", "content": clean}
                ], "max_tokens": 90}, timeout=5)
            if r.status_code == 200:
                i0 = int("0")
                t = r.json()["choices"][i0]["message"]["content"].strip()
                if t: return t
        except Exception: pass
    return "RAW candid photograph of " + clean + ", ARRI Alexa 65, 85mm f/1.4 lens, golden hour lighting, sharp details, 8k"

@app.route("/api/image", methods=["POST", "OPTIONS"])
def api_image():
    if request.method == "OPTIONS": return ("", 204, cors())
    en_p = fast_prompt((request.get_json(silent=True) or {}).get("prompt", ""))
    # 1. Cloudflare FLUX (الأسرع والأكثر استقراراً بدون علامة مائية)
    if CF_ACC and CF_TOK:
        try:
            u = "https:" + S + S + "://cloudflare.com" + S + "client" + S + "v4" + S + "accounts" + S + CF_ACC + S + "ai" + S + "run" + S + "@cf" + S + "black-forest-labs" + S + "flux-1-schnell"
            r = requests.post(u, headers={"Authorization": "Bearer " + CF_TOK, "Content-Type": "application/json"}, json={"prompt": en_p}, timeout=18)
            if r.status_code == 200:
                b64 = r.json().get("result", {}).get("image")
                if b64: return Response(base64.b64decode(b64), mimetype="image/png", headers=cors())
        except Exception: pass
    # 2. Hugging Face FLUX.1-schnell ثم FLUX.1-dev بالتتابع الخفيف
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
    sys_msg = "أنت العقل الذكي لاستوديو DARK HORIZON FILMS وتفهم كل اللغات واللهجات (منها الدارجة الجزائرية)."
    if GROQ_KEY:
        try:
            gu = "https:" + S + S + "://groq.com" + S + "openai" + S + "v1" + S + "chat" + S + "completions"
            r = requests.post(gu, headers={"Authorization": "Bearer " + GROQ_KEY, "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": msg}], "max_tokens": 800}, timeout=12)
            if r.status_code == 200:
                i0 = int("0")
                return jsonify({"reply": r.json()["choices"][i0]["message"]["content"]}), 200, cors()
        except Exception: pass
    try:
        r = requests.post(HF_CHAT, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"},
            json={"model": "Qwen/Qwen2.5-72B-Instruct", "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": msg}], "max_tokens": 800}, timeout=20)
        if r.status_code == 200:
            i0 = int("0")
            return jsonify({"reply": r.json()["choices"][i0]["message"]["content"]}), 200, cors()
    except Exception: pass
    return jsonify({"reply": "⚡ الخادم نشط وجاهز!"}), 200, cors()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
