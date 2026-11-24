import os, random, requests
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
HF_TOKEN = os.environ.get("HF_TOKEN", "").strip()
SL = chr(47)
HF_CHAT = f"https:{SL}{SL}router.huggingface.co{SL}v1{SL}chat{SL}completions"
HF_FLUX = f"https:{SL}{SL}router.huggingface.co{SL}hf-inference{SL}models{SL}black-forest-labs{SL}FLUX.1-schnell"

SCENES = [
    "black Mercedes AMG GT sports car speeding on coastal highway at golden sunset, dramatic orange sky, motion blur, 8k automotive photography",
    "majestic Arabian stallion running in golden desert dunes at sunset, dramatic rim lighting, shallow depth of field, 85mm f/1.4 lens, 8k photorealistic",
    "futuristic hypercars racing on neon red lit highway at night, glossy wet asphalt reflections, dynamic motion blur, 8k cinema shot"
]

def cors():
    return {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type,Authorization", "Access-Control-Allow-Methods": "GET,POST,OPTIONS"}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ONLINE", "version": "MASTER-v18.0", "token": bool(HF_TOKEN)}), 200, cors()

def smart_prompt(q):
    clean = q.replace("صمم", "").replace("صورة", "").replace("صور", "").replace("ارسم", "").strip()
    if len(clean) < 2:
        return random.choice(SCENES)
    try:
        r = requests.post(HF_CHAT, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"},
            json={"model": "Qwen/Qwen2.5-72B-Instruct", "messages": [
                {"role": "system", "content": "Understand any language or dialect (including Algerian Darja) and convert the request into an ultra-photorealistic 8K English photography prompt with dramatic lighting and sharp focus. Output ONLY the English prompt."},
                {"role": "user", "content": clean}
            ], "max_tokens": 100}, timeout=10)
        if r.status_code == 200:
            i0 = int("0")
            t = r.json()["choices"][i0]["message"]["content"].strip()
            if t: return t
    except Exception: pass
    return f"cinematic ultra-photorealistic shot of {clean}, dramatic golden hour lighting, 85mm f/1.4 lens, sharp focus, 8k"

@app.route("/api/image", methods=["POST", "OPTIONS"])
def api_image():
    if request.method == "OPTIONS": return ("", 204, cors())
    q = (request.get_json(silent=True) or {}).get("prompt", "").strip()
    en_p = smart_prompt(q)
    try:
        r = requests.post(HF_FLUX, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"},
            json={"inputs": en_p}, timeout=35)
        if r.status_code == 200 and len(r.content) > 6000:
            return Response(r.content, mimetype="image/png", headers=cors())
        return jsonify({"error": r.text}), r.status_code, cors()
    except Exception as e:
        return jsonify({"error": str(e)}), 500, cors()

@app.route("/api/chat", methods=["POST", "OPTIONS"])
def api_chat():
    if request.method == "OPTIONS": return ("", 204, cors())
    msg = (request.get_json(silent=True) or {}).get("message", "مرحبا").strip()
    try:
        r = requests.post(HF_CHAT, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"},
            json={"model": "Qwen/Qwen2.5-72B-Instruct", "messages": [
                {"role": "system", "content": "أنت العقل الذكي لاستوديو DARK HORIZON FILMS. تفهم كل لغات ولهجات العالم بما فيها الدارجة الجزائرية وتجيب بذكاء واحترافية."},
                {"role": "user", "content": msg}
            ], "max_tokens": 700}, timeout=20)
        if r.status_code == 200:
            i0 = int("0")
            return jsonify({"reply": r.json()["choices"][i0]["message"]["content"]}), 200, cors()
    except Exception: pass
    return jsonify({"reply": "⚡ الخادم نشط وجاهز!"}), 200, cors()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
