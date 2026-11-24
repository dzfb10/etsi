import os, base64, requests
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
HF_TOKEN = os.environ.get("HF_TOKEN", "").strip()
CF_ACC = os.environ.get("CF_ACCOUNT_ID", "").strip()
CF_TOK = os.environ.get("CF_API_TOKEN", "").strip()
GROQ_KEY = os.environ.get("GROQ_API_KEY", "").strip()
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

S = chr(47)
HF_CHAT = "https:" + S + S + "router.huggingface.co" + S + "v1" + S + "chat" + S + "completions"
HF_INF = "https:" + S + S + "router.huggingface.co" + S + "hf-inference" + S + "models" + S

def cors():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
    }

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ONLINE",
        "engine": "CLOUDFLARE-AND-HF-PRO-CORE",
        "cloudflare": bool(CF_ACC and CF_TOK),
        "hf": bool(HF_TOKEN)
    }), 200, cors()

def ask_brain(messages, max_tok=900, tout=14):
    i0 = int("0")
    if GROQ_KEY:
        try:
            u = "https:" + S + S + "://groq.com" + S + "openai" + S + "v1" + S + "chat" + S + "completions"
            r = requests.post(u, headers={"Authorization": "Bearer " + GROQ_KEY, "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": messages, "max_tokens": max_tok}, timeout=tout)
            if r.status_code == 200:
                return r.json()["choices"][i0]["message"]["content"].strip()
        except Exception:
            pass
    if GEMINI_KEY:
        try:
            flat = "\n".join([m["role"].upper() + ": " + m["content"] for m in messages])
            gu = "https:" + S + S + "://googleapis.com" + S + "v1beta" + S + "models" + S + "gemini-2.5-flash:generateContent?key=" + GEMINI_KEY
            r = requests.post(gu, headers={"Content-Type": "application/json"}, json={"contents": [{"parts": [{"text": flat}]}]}, timeout=tout)
            if r.status_code == 200:
                return r.json()["candidates"][i0]["content"]["parts"][i0]["text"].strip()
        except Exception:
            pass
    try:
        r = requests.post(HF_CHAT, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"},
            json={"model": "Qwen/Qwen2.5-72B-Instruct", "messages": messages, "max_tokens": max_tok}, timeout=18)
        if r.status_code == 200:
            return r.json()["choices"][i0]["message"]["content"].strip()
    except Exception:
        pass
    return None

@app.route("/api/image", methods=["POST", "OPTIONS"])
def api_image():
    if request.method == "OPTIONS":
        return ("", 204, cors())
    raw_q = (request.get_json(silent=True) or {}).get("prompt", "black Mercedes AMG GT at golden sunset, 8k raw photograph")
    en_p = ask_brain([
        {"role": "system", "content": "Translate into a hyper-realistic 8K RAW camera photograph prompt in English. No watermarks. Output ONLY the English prompt."},
        {"role": "user", "content": raw_q}
    ], max_tok=90, tout=7) or raw_q

    # 1. Cloudflare Workers AI (FLUX.1-schnell)
    if CF_ACC and CF_TOK:
        try:
            u = "https:" + S + S + "://cloudflare.com" + S + "client" + S + "v4" + S + "accounts" + S + CF_ACC + S + "ai" + S + "run" + S + "@cf" + S + "black-forest-labs" + S + "flux-1-schnell"
            r = requests.post(u, headers={"Authorization": "Bearer " + CF_TOK, "Content-Type": "application/json"}, json={"prompt": en_p}, timeout=18)
            if r.status_code == 200 and r.json().get("result", {}).get("image"):
                return Response(base64.b64decode(r.json()["result"]["image"]), mimetype="image/png", headers=cors())
        except Exception:
            pass

    # 2. Hugging Face (FLUX.1-schnell & FLUX.1-dev)
    for mdl in ["black-forest-labs/FLUX.1-schnell", "black-forest-labs/FLUX.1-dev", "stabilityai/stable-diffusion-xl-base-1.0"]:
        try:
            r = requests.post(HF_INF + mdl, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"}, json={"inputs": en_p}, timeout=22)
            if r.status_code == 200 and len(r.content) > 6000:
                return Response(r.content, mimetype="image/png", headers=cors())
        except Exception:
            continue
    return jsonify({"error": "busy"}), 503, cors()

@app.route("/api/chat", methods=["POST", "OPTIONS"])
def api_chat():
    if request.method == "OPTIONS":
        return ("", 204, cors())
    data = request.get_json(silent=True) or {}
    msg = data.get("message", "مرحبا")
    hist = data.get("history") or []
    msgs = [{"role": "system", "content": "أنت العقل الخارق لاستوديو DARK HORIZON FILMS وتفهم كل اللغات واللهجات (منها الدارجة الجزائرية) وتكتب أكواداً نظيفة."}] + hist[-6:] + [{"role": "user", "content": msg}]
    reply = ask_brain(msgs, max_tok=950, tout=15)
    return jsonify({"reply": reply or "⚡ الخادم نشط وجاهز!"}), 200, cors()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
