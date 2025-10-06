from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ANNIEMUSIC import app
from config import BOT_USERNAME

repo_caption = """
<b>🎵 ᴧᴜʀᴏʀᴧ x ᴍᴜsɪᴄ ʀᴇᴘᴏsɪᴛᴏʀʏ 🎵</b>

<b>✦ ᴏғғɪᴄɪᴀʟ ɢɪᴛʜᴜʙ ʀᴇᴘᴏ ✦</b>
➤ <b>ғᴜʟʟʏ sᴛᴀʙʟᴇ & ᴜᴘᴅᴀᴛᴇᴅ ᴄᴏᴅᴇ</b>
➤ <b>ɴᴏ ʜᴇʀᴏᴋᴜ ʙᴀɴ ɪssᴜᴇs</b>
➤ <b>ɴᴏ ɪᴅ ʙᴀɴ ᴘʀᴏʙʟᴇᴍs</b>
➤ <b>ᴜɴʟɪᴍɪᴛᴇᴅ ᴅʏɴᴏ ʜᴏᴜʀs</b>
➤ <b>24/7 ʟᴀɢ-ғʀᴇᴇ ᴘᴇʀғᴏʀᴍᴀɴᴄᴇ</b>

<b>📢 ɴᴏᴛᴇ:</b>
➤ <b>ᴛʜɪs ʀᴇᴘᴏ ɪs ᴘʀɪᴠᴀᴛᴇʟʏ ᴍᴀɴᴀɢᴇᴅ</b>
➤ <b>ғᴏʀ ʀᴇᴘᴏ ᴀᴄᴄᴇss, ᴄᴏɴᴛᴀᴄᴛ ᴏᴡɴᴇʀ</b>

© <b>ᴅʀᴀɢᴏɴʙʏᴛᴇ 2025 - ᴀʟʟ ʀɪɢʜᴛs ʀᴇsᴇʀᴠᴇᴅ</b>
"""

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
            reply_markup=reply_markup,
            parse_mode="html"
        )
    except Exception as e:
        print(f"Error sending repo: {e}")
