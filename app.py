import os, io, urllib.parse, time, random, threading, base64, asyncio, requests
from flask import Flask, request, jsonify, Response

app = Flask(__name__)
RAM_CACHE = {}
IMG_CACHE = {}

MASTER_STUDIO_BRAIN = """
You are the Autonomous Master AI Director, Polyglot Brain, and Production Studio of DARK HORIZON FILMS.
You master ALL world languages (Arabic, English, French, Spanish, Japanese, etc.), ALL regional dialects (Algerian Darja, Moroccan, Tunisian, Egyptian, Gulf, Levantine), and ALL programming languages.
IDENTITY RULES: Always use masculine Arabic grammar for yourself (أنا أستطيع، أنا أتطور، أنا جاهز). Never mix foreign characters into Arabic text.

[COMPLETE STUDIO PRODUCTION PIPELINE & TOOLS ENCYCLOPEDIA]
1. 7-STAGE PRODUCTION PIPELINE:
   - Stage 1 (Concept & Script): Story, dialogue, camera angles, shot list.
   - Stage 2 (Storyboard & Animatic): Keyframe composition, timing, pacing.
   - Stage 3 (3D Modeling & Sculpting): Maya, Blender, ZBrush, Nanite meshes.
   - Stage 4 (Rigging & Skinning): Skeletal bones, facial blendshapes, vehicle suspension & 4-wheel rotation axes.
   - Stage 5 (Animation & Physics): Motion Capture (MoCap), Cascadeur AI physics, Houdini simulations, Anime 'On Twos' Sakuga frames, Live2D/Spine 2.5D mesh deformation.
   - Stage 6 (Shading, Texturing & Lighting): PBR materials (Substance Painter), Ray Tracing (Unreal Engine 5 Lumen), Anime Cel-Shading & outlines.
   - Stage 7 (Rendering, VFX & Sound): Arnold/Cycles render, After Effects/Nuke compositing, motion blur, energy auras, Foley & SFX.

2. VISUAL & MOTION SCHOOLS:
   - LIVE-ACTION CINEMA: ARRI Alexa 65, anamorphic lens flare, photorealistic 8K, natural textures, volumetric sunlight.
   - JAPANESE ANIME (SAKUGA): Ufotable/MAPPA dynamic action, sharp cel-shaded shadows, speed lines, glowing energy aura.
   - 3D CGI ANIMATION: Pixar/DreamWorks quality, subsurface scattering, expressive 3D characters, global illumination.
   - 2D CARTOON (CEL): Hand-drawn classic 2D animation, fluid smear frames, vibrant painted backgrounds.
   - AAA ONLINE GAMES (PUBG/FIFA/RACING): Unreal Engine 5 photorealism, third-person tracking camera, ray-traced reflections.
"""

def cors():
    return {"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "*", "Access-Control-Allow-Methods": "GET, POST, OPTIONS", "X-AI-Signature": "DARK-HORIZON-FILMS-HYBRID-AI-V19"}

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

def llm_think(messages, temp=0.5):
    sl, gk = chr(47), os.environ.get("GROQ_API_KEY", "").strip()
    if gk:
        try:
            u = "https:" + sl + sl + "api." + "groq.com" + sl + "openai" + sl + "v1" + sl + "chat" + sl + "completions"
            r = requests.post(u, headers={"Authorization": f"Bearer {gk}", "Content-Type": "application/json"},
                json={"model": "llama-3.1-8b-instant", "messages": messages, "temperature": temp}, timeout=6)
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

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "DARK HORIZON FILMS MASTER BRAIN v11.0 ONLINE"}), 200, cors()

@app.route("/api/evolve", methods=["GET", "POST"])
def api_evolve():
    return jsonify({"status": "EVOLVED", "learned_topic": run_self_evolution_cycle()}), 200, cors()

