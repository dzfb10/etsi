import os, base64, requests
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
HF_TOKEN = os.environ.get("HF_TOKEN", "").strip()
CF_ACC = os.environ.get("CF_ACCOUNT_ID", "").strip()
CF_TOK = os.environ.get("CF_API_TOKEN", "").strip()
GROQ_KEY = os.environ.get("GROQ_API_KEY", "").strip()
GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
OR_KEY = os.environ.get("OPENROUTER_API_KEY", "").strip()

S = chr(47)
HF_CHAT = "https:" + S + S + "router.huggingface.co" + S + "v1" + S + "chat" + S + "completions"
HF_INF = "https:" + S + S + "router.huggingface.co" + S + "hf-inference" + S + "models" + S

def cors():
    return {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type,Authorization", "Access-Control-Allow-Methods": "GET,POST,OPTIONS"}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ONLINE", "architecture": "TRI-CORE-AI-v37", "cores": ["REASONING_MEMORY_CORE", "FLUX_VISUAL_CORE", "WAN21_VIDEO_CORE"]}), 200, cors()

def reasoning_core(messages, max_tok=900, tout=14):
    i0 = int("0")
    if GROQ_KEY:
        try:
            u = "https:" + S + S + "://groq.com" + S + "openai" + S + "v1" + S + "chat" + S + "completions"
            r = requests.post(u, headers={"Authorization": "Bearer " + GROQ_KEY, "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": messages, "max_tokens": max_tok}, timeout=tout)
            if r.status_code == 200:
                t = r.json()["choices"][i0]["message"]["content"].strip()
                if t: return t
        except Exception: pass
    if GEMINI_KEY:
        try:
            flat = "\n".join([m["role"].upper() + ": " + m["content"] for m in messages])
            gu = "https:" + S + S + "://googleapis.com" + S + "v1beta" + S + "models" + S + "gemini-2.5-flash:generateContent?key=" + GEMINI_KEY
            r = requests.post(gu, headers={"Content-Type": "application/json"}, json={"contents": [{"parts": [{"text": flat}]}]}, timeout=tout)
            if r.status_code == 200:
                t = r.json()["candidates"][i0]["content"]["parts"][i0]["text"].strip()
                if t: return t
        except Exception: pass
    if OR_KEY:
        try:
            ou = "https:" + S + S + "openrouter.ai" + S + "api" + S + "v1" + S + "chat" + S + "completions"
            r = requests.post(ou, headers={"Authorization": "Bearer " + OR_KEY, "Content-Type": "application/json"},
                json={"model": "google/gemini-2.0-flash-001", "messages": messages, "max_tokens": max_tok}, timeout=tout)
            if r.status_code == 200:
                t = r.json()["choices"][i0]["message"]["content"].strip()
                if t: return t
        except Exception: pass
    try:
        r = requests.post(HF_CHAT, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"},
            json={"model": "Qwen/Qwen2.5-72B-Instruct", "messages": messages, "max_tokens": max_tok}, timeout=18)
        if r.status_code == 200:
            t = r.json()["choices"][i0]["message"]["content"].strip()
            if t: return t
    except Exception: pass
    return None

def visual_director(q):
    clean = q.replace("صمم", "").replace("صورة", "").replace("صور", "").replace("ارسم", "").strip()
    if len(clean) < 2:
        return "black Mercedes AMG GT sports car speeding on coastal highway at golden sunset, shot on ARRI Alexa 65, 85mm f/1.4 lens, sharp focus, 8k raw photograph"
    sys_v = "Convert any language or dialect (including Algerian Darja) into a hyper-realistic 8K RAW camera photograph prompt in English. Include ARRI Alexa 65, 85mm f/1.4 lens, natural lighting, no watermarks. Output ONLY the English prompt."
    res = reasoning_core([{"role": "system", "content": sys_v}, {"role": "user", "content": clean}], max_tok=100, tout=7)
    return res if res else ("RAW candid photograph of " + clean + ", ARRI Alexa 65, 85mm f/1.4 lens, golden hour lighting, sharp details, 8k")

@app.route("/api/image", methods=["POST", "OPTIONS"])
def api_image():
    if request.method == "OPTIONS": return ("", 204, cors())
    en_p = visual_director((request.get_json(silent=True) or {}).get("prompt", ""))
    if CF_ACC and CF_TOK:
        try:
            u = "https:" + S + S + "://cloudflare.com" + S + "client" + S + "v4" + S + "accounts" + S + CF_ACC + S + "ai" + S + "run" + S + "@cf" + S + "black-forest-labs" + S + "flux-1-schnell"
            r = requests.post(u, headers={"Authorization": "Bearer " + CF_TOK, "Content-Type": "application/json"}, json={"prompt": en_p}, timeout=18)
            if r.status_code == 200:
                b64 = r.json().get("result", {}).get("image")
                if b64: return Response(base64.b64decode(b64), mimetype="image/png", headers=cors())
        except Exception: pass
    for m in ["black-forest-labs/FLUX.1-schnell", "black-forest-labs/FLUX.1-dev", "stabilityai/stable-diffusion-xl-base-1.0"]:
        try:
            r = requests.post(HF_INF + m, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"}, json={"inputs": en_p}, timeout=20)
            if r.status_code == 200 and len(r.content) > 8000:
                return Response(r.content, mimetype="image/png", headers=cors())
        except Exception: continue
    return jsonify({"error": "busy"}), 503, cors()

@app.route("/api/video", methods=["POST", "OPTIONS"])
def api_video():
    if request.method == "OPTIONS": return ("", 204, cors())
    en_p = visual_director((request.get_json(silent=True) or {}).get("prompt", ""))
    for m in ["Wan-AI/Wan2.1-T2V-1.3B", "THUDM/CogVideoX-2b"]:
        try:
            r = requests.post(HF_INF + m, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"}, json={"inputs": en_p}, timeout=35)
            if r.status_code == 200 and len(r.content) > 15000:
                return Response(r.content, mimetype="video/mp4", headers=cors())
        except Exception: continue
    return jsonify({"fallback": True}), 202, cors()

@app.route("/api/chat", methods=["POST", "OPTIONS"])
def api_chat():
    if request.method == "OPTIONS": return ("", 204, cors())
    data = request.get_json(silent=True) or {}
    msg = data.get("message", "مرحبا")
    hist = data.get("history") or []
    sys_core = "أنت العقل المركزي الذكي لاستوديو DARK HORIZON FILMS (مثل Gemini و ChatGPT). تتذكر سياق المحادثة، وتفهم الدارجة الجزائرية وكل لغات العالم، وتكتب أكواداً نظيفة متكاملة، وتولّد أفكاراً إبداعية مذهلة."
    msgs = [{"role": "system", "content": sys_core}] + hist[-6:] + [{"role": "user", "content": msg}]
    reply = reasoning_core(msgs, max_tok=1000, tout=16)
    return jsonify({"reply": reply or "⚡ النواة الثلاثية متصلة وجاهزة!"}, 200, cors()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
