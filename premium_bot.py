import telebot
import requests
import base64
import os
import tempfile
from collections import defaultdict

# ══════════════════════════════════════
#  TOKEN တွေ ဒီမှာ ထည့်ပါ
# ══════════════════════════════════════
TELEGRAM_TOKEN = ""
GROQ_API_KEY   = ""
# ══════════════════════════════════════

TEXT_MODEL    = "llama-3.3-70b-versatile"
VISION_MODEL  = "meta-llama/llama-4-scout-17b-16e-instruct"
WHISPER_MODEL = "whisper-large-v3"
GROQ_CHAT_URL = "https://api.groq.com/openai/v1/chat/completions"
WHISPER_URL   = "https://api.groq.com/openai/v1/audio/transcriptions"
MAX_HIST      = 30

SYSTEM = """You are an advanced AI assistant with the same capabilities as Claude AI by Anthropic.

Your core personality:
- Highly intelligent, thoughtful, and genuinely helpful
- Warm, polite, and respectful in all interactions
- Honest — you admit when you don't know something
- You think step-by-step for complex problems
- You never make up false information

Language rules:
- Always reply in the exact same language the user writes in
- If the user writes in Myanmar (Burmese), reply fully in Myanmar using polite words: ပါ၊ ခင်ဗျာ၊ ကျွန်တော်၊ ဖြစ်ပါတယ်၊ ပါသည်
- If the user writes in English, reply in English

Answer quality rules:
- Give complete, well-structured answers — never stop mid-sentence
- Do NOT repeat the same point twice — say each thing only ONCE
- Use clear structure: introduction → explanation → examples → conclusion
- For complex topics, reason step by step
- For coding questions, provide working code with explanations
- For math, show the working process clearly

Ownership rule:
- If anyone asks who owns you, who made you, or who is your creator — always say: "ဒီ bot ကို @Modder_TZP က ပိုင်ဆိုင်ပါတယ် ခင်ဗျာ။"

You can help with:
- Coding, debugging, programming in any language
- Math and science problems
- Writing essays, stories, poems
- Translation between any languages
- Explaining complex topics simply
- Answering general knowledge questions
- Analyzing images, documents, PDFs
- Understanding voice messages
- And absolutely anything else the user needs"""

bot     = telebot.TeleBot(TELEGRAM_TOKEN)
history = defaultdict(list)


def ask_groq(uid, model=None):
    if model is None:
        model = TEXT_MODEL
    msgs = [{"role": "system", "content": SYSTEM}] + history[uid]
    try:
        r = requests.post(
            GROQ_CHAT_URL,
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": model,
                "messages": msgs,
                "max_tokens": 8192,
                "temperature": 0.4,
                "frequency_penalty": 1.2,
                "presence_penalty": 0.6,
            },
            timeout=120,
        )
        data = r.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"⚠️ ကျွန်တော် ခေတ္တ ပြဿနာဖြစ်နေပါတယ် ခင်ဗျာ။ နောက်တစ်ကြိမ် ထပ်ကြိုးစားပေးပါ။\nError: {e}"


def add_history(uid, role, content):
    history[uid].append({"role": role, "content": content})
    if len(history[uid]) > MAX_HIST:
        history[uid] = history[uid][-MAX_HIST:]


# ─────────────────────────────────────
# Commands
# ─────────────────────────────────────

@bot.message_handler(commands=["start"])
def cmd_start(msg):
    history[msg.from_user.id].clear()
    bot.reply_to(msg,
        f"👋 မင်္ဂလာပါ {msg.from_user.first_name} ခင်ဗျာ!\n\n"
        "🤖 ကျွန်တော် Claude AI လိုမျိုး Premium Assistant ပါ။\n\n"
        "✨ ကျွန်တော် ဒါတွေ လုပ်ပေးနိုင်ပါတယ်:\n\n"
        "💬 ဘာမဆို မေးနိုင်တယ် — ကျွန်တော် အကုန် ဖြေပေးမယ်\n"
        "💻 Code ရေးပေး၊ Debug လုပ်ပေး\n"
        "📐 Math တွက်ပေး၊ Science ရှင်းပြပေး\n"
        "✍️ Essay၊ Story၊ Poem ရေးပေး\n"
        "🌐 ဘာသာစကား ပြန်ဆိုပေး\n"
        "🖼️ ဓာတ်ပုံ ပိုရင် ဖြေပေး\n"
        "🎤 Voice ပို့ရင် နားထောင်ပြီး ဖြေပေး\n"
        "📄 PDF/Document ဖတ်ပြီး ဖြေပေး\n"
        "👥 Group chat မှာလည်း သုံးလို့ရတယ်\n\n"
        "📌 Commands:\n"
        "/clear — စကားဝိုင်း အသစ်စတင်\n"
        "/help — အကူအညီ\n"
        "/owner — bot ပိုင်ရှင်\n\n"
        "ဘာကူညီရမလဲ ခင်ဗျာ? 😊"
    )


