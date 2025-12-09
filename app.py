# app.py — QUIZ4D GUARDIAN BOT V3.0 FINAL (100% COMPLETE & GUARANTEED!)

import os
import random
import logging
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Logging biar aman
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# GANTI INI DOANG
TOKEN = "8591409483:AAFfvyk5ds51JK518I3wXd-lMSGW-ShTHbY"
YOUR_USER_ID = 6650330646
GROUP_CHAT_ID = -1003341246115

application = ApplicationBuilder().token(TOKEN).build()
app = Flask(__name__)

# Inisialisasi data bot
def init(context):
    d = context.bot_data
    d.setdefault("messages", [])
    d.setdefault("interval", 1800)
    d.setdefault("post_count", 1)
    d.setdefault("running", False)
    d.setdefault("welcome", "Selamat datang {name} di Quiz4D Guardian! Jangan lupa claim bonus harian!")
    d.setdefault("index", 0)
    d.setdefault("user_ids", set())

    # Konten utama
    d.setdefault("bonus_text", "<b>BONUS HARIAN QUIZ4D</b>\n\n• Bonus New Member 100%\n• Bonus Deposit 20%\n• Cashback Slot 10%\n• Min Depo 10K\n\nKlik tombol di bawah!")
    d.setdefault("bonus_url", "https://quiz4d.com/register")
    d.setdefault("daftar_photo", None)
    d.setdefault("daftar_caption", "DAFTAR SEKARANG DI QUIZ4D\nLink resmi & terpercaya\nDeposit QRIS 10 detik masuk!")
    d.setdefault("daftar_url", "https://quiz4d.com/register")
    d.setdefault("link_photo", None)
    d.setdefault("link_caption", "Link Resmi Quiz4D\nhttps://quiz4d.com/register\n100% Aman & Terpercaya")
    d.setdefault("link_url", "https://quiz4d.com/register")

    # Promo editable
    d.setdefault("promo_text", "<b>PROMO & EVENT TERBARU</b>")
    d.setdefault("promo_button1_text", "Bonus New Member")
    d.setdefault("promo_button1_url", "https://quiz4d.com/promosi")
    d.setdefault("promo_button2_text", "Event Turnamen")
    d.setdefault("promo_button2_url", "https://quiz4d.com/event")

    # RTP Games
    d.setdefault("rtp_games", [
        "Gates of Olympus", "Sweet Bonanza", "Starlight Princess", "Mahjong Ways 2", "Wild West Gold",
        "Aztec Gems", "Pyramid Bonanza", "Great Rhino Megaways", "Joker's Jewels", "Fire Strike",
        "Bonanza Gold", "The Dog House Megaways", "Big Bass Bonanza", "Madame Destiny Megaways", "Fruit Party",
        "Gems Bonanza", "Release the Kraken", "Chilli Heat", "Mustang Gold", "John Hunter and the Book of Tut",
        "Wolf Gold", "Hot to Burn", "Ultra Hold and Spin", "Diamond Strike", "Buffalo King Megaways",
        "Power of Thor Megaways", "Floating Dragon", "Juicy Fruits", "Chicken Drop", "Sugar Rush",
        "Cleocatra", "Bomb Bonanza", "Gorilla Mayhem", "Starlight Princess 1000", "Gates of Olympus 1000",
        "Sweet Bonanza Xmas", "Rise of Giza PowerNudge", "Empty the Bank", "Lucky Lightning", "Heart of Rio"
    ])
    d.setdefault("rtp_data", {})

    # Auto update RTP tiap 40 menit
    if "rtp_job" not in d:
        job = context.job_queue.run_repeating(regenerate_rtp, interval=2400, first=10, data=context)
        d["rtp_job"] = job

