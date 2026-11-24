import os, time, random, base64, threading, urllib.parse, requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
HF_TOKEN = os.environ.get("HF_TOKEN", "").strip()
CF_ACC = os.environ.get("CF_ACCOUNT_ID", "").strip()
CF_TOK = os.environ.get("CF_API_TOKEN", "").strip()

S = chr(47)
HF_CHAT = "https:" + S + S + "router.huggingface.co" + S + "v1" + S + "chat" + S + "completions"
HF_INF = "https:" + S + S + "router.huggingface.co" + S + "hf-inference" + S + "models" + S

def keep_alive():
    u = "https:" + S + S + "://onrender.com" + S
    while True:
        time.sleep(600)
        try: requests.get(u, timeout=10)
        except Exception: pass

threading.Thread(target=keep_alive, daemon=True).start()

def cors():
    return {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type,Authorization", "Access-Control-Allow-Methods": "GET,POST,OPTIONS"}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ONLINE_24_7", "engine": "NEXT-GEN-FREE-AI-v32", "hf": bool(HF_TOKEN)}), 200, cors()

def build_cinema_prompt(q):
    clean = q.replace("صمم", "").replace("صورة", "").replace("صور", "").replace("ارسم", "").strip()
    if len(clean) < 2:
        return "black Mercedes AMG GT sports car speeding on coastal highway at golden sunset, shot on ARRI Alexa 65, 85mm f/1.4 lens, sharp focus, 8k raw photograph"
    for llm in ["Qwen/Qwen3-235B-A22B", "Qwen/Qwen2.5-72B-Instruct"]:
        try:
            r = requests.post(HF_CHAT, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"},
                json={"model": llm, "messages": [
                    {"role": "system", "content": "Translate any language/dialect (including Algerian Darja) into a hyper-realistic 8K RAW camera photograph prompt in English. Include ARRI Alexa 65, 85mm f/1.4 lens, natural lighting, crisp textures, no CGI or 3D look. Output ONLY the English prompt."},
                    {"role": "user", "content": clean}
                ], "max_tokens": 110}, timeout=9)
            if r.status_code == 200:
                t = r.json()["choices"][0]["message"]["content"].strip()
                if t: return t
        except Exception: continue
    return "RAW candid photograph of " + clean + ", shot on ARRI Alexa 65, 85mm f/1.4 lens, natural golden hour lighting, sharp micro-details, 8k uhd"

def call_hf(mdl, en_p):
    try:
        r = requests.post(HF_INF + mdl, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"}, json={"inputs": en_p}, timeout=26)
        return r.content if (r.status_code == 200 and len(r.content) > 7000) else None
    except Exception: return None

def call_pollinations_flux(en_p):
    try:
        enc = urllib.parse.quote(en_p)
        u = f"https:{S}{S}image.pollinations.ai{S}prompt{S}{enc}?width=1024&height=1024&model=flux&nologo=true&seed={random.randint(1,999999)}"
        r = requests.get(u, timeout=22)
        return r.content if (r.status_code == 200 and len(r.content) > 12000) else None
    except Exception: return None

@app.route("/api/image", methods=["POST", "OPTIONS"])
def api_image():
    if request.method == "OPTIONS": return ("", 204, cors())
    en_p = build_cinema_prompt((request.get_json(silent=True) or {}).get("prompt", ""))
    top_models = [
        "black-forest-labs/FLUX.1-dev",
        "black-forest-labs/FLUX.1-schnell",
        "HiDream-ai/HiDream-I1-Full",
        "stabilityai/stable-diffusion-3.5-large"
    ]
    with ThreadPoolExecutor(max_workers=5) as ex:
        futs = [ex.submit(call_hf, m, en_p) for m in top_models] + [ex.submit(call_pollinations_flux, en_p)]
        for fut in as_completed(futs):
            img = fut.result()
            if img: return Response(img, mimetype="image/png", headers=cors())
    return jsonify({"error": "busy"}), 503, cors()

@app.route("/api/chat", methods=["POST", "OPTIONS"])
def api_chat():
    if request.method == "OPTIONS": return ("", 204, cors())
    msg = (request.get_json(silent=True) or {}).get("message", "مرحبا")
    sys_msg = "أنت العقل الخارق لاستوديو DARK HORIZON FILMS. تفهم كل لغات واللهجات العالمية (بما فيها الدارجة الجزائرية)، وتكتب أكواداً نظيفة متكاملة، وتولّد أفكاراً إبداعية مذهلة."
    for llm in ["Qwen/Qwen3-235B-A22B", "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B", "meta-llama/Llama-3.3-70B-Instruct", "Qwen/Qwen2.5-72B-Instruct"]:
        try:
            r = requests.post(HF_CHAT, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"},
                json={"model": llm, "messages": [{"role": "system", "content": sys_msg}, {"role": "user", "content": msg}], "max_tokens": 900}, timeout=22)
            if r.status_code == 200:
                reply = r.json()["choices"][0]["message"]["content"]
                reply = reply.split("</think>")[-1].strip()
                return jsonify({"reply": reply}), 200, cors()
        except Exception: continue
    return jsonify({"reply": "⚡ العقول السحابية متصلة وجاهزة!"}, 200, cors()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