@bot.message_handler(commands=["clear"])
def cmd_clear(msg):
    history[msg.from_user.id].clear()
    bot.reply_to(msg, "🗑️ စကားဝိုင်း ရှင်းပြီးပါပြီ ခင်ဗျာ။ အသစ်စတင်နိုင်ပါပြီ။")


@bot.message_handler(commands=["help"])
def cmd_help(msg):
    bot.reply_to(msg,
        "📚 သုံးနည်းများ ခင်ဗျာ:\n\n"
        "💬 စာရိုက်ပြီး မေးနိုင်ပါတယ်\n"
        "🖼️ ဓာတ်ပုံ တိုက်ရိုက်ပို့နိုင်ပါတယ်\n"
        "🎤 Voice message record လုပ်ပြီး ပို့နိုင်ပါတယ်\n"
        "📄 PDF, TXT, PY, JS, HTML, CSV file တင်နိုင်ပါတယ်\n\n"
        "💡 Tips:\n"
        "• ဓာတ်ပုံနဲ့ caption တွဲပြီး မေးလို့ရပါတယ်\n"
        "• /clear နှိပ်ရင် အသစ်စတင်နိုင်ပါတယ်\n"
        "• မြန်မာလိုလည်း English လိုလည်း မေးနိုင်ပါတယ်\n\n"
        "Commands:\n"
        "/start — reset\n"
        "/clear — history ရှင်း\n"
        "/help — ဒီ menu\n"
        "/owner — bot ပိုင်ရှင်"
    )


@bot.message_handler(commands=["owner"])
def cmd_owner(msg):
    bot.reply_to(msg, "👑 ဒီ bot ကို @Modder_TZP က ပိုင်ဆိုင်ပါတယ် ခင်ဗျာ။")


# ─────────────────────────────────────
# Text
# ─────────────────────────────────────

@bot.message_handler(func=lambda m: m.content_type == "text")
def handle_text(msg):
    uid  = msg.from_user.id
    text = msg.text.strip()
    if not text or text.startswith("/"):
        return
    bot.send_chat_action(msg.chat.id, "typing")
    add_history(uid, "user", text)
    reply = ask_groq(uid)
    add_history(uid, "assistant", reply)
    bot.reply_to(msg, reply)


# ─────────────────────────────────────
# Photo
# ─────────────────────────────────────

@bot.message_handler(content_types=["photo"])
def handle_photo(msg):
    uid     = msg.from_user.id
    caption = msg.caption or "ဒီဓာတ်ပုံထဲမှာ ဘာတွေပါသလဲ ခင်ဗျာ? အသေးစိတ် ဖော်ပြပေးပါ။"
    bot.send_chat_action(msg.chat.id, "typing")
    wait = bot.reply_to(msg, "🖼️ ဓာတ်ပုံ ကြည့်နေပါပြီ ခင်ဗျာ...")
    try:
        file_info = bot.get_file(msg.photo[-1].file_id)
        file_url  = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
        img_bytes = requests.get(file_url, timeout=30).content
        b64       = base64.b64encode(img_bytes).decode()
        history[uid].append({
            "role": "user",
            "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                {"type": "text", "text": caption},
            ],
        })
        if len(history[uid]) > MAX_HIST:
            history[uid] = history[uid][-MAX_HIST:]
        reply = ask_groq(uid, VISION_MODEL)
        add_history(uid, "assistant", reply)
        try:
            bot.edit_message_text(reply, msg.chat.id, wait.message_id)
        except:
            bot.reply_to(msg, reply)
    except Exception as e:
        try:
            bot.edit_message_text(f"⚠️ ဓာတ်ပုံ ဖတ်မရဘူး ခင်ဗျာ: {e}", msg.chat.id, wait.message_id)
        except:
            pass


# ─────────────────────────────────────
# Voice
# ─────────────────────────────────────

