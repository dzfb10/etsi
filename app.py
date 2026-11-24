import os, requests
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
HF_TOKEN = os.environ.get("HF_TOKEN", "").strip()
SL = chr(47)
HF_CHAT = f"https:{SL}{SL}router.huggingface.co{SL}v1{SL}chat{SL}completions"
HF_INF = f"https:{SL}{SL}router.huggingface.co{SL}hf-inference{SL}models{SL}"

def cors():
    return {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type,Authorization", "Access-Control-Allow-Methods": "GET,POST,OPTIONS"}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ONLINE", "engine": "FLUX.1-PURE-MASTER", "token": bool(HF_TOKEN)}), 200, cors()

def build_prompt(q):
    try:
        r = requests.post(HF_CHAT, headers={"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"},
            json={"model": "Qwen/Qwen2.5-72B-Instruct", "messages": [
                {"role": "system", "content": "Translate into a hyper-realistic 8K photography prompt in English (25 words), cinematic lighting, sharp focus, single cohesive subject. Output ONLY the English prompt."},
                {"role": "user", "content": q}
            ], "max_tokens": 90}, timeout=10)
        if r.status_code == 200:
            i0 = int("0")
            t = r.json()["choices"][i0]["message"]["content"].strip()
            if t: return t
    except Exception: pass
    return f"hyper-realistic 8k photograph of {q}, cinematic lighting, sharp focus, single frame"

@app.route("/api/image", methods=["POST", "OPTIONS"])
def api_image():
    if request.method == "OPTIONS": return ("", 204, cors())
    q = (request.get_json(silent=True) or {}).get("prompt", "cinematic horse at sunset").strip()
    en_p = build_prompt(q)
    for mdl in ["black-forest-labs/FLUX.1-schnell", "black-forest-labs/FLUX.1-dev", "stabilityai/stable-diffusion-xl-base-1.0"]:
        try:
            r = requests.post(HF_INF + mdl, headers={"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"},
                json={"inputs": en_p}, timeout=35)
            if r.status_code == 200 and len(r.content) > 6000:
                return Response(r.content, mimetype="image/png", headers=cors())
        except Exception: continue
    return jsonify({"error": "hf_busy"}), 503, cors()

@app.route("/api/chat", methods=["POST", "OPTIONS"])
def api_chat():
    if request.method == "OPTIONS": return ("", 204, cors())
    msg = (request.get_json(silent=True) or {}).get("message", "مرحبا").strip()
    try:
        r = requests.post(HF_CHAT, headers={"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"},
            json={"model": "Qwen/Qwen2.5-72B-Instruct", "messages": [
                {"role": "system", "content": "أنت المساعد الذكي لاستوديو DARK HORIZON FILMS. أجب بالعربية بذكاء واحترافية."},
                {"role": "user", "content": msg}
            ], "max_tokens": 600}, timeout=20)
        if r.status_code == 200:
            i0 = int("0")
            return jsonify({"reply": r.json()["choices"][i0]["message"]["content"]}), 200, cors()
    except Exception: pass
    return jsonify({"reply": "⚡ الخادم متصل وجاهز!"}), 200, cors()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
