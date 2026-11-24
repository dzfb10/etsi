import os, io, threading, base64, asyncio, urllib.parse, xml.etree.ElementTree as ET, requests
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
IMG_CACHE = {}

MASTER_BRAIN = """
You are the Master AI Director and Polyglot Studio Brain of DARK HORIZON FILMS.
You master ALL languages, dialects (Algerian, Gulf, Egyptian, Levantine, etc.), and programming languages.
IDENTITY: Always use masculine Arabic grammar for yourself (أنا أستطيع، أنا أتطور، أنا جاهز).
You master the 7-Stage Production Pipeline across Live-Action Cinema, Japanese Anime (Sakuga), 3D CGI, 2D Cartoon, and AAA Games.
"""

def cors():
    return {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "GET, POST, OPTIONS"}

def save_db(q, a):
    u, k = os.environ.get("SUPABASE_URL", "").strip(), os.environ.get("SUPABASE_KEY", "").strip()
    if not u or not k: return
    try:
        requests.post(f"{u}/rest/v1/archives",
            headers={"apikey": k, "Authorization": f"Bearer {k}", "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"prompt": q[:1500], "response": a[:4000]}, timeout=4)
    except Exception: pass

def llm_think(messages, temp=0.4):
    sl, gk = chr(47), os.environ.get("GROQ_API_KEY", "").strip()
    if gk:
        try:
            u = "https:" + sl + sl + "api." + "groq.com" + sl + "openai" + sl + "v1" + sl + "chat" + sl + "completions"
            r = requests.post(u, headers={"Authorization": f"Bearer {gk}", "Content-Type": "application/json"},
                json={"model": "llama-3.3-70b-versatile", "messages": messages, "temperature": temp}, timeout=12)
            if r.status_code == 200:
                ch = next(iter(r.json().get("choices") or []), None)
                if ch: return ch.get("message", {}).get("content", "").strip()
        except Exception: pass
    cid, ctok = os.environ.get("CF_ACCOUNT_ID", "").strip(), os.environ.get("CF_API_TOKEN", "").strip()
    if cid and ctok:
        try:
            u = "https:" + sl + sl + "api." + "cloudflare.com" + sl + "client" + sl + "v4" + sl + "accounts" + sl + cid + sl + "ai" + sl + "run" + sl + "@cf" + sl + "meta" + sl + "llama-3.3-70b-instruct-fp8-fast"
            r = requests.post(u, headers={"Authorization": f"Bearer {ctok}", "Content-Type": "application/json"},
                json={"messages": messages}, timeout=14)
            if r.status_code == 200:
                rep = (r.json().get("result") or {}).get("response", "").strip()
                if rep: return rep
        except Exception: pass
    return ""

def live_research(q):
    sl, enc = chr(47), urllib.parse.quote(q)
    is_ar = any("\u0600" <= c <= "\u06FF" for c in q)
    out = []
    try:
        hl = "ar&gl=DZ&ceid=DZ:ar" if is_ar else "en-US&gl=US&ceid=US:en"
        r = requests.get(f"https:{sl}{sl}://google.com{sl}rss{sl}search?q={enc}&hl={hl}", timeout=3.5)
        if r.status_code == 200:
            for it in ET.fromstring(r.text).findall(".//item")[:3]: out.append(f"[News]: {it.findtext('title','')}")
    except Exception: pass
    try:
        lang = "ar" if is_ar else "en"
        wr = requests.get(f"https:{sl}{sl}{lang}.wikipedia.org{sl}w{sl}api.php",
            params={"action": "query", "list": "search", "srsearch": q, "format": "json", "srlimit": 2},
            headers={"User-Agent": "DarkHorizonFilms/FINAL"}, timeout=3.5)
        if wr.status_code == 200:
            for x in (wr.json().get("query") or {}).get("search") or []:
                snip = x.get("snippet", "").replace('<span class="searchmatch">', "").replace("</span>", "")
                out.append(f"[Wiki - {x.get('title')}]: {snip}")
    except Exception: pass
    return "\n".join(out)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"studio": "DARK HORIZON FILMS FINAL MASTER", "status": "ONLINE"}), 200, cors()

@app.route("/api/chat", methods=["POST", "OPTIONS"])
def api_chat():
    if request.method == "OPTIONS": return ("", 204, cors())
    prompt = (request.get_json(silent=True) or {}).get("prompt", "").strip()
    ctx = f"\n[LIVE RESEARCH]:\n{live_research(prompt)}" if len(prompt.split()) >= 2 else ""
    rep = llm_think([
        {"role": "system", "content": MASTER_BRAIN + "\nReply in the exact language/dialect of the user." + ctx},
        {"role": "user", "content": prompt}
    ], temp=0.55) or "⚡ جاهز لخدمتك في DARK HORIZON FILMS."
    threading.Thread(target=save_db, args=(prompt, rep), daemon=True).start()
    return jsonify({"reply": rep}), 200, cors()

