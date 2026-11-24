import os, io, threading, base64, asyncio, urllib.parse, xml.etree.ElementTree as ET, requests
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
IMG_CACHE = {}
# NO_CACHE_FORCE_AI

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
    ], temp=0.45) or "⚡ جاهز لخدمتك في DARK HORIZON FILMS."
    threading.Thread(target=save_db, args=(prompt, rep), daemon=True).start()
    return jsonify({"reply": rep}), 200, cors()

def lightning_craft_ai_prompt(raw_q):
    # استخراج الوصف البصري والهندسي الدقيق في ضربة واحدة (0.3 ثانية عبر Groq LPU) دون تأخير متسلسل
    sys_dir = (
        "You are an Elite AI Cinema Director. Convert the user request into a vivid, highly detailed English 8k image prompt (22-28 words). "
        "Capture exact real-world appearance, iconic uniform/clothing, pose, facial features, stadium/environment, and dramatic cinematic lighting without using blocked trademarked names directly. "
        "Output ONLY the raw English prompt."
    )
    en_prompt = llm_think([{"role": "system", "content": sys_dir}, {"role": "user", "content": raw_q}], temp=0.35).replace('"', '').strip()
    if not en_prompt:
        en_prompt = f"cinematic dramatic portrait and action scene inspired by {raw_q}, ultra detailed 8k"
    final_p = en_prompt + ", photorealistic 8k cinema render, sharp focus, no text"
    threading.Thread(target=save_db, args=(f"[LIGHTNING_STYLE] {raw_q}", final_p), daemon=True).start()
    return final_p

@app.route("/api/image", methods=["POST", "OPTIONS"])
def api_image():
    if request.method == "OPTIONS": return ("", 204, cors())
    raw_q = (request.get_json(silent=True) or {}).get("prompt", "cinematic supercar").strip()
    en_prompt = lightning_craft_ai_prompt(raw_q)

    cid, ctok, sl = os.environ.get("CF_ACCOUNT_ID", "").strip(), os.environ.get("CF_API_TOKEN", "").strip(), chr(47)
    if cid and ctok:
        cf_base = "https:" + sl + sl + "api." + "cloudflare.com" + sl + "client" + sl + "v4" + sl + "accounts" + sl + cid + sl + "ai" + sl + "run" + sl
        # استخدام num_steps=4 في FLUX-1-schnell لأقصى سرعة توليد (1.5 ثانية)
        for mdl, payload in [
            ("@cf/black-forest-labs/flux-1-schnell", {"prompt": en_prompt + ", hyperrealistic, sharp focus, intricate details, 16k ultra hd, extreme micro-detail, cinema master, hyper-sharp", "num_steps": 8}),
            ("@cf/lykon/dreamshaper-8-lcm", {"prompt": en_prompt + ", sharp focus, 16k ultra hd, extreme micro-detail, cinema master, hyper-sharp", "num_steps": 8}),
            ("@cf/stabilityai/stable-diffusion-xl-base-1.0", {"prompt": en_prompt})
        ]:
            try:
                r = requests.post(cf_base + mdl, headers={"Authorization": f"Bearer {ctok}", "Content-Type": "application/json"}, json=payload, timeout=12)
                if r.status_code == 200:
                    ct = r.headers.get("Content-Type", "")
                    if "image" in ct and len(r.content) > 4000: return Response(r.content, mimetype=ct, headers=cors())
                    b64 = (r.json().get("result") or {}).get("image")
                    if b64: return Response(base64.b64decode(b64), mimetype="image/jpeg", headers=cors())
            except Exception: continue

    hf = os.environ.get("HF_TOKEN", "").strip()
    if hf:
        try:
            from huggingface_hub import InferenceClient
            pil_img = InferenceClient(token=hf).text_to_image(en_prompt, model="black-forest-labs/FLUX.1-schnell")
            buf = io.BytesIO(); pil_img.save(buf, format="JPEG", quality=92)
            return Response(buf.getvalue(), mimetype="image/jpeg", headers=cors())
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



