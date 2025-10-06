from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ANNIEMUSIC import app
from config import BOT_USERNAME
import aiohttp
import html

# ---------------------- #
# 🔹 REPO COMMAND 🔹
# ---------------------- #

repo_caption = """**
🎵 **ᴧᴜʀᴏʀᴧ x ᴍᴜsɪᴄ ʀᴇᴘᴏsɪᴛᴏʀʏ** 🎵

✦ **ᴏғғɪᴄɪᴀʟ ɢɪᴛʜᴜʙ ʀᴇᴘᴏ** ✦
➤ **ғᴜʟʟʏ sᴛᴀʙʟᴇ & ᴜᴘᴅᴀᴛᴇᴅ ᴄᴏᴅᴇ**
➤ **ɴᴏ ʜᴇʀᴏᴋᴜ ʙᴀɴ ɪssᴜᴇs**
➤ **ɴᴏ ɪᴅ ʙᴀɴ ᴘʀᴏʙʟᴇᴍs**
➤ **ᴜɴʟɪᴍɪᴛᴇᴅ ᴅʏɴᴏ ʜᴏᴜʀs**
➤ **24/7 ʟᴀɢ-ғʀᴇᴇ ᴘᴇʀғᴏʀᴍᴀɴᴄᴇ**

📢 **ɴᴏᴛᴇ:** 
➤ **ᴛʜɪs ʀᴇᴘᴏ ɪs ᴘʀɪᴠᴀᴛᴇʟʏ ᴍᴀɴᴀɢᴇᴅ**
➤ **ғᴏʀ ʀᴇᴘᴏ ᴀᴄᴄᴇss, ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ**

© **ᴅʀᴀɢᴏɴʙʏᴛᴇ 2025 - ᴀʟʟ ʀɪɢʜᴛs ʀᴇsᴇʀᴠᴇᴅ**
**"""

