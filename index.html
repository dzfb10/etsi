const HORDE_API = String.fromCharCode(104,116,116,112,115,58,47,47,115,116,97,98,108,101,104,111,114,100,101,46,110,101,116,47,97,112,105,47,118,50);
const CF_WORKER = "\x68\x74\x74\x70\x73\x3a\x2f\x2f\x64\x61\x72\x6b\x2d\x68\x6f\x72\x69\x7a\x6f\x6e\x2d\x61\x69\x2e\x6f\x6e\x72\x65\x6e\x64\x65\x72\x2e\x63\x6f\x6d";


fetch(CF_WORKER + "/", { mode: "no-cors" }).catch(() => {});
let history = [], attData = null, attType = null, attName = "", imgActionMode = "vision";

function toggleMenu() {
  const m = document.getElementById("plusMenu");
  m.style.display = (m.style.display === "flex") ? "none" : "flex";
}
function quickFill(t) {
  const q = document.getElementById("q");
  q.value = t; q.focus();
  document.getElementById("plusMenu").style.display = "none";
}
function clearAttach() {
  attData = null; attType = null; attName = "";
  const fi = document.getElementById("fileInp");
  if (fi) fi.value = "";
  document.getElementById("previewBar").style.display = "none";
}
function addMsg(h, c) {
  const w = document.getElementById("welcomeBox");
  if (w) w.remove();
  const ch = document.getElementById("chat");
  const d = document.createElement("div");
  d.className = "msg " + c;
  d.innerHTML = h;
  ch.appendChild(d);
  ch.scrollTop = ch.scrollHeight;
  return d;
}

async function applyLogoLightweight(imgUrl) {
  return await new Promise(res => {
    const im = new Image(); im.crossOrigin = "anonymous";
    im.onload = async () => {
      const c = document.createElement("canvas");
      c.width = 896; c.height = 896;
      const ctx = c.getContext("2d");
      ctx.drawImage(im, 0, 0, 896, 896);
      const customLogo = localStorage.getItem("dh_media_logo");
      if (customLogo) {
        await new Promise(r2 => {
          const lm = new Image();
          lm.onload = () => {
            ctx.save(); ctx.globalAlpha = 0.92;
            ctx.beginPath(); ctx.roundRect(790, 790, 82, 82, 16); ctx.clip();
            ctx.drawImage(lm, 790, 790, 82, 82); ctx.restore(); r2();
          };
          lm.onerror = () => r2(); lm.src = customLogo;
        });
      } else {
        ctx.save();
        ctx.fillStyle = "rgba(6, 9, 19, 0.78)";
        ctx.beginPath(); ctx.roundRect(686, 834, 188, 38, 10); ctx.fill();
        ctx.strokeStyle = "#38bdf8"; ctx.lineWidth = 1.5; ctx.stroke();
        ctx.fillStyle = "#38bdf8"; ctx.font = "bold 15px sans-serif"; ctx.textAlign = "center";
        ctx.fillText("DARK HORIZON ✦", 780, 858);
        ctx.restore();
      }
      res(c.toDataURL("image/jpeg", 0.92));
    };
    im.onerror = () => res(imgUrl);
    im.src = imgUrl;
  });
}