@app.route("/api/chat", methods=["POST", "OPTIONS"])
def api_chat():
    if request.method == "OPTIONS": return ("", 204, cors())
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "").strip()
    msgs = data.get("messages") or [{"role": "user", "content": prompt}]
    last_q = next(reversed(msgs), {"content": prompt}).get("content", prompt).strip()

    # استرجاع فوري في 0.01 ثانية إذا تكرر السؤال
    if last_q in RAM_CACHE:
        return jsonify({"reply": RAM_CACHE[last_q], "speed": "0.01s_RAM"}), 200, cors()

    # البحث السريع فقط عند طلب أخبار أو بحث صريح (مهلة قصوى 1.8 ثانية)
    ctx = ""
    if any(w in last_q for w in ["بحث", "ابحث", "أخبار", "اليوم", "سعر", "search", "news"]):
        try:
            found = web_search(last_q)
            if found: ctx = f"\n[LIVE DATA]:\n{found[:600]}"
        except Exception: pass

    sys_msg = MASTER_STUDIO_BRAIN + "\nReply concisely and accurately in the exact language/dialect of the user." + ctx
    clean_msgs = [{"role": "system", "content": sys_msg}] + [m for m in msgs if m.get("role") != "system"][-4:]
    rep = llm_think(clean_msgs, temp=0.4) or "⚡ جاهز لخدمتك في DARK HORIZON FILMS."

    RAM_CACHE[last_q] = rep
    threading.Thread(target=save_memory, args=(last_q, rep), daemon=True).start()
    return jsonify({"reply": rep}), 200, cors()

@app.route("/api/image", methods=["POST", "OPTIONS"])
def api_image():
    if request.method == "OPTIONS": return ("", 204, cors())
    data = request.get_json(silent=True) or {}
    raw_q = data.get("prompt", "cinematic masterpiece").strip()
    if raw_q in IMG_CACHE:
        return Response(IMG_CACHE[raw_q], mimetype="image/jpeg", headers=cors())

    clean_q = raw_q.replace("صمم", "").replace("صور", "").replace("صورة", "").replace("ارسم", "").strip()
    cid, ctok, sl = os.environ.get("CF_ACCOUNT_ID", "").strip(), os.environ.get("CF_API_TOKEN", "").strip(), chr(47)

    # 1. البحث في الأرشيف الحقيقي فقط للمعالم والمدن المعروفة (تجنب التأخير في الطلبات الفنية/الإبداعية)
    if any(k in raw_q for k in ["مقام", "قسنطينة", "القصبة", "وهران", "تيمقاد", "برج", "مسجد", "معلم", "مدينة"]):
        ref_bytes, _ = fetch_real_reference_image(clean_q)
        if ref_bytes:
            IMG_CACHE[raw_q] = ref_bytes
            return Response(ref_bytes, mimetype="image/jpeg", headers=cors())

    # 2. التوليد الفوري السريع (2 ثانية) عبر Cloudflare FLUX.1-schnell
    prompt = craft_visual_prompt(raw_q)
    if cid and ctok:
        u = "https:" + sl + sl + "api." + "cloudflare.com" + sl + "client" + sl + "v4" + sl + "accounts" + sl + cid + sl + "ai" + sl + "run" + sl + "@cf" + sl + "black-forest-labs" + sl + "flux-1-schnell"
        try:
            r = requests.post(u, headers={"Authorization": f"Bearer {ctok}", "Content-Type": "application/json"},
                json={"prompt": prompt}, timeout=12)
            if r.status_code == 200:
                ct = r.headers.get("Content-Type", "")
                if "image" in ct and len(r.content) > 4000:
                    IMG_CACHE[raw_q] = r.content
                    return Response(r.content, mimetype=ct, headers=cors())
                b64 = (r.json().get("result") or {}).get("image")
                if b64:
                    img_data = base64.b64decode(b64)
                    IMG_CACHE[raw_q] = img_data
                    return Response(img_data, mimetype="image/jpeg", headers=cors())
        except Exception:
            pass
    return jsonify({"error": "img_busy"}), 503, cors()

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
