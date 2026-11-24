import os, random, requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
HF_TOKEN = os.environ.get("HF_TOKEN", "").strip()
SL = chr(47)
HF_CHAT = f"https:{SL}{SL}router.huggingface.co{SL}v1{SL}chat{SL}completions"
SCENES = ["black Mercedes AMG GT sports car speeding at golden sunset, 8k", "majestic Arabian stallion in golden desert dunes at sunset, 8k", "futuristic hypercar on neon highway at night, 8k"]

def cors():
    return {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type,Authorization", "Access-Control-Allow-Methods": "GET,POST,OPTIONS"}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ONLINE", "version": "ALL-10-WITH-CLOUDFLARE-v22", "token": bool(HF_TOKEN)}), 200, cors()

def smart_prompt(q):
    clean = q.replace("صمم", "").replace("صورة", "").replace("صور", "").replace("ارسم", "").strip()
    if len(clean) < 2: return random.choice(SCENES)
    try:
        r = requests.post(HF_CHAT, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"},
            json={"model": "Qwen/Qwen2.5-72B-Instruct", "messages": [{"role": "system", "content": "Translate any language/dialect into a vivid 8K English photography prompt. Output ONLY the English prompt."}, {"role": "user", "content": clean}], "max_tokens": 90}, timeout=8)
        if r.status_code == 200:
            i0 = int("0")
            t = r.json()["choices"][i0]["message"]["content"].strip()
            if t: return t
    except Exception: pass
    return f"cinematic ultra-photorealistic shot of {clean}, golden hour lighting, sharp focus, 8k"


CF_ACC = os.environ.get("CF_ACCOUNT_ID", "").strip()
CF_TOK = os.environ.get("CF_API_TOKEN", "").strip()

def call_cloudflare_flux(en_p):
    if not (CF_ACC and CF_TOK): return None
    url = f"https://cloudflare.com{CF_ACC}/ai/run/@cf/black-forest-labs/flux-1-schnell"
    r = requests.post(url, headers={"Authorization": "Bearer " + CF_TOK, "Content-Type": "application/json"}, json={"prompt": en_p}, timeout=20)
    if r.status_code == 200:
        import base64
        b64 = r.json().get("result", {}).get("image")
        if b64: return base64.b64decode(b64)
    return None

def call_hf_model(mdl, en_p):
    url = f"https:{SL}{SL}router.huggingface.co{SL}hf-inference{SL}models{SL}{mdl}"
    r = requests.post(url, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"}, json={"inputs": en_p}, timeout=24)
    if r.status_code == 200 and len(r.content) > 6000:
        return r.content
    return None

@app.route("/api/image", methods=["POST", "OPTIONS"])
def api_image():
    if request.method == "OPTIONS": return ("", 204, cors())
    en_p = smart_prompt((request.get_json(silent=True) or {}).get("prompt", ""))
    models = ["black-forest-labs/FLUX.1-schnell", "black-forest-labs/FLUX.1-dev", "ByteDance/SDXL-Lightning", "stabilityai/stable-diffusion-xl-base-1.0"]
    with ThreadPoolExecutor(max_workers=4) as ex:
        futs = [ex.submit(call_hf_model, m, en_p) for m in models] + [ex.submit(call_cloudflare_flux, en_p)]
        for fut in as_completed(futs):
            img_bytes = fut.result()
            if img_bytes:
                return Response(img_bytes, mimetype="image/png", headers=cors())
    return jsonify({"error": "busy"}), 503, cors()

@app.route("/api/chat", methods=["POST", "OPTIONS"])
def api_chat():
    if request.method == "OPTIONS": return ("", 204, cors())
    msg = (request.get_json(silent=True) or {}).get("message", "مرحبا")
    try:
        r = requests.post(HF_CHAT, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"},
            json={"model": "Qwen/Qwen2.5-72B-Instruct", "messages": [{"role": "system", "content": "أنت العقل الذكي لاستوديو DARK HORIZON FILMS وتفهم كل اللغات واللهجات."}, {"role": "user", "content": msg}], "max_tokens": 600}, timeout=20)
        if r.status_code == 200:
            i0 = int("0")
            return jsonify({"reply": r.json()["choices"][i0]["message"]["content"]}), 200, cors()
    except Exception: pass
    return jsonify({"reply": "⚡ الخادم نشط وجاهز!"}), 200, cors()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