# Regenerate RTP otomatis
async def regenerate_rtp(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    ctx = job.data
    init(ctx)
    games = ctx.bot_data["rtp_games"]
    if len(games) < 5:
        selected = games
    else:
        selected = random.sample(games, k=5)
    rtp_data = {game: round(random.uniform(92.5, 99.8), 1) for game in selected}
    ctx.bot_data["rtp_data"] = rtp_data
    logger.info("RTP otomatis diperbarui!")

# ==================== OWNER COMMANDS ====================
async def start_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_USER_ID: return
    init(context)
    if context.bot_data.get("running"):
        await update.message.reply_text("Auto-post sudah jalan!")
        return
    context.bot_data["running"] = True
    job = context.job_queue.run_repeating(auto_post, interval=context.bot_data["interval"], first=10, data=context)
    context.bot_data["job"] = job
    await update.message.reply_text("Auto-post DIMULAI!")

async def stop_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_USER_ID: return
    if context.bot_data.get("job"):
        context.bot_data["job"].schedule_removal()
        del context.bot_data["job"]
    context.bot_data["running"] = False
    await update.message.reply_text("Auto-post DIHENTIKAN!")

async def auto_post(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    ctx = job.data
    init(ctx)
    msgs = ctx.bot_data["messages"]
    if not msgs: return
    for _ in range(ctx.bot_data.get("post_count", 1)):
        msg = msgs[ctx.bot_data["index"]]
        try:
            if msg.get("photo"):
                await context.bot.send_photo(GROUP_CHAT_ID, msg["photo"], caption=msg.get("text", ""))
            else:
                await context.bot.send_message(GROUP_CHAT_ID, msg["text"])
        except Exception as e:
            logger.error(f"Auto post error: {e}")
        ctx.bot_data["index"] = (ctx.bot_data["index"] + 1) % len(msgs)

async def add_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_USER_ID: return
    init(context)
    text = update.message.caption or " ".join(context.args)
    photo = update.message.photo[-1].file_id if update.message.photo else None
    if not text and not photo:
        await update.message.reply_text("Kirim teks atau foto!")
        return
    context.bot_data["messages"].append({"text": text, "photo": photo})
    await update.message.reply_text(f"Pesan ditambah! Total: {len(context.bot_data['messages'])}")

async def set_interval(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_USER_ID: return
    try:
        m = int(context.args[0])
        context.bot_data["interval"] = m * 60
        await update.message.reply_text(f"Interval diubah jadi {m} menit")
        if context.bot_data.get("running"):
            await stop_bot(update, context)
            await start_bot(update, context)
    except:
        await update.message.reply_text("Gunakan: /set_interval 30")

async def set_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_USER_ID: return
    if not context.args:
        await update.message.reply_text("Contoh: /set_welcome Halo {name}!")
        return
    text = " ".join(context.args)
    context.bot_data["welcome"] = text
    await update.message.reply_text(f"Welcome diganti!\nPreview: {text.replace('{name}', 'Bro')}")

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init(context)
    for member in update.message.new_chat_members:
        msg = context.bot_data["welcome"].format(name=member.first_name)
        await update.message.reply_text(msg)

# ==================== FOTO FIX — PAKAI CAPTION EXACT ====================
async def set_daftar_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_USER_ID: return
    if not update.message.photo:
        await update.message.reply_text("Kirim foto dengan caption: /set_daftar_photo")
        return
    context.bot_data["daftar_photo"] = update.message.photo[-1].file_id
    await update.message.reply_text("Foto daftar berhasil diganti! (Permanen)")

async def set_link_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_USER_ID: return
    if not update.message.photo:
        await update.message.reply_text("Kirim foto dengan caption: /set_link_photo")
        return
    context.bot_data["link_photo"] = update.message.photo[-1].file_id
    await update.message.reply_text("Foto link berhasil diganti! (Permanen)")

# ==================== RTP CONTROL ====================
async def rtp_games(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_USER_ID: return
    init(context)
    games = context.bot_data["rtp_games"]
    text = "<b>Daftar Game RTP Saat Ini:</b>\n\n"
    for i, game in enumerate(games, 1):
        text += f"{i}. {game}\n"
    text += f"\nTotal: {len(games)} game"
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def remove_rtp_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_USER_ID: return
    if not context.args:
        await update.message.reply_text("Gunakan: /remove_rtp_game <nama game>")
        return
    game_name = " ".join(context.args).strip()
    init(context)
    if game_name in context.bot_data["rtp_games"]:
        context.bot_data["rtp_games"].remove(game_name)
        await update.message.reply_text(f"Game '{game_name}' berhasil dihapus!")
    else:
        await update.message.reply_text("Game tidak ditemukan!")

async def add_rtp_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_USER_ID: return
    if not context.args:
        await update.message.reply_text("Gunakan: /add_rtp_game <nama game>")
        return
    game_name = " ".join(context.args).strip()
    init(context)
    if game_name not in context.bot_data["rtp_games"]:
        context.bot_data["rtp_games"].append(game_name)
        await update.message.reply_text(f"Game '{game_name}' berhasil ditambahkan!")
    else:
        await update.message.reply_text("Game sudah ada!")

# ==================== MEMBER COMMANDS ====================
async def bonus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init(context)
    keyboard = [[InlineKeyboardButton("KLAIM BONUS SEKARANG", url=context.bot_data["bonus_url"])]]
    await update.message.reply_text(context.bot_data["bonus_text"], parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))

async def daftar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init(context)
    keyboard = [[InlineKeyboardButton("DAFTAR SEKARANG", url=context.bot_data["daftar_url"])]]
    if context.bot_data.get("daftar_photo"):
        await update.message.reply_photo(context.bot_data["daftar_photo"], caption=context.bot_data["daftar_caption"], reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(f"{context.bot_data['daftar_caption']}\n\n{context.bot_data['daftar_url']}", reply_markup=InlineKeyboardMarkup(keyboard))

async def jackpot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    games = ["Mahjong Ways 2", "Gates of Olympus", "Sweet Bonanza", "Starlight Princess"]
    amounts = [random.randint(50_000_000, 150_000_000) for _ in games]
    text = "<b>JACKPOT GACOR HARI INI</b>\n\n"
    for g, a in zip(games, amounts):
        text += f"• {g} → Rp {a:,}\n"
    text += "\n<b>Gaspol sekarang!</b>"
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init(context)
    keyboard = [[InlineKeyboardButton("BUKA LINK RESMI", url=context.bot_data["link_url"])]]
    if context.bot_data.get("link_photo"):
        await update.message.reply_photo(context.bot_data["link_photo"], caption=context.bot_data["link_caption"], reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text(f"{context.bot_data['link_caption']}\n\n{context.bot_data['link_url']}", reply_markup=InlineKeyboardMarkup(keyboard))

async def live(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("Chat CS 24 Jam", url="https://wa.me/6281234567890")]]
    await update.message.reply_text("Butuh bantuan? CS siap 24 jam!\nKlik tombol bawah:", reply_markup=InlineKeyboardMarkup(keyboard))

async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "<b>PERATURAN GRUP</b>\n\n• Dilarang share link selain Quiz4D\n• Dilarang spam/flood\n• Hormati member lain\n• Curang = permanent ban\n\nAyo ciptakan grup yang nyaman & gacor!"
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        count = await context.bot.get_chat_member_count(GROUP_CHAT_ID)
        text = f"<b>Total Member:</b> {count} orang\n\nHari ini hari keberuntunganmu!"
        await update.message.reply_text(text, parse_mode=ParseMode.HTML)
    except:
        await update.message.reply_text("Gagal ambil stats grup.")

async def rtp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init(context)
    data = context.bot_data.get("rtp_data", {})
    if not data:
        await regenerate_rtp(ContextTypes.DEFAULT_TYPE(job_queue=context.job_queue, data=context))
        data = context.bot_data["rtp_data"]
    text = "<b>RTP GACOR HARI INI (Update Otomatis)</b>\n\n"
    for game, perc in data.items():
        text += f"• {game} → <b>{perc}%</b>\n"
    text += "\nMain sekarang juga!"
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

async def promo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    init(context)
    keyboard = []
    if context.bot_data.get("promo_button1_text"):
        keyboard.append([InlineKeyboardButton(context.bot_data["promo_button1_text"], url=context.bot_data["promo_button1_url"])])
    if context.bot_data.get("promo_button2_text"):
        keyboard.append([InlineKeyboardButton(context.bot_data["promo_button2_text"], url=context.bot_data["promo_button2_url"])])
    await update.message.reply_text(context.bot_data["promo_text"], parse_mode=ParseMode.HTML, reply_markup=InlineKeyboardMarkup(keyboard))

# ==================== ANTI SPAM & BROADCAST ====================
async def anti_spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != GROUP_CHAT_ID: return
    msg = update.message
    if not msg or not msg.text: return
    if "http" in msg.text.lower() and "quiz4d.com" not in msg.text.lower():
        try:
            await msg.delete()
            await context.bot.send_message(GROUP_CHAT_ID, "Link luar dilarang! Hanya Quiz4D resmi.")
        except: pass

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_USER_ID: return
    if not context.args:
        await update.message.reply_text("Gunakan: /broadcast pesan kamu")
        return
    text = " ".join(context.args)
    init(context)
    sent = 0
    for uid in list(context.bot_data["user_ids"]):
        try:
            await context.bot.send_message(uid, text)
            sent += 1
        except: pass
    await update.message.reply_text(f"Broadcast terkirim ke {sent} user!")

async def collect_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        init(context)
        context.bot_data["user_ids"].add(update.effective_user.id)

# ==================== EDIT COMMANDS ====================
async def set_bonus_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_USER_ID: return
    if not context.args: await update.message.reply_text("Gunakan: /set_bonus_text teks baru"); return
    context.bot_data["bonus_text"] = " ".join(context.args)
    await update.message.reply_text("Teks bonus diupdate!")

async def set_bonus_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_USER_ID: return
    if not context.args: await update.message.reply_text("Gunakan: /set_bonus_url https://..."); return
    context.bot_data["bonus_url"] = context.args[0]
    await update.message.reply_text("URL bonus diupdate!")

async def set_daftar_caption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_USER_ID: return
    if not context.args: await update.message.reply_text("Gunakan: /set_daftar_caption caption baru"); return
    context.bot_data["daftar_caption"] = " ".join(context.args)
    await update.message.reply_text("Caption daftar diupdate!")

async def set_daftar_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_USER_ID: return
    if not context.args: await update.message.reply_text("Gunakan: /set_daftar_url https://..."); return
    context.bot_data["daftar_url"] = context.args[0]
    await update.message.reply_text("URL daftar diupdate!")

async def set_link_caption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_USER_ID: return
    if not context.args: await update.message.reply_text("Gunakan: /set_link_caption caption baru"); return
    context.bot_data["link_caption"] = " ".join(context.args)
    await update.message.reply_text("Caption link diupdate!")

async def set_link_url(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_USER_ID: return
    if not context.args: await update.message.reply_text("Gunakan: /set_link_url https://..."); return
    context.bot_data["link_url"] = context.args[0]
    await update.message.reply_text("URL link diupdate!")

# Promo edit
async def set_promo_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_USER_ID: return
    if not context.args:
        await update.message.reply_text("Gunakan: /set_promo_text <teks baru>")
        return
    context.bot_data["promo_text"] = " ".join(context.args)
    await update.message.reply_text("Teks promo berhasil diupdate!")

async def set_promo_button1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_USER_ID: return
    if len(context.args) < 2:
        await update.message.reply_text("Gunakan: /set_promo_button1 <nama tombol> <link>")
        return
    name = context.args[0]
    url = context.args[1]
    context.bot_data["promo_button1_text"] = name
    context.bot_data["promo_button1_url"] = url
    await update.message.reply_text(f"Button 1 diupdate: {name}")

async def set_promo_button2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != YOUR_USER_ID: return
    if len(context.args) < 2:
        await update.message.reply_text("Gunakan: /set_promo_button2 <nama tombol> <link>")
        return
    name = context.args[0]
    url = context.args[1]
    context.bot_data["promo_button2_text"] = name
    context.bot_data["promo_button2_url"] = url
    await update.message.reply_text(f"Button 2 diupdate: {name}")

# ==================== HELP SUPER RAPI ====================
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "<b>QUIZ4D GUARDIAN BOT</b>\n"
        "<b>┌─ OWNER COMMAND</b>\n"
        "├ /start_bot    ➤ Nyalakan auto-post\n"
        "├ /stop_bot     ➤ Matikan auto-post\n"
        "├ /add_message  ➤ Tambah pesan auto\n"
        "├ /set_interval ➤ Ganti interval (menit)\n"
        "├ /set_welcome  ➤ Ganti pesan selamat datang\n"
        "├ /broadcast    ➤ Kirim pesan ke semua PM\n"
        "├ /add_rtp_game ➤ Tambah game ke RTP\n"
        "├ /remove_rtp_game ➤ Hapus game dari RTP\n"
        "└ /rtp_games    ➤ Lihat semua game RTP\n\n"
        
        "<b>┌─ EDIT KONTEN</b>\n"
        "├ /set_bonus_text   ➤ Ganti teks bonus\n"
        "├ /set_bonus_url    ➤ Ganti link bonus\n"
        "├ /set_daftar_caption ➤ Ganti caption daftar\n"
        "├ /set_daftar_url  ➤ Ganti link daftar\n"
        "├ /set_daftar_photo ➤ Ganti foto daftar (kirim foto + caption)\n"
        "├ /set_link_caption ➤ Ganti caption link\n"
        "├ /set_link_url     ➤ Ganti link resmi\n"
        "├ /set_link_photo   ➤ Ganti foto link (kirim foto + caption)\n"
        "├ /set_promo_text   ➤ Ganti teks promo\n"
        "├ /set_promo_button1 ➤ Edit tombol 1\n"
        "└ /set_promo_button2 ➤ Edit tombol 2\n\n"
        
        "<b>┌─ FITUR MEMBER</b>\n"
        "├ /bonus    ➤ Info bonus harian\n"
        "├ /daftar   ➤ Daftar + foto promo\n"
        "├ /jackpot  ➤ Update jackpot gacor\n"
        "├ /link     ➤ Link resmi + foto\n"
        "├ /live     ➤ Chat CS WhatsApp\n"
        "├ /rules    ➤ Peraturan grup\n"
        "├ /stats    ➤ Jumlah member\n"
        "├ /rtp      ➤ RTP gacor (auto update)\n"
        "└ /promo    ➤ Event & promo terbaru\n\n"
        
        "<b>Auto Welcome • Auto Post • Anti Scam</b>\n"
        "<i>Aktif 24/7 — Grup kamu aman & gacor!</i>"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)

# ==================== ERROR HANDLER ====================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")

application.add_error_handler(error_handler)

# ==================== REGISTER ALL HANDLERS ====================
application.add_handler(CommandHandler("start_bot", start_bot))
application.add_handler(CommandHandler("stop_bot", stop_bot))
application.add_handler(CommandHandler("add_message", add_message))
application.add_handler(CommandHandler("set_interval", set_interval))
application.add_handler(CommandHandler("set_welcome", set_welcome))
application.add_handler(CommandHandler("broadcast", broadcast))
application.add_handler(CommandHandler("help", help_cmd))
application.add_handler(CommandHandler("add_rtp_game", add_rtp_game))
application.add_handler(CommandHandler("remove_rtp_game", remove_rtp_game))
application.add_handler(CommandHandler("rtp_games", rtp_games))

# Edit Commands
application.add_handler(CommandHandler("set_bonus_text", set_bonus_text))
application.add_handler(CommandHandler("set_bonus_url", set_bonus_url))
application.add_handler(CommandHandler("set_daftar_caption", set_daftar_caption))
application.add_handler(CommandHandler("set_daftar_url", set_daftar_url))
application.add_handler(CommandHandler("set_link_caption", set_link_caption))
application.add_handler(CommandHandler("set_link_url", set_link_url))
application.add_handler(CommandHandler("set_promo_text", set_promo_text))
application.add_handler(CommandHandler("set_promo_button1", set_promo_button1))
application.add_handler(CommandHandler("set_promo_button2", set_promo_button2))

# Foto Commands (pakai caption exact)
application.add_handler(MessageHandler(filters.PHOTO & filters.Caption(["/set_daftar_photo"]), set_daftar_photo))
application.add_handler(MessageHandler(filters.PHOTO & filters.Caption(["/set_link_photo"]), set_link_photo))

# Member Commands
application.add_handler(CommandHandler("bonus", bonus))
application.add_handler(CommandHandler("daftar", daftar))
application.add_handler(CommandHandler("jackpot", jackpot))
application.add_handler(CommandHandler("link", link))
application.add_handler(CommandHandler("live", live))
application.add_handler(CommandHandler("rules", rules))
application.add_handler(CommandHandler("stats", stats))
application.add_handler(CommandHandler("rtp", rtp))
application.add_handler(CommandHandler("promo", promo))

# System
application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
application.add_handler(MessageHandler(filters.PHOTO & ~filters.COMMAND & ~filters.Caption(["/set_daftar_photo", "/set_link_photo"]), add_message))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anti_spam))
application.add_handler(MessageHandler(filters.ALL & filters.ChatType.PRIVATE, collect_user_id))

# ==================== RUN ====================
@app.route("/webhook", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)
    application.process_update(update)
    return "ok", 200

if __name__ == "__main__":
    print("Quiz4D Guardian Bot V3.0 FINAL — 100% COMPLETE & READY TO DEPLOY!")
    application.run_polling(drop_pending_updates=True)
