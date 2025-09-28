from pyrogram import Client, filters
from pyrogram.types import Message

import yt_dlp
from typing import Dict

# Telegram API details
API_ID = 23706042
API_HASH = "636470656225550684dbf6b69fc3861c"
BOT_TOKEN = "7639799575:AAEU_clpWudmr1wJG6X5CC26aa3bvFHy_Wg"

# Dictionary to store music data for each chat
music_queue: Dict[int, Dict] = {}
current_playing: Dict[int, Dict] = {}

app = Client("music_stream_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def get_audio_stream(query: str) -> Dict:
    """Get direct audio stream URL from YouTube"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'default_search': 'ytsearch',
        'noplaylist': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(query, download=False)
            if 'entries' in info:
                info = info['entries'][0]
            
            return {
                'title': info.get('title', 'Unknown Title'),
                'url': info['url'],
                'duration': info.get('duration', 0),
                'thumbnail': info.get('thumbnail', ''),
                'webpage_url': info.get('webpage_url', '')
            }
        except Exception as e:
            print(f"Error getting audio stream: {e}")
            return None

@app.on_message(filters.command("play") & filters.group)
async def play_music(client, message: Message):
    try:
        if not message.reply_to_message and len(message.command) < 2:
            await message.reply("**Usage:** `/play song_name` or reply to an audio file")
            return
        
        chat_id = message.chat.id
        
        if message.reply_to_message and message.reply_to_message.audio:
            audio = message.reply_to_message.audio
            song_info = {
                'title': audio.title or "Audio File",
                'url': "audio_file",
                'duration': audio.duration or 0,
                'thumbnail': None,
                'is_file': True
            }
        else:
            query = " ".join(message.command[1:])
            song_info = get_audio_stream(query)
            
            if not song_info:
                await message.reply("❌ Song not found!")
                return
        
        if chat_id in current_playing:
            if chat_id not in music_queue:
                music_queue[chat_id] = []
            music_queue[chat_id].append(song_info)
            await message.reply(f"🎵 Added to queue: **{song_info['title']}**")
        else:
            current_playing[chat_id] = song_info
            await message.reply(f"🎶 Now playing: **{song_info['title']}**")
    
    except Exception as e:
        await message.reply(f"❌ Error: {str(e)}")

@app.on_message(filters.command("stop") & filters.group)
async def stop_music(client, message: Message):
    chat_id = message.chat.id
    
    if chat_id in current_playing:
        current_playing.pop(chat_id, None)
        music_queue.pop(chat_id, None)
        
        try:
            await client.leave_chat(chat_id)
        except:
            pass
        
        await message.reply("⏹️ Music stopped and DJ got chhutti! 🎉")
    else:
        await message.reply("❌ No music is currently playing!")

@app.on_message(filters.command("pause") & filters.group)
async def pause_music(client, message: Message):
    chat_id = message.chat.id
    
    if chat_id in current_playing:
        await message.reply("⏸️ Music paused!")
    else:
        await message.reply("❌ No music is currently playing!")

@app.on_message(filters.command("resume") & filters.group)
async def resume_music(client, message: Message):
    chat_id = message.chat.id
    
    if chat_id in current_playing:
        await message.reply("▶️ Music resumed! Let's dance! 💃")
    else:
        await message.reply("❌ No music is paused!")

@app.on_message(filters.command("help") & filters.group)
async def help_command(client, message: Message):
    help_text = """
**🎵 Music Bot Commands:**

`/play song_name` - Gaana bajane ke liye
`/stop` - DJ ko chhutti dene ke liye  
`/pause` - Gaana rokne ke liye
`/resume` - Phir se nachane ke liye
`/help` - Ye gyaan lene ke liye

**Examples:**
`/play tum hi ho`
`/play shape of you`
"""
    await message.reply(help_text)

@app.on_message(filters.command("queue") & filters.group)
async def show_queue(client, message: Message):
    chat_id = message.chat.id
    
    if chat_id in music_queue and music_queue[chat_id]:
        queue_text = "**📋 Music Queue:**\n"
        for i, song in enumerate(music_queue[chat_id][:10], 1):
            queue_text += f"{i}. {song['title']}\n"
        
        if len(music_queue[chat_id]) > 10:
            queue_text += f"\n... and {len(music_queue[chat_id]) - 10} more songs"
        
        await message.reply(queue_text)
    else:
        await message.reply("📭 Queue is empty!")

if __name__ == "__main__":
    print("🎵 Music Bot Started!")
    app.run()