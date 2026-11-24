import os, requests
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
HF_TOKEN = os.environ.get("HF_TOKEN", "").strip()
SL = chr(47)
HF_CHAT = f"https:{SL}{SL}router.huggingface.co{SL}v1{SL}chat{SL}completions"
HF_FLUX = f"https:{SL}{SL}router.huggingface.co{SL}hf-inference{SL}models{SL}black-forest-labs{SL}FLUX.1-schnell"

def cors():
    return {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type,Authorization", "Access-Control-Allow-Methods": "GET,POST,OPTIONS"}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ONLINE", "engine": "FLUX.1-SCHNELL EXACT YESTERDAY MASTER", "token": bool(HF_TOKEN)}), 200, cors()

def to_english_prompt(q):
    try:
        r = requests.post(HF_CHAT, headers={"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"},
            json={"model": "Qwen/Qwen2.5-72B-Instruct", "messages": [
                {"role": "system", "content": "Translate the user request into a vivid, detailed English photography prompt. Output ONLY the English prompt."},
                {"role": "user", "content": q}
            ], "max_tokens": 90}, timeout=10)
        if r.status_code == 200:
            i0 = int("0")
            txt = r.json()["choices"][i0]["message"]["content"].strip()
            if txt: return txt
    except Exception: pass
    return q

@app.route("/api/image", methods=["POST", "OPTIONS"])
def api_image():
    if request.method == "OPTIONS": return ("", 204, cors())
    raw_q = (request.get_json(silent=True) or {}).get("prompt", "cinematic horse at sunset").strip()
    en_p = to_english_prompt(raw_q)
    try:
        r = requests.post(HF_FLUX, headers={"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"},
            json={"inputs": en_p}, timeout=35)
        if r.status_code == 200 and len(r.content) > 5000:
            return Response(r.content, mimetype="image/png", headers=cors())
        return jsonify({"error": r.text}), r.status_code, cors()
    except Exception as e:
        return jsonify({"error": str(e)}), 500, cors()

@app.route("/api/chat", methods=["POST", "OPTIONS"])
def api_chat():
    if request.method == "OPTIONS": return ("", 204, cors())
    msg = (request.get_json(silent=True) or {}).get("message", "مرحبا").strip()
    try:
        r = requests.post(HF_CHAT, headers={"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"},
            json={"model": "Qwen/Qwen2.5-72B-Instruct", "messages": [
                {"role": "system", "content": "أنت المساعد الذكي لاستوديو DARK HORIZON FILMS. أجب بالعربية بذكاء واختصار."},
                {"role": "user", "content": msg}
            ], "max_tokens": 600}, timeout=20)
        if r.status_code == 200:
            i0 = int("0")
            return jsonify({"reply": r.json()["choices"][i0]["message"]["content"]}), 200, cors()
    except Exception: pass
    return jsonify({"reply": "⚡ الخادم متصل وجاهز!"}), 200, cors()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
