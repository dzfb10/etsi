import os, base64, requests
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
    return jsonify({"status": "ONLINE", "version": "DARK HORIZON ULTRA v12.0 ALL-FREE-ENGINES", "token_ready": bool(HF_TOKEN)}), 200, cors()

def expand_prompt(q, mode="photo"):
    sys_msg = "Expand the prompt into a vivid, hyper-detailed English 8K cinematic prompt (25 words). Output ONLY the English prompt."
    try:
        r = requests.post(HF_CHAT, headers={"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"},
            json={"model": "Qwen/Qwen2.5-72B-Instruct", "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": q}], "max_tokens": 110}, timeout=10)
        if r.status_code == 200:
            t = r.json()["choices"]["message"]["content"].strip()
            if t: return t + (", ultra sharp 8k raw photograph, ARRI Alexa 65" if mode == "photo" else ", smooth cinematic camera motion, 60fps 8k")
    except Exception: pass
    return f"cinematic ultra-detailed 8k masterpiece of {q}, dramatic lighting, sharp focus"

@app.route("/api/image", methods=["POST", "OPTIONS"])
def api_image():
    if request.method == "OPTIONS": return ("", 204, cors())
    raw_q = (request.get_json(silent=True) or {}).get("prompt", "futuristic supercar").strip()
    en_p = expand_prompt(raw_q, "photo")
    for mdl in ["black-forest-labs/FLUX.1-schnell", "black-forest-labs/FLUX.1-dev", "stabilityai/stable-diffusion-xl-base-1.0"]:
        try:
            r = requests.post(HF_INF + mdl, headers={"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"},
                json={"inputs": en_p, "parameters": {"width": 1024, "height": 1024, "num_inference_steps": 4 if "schnell" in mdl else 24}}, timeout=30)
            if r.status_code == 200 and len(r.content) > 8000:
                return Response(r.content, mimetype="image/png", headers=cors())
        except Exception: continue
    return jsonify({"error": "busy"}), 503, cors()

@app.route("/api/video", methods=["POST", "OPTIONS"])
def api_video():
    if request.method == "OPTIONS": return ("", 204, cors())
    raw_q = (request.get_json(silent=True) or {}).get("prompt", "futuristic city").strip()
    en_p = expand_prompt(raw_q, "video")
    for mdl in ["Wan-AI/Wan2.1-T2V-1.3B", "THUDM/CogVideoX-2b", "ali-vilab/text-to-video-ms-1.7b"]:
        try:
            r = requests.post(HF_INF + mdl, headers={"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"},
                json={"inputs": en_p}, timeout=45)
            if r.status_code == 200 and len(r.content) > 15000:
                return Response(r.content, mimetype="video/mp4", headers=cors())
        except Exception: continue
    return jsonify({"fallback": True}), 202, cors()

@app.route("/api/remix", methods=["POST", "OPTIONS"])
def api_remix():
    if request.method == "OPTIONS": return ("", 204, cors())
    data = request.get_json(silent=True) or {}
    img_b64 = data.get("image", "").split(",")[-1]
    en_p = expand_prompt(data.get("prompt", "cinematic cyberpunk style"), "photo")
    try:
        r = requests.post(HF_INF + "timbrooks/instruct-pix2pix",
            headers={"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"},
            json={"inputs": img_b64, "parameters": {"prompt": en_p}}, timeout=30)
        if r.status_code == 200 and len(r.content) > 5000:
            return Response(r.content, mimetype="image/png", headers=cors())
    except Exception: pass
    return jsonify({"fallback": True}), 202, cors()

@app.route("/api/chat", methods=["POST", "OPTIONS"])
def api_chat():
    if request.method == "OPTIONS": return ("", 204, cors())
    msg = (request.get_json(silent=True) or {}).get("message", "مرحبا").strip()
    try:
        r = requests.post(HF_CHAT, headers={"Authorization": f"Bearer {HF_TOKEN}", "Content-Type": "application/json"},
            json={"model": "Qwen/Qwen2.5-72B-Instruct", "messages": [
                {"role": "system", "content": "أنت المساعد الذكي الشامل لاستوديو DARK HORIZON FILMS. أجب بالعربية بوضوح ودقة، واكتب الأكواد النظيفة عند الطلب."},
                {"role": "user", "content": msg}], "max_tokens": 700}, timeout=20)
        if r.status_code == 200:
            return jsonify({"reply": r.json()["choices"]["message"]["content"]}), 200, cors()
    except Exception: pass
    return jsonify({"reply": "⚡ الخادم نشط وجاهز! أعد الإرسال الآن."}), 200, cors()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
