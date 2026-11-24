import os, random, requests
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
HF_TOKEN = os.environ.get("HF_TOKEN", "").strip()
HF_CHAT = "https://huggingface.co"
HF_FLUX = "https://huggingface.co"

DEFAULT_SCENES = [
    "black Mercedes AMG GT sports car speeding on coastal highway at golden sunset, dramatic orange sky, motion blur, 8k automotive photography",
    "majestic Arabian stallion running in golden desert dunes at sunset, dramatic rim lighting, shallow depth of field, 85mm f/1.4 lens, 8k photorealistic",
    "futuristic hypercars racing on neon red lit highway at night, glossy wet asphalt reflections, dynamic motion blur, 8k cinema shot"
]

def cors():
    return {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type,Authorization", "Access-Control-Allow-Methods": "GET,POST,OPTIONS"}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ONLINE", "engine": "FLUX.1-CINEMA-DIRECTOR", "token": bool(HF_TOKEN)}), 200, cors()

def build_master_prompt(q):
    clean = q.replace("صمم", "").replace("صورة", "").replace("صور", "").replace("ارسم", "").strip()
    if len(clean) < 2:
        return random.choice(DEFAULT_SCENES)
    try:
        r = requests.post(HF_CHAT, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"},
            json={"model": "Qwen/Qwen2.5-72B-Instruct", "messages": [
                {"role": "system", "content": "Translate the user request into an ultra-photorealistic 8K cinematic photograph prompt in English. Include dramatic golden hour or rim lighting, shallow depth of field (85mm f/1.4 lens), and sharp focus. Output ONLY the English prompt."},
                {"role": "user", "content": clean}
            ], "max_tokens": 100}, timeout=10)
        if r.status_code == 200:
            txt = r.json()["choices"][0]["message"]["content"].strip()
            if txt: return txt
    except Exception: pass
    return "cinematic ultra-photorealistic shot of " + clean + ", dramatic golden hour rim lighting, 85mm f/1.4 lens, shallow depth of field, 8k uhd"

@app.route("/api/image", methods=["POST", "OPTIONS"])
def api_image():
    if request.method == "OPTIONS": return ("", 204, cors())
    raw_q = (request.get_json(silent=True) or {}).get("prompt", "").strip()
    en_p = build_master_prompt(raw_q)
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
                {"role": "system", "content": "أنت المخرج الذكي لاستوديو DARK HORIZON FILMS. أجب بالعربية بذكاء واحترافية."},
                {"role": "user", "content": msg}
            ], "max_tokens": 600}, timeout=20)
        if r.status_code == 200:
            return jsonify({"reply": r.json()["choices"][0]["message"]["content"]}), 200, cors()
    except Exception: pass
    return jsonify({"reply": "⚡ الخادم متصل وجاهز!"}), 200, cors()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
