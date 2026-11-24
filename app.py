import os, io, base64, requests
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
HF_TOKEN = os.environ.get("HF_TOKEN") or ""

def cors():
    return {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type,Authorization", "Access-Control-Allow-Methods": "GET,POST,OPTIONS"}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ONLINE", "engine": "FLUX.1-SCHNELL + SDXL ULTRA"}), 200, cors()

def translate_to_en_prompt(q):
    try:
        r = requests.post(
            "https:" + chr(47)*2 + "router.huggingface.co" + chr(47) + "v1" + chr(47) + "chat" + chr(47) + "completions",
            headers={"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"},
            json={
                "model": "Qwen/Qwen2.5-72B-Instruct",
                "messages": [
                    {"role": "system", "content": "Convert the user image request into a vivid, highly detailed English 8k cinematic photography/art prompt (20-30 words). Output ONLY the English prompt."},
                    {"role": "user", "content": q}
                ],
                "max_tokens": 90
            }, timeout=10
        )
        if r.status_code == 200:
            txt = r.json()["choices"][0]["message"]["content"].strip()
            if txt: return txt
    except Exception: pass
    return f"cinematic ultra-detailed masterpiece of {q}, dramatic lighting, sharp focus, 8k photorealistic"

@app.route("/api/image", methods=["POST", "OPTIONS"])
def api_image():
    if request.method == "OPTIONS": return ("", 204, cors())
    raw_q = (request.get_json(silent=True) or {}).get("prompt", "futuristic supercar").strip()
    en_p = translate_to_en_prompt(raw_q)

    models = [
        "black-forest-labs/FLUX.1-schnell",
        "stabilityai/stable-diffusion-xl-base-1.0",
        "ByteDance/SDXL-Lightning"
    ]
    for mdl in models:
        try:
            url = "https:" + chr(47)*2 + "router.huggingface.co" + chr(47) + "hf-inference" + chr(47) + "models" + chr(47) + mdl
            r = requests.post(url, headers={"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}, json={"inputs": en_p}, timeout=25)
            if r.status_code == 200 and len(r.content) > 4000:
                return Response(r.content, mimetype="image/jpeg", headers=cors())
        except Exception: continue

    return jsonify({"error": "busy"}), 503, cors()

@app.route("/api/chat", methods=["POST", "OPTIONS"])
def api_chat():
    if request.method == "OPTIONS": return ("", 204, cors())
    msg = (request.get_json(silent=True) or {}).get("message", "مرحبا").strip()
    try:
        r = requests.post(
            "https:" + chr(47)*2 + "router.huggingface.co" + chr(47) + "v1" + chr(47) + "chat" + chr(47) + "completions",
            headers={"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"},
            json={
                "model": "Qwen/Qwen2.5-72B-Instruct",
                "messages": [
                    {"role": "system", "content": "أنت المساعد الذكي لاستوديو DARK HORIZON FILMS. أجب بالعربية بذكاء واختصار واحترافية."},
                    {"role": "user", "content": msg}
                ],
                "max_tokens": 500
            }, timeout=15
        )
        if r.status_code == 200:
            return jsonify({"reply": r.json()["choices"][0]["message"]["content"]}), 200, cors()
    except Exception: pass
    return jsonify({"reply": "⚡ أهلاً بك في DARK HORIZON FILMS! الخادم متصل وجاهز."}), 200, cors()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