@app.on_message(filters.command("repo"))
async def show_repo(_, msg):
    buttons = [
        [InlineKeyboardButton(" ⌯ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ⌯ ", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")],
        [
            InlineKeyboardButton(" ⌯ ᴏᴡɴᴇʀ ⌯ ", url="https://t.me/xFlexyy"),
            InlineKeyboardButton(" ⌯ sᴜᴘᴘᴏʀᴛ ⌯ ", url="https://t.me/ThronexCodex")
        ],
        [
            InlineKeyboardButton(" ⌯ sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ ⌯ ", url="https://t.me/Thronex_Chats"),
            InlineKeyboardButton(" ⌯ ɢᴇᴛ ʀᴇᴘᴏ ⌯ ", url="https://t.me/xFlexyy")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(buttons)

    try:  
        await msg.reply_photo(
            photo="https://files.catbox.moe/nnjeeo.jpg",
            caption=repo_caption,
            reply_markup=reply_markup
        )
    except Exception as e:
        print(f"Error sending repo: {e}")

# ---------------------- #
# 🔹 TMDB COMMAND 🔹
# ---------------------- #

def html_escape(text: str):
    return html.escape(text or "")

async def fetch_json(session, url, retries=2, timeout=30):
    for attempt in range(retries + 1):
        try:
            async with session.get(url, timeout=timeout) as resp:
                return await resp.json()
        except Exception as e:
            if attempt == retries:
                raise e

@app.on_message(filters.command("tmdb"))
async def tmdb_search(_, message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.reply_text(
            "❌ <b>Please provide a movie or series name.</b>\n\n"
            "<b>Usage:</b>\n<code>/tmdb (movie or anime name)</code>\n"
            "<b>Example:</b>\n<code>/tmdb stardom</code>",
            parse_mode="HTML",
        )
        return

    query = args[1]
    tmdb_api = "371c10909d11f866a3a1786e3a43cd8e"

    search_url = f"https://api.themoviedb.org/3/search/multi?query={query}&api_key={tmdb_api}&language=en-US"

    async with aiohttp.ClientSession() as session:
        try:
            search_data = await fetch_json(session, search_url)
            results = search_data.get("results", [])[:5]
            found = False

            for res in results:
                if res.get("media_type") not in ["movie", "tv"]:
                    continue

                found = True
                title = html_escape(res.get("title") or res.get("name"))
                overview = html_escape(res.get("overview", "No overview available."))
                release = res.get("release_date") or res.get("first_air_date", "N/A")
                year = release.split("-")[0] if release != "N/A" else "N/A"
                tmdb_id = res.get("id", "N/A")
                media_type = res.get("media_type", "movie")

                details_url = f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}?api_key={tmdb_api}&language=en-US&append_to_response=images&include_image_language=en,null"
                details = await fetch_json(session, details_url)

                genres = " | ".join([g["name"] for g in details.get("genres", [])]) or "N/A"
                runtime = details.get("runtime", None)
                duration = f"{runtime // 60}h {runtime % 60}min" if runtime else "N/A"
                seasons = details.get("number_of_seasons")
                episodes = details.get("number_of_episodes")

                backdrops = details.get("images", {}).get("backdrops", [])
                english_backdrop = next((b for b in backdrops if b.get("iso_639_1") == "en"), None)
                backdrop_path = english_backdrop.get("file_path") if english_backdrop else None
                backdrop_url = f"https://image.tmdb.org/t/p/w1280{backdrop_path}" if backdrop_path else None

                if media_type == "movie":
                    caption = f"""
<b>›› 𝖬𝗈𝗏𝗂𝖾: {title}  
›› 𝖸𝖾𝖺𝗋: {year}  
›› 𝖣𝗎𝗋𝖺𝗍𝗂𝗈𝗇: {duration}  
›› 𝖦𝖾𝗇𝗋𝖾𝗌: {genres}  
›› 𝖰𝗎𝖺𝗅𝗂𝗍𝗒: 1080p  
›› 𝖠𝗎𝖽𝗂𝗈: 𝖧𝗂𝗇𝖽𝗂 | #𝖮𝖿𝖿𝗂𝖼𝗂𝖺𝗅  

›› 𝖲𝗒𝗇𝗈𝗉𝗌𝗂𝗌:  
{overview}</b>  
━━━━━━━━━━━━━━━━━━━━━━
"""
                else:
                    caption = f"""
<b>›› 𝖲𝗁𝗈𝗐: {title}  
›› 𝖲𝖾𝖺𝗌𝗈𝗇: {str(seasons) if seasons else "N/A"}  
›› 𝖳𝗈𝗍𝖺𝗅 𝖤𝗉𝗂𝗌𝗈𝖽𝖾𝗌: {str(episodes) if episodes else "N/A"}  
›› 𝖦𝖾𝗇𝗋𝖾𝗌: {genres}  
›› 𝖰𝗎𝖺𝗅𝗂𝗍𝗒: 1080p / 720p / 480p  
›› 𝖠𝗎𝖽𝗂𝗈: 𝖧𝗂𝗇𝖽𝗂 | #𝖮𝖿𝖿𝗂𝖼𝗂𝖺𝗅  

›› 𝖲𝗒𝗇𝗈𝗉𝗌𝗂𝗌:  
{overview}</b>  
━━━━━━━━━━━━━━━━━━━━━━
"""

                buttons = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("⌯ ᴏᴡɴᴇʀ ⌯ ", url="https://t.me/xFlexyy")]]
                )

                if backdrop_url:
                    await message.reply_photo(
                        photo=backdrop_url,
                        caption=caption,
                        parse_mode="HTML",
                        reply_markup=buttons,
                    )
                else:
                    await message.reply_text(
                        caption, parse_mode="HTML", reply_markup=buttons
                    )

            if not found:
                await message.reply_text(
                    "❌ <b>No movie or series found on TMDB.</b>\n\n<i>👨‍💻 Contact: @xFlexyy</i>",
                    parse_mode="HTML",
                )

        except Exception as e:
            err_text = html_escape(str(e))
            await message.reply_text(
                f"❌ <b>Error occurred:</b>\n<code>{err_text}</code>\n\n⚠️ <i>Contact: @xFlexyy</i>",
                parse_mode="HTML",
            )