@app.route("/api/image", methods=["POST", "OPTIONS"])
def api_image():
    if request.method == "OPTIONS": return ("", 204, cors())
    raw_q = (request.get_json(silent=True) or {}).get("prompt", "cinematic supercar at sunset").strip()
    if raw_q in IMG_CACHE: return Response(IMG_CACHE[raw_q], mimetype="image/jpeg", headers=cors())
    en_prompt = llm_think([
        {"role": "system", "content": "Translate into a vivid English image prompt (max 22 words, photorealistic 8k, no text). Output ONLY the prompt."},
        {"role": "user", "content": raw_q}
    ], temp=0.15).replace('"', '').strip() or "cinematic futuristic scene, photorealistic 8k"

    cid, ctok, sl = os.environ.get("CF_ACCOUNT_ID", "").strip(), os.environ.get("CF_API_TOKEN", "").strip(), chr(47)
    if cid and ctok:
        cf_base = "https:" + sl + sl + "api." + "cloudflare.com" + sl + "client" + sl + "v4" + sl + "accounts" + sl + cid + sl + "ai" + sl + "run" + sl
        for mdl in ["@cf/black-forest-labs/flux-1-schnell", "@cf/lykon/dreamshaper-8-lcm", "@cf/stabilityai/stable-diffusion-xl-base-1.0"]:
            try:
                r = requests.post(cf_base + mdl, headers={"Authorization": f"Bearer {ctok}", "Content-Type": "application/json"},
                    json={"prompt": en_prompt + ", no text"}, timeout=15)
                if r.status_code == 200:
                    ct = r.headers.get("Content-Type", "")
                    if "image" in ct and len(r.content) > 4000: IMG_CACHE[raw_q] = r.content; return Response(r.content, mimetype=ct, headers=cors())
                    b64 = (r.json().get("result") or {}).get("image")
                    if b64: ib = base64.b64decode(b64); IMG_CACHE[raw_q] = ib; return Response(ib, mimetype="image/jpeg", headers=cors())
            except Exception: continue

    hf = os.environ.get("HF_TOKEN", "").strip()
    if hf:
        try:
            from huggingface_hub import InferenceClient
            pil_img = InferenceClient(token=hf).text_to_image(en_prompt, model="black-forest-labs/FLUX.1-schnell")
            buf = io.BytesIO(); pil_img.save(buf, format="JPEG", quality=92); ib = buf.getvalue()
            IMG_CACHE[raw_q] = ib; return Response(ib, mimetype="image/jpeg", headers=cors())
        except Exception: pass
    return jsonify({"error": "img_busy"}), 503, cors()

@app.route("/api/video", methods=["POST", "OPTIONS"])
def api_video():
    if request.method == "OPTIONS": return ("", 204, cors())
    raw_q = (request.get_json(silent=True) or {}).get("prompt", "football match").strip()
    en_kw = llm_think([
        {"role": "system", "content": "Extract 2 English keywords for searching a real action video (e.g. 'football match', 'car racing'). Output ONLY 2 words."},
        {"role": "user", "content": raw_q}
    ], temp=0.1).replace('"', '').strip() or "football match"
    sl = chr(47)
    try:
        r = requests.get(f"https:{sl}{sl}commons.wikimedia.org{sl}w{sl}api.php", params={
            "action": "query", "generator": "search", "gsrsearch": f"filetype:video {en_kw} -sign",
            "gsrnamespace": 6, "gsrlimit": 5, "prop": "imageinfo", "iiprop": "url|size", "format": "json"
        }, headers={"User-Agent": "DarkHorizonFilms/FINAL"}, timeout=5)
        if r.status_code == 200:
            for p in ((r.json().get("query") or {}).get("pages") or {}).values():
                if "sign" in p.get("title", "").lower(): continue
                ii = next(iter(p.get("imageinfo") or []), {})
                vu, sz = ii.get("url"), ii.get("size", 99999999)
                if vu and sz < 13000000 and any(ext in vu.lower() for ext in [".webm", ".mp4"]):
                    vr = requests.get(vu, headers={"User-Agent": "DarkHorizonFilms/FINAL"}, timeout=9)
                    if vr.status_code == 200 and len(vr.content) > 20000: return Response(vr.content, mimetype="video/mp4", headers=cors())
    except Exception: pass
    return jsonify({"error": "use_ai_frames"}), 503, cors()

@app.route("/api/tts", methods=["POST", "OPTIONS"])
def api_tts():
    if request.method == "OPTIONS": return ("", 204, cors())
    txt = (request.get_json(silent=True) or {}).get("text", "").strip()
    if not txt: return ("", 400, cors())
    voice = "ar-SA-HamedNeural" if any("\u0600" <= c <= "\u06FF" for c in txt) else "en-US-AndrewNeural"
    try:
        import edge_tts
        async def gen():
            comm = edge_tts.Communicate(txt[:1000], voice)
            buf = io.BytesIO()
            async for ch in comm.stream():
                if ch["type"] == "audio": buf.write(ch["data"])
            return buf.getvalue()
        return Response(asyncio.run(gen()), mimetype="audio/mpeg", headers=cors())
    except Exception: return ("", 500, cors())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))
