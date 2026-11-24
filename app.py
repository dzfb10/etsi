import os, time, random, base64, threading, requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
HF_TOKEN = os.environ.get("HF_TOKEN", "").strip()
CF_ACC = os.environ.get("CF_ACCOUNT_ID", "").strip()
CF_TOK = os.environ.get("CF_API_TOKEN", "").strip()

S = chr(47)
HF_CHAT = "https:" + S + S + "router.huggingface.co" + S + "v1" + S + "chat" + S + "completions"
HF_INF = "https:" + S + S + "router.huggingface.co" + S + "hf-inference" + S + "models" + S
SCENES = [
    "black Mercedes AMG GT sports car speeding on coastal highway at golden sunset, 8k automotive photography",
    "majestic Arabian stallion running in golden desert dunes at sunset, dramatic rim lighting, 8k photorealistic",
    "futuristic hypercar racing on neon red lit highway at night, glossy reflections, 8k cinema shot"
]

def keep_alive_loop():
    srv_url = "https:" + S + S + "://onrender.com" + S
    while True:
        time.sleep(600)
        try:
            requests.get(srv_url, timeout=10)
        except Exception:
            pass

threading.Thread(target=keep_alive_loop, daemon=True).start()

def cors():
    return {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Content-Type,Authorization", "Access-Control-Allow-Methods": "GET,POST,OPTIONS"}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ONLINE_24_7", "version": "RENDER-PRO-v27.0", "hf": bool(HF_TOKEN), "cf": bool(CF_ACC and CF_TOK)}), 200, cors()

def smart_prompt(q):
    clean = q.replace("صمم", "").replace("صورة", "").replace("صور", "").replace("ارسم", "").strip()
    if len(clean) < 2:
        return random.choice(SCENES)
    try:
        r = requests.post(HF_CHAT, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"},
            json={"model": "Qwen/Qwen2.5-72B-Instruct", "messages": [
                {"role": "system", "content": "Translate any language/dialect (including Algerian Darja) into a vivid 8K English photography prompt. Output ONLY the English prompt."},
                {"role": "user", "content": clean}
            ], "max_tokens": 90}, timeout=8)
        if r.status_code == 200:
            i0 = int("0")
            t = r.json()["choices"][i0]["message"]["content"].strip()
            if t:
                return t
    except Exception:
        pass
    return "cinematic ultra-photorealistic shot of " + clean + ", golden hour lighting, sharp focus, 8k"

def call_hf(mdl, en_p):
    try:
        r = requests.post(HF_INF + mdl, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"}, json={"inputs": en_p}, timeout=22)
        return r.content if (r.status_code == 200 and len(r.content) > 6000) else None
    except Exception:
        return None

def call_cf(en_p):
    if not (CF_ACC and CF_TOK):
        return None
    try:
        u = "https:" + S + S + "://cloudflare.com" + S + "client" + S + "v4" + S + "accounts" + S + CF_ACC + S + "ai" + S + "run" + S + "@cf" + S + "black-forest-labs" + S + "flux-1-schnell"
        r = requests.post(u, headers={"Authorization": "Bearer " + CF_TOK, "Content-Type": "application/json"}, json={"prompt": en_p}, timeout=20)
        b64 = r.json().get("result", {}).get("image") if r.status_code == 200 else None
        return base64.b64decode(b64) if b64 else None
    except Exception:
        return None

def call_horde(en_p):
    try:
        u_a = "https:" + S + S + "stablehorde.net" + S + "api" + S + "v2" + S + "generate" + S + "async"
        r = requests.post(u_a, headers={"Content-Type": "application/json", "apikey": "0000000000"},
            json={"prompt": en_p + " ### blurry, low quality", "params": {"width": 512, "height": 512, "steps": 14, "n": 1}}, timeout=10)
        hid = r.json().get("id")
        if not hid:
            return None
        u_s = "https:" + S + S + "stablehorde.net" + S + "api" + S + "v2" + S + "generate" + S + "status" + S + hid
        i0 = int("0")
        for _ in range(18):
            time.sleep(1.5)
            st = requests.get(u_s, timeout=8).json()
            gens = st.get("generations") or []
            if st.get("done") and gens and gens[i0].get("img"):
                iu = gens[i0].get("img")
                return requests.get(iu, timeout=12).content if iu.startswith("http") else base64.b64decode(iu)
    except Exception:
        pass
    return None

@app.route("/api/image", methods=["POST", "OPTIONS"])
def api_image():
    if request.method == "OPTIONS":
        return ("", 204, cors())
    en_p = smart_prompt((request.get_json(silent=True) or {}).get("prompt", ""))
    models = ["black-forest-labs/FLUX.1-schnell", "stabilityai/stable-diffusion-3.5-large-turbo", "Qwen/Qwen-Image", "stabilityai/stable-diffusion-xl-base-1.0"]
    with ThreadPoolExecutor(max_workers=6) as ex:
        futs = [ex.submit(call_hf, m, en_p) for m in models] + [ex.submit(call_cf, en_p), ex.submit(call_horde, en_p)]
        for fut in as_completed(futs):
            img = fut.result()
            if img:
                return Response(img, mimetype="image/png", headers=cors())
    return jsonify({"error": "busy"}), 503, cors()

@app.route("/api/chat", methods=["POST", "OPTIONS"])
def api_chat():
    if request.method == "OPTIONS":
        return ("", 204, cors())
    msg = (request.get_json(silent=True) or {}).get("message", "مرحبا")
    try:
        r = requests.post(HF_CHAT, headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"},
            json={"model": "Qwen/Qwen2.5-72B-Instruct", "messages": [
                {"role": "system", "content": "أنت العقل الذكي لاستوديو DARK HORIZON FILMS وتفهم كل اللغات واللهجات."},
                {"role": "user", "content": msg}
            ], "max_tokens": 600}, timeout=20)
        if r.status_code == 200:
            i0 = int("0")
            return jsonify({"reply": r.json()["choices"][i0]["message"]["content"]}), 200, cors()
    except Exception:
        pass
    return jsonify({"reply": "⚡ الخادم نشط وجاهز!"}), 200, cors()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
