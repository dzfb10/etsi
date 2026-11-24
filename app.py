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
    return jsonify({"status": "ONLINE", "version": "FIXED-v38"}), 200, cors()

def to_en(q):
    clean = q.replace("صمم", "").replace("صورة", "").replace("صور", "").replace("ارسم", "").strip()
    if len(clean) < 2: return "black Mercedes AMG GT sports car speeding at golden sunset, 8k raw photograph"
    if GROQ_KEY:
        try:
            u = "https:" + S + S + "://groq.com" + S + "openai" + S + "v1" + S + "chat" + S + "completions"
            r = requests.post(u, headers={"Authorization": "Bearer " + GROQ_KEY, "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": [{"role": "system", "content": "Translate into a vivid 8K English photography prompt. Output ONLY the English prompt."}, {"role": "user", "content": clean}], "max_tokens": 80}, timeout=6)
            if r.status_code == 200: return r.json()["choices"][0]["message"]["content"].strip()
        except Exception: pass
    return "RAW candid photograph of " + clean + ", golden hour lighting, sharp focus, 8k"

@app.route("/api/image", methods=["POST", "OPTIONS"])
def api_image():
    if request.method == "OPTIONS": return ("", 204, cors())
    en_p = to_en((request.get_json(silent=True) or {}).get("prompt", ""))
    if CF_ACC and CF_TOK:
        try:
            u = "https:" + S + S + "://cloudflare.com" + S + "client" + S + "v4" + S + "accounts" + S + CF_ACC + S + "ai" + S + "run" + S + "@cf" + S + "black-forest-labs" + S + "flux-1-schnell"
            r = requests.post(u, headers={"Authorization": "Bearer " + CF_TOK, "Content-Type": "application/json"}, json={"prompt": en_p}, timeout=18)
            if r.status_code == 200 and r.json().get("result", {}).get("image"):
                return Response(base64.b64decode(r.json()["result"]["image"]), mimetype="image/png", headers=cors())
        except Exception: pass
    for m in ["black-forest-labs/FLUX.1-schnell", "stabilityai/stable-diffusion-xl-base-1.0"]:
        try:
            r = requests.post(HF_INF + m, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"}, json={"inputs": en_p}, timeout=20)
            if r.status_code == 200 and len(r.content) > 6000: return Response(r.content, mimetype="image/png", headers=cors())
        except Exception: continue
    return jsonify({"error": "busy"}), 503, cors()

@app.route("/api/chat", methods=["POST", "OPTIONS"])
def api_chat():
    if request.method == "OPTIONS": return ("", 204, cors())
    data = request.get_json(silent=True) or {}
    msg = data.get("message", "مرحبا")
    hist = data.get("history") or []
    msgs = [{"role": "system", "content": "أنت العقل الذكي لاستوديو DARK HORIZON FILMS وتفهم كل اللغات واللهجات."}] + hist[-6:] + [{"role": "user", "content": msg}]
    if GROQ_KEY:
        try:
            u = "https:" + S + S + "://groq.com" + S + "openai" + S + "v1" + S + "chat" + S + "completions"
            r = requests.post(u, headers={"Authorization": "Bearer " + GROQ_KEY, "Content-Type": "application/json"}, json={"model": "llama-3.3-70b-versatile", "messages": msgs, "max_tokens": 800}, timeout=12)
            if r.status_code == 200: return jsonify({"reply": r.json()["choices"][0]["message"]["content"]}), 200, cors()
        except Exception: pass
    try:
        r = requests.post(HF_CHAT, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"}, json={"model": "Qwen/Qwen2.5-72B-Instruct", "messages": msgs, "max_tokens": 800}, timeout=18)
        if r.status_code == 200: return jsonify({"reply": r.json()["choices"][0]["message"]["content"]}), 200, cors()
    except Exception: pass
    return jsonify({"reply": "⚡ الخادم نشط وجاهز!"}, 200, cors()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
