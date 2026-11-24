import os, requests
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
HF_TOKEN = os.environ.get("HF_TOKEN", "").strip()

def cors():
    return {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type,Authorization", "Access-Control-Allow-Methods": "GET,POST,OPTIONS"}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ONLINE", "engine": "FLUX.1-1024-PHOTOREAL-ULTRA", "has_token": bool(HF_TOKEN)}), 200, cors()

def build_cinema_prompt(q):
    try:
        r = requests.post(
            "https:" + chr(47)*2 + "router.huggingface.co" + chr(47) + "v1" + chr(47) + "chat" + chr(47) + "completions",
            headers={"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"},
            json={
                "model": "Qwen/Qwen2.5-72B-Instruct",
                "messages": [
                    {"role": "system", "content": "Translate and expand the user prompt into a hyper-realistic 8K photograph prompt in English. Include camera lens (85mm f/1.4), natural lighting, crisp textures, reflections, and high contrast. Output ONLY the English prompt."},
                    {"role": "user", "content": q}
                ],
                "max_tokens": 110
            }, timeout=10
        )
        if r.status_code == 200:
            txt = r.json()["choices"]["message"]["content"].strip()
            if txt: return txt + ", shot on ARRI Alexa 65, ultra sharp focus, intricate textures, 8k raw photo"
    except Exception: pass
    return f"hyper-realistic raw photograph of {q}, shot on ARRI Alexa 65, 85mm f/1.4 lens, dramatic cinematic lighting, sharp micro-details, realistic reflections, 8k uhd"

@app.route("/api/image", methods=["POST", "OPTIONS"])
def api_image():
    if request.method == "OPTIONS": return ("", 204, cors())
    raw_q = (request.get_json(silent=True) or {}).get("prompt", "futuristic supercar").strip()
    en_p = build_cinema_prompt(raw_q)

    models = [
        "black-forest-labs/FLUX.1-schnell",
        "black-forest-labs/FLUX.1-dev",
        "stabilityai/stable-diffusion-xl-base-1.0"
    ]
    for mdl in models:
        try:
            url = "https:" + chr(47)*2 + "router.huggingface.co" + chr(47) + "hf-inference" + chr(47) + "models" + chr(47) + mdl
            payload = {"inputs": en_p, "parameters": {"width": 1024, "height": 1024, "num_inference_steps": 4 if "schnell" in mdl else 24}}
            r = requests.post(url, headers={"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"}, json=payload, timeout=30)
            if r.status_code == 200 and len(r.content) > 8000:
                return Response(r.content, mimetype="image/png", headers=cors())
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
            return jsonify({"reply": r.json()["choices"]["message"]["content"]}), 200, cors()
    except Exception: pass
    return jsonify({"reply": "⚡ أهلاً بك في DARK HORIZON FILMS! الخادم متصل وجاهز."}), 200, cors()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