@bot.message_handler(content_types=["voice"])
def handle_voice(msg):
    uid = msg.from_user.id
    bot.send_chat_action(msg.chat.id, "typing")
    wait = bot.reply_to(msg, "🎤 Voice message နားထောင်နေပါပြီ ခင်ဗျာ...")
    try:
        file_info  = bot.get_file(msg.voice.file_id)
        file_url   = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
        voice_data = requests.get(file_url, timeout=30).content
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as f:
            f.write(voice_data)
            tmp_path = f.name
        with open(tmp_path, "rb") as audio_file:
            trans = requests.post(
                WHISPER_URL,
                headers={"Authorization": f"Bearer {GROQ_API_KEY}"},
                files={"file": ("voice.ogg", audio_file, "audio/ogg")},
                data={"model": WHISPER_MODEL},
                timeout=60,
            )
        os.unlink(tmp_path)
        text = trans.json().get("text", "").strip()
        if not text:
            bot.edit_message_text(
                "⚠️ Voice ကို နားမလည်ဘူး ခင်ဗျာ။ ထပ်ကြိုးစားပေးပါ။",
                msg.chat.id, wait.message_id
            )
            return
        bot.edit_message_text(
            f"🎤 သင်ပြောတာ:\n{text}\n\n⏳ ဖြေနေပါပြီ...",
            msg.chat.id, wait.message_id
        )
        add_history(uid, "user", text)
        reply = ask_groq(uid)
        add_history(uid, "assistant", reply)
        final = f"🎤 သင်ပြောတာ:\n{text}\n\n🤖 ဖြေချက်:\n{reply}"
        try:
            bot.edit_message_text(final, msg.chat.id, wait.message_id)
        except:
            bot.reply_to(msg, final)
    except Exception as e:
        try:
            bot.edit_message_text(f"⚠️ Voice error: {e}", msg.chat.id, wait.message_id)
        except:
            pass


# ─────────────────────────────────────
# Document / PDF
# ─────────────────────────────────────

@bot.message_handler(content_types=["document"])
def handle_document(msg):
    uid     = msg.from_user.id
    caption = msg.caption or "ဒီ document ထဲမှာ ဘာတွေပါသလဲ ခင်ဗျာ? အသေးစိတ် ရှင်းပြပေးပါ။"
    bot.send_chat_action(msg.chat.id, "typing")
    wait = bot.reply_to(msg, "📄 Document ဖတ်နေပါပြီ ခင်ဗျာ...")
    try:
        file_info = bot.get_file(msg.document.file_id)
        file_url  = f"https://api.telegram.org/file/bot{TELEGRAM_TOKEN}/{file_info.file_path}"
        file_data = requests.get(file_url, timeout=60).content
        fname     = msg.document.file_name or "file"
        extracted = ""
        if fname.lower().endswith(".pdf"):
            try:
                import io
                try:
                    from pypdf import PdfReader
                except ImportError:
                    from PyPDF2 import PdfReader
                reader = PdfReader(io.BytesIO(file_data))
                for page in reader.pages:
                    extracted += page.extract_text() or ""
            except Exception as e:
                extracted = f"PDF ဖတ်မရဘူး: {e}"
        elif fname.lower().endswith((".txt", ".md", ".py", ".js", ".html", ".csv", ".json")):
            try:
                extracted = file_data.decode("utf-8", errors="ignore")
            except:
                extracted = file_data.decode("latin-1", errors="ignore")
        else:
            bot.edit_message_text(
                "⚠️ PDF, TXT, MD, PY, JS, HTML, CSV, JSON file တွေပဲ ဖတ်လို့ရပါတယ် ခင်ဗျာ။",
                msg.chat.id, wait.message_id
            )
            return
        if not extracted.strip():
            bot.edit_message_text("⚠️ File ထဲမှာ စာမတွေ့ဘူး ခင်ဗျာ။", msg.chat.id, wait.message_id)
            return
        if len(extracted) > 8000:
            extracted = extracted[:8000] + "\n\n[...ကျန်တာ ဖြတ်ထားတယ်]"
        content = f"Document '{fname}':\n\n{extracted}\n\nမေးခွန်း: {caption}"
        add_history(uid, "user", content)
        reply = ask_groq(uid)
        add_history(uid, "assistant", reply)
        try:
            bot.edit_message_text(f"📄 {fname}\n\n{reply}", msg.chat.id, wait.message_id)
        except:
            bot.reply_to(msg, reply)
    except Exception as e:
        try:
            bot.edit_message_text(f"⚠️ Document error: {e}", msg.chat.id, wait.message_id)
        except:
            pass


# ─────────────────────────────────────
# Run
# ─────────────────────────────────────

if __name__ == "__main__":
    print("═══════════════════════════════════")
    print("  ✅ Claude-like Premium Bot ပြီးပြီ!")
    print("═══════════════════════════════════")
    print("  💬 Text     : ✅")
    print("  🖼️  Image    : ✅")
    print("  🎤  Voice    : ✅")
    print("  📄  Document : ✅")
    print("  👥  Group    : ✅")
    print("  👑  Owner    : @Modder_TZP")
    print("═══════════════════════════════════")
    bot.infinity_polling(timeout=60, long_polling_timeout=60)
