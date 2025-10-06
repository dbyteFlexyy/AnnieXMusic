from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ANNIEMUSIC import app
from config import BOT_USERNAME

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