# === SMART MERGED FEATURES ===
def save_memory(q, a):
    u, k = os.environ.get("SUPABASE_URL", "").strip(), os.environ.get("SUPABASE_KEY", "").strip()
    if not u or not k: return
    try:
        requests.post(f"{u}/rest/v1/archives",
            headers={"apikey": k, "Authorization": f"Bearer {k}", "Content-Type": "application/json", "Prefer": "return=minimal"},
            json={"prompt": q[:1500], "response": a[:4000]}, timeout=4)
    except Exception: pass

def recall_memory():
    u, k = os.environ.get("SUPABASE_URL", "").strip(), os.environ.get("SUPABASE_KEY", "").strip()
    if not u or not k: return ""
    try:
        r = requests.get(f"{u}/rest/v1/archives?select=prompt,response&order=id.desc&limit=5",
            headers={"apikey": k, "Authorization": f"Bearer {k}"}, timeout=4)
        if r.status_code == 200 and r.json():
            return "\n[STUDIO MEMORY]:\n" + "\n".join(f"- {i.get('prompt','')[:100]} -> {i.get('response','')[:140]}" for i in r.json())
    except Exception: pass
    return ""

def web_search(q):
    sl, chunks = chr(47), []
    lang = "ar" if any("\u0600" <= c <= "\u06FF" for c in q) else "en"
    try:
        wu = f"https:{sl}{sl}{lang}.wikipedia.org{sl}w{sl}api.php"
        wr = requests.get(wu, params={"action": "query", "list": "search", "srsearch": q, "format": "json", "srlimit": 2},
            headers={"User-Agent": "DarkHorizonFilms/11.0"}, timeout=4)
        if wr.status_code == 200:
            for item in (wr.json().get("query") or {}).get("search") or []:
                snip = item.get("snippet", "").replace('<span class="searchmatch">', "").replace("</span>", "")
                chunks.append(f"[Wikipedia - {item.get('title')}]: {snip}")
    except Exception: pass

    tk = os.environ.get("TAVILY_API_KEY", "").strip()
    if tk:
        try:
            u = "https:" + sl + sl + "api." + "tavily.com" + sl + "search"
            r = requests.post(u, json={"api_key": tk, "query": q, "max_results": 3}, timeout=6)
            if r.status_code == 200 and r.json().get("results"):
                for x in r.json()["results"]: chunks.append(f"[Web - {x.get('title')}]: {x.get('content','')[:240]}")
        except Exception: pass
    return "\n".join(chunks)

def fetch_real_reference_image(query_ar):
    sl = chr(47)
    # تحويل الاسم العربي إلى مصطلح البحث الدقيق في Wikimedia Commons
    en_q = llm_think([
        {"role": "system", "content": "Extract ONLY the exact English Wikipedia/Wikimedia title for this landmark, person, object, or place (e.g. 'Maqam Echahid', 'Mercedes-AMG GT', 'Constantine bridges'). Output ONLY the exact title."},
        {"role": "user", "content": query_ar}
    ], temp=0.1).replace('"', '').strip() or query_ar

    try:
        api_u = f"https:{sl}{sl}commons.wikimedia.org{sl}w{sl}api.php"
        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": f"filetype:bitmap {en_q}",
            "gsrnamespace": 6,
            "gsrlimit": 3,
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": 1024,
            "format": "json"
        }
        r = requests.get(api_u, params=params, headers={"User-Agent": "DarkHorizonFilms/18.0"}, timeout=6)
        if r.status_code == 200:
            pages = (r.json().get("query") or {}).get("pages") or {}
            for p in pages.values():
                ii = next(iter(p.get("imageinfo") or []), {})
                img_u = ii.get("thumburl") or ii.get("url")
                if img_u and any(ext in img_u.lower() for ext in [".jpg", ".jpeg", ".png"]):
                    ir = requests.get(img_u, headers={"User-Agent": "DarkHorizonFilms/18.0"}, timeout=8)
                    if ir.status_code == 200 and len(ir.content) > 15000:
                        return ir.content, en_q
    except Exception:
        pass
    return None, en_q