function buildProVisualPrompt(rawText) {
  const dict = {
    "قرصان": "cinematic portrait of a legendary pirate captain on wooden galleon ship in stormy ocean at sunset, realistic skin texture, dramatic lighting",
    "جزيرة": "epic pirate galleon fleet attacking a mysterious treasure island at sunset, cannons firing, cinematic waves",
    "حصان": "majestic Arabian stallion running in golden desert dunes at sunset, dust particles, dramatic rim lighting",
    "محارب": "epic armored desert warrior holding glowing sword under starry night sky, realistic armor reflections",
    "مدينة": "futuristic cyberpunk metropolis at night with neon reflections on wet streets, photorealistic",
    "طبيعة": "breathtaking emerald mountain valley with crystal waterfall and golden sunbeams",
    "أسد": "majestic golden lion standing on rocky cliff at sunrise, sharp fur detail",
    "أنمي": "high budget anime masterpiece scene, dynamic action pose, vibrant cinematic lighting"
  };
  let base = rawText.replace(/صمم لي صورة 8K واقعية لـ?|حول النص إلى فيديو سينمائي:|صمم|صورة|صور|ارسم|مشهد|فيديو/g, "").trim();
  for (const [ar, en] of Object.entries(dict)) {
    if (base.includes(ar)) base = en + ", " + base;
  }
  if (!base) base = "majestic Arabian horse in golden desert sunset, dramatic cinematic lighting";
  return base.slice(0, 200) + ", ultra photorealistic, 8k DSLR photography, natural lighting, sharp focus, masterpiece";
}

// 1. شبكة AI Horde العالمية (كروت RTX 4090 / A100 الموزعة - تدعم CORS 100% وتعمل بأقوى نماذج الواقعية)
async function generateViaGlobalHorde(enPrompt) {
  const r1 = await fetch(HORDE_API + "/generate/async", {
    method: "POST",
    headers: { "Content-Type": "application/json", "apikey": "0000000000", "Client-Agent": "DarkHorizon:1.0:user" },
    body: JSON.stringify({
      prompt: enPrompt + " ### blurry, low quality, distorted, cartoon, watermark, ugly, deformed",
      params: { sampler_name: "k_euler_a", cfg_scale: 7.5, width: 512, height: 512, steps: 15, n: 1 },
      models: ["Juggernaut XL", "AlbedoBase XL (SDXL)", "DreamShaper XL", "Deliberate", "EpicRealism"],
      nsfw: false
    })
  });
  if (!r1.ok) throw new Error("horde_init_" + r1.status);
  const j1 = await r1.json();
  if (!j1 || !j1.id) throw new Error("no_id");

  for (let i = 0; i < 30; i++) {
    await new Promise(r => setTimeout(r, 2000));
    const chk = await fetch(HORDE_API + "/generate/check/" + j1.id, {
      headers: { "Client-Agent": "DarkHorizon:1.0:user" }
    });
    if (!chk.ok) continue;
    const st = await chk.json();
    if (st && st.done) {
      const fin = await fetch(HORDE_API + "/generate/status/" + j1.id, {
        headers: { "Client-Agent": "DarkHorizon:1.0:user" }
      });
      const fd = await fin.json();
      const gen = fd && fd.generations ? fd.generations.at(0) : null;
      if (gen && gen.img) {
        const imgSrc = gen.img.startsWith("http") ? gen.img : ("data:image/webp;base64," + gen.img);
        return { url: imgSrc, engine: (gen.model || "Juggernaut-XL-GPU") };
      }
      break;
    }
  }
  throw new Error("horde_timeout");
}

