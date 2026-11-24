import os, asyncio, requests, edge_tts
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
HF_TOKEN = os.environ.get("HF_TOKEN", "").strip()
S = chr(47)
HF_CHAT = "https:" + S + S + "router.huggingface.co" + S + "v1" + S + "chat" + S + "completions"
HF_INF = "https:" + S + S + "router.huggingface.co" + S + "hf-inference" + S + "models" + S

def cors():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
    }

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "ONLINE", "version": "DARK-HORIZON-ORIGINAL-v11.0", "hf": bool(HF_TOKEN)}), 200, cors()

def llm_think(messages, max_tok=800, temp=0.6):
    i0 = int("0")
    try:
        r = requests.post(
            HF_CHAT,
            headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"},
            json={"model": "Qwen/Qwen2.5-72B-Instruct", "messages": messages, "max_tokens": max_tok, "temperature": temp},
            timeout=18
        )
        if r.status_code == 200:
            return r.json()["choices"][i0]["message"]["content"].strip()
    except Exception:
        pass
    return None

def craft_visual_prompt(raw_q):
    if any(k in raw_q for k in ["حصان", "خيول", "خيل"]):
        return "majestic Arabian horse galloping in golden desert dunes at sunset, dramatic warm lighting, photorealistic 8k, no text"
    if any(k in raw_q for k in ["مرسيدس", "mercedes"]):
        return "sleek black Mercedes AMG sports car speeding on coastal highway at sunset, motion blur, photorealistic 8k, no text"
    if any(k in raw_q for k in ["سيارة", "car"]):
        return "luxury sports car speeding on coastal highway at sunset, motion blur, photorealistic 8k, no text"
    if any(k in raw_q for k in ["مقام", "الشهيد"]):
        return "Maqam Echahid Martyrs Memorial monument in Algiers Algeria, three curving concrete palm leaves meeting at top, sunset, 8k, no text"

    sys_dir = (
        "Translate the user visual request from Arabic/French/any dialect into a direct English image prompt (max 20 words). "
        "CRITICAL: Output ONLY the English visual description itself. Do NOT write 'Here is', 'Sure', or any conversational words."
    )
    en = llm_think([{"role": "system", "content": sys_dir}, {"role": "user", "content": raw_q}], max_tok=60, temp=0.1)
    if en and len(en) > 4:
        clean_en = en.replace('"', '').strip() + ", photorealistic 8k, cinematic lighting, no text"
        return clean_en
    return raw_q + ", photorealistic 8k, no text"

@app.route("/api/image", methods=["POST", "OPTIONS"])
def api_image():
    if request.method == "OPTIONS":
        return ("", 204, cors())
    raw_q = (request.get_json(silent=True) or {}).get("prompt", "sports car at sunset")
    en_p = craft_visual_prompt(raw_q)
    for mdl in ["black-forest-labs/FLUX.1-schnell", "stabilityai/stable-diffusion-xl-base-1.0"]:
        try:
            r = requests.post(
                HF_INF + mdl,
                headers={"Authorization": "Bearer " + HF_TOKEN, "Content-Type": "application/json"},
                json={"inputs": en_p},
                timeout=24
            )
            if r.status_code == 200 and len(r.content) > 6000:
                return Response(r.content, mimetype="image/png", headers=cors())
        except Exception:
            continue
    return jsonify({"error": "busy"}), 503, cors()

@app.route("/api/chat", methods=["POST", "OPTIONS"])
def api_chat():
    if request.method == "OPTIONS":
        return ("", 204, cors())
    msg = (request.get_json(silent=True) or {}).get("message", "مرحبا")
    rep = llm_think([
        {"role": "system", "content": "أنت العقل الذكي لاستوديو DARK HORIZON FILMS وتفهم كل اللهجات واللغات وتساعد المستخدم بذكاء ووضوح."},
        {"role": "user", "content": msg}
    ], max_tok=800, temp=0.6)
    return jsonify({"reply": rep or "⚡ جاهز لخدمتك في DARK HORIZON FILMS."}), 200, cors()

@app.route("/api/tts", methods=["POST", "OPTIONS"])
def api_tts():
    if request.method == "OPTIONS":
        return ("", 204, cors())
    txt = (request.get_json(silent=True) or {}).get("text", "").strip()
    if not txt:
        return ("", 400, cors())
    voice = "ar-SA-HamedNeural" if any("\u0600" <= c <= "\u06FF" for c in txt) else "en-US-AndrewNeural"
    async def gen():
        comm = edge_tts.Communicate(txt[:1000], voice)
        buf = bytearray()
        async for ch in comm.stream():
            if ch["type"] == "audio":
                buf.extend(ch["data"])
        return bytes(buf)
    try:
        return Response(asyncio.run(gen()), mimetype="audio/mpeg", headers=cors())
    except Exception:
        return ("", 500, cors())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