def craft_visual_prompt(raw_q):
    # قاموس هندسي مباشر للمعالم الشهيرة لضمان دقة الشكل المعماري 100%
    landmarks = {
        "مقام الشهيد": "Maqam Echahid Martyrs Memorial in Algiers Algeria, three massive curving white concrete fins leaning inward and joining together beneath a small ribbed Islamic dome at the top, no bird, no wings, golden sunset, photorealistic 8k, no text",
        "القصبة": "Casbah of Algiers old whitewashed Ottoman hillside houses, narrow stepped stone alleys, Mediterranean sea in background, sunny day, photorealistic 8k, no text",
        "قسنطينة": "Sidi M'Cid suspension bridge in Constantine Algeria spanning a dramatic deep rocky gorge canyon, historic buildings on cliff edge, photorealistic 8k, no text",
        "وهران": "Santa Cruz fort overlooking Oran bay and Mediterranean coast in Algeria at sunset, photorealistic 8k, no text",
        "تيمقاد": "Timgad ancient Roman ruins in Algeria with Triumphal Arch of Trajan and stone colonnades at golden hour, photorealistic 8k, no text"
    }
    for k, v in landmarks.items():
        if k in raw_q:
            return v

    # البحث المرجعي ثم إلزام الذكاء الاصطناعي بوصف الشكل الهندسي والمادي وليس ترجمة الاسم حرفياً
    ref_context = ""
    try: ref_context = web_search(raw_q)[:500]
    except Exception: pass

    sys_dir = (
        "You are a Visual Concept Director. NEVER translate landmark or object names literally (never write words like 'Martyrs' or 'Monument' alone). "
        "Instead, describe the EXACT physical geometry, architectural shape, materials, colors, and setting in vivid English (20-30 words). "
        "Output ONLY the raw English visual description. ZERO quotes, ZERO text/watermarks."
    )
    user_payload = f"User Request: {raw_q}\nReference Facts:\n{ref_context}" if ref_context else f"User Request: {raw_q}"
    en = llm_think([{"role": "system", "content": sys_dir}, {"role": "user", "content": user_payload}], temp=0.15)

    if len(en) > 4:
        if ":" in en: en = en.split(":")[-1]
        clean_en = en.replace('"', '').replace("'", "").strip() + ", photorealistic 8k, no text, no letters"
        threading.Thread(target=save_memory, args=(f"[ARCH_VISUAL] {raw_q}", clean_en), daemon=True).start()
        return clean_en

    return raw_q + ", photorealistic 8k, no text"

EVOLUTION_TOPICS = [
    "Unreal Engine 5 Lumen Nanite real-time rendering techniques",
    "Japanese anime sakuga keyframe animation and cel shading techniques",
    "Modern AI video diffusion temporal consistency and physics simulation",
    "Hollywood cinematography lighting, anamorphic lenses, and color grading",
    "AAA game character rigging, motion capture, and inverse kinematics"
]

def run_self_evolution_cycle():
    topic = random.choice(EVOLUTION_TOPICS)
    research = web_search(topic)
    if not research: return "no_data"
    insight = llm_think([
        {"role": "system", "content": "Summarize these findings into 3 actionable technical rules for filmmaking, anime, game design, and AI:"},
        {"role": "user", "content": f"Topic: {topic}\nFindings:\n{research}"}
    ], temp=0.4)
    if insight:
        save_memory(f"[AUTO_EVOLUTION] {topic}", insight)
        return topic
    return "skipped"

def background_brain_loop():
    while True:
        try: run_self_evolution_cycle()
        except Exception: pass
        time.sleep(900)

threading.Thread(target=background_brain_loop, daemon=True).start()

def api_evolve():
    return jsonify({"status": "EVOLVED", "learned_topic": run_self_evolution_cycle()}), 200, cors()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 7860)))