async function generateSuperImage(rawPrompt) {
  const enPrompt = buildProVisualPrompt(rawPrompt);
  const racers = [
    generateViaGlobalHorde(enPrompt),
    (async () => {
      const r = await fetch(CF_WORKER + "/image", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: enPrompt, width: 896, height: 896 })
      });
      if (!r.ok) throw new Error("cf_fail");
      const d = await r.json();
      if (d && d.image_url) return { url: d.image_url, engine: d.engine || "Cloudflare-FLUX" };
      throw new Error("cf_empty");
    })(),
    (async () => {
      if (!window.puter || !puter.ai || !puter.ai.txt2img) throw new Error("noputer");
      const el = await puter.ai.txt2img(enPrompt, { model: "google/imagen-4.0-ultra" });
      if (el && el.src) return { url: el.src, engine: "Google-Imagen-4-Ultra" };
      throw new Error("empty");
    })()
  ];
  try {
    const win = await Promise.any(racers);
    win.url = await applyLogoLightweight(win.url);
    return win;
  } catch (e) {
    return null;
  }
}
async function instantGlobalChat(userPrompt) {
  const sys = "أنت DARK HORIZON AI، مساعد ذكاء اصطناعي خبير تتحدث بالعربية بطلاقة ووضوح.";
  const chatRacers = [
    (async () => {
      const r = await fetch(CF_WORKER + "/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: [{ role: "system", content: sys }, ...history.slice(-6)] })
      });
      if (!r.ok) throw new Error("cf_chat");
      const d = await r.json();
      if (d && d.reply) return d.reply;
      throw new Error("cf_empty");
    })(),
    (async () => {
      if (!window.puter || !puter.ai || !puter.ai.chat) throw new Error("noputer");
      const pr = await puter.ai.chat(sys + "\n\n" + userPrompt);
      const t = (typeof pr === "string") ? pr : (pr?.message?.content || String(pr));
      if (t && t.length > 1) return t;
      throw new Error("p_empty");
    })(),
    (async () => {
      const r1 = await fetch(HORDE_API + "/generate/text/async", {
        method: "POST",
        headers: { "Content-Type": "application/json", "apikey": "0000000000", "Client-Agent": "DarkHorizon:1.0:user" },
        body: JSON.stringify({ prompt: sys + "\nالمستخدم: " + userPrompt + "\nالمساعد:", params: { max_length: 250, temperature: 0.7 } })
      });
      if (!r1.ok) throw new Error("ht1");
      const j1 = await r1.json();
      for (let i = 0; i < 15; i++) {
        await new Promise(r => setTimeout(r, 1500));
        const st = await (await fetch(HORDE_API + "/generate/text/status/" + j1.id)).json();
        if (st && st.done && st.generations && st.generations.at(0)) return st.generations.at(0).text.trim();
      }
      throw new Error("ht_timeout");
    })()
  ];
  try { return await Promise.any(chatRacers); } catch (e) { return "⚠️ يرجى المحاولة مرة أخرى."; }
}

function playStudioVoice(text) {
  const clean = text.replace(/[*#|_~`(){}<>\/\\•\-:؛،."'!؟]/g, " ").trim();
  if (!clean) return;
  if ("speechSynthesis" in window) {
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(clean);
    u.lang = "ar-SA";
    window.speechSynthesis.speak(u);
  }
}

async function buildCinemaVideo(promptTxt, uploadedImgUrl, targetBubble) {
  targetBubble.innerHTML = "🎬 جاري توليد الفيديو عبر خادم Render (Gemini 2.0 / Cloudflare) وكروت GPU...";

  // محاولة مسار Text-to-Video / Image-to-Video الحقيقي على خادم Render أولاً
  try {
    const ep = uploadedImgUrl ? "/i2v" : "/video";
    const bodyData = uploadedImgUrl ? { image: uploadedImgUrl, prompt: promptTxt } : { prompt: promptTxt };
    const rv = await fetch(CF_WORKER + ep, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(bodyData)
    });
    if (rv.ok) {
      const vd = await rv.json();
      const vSrc = vd.video_url || vd.url || vd.video;
      if (vSrc) {
        targetBubble.innerHTML = `<div>🎬 تم إنتاج الفيديو عبر خادم Render (Text-to-Video):</div><video src="${vSrc}" controls autoplay loop playsinline></video><div class="actions"><a class="act-btn" href="${vSrc}" download="DarkHorizon_Render.mp4">⬇️ تحميل الفيديو</a></div>`;
        return;
      }
    }
  } catch (e) {}

  let frames = uploadedImgUrl ? [uploadedImgUrl] : [];
  if (!frames.length) {
    const r1 = await generateSuperImage(promptTxt + ", wide cinematic establishing shot");
    const r2 = await generateSuperImage(promptTxt + ", dramatic close up action shot");
    if (r1 && r1.url) frames.push(r1.url);
    if (r2 && r2.url) frames.push(r2.url);
  }
  if (!frames.length) { targetBubble.innerHTML = "⚠️ كروت GPU العالمية مشغولة حالياً، أعد المحاولة."; return; }

  const canvas = document.createElement("canvas");
  canvas.width = 640; canvas.height = 640;
  const ctx = canvas.getContext("2d");

  const validImgs = (await Promise.all(frames.map(src => new Promise(res => {
    const im = new Image(); im.crossOrigin = "anonymous";
    im.onload = () => res(im); im.onerror = () => res(null); im.src = src;
  })))).filter(Boolean);

  if (!validImgs.length) { targetBubble.innerHTML = "⚠️ تعذر معالجة الإطارات."; return; }

  const stream = canvas.captureStream(24);
  const recorder = new MediaRecorder(stream, { mimeType: "video/webm" });
  const chunks = [];
  recorder.ondataavailable = e => { if (e.data.size > 0) chunks.push(e.data); };
  recorder.onstop = () => {
    const vUrl = URL.createObjectURL(new Blob(chunks, { type: "video/webm" }));
    targetBubble.innerHTML = `<div>🎬 تم إنتاج الفيديو السينمائي مع اللوغو الخاص بك:</div><video src="${vUrl}" controls autoplay loop playsinline></video><div class="actions"><a class="act-btn" href="${vUrl}" download="DarkHorizon_Cinema.webm">⬇️ تحميل الفيديو</a><button type="button" class="act-btn" onclick="playStudioVoice('${promptTxt.replace(/'/g, "")}')">🎙️ تعليق صوتي</button></div>`;
    playStudioVoice(promptTxt);
  };

  recorder.start();
  const totalFrames = 96;
  const perShot = totalFrames / validImgs.length;
  let f = 0;

  const timer = setInterval(() => {
    const idx = Math.min(Math.floor(f / perShot), validImgs.length - 1);
    const localP = (f % perShot) / perShot;
    const img = validImgs.at(idx);
    const scale = 1.0 + localP * 0.14;
    const w = 640 * scale, h = 640 * scale;
    ctx.clearRect(0, 0, 640, 640);
    ctx.drawImage(img, (640 - w) / 2, (640 - h) * 0.22, w, h);
    if (++f >= totalFrames) { clearInterval(timer); recorder.stop(); }
  }, 1000 / 24);
}
async function send() {
  const inp = document.getElementById("q"), val = inp.value.trim();
  if (!val && !attData) return;
  const cd = attData, ct = attType, cn = attName, curImgMode = imgActionMode;
  clearAttach(); inp.value = "";
  let uh = val ? "<div>" + val.replace(/</g, "&lt;") + "</div>" : "";
  if (ct === "img" && cd) uh += "<img src='" + cd + "'>";
  if (ct === "doc") uh += "<div style='font-size:12px;margin-top:4px'>📄 " + cn + "</div>";
  addMsg(uh, "user");
  const wait = addMsg("<div class='loader'><span></span><span></span><span></span></div>", "bot");

  if (ct === "img" && cd) {
    if (curImgMode === "video" || /(فيديو|حرك|video)/i.test(val)) await buildCinemaVideo(val || "مشهد متحرك", cd, wait);
    else {
      const rep = await instantGlobalChat("صف هذه الصورة بالتفصيل بالعربية: " + (val || ""));
      wait.innerHTML = `<div class="txt-body">${rep.replace(/\n/g, "<br>")}</div>`;
    }
    return;
  }
  if (/(فيديو|مشهد|حرك|أنيميشن|video)/i.test(val)) { await buildCinemaVideo(val, null, wait); return; }
  if (/(صمم|صورة|صور|ارسم|أنمي|انمي|image|draw)/i.test(val) && ct !== "doc") {
    const imgObj = await generateSuperImage(val);
    if (imgObj && imgObj.url) wait.innerHTML = `<div>🎨 تم التصميم بواسطة <b>${imgObj.engine}</b> مع اللوغو الخاص بك:</div><img src="${imgObj.url}"><div class="actions"><a class="act-btn" href="${imgObj.url}" download="DarkHorizon_Pro.jpg">⬇️ تحميل الصورة</a><button type="button" class="act-btn" onclick="buildCinemaVideo('${val.replace(/'/g, "").slice(0, 60)}', '${imgObj.url}', this.closest('.msg'))">🎬 تحويل لفيديو</button></div>`;
    else wait.innerHTML = "⚠️ كروت GPU العالمية مشغولة حالياً، اضغط إرسال مرة أخرى.";
    return;
  }
  let fp = (ct === "doc" && cd) ? `محتوى الملف (${cn}):\n${String(cd).slice(0, 4000)}\n\nالمطلوب: ${val || "لخّص هذا الملف"}` : val;
  history.push({ role: "user", content: fp });
  const rep = await instantGlobalChat(fp);
  history.push({ role: "assistant", content: rep });
  wait.innerHTML = `<div class="txt-body">${rep.replace(/</g, "&lt;").replace(/\n/g, "<br>")}</div><div class="actions"><button type="button" class="act-btn copy-btn">📋 نسخ</button><button type="button" class="act-btn tts-btn">🎙️ تعليق صوتي</button></div>`;
  wait.querySelector(".copy-btn").onclick = function() { navigator.clipboard.writeText(rep); this.textContent = "✅ تم النسخ"; };
  wait.querySelector(".tts-btn").onclick = function() { playStudioVoice(rep); };
}

window.addEventListener("DOMContentLoaded", function() {
  document.getElementById("sendBtn").onclick = send;
  document.getElementById("plusBtn").onclick = function(e) { e.stopPropagation(); toggleMenu(); };
  document.getElementById("newBtn").onclick = function() { history = []; clearAttach(); document.getElementById("chat").innerHTML = ""; };
  document.getElementById("clearAttBtn").onclick = clearAttach;
  document.getElementById("q").onkeydown = function(e) { if (e.key === "Enter") { e.preventDefault(); send(); } };
  document.getElementById("pickLogoBtn").onclick = function() { attType = "logo"; document.getElementById("plusMenu").style.display = "none"; const f = document.getElementById("fileInp"); f.accept = "image/*"; f.click(); };
  document.getElementById("pickImgVisionBtn").onclick = function() { attType = "img"; imgActionMode = "vision"; document.getElementById("plusMenu").style.display = "none"; const f = document.getElementById("fileInp"); f.accept = "image/*"; f.click(); };
  document.getElementById("pickImgVidBtn").onclick = function() { attType = "img"; imgActionMode = "video"; document.getElementById("plusMenu").style.display = "none"; const f = document.getElementById("fileInp"); f.accept = "image/*"; f.click(); };
  document.getElementById("pickDocBtn").onclick = function() { attType = "doc"; document.getElementById("plusMenu").style.display = "none"; const f = document.getElementById("fileInp"); f.accept = ".txt,.py,.js,.json,.csv,.md,.html"; f.click(); };
  document.getElementById("fileInp").onchange = function() {
    const f = this.files ? this.files.at(0) : null; if (!f) return; attName = f.name;
    const r = new FileReader();
    r.onload = function(e) {
      if (attType === "logo") {
        localStorage.setItem("dh_media_logo", e.target.result);
        addMsg("✅ تم حفظ اللوغو الخاص بك! سيُطبع تلقائياً داخل زاوية كل صورة وفيديو تُنشئه.", "bot");
        attType = null; return;
      }
      attData = e.target.result;
      document.getElementById("prevName").textContent = (attType === "img" ? "🖼️ " : "📄 ") + attName;
      document.getElementById("previewBar").style.display = "flex";
    };
    if (attType === "doc") r.readAsText(f); else r.readAsDataURL(f);
  };
  document.querySelectorAll("[data-fill]").forEach(el => { el.onclick = function() { quickFill(this.getAttribute("data-fill")); }; });
  document.addEventListener("click", e => { if (!e.target.closest("#plusBtn") && !e.target.closest("#plusMenu")) document.getElementById("plusMenu").style.display = "none"; });
});
