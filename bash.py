from pyrogram import Client, filters
import os
import time
import asyncio
import traceback
import sys
import math  
import shutil
from datetime import datetime

bot_start_time = datetime.utcnow()
AUTH_USERS = [6360672597, 1130243906]
TEMP_DOWNLOAD_DIRECTORY = 'temp/'
os.makedirs(TEMP_DOWNLOAD_DIRECTORY, exist_ok=True)
MAX_MESSAGE_LENGTH = 4096
FINISHED_PROGRESS_STR = "✅"
UN_FINISHED_PROGRESS_STR = "❎"

api_id = '19975263'
api_hash = 'c06e6a449ce68bbc5b30160a05ab8fdb'
bot_token = '6889319174:AAG9VzteT2W4pEADjUIhSDF5T6a1ueCmRoY'
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

@app.on_message(filters.command(["start"], prefixes=["/", "!", ".", ""] ) & filters.private)
async def start_bot(client, message):
    current_time = datetime.utcnow()
    uptime_seconds = (current_time - bot_start_time).total_seconds()
    uptime_hours, remainder = divmod(int(uptime_seconds), 3600)
    uptime_minutes, uptime_seconds = divmod(remainder, 60)
    uptime_string = f"{uptime_hours} hours, {uptime_minutes} minutes, {uptime_seconds} seconds"
    start_message = f"Hello, I'm your Crunchyroll ripping bot.⏰ Bot Uptime: {uptime_string}\n\n"
    await message.reply_text(start_message)

@app.on_message(filters.incoming & filters.command(["ul"]))
async def upload_message(client, message):
    await upload_dir(client, message)


@app.on_message(filters.incoming & filters.command(["download"]))
async def download_message(client, message):
    await download_dir(client, message)


@app.on_message(filters.incoming & filters.command(["shell", "run", "bash"]))
async def bash_message(client, message):
    await exec_message(client, message)

@app.on_message(filters.command(["clear"], prefixes="/") & filters.user(AUTH_USERS))
async def clear_storage(client, message):
    if os.path.exists(TEMP_DOWNLOAD_DIRECTORY) and os.path.isdir(TEMP_DOWNLOAD_DIRECTORY):
        try:
            
            for filename in os.listdir(TEMP_DOWNLOAD_DIRECTORY):
                file_path = os.path.join(TEMP_DOWNLOAD_DIRECTORY, filename)
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            await message.reply_text("✅ Storage cleared successfully.")
        except Exception as e:
            await message.reply_text(f"❌ An error occurred while clearing storage: {e}")
    else:
        await message.reply_text("❌ Storage directory does not exist.")


async def upload_dir(client, message):
    if message.from_user.id not in AUTH_USERS:
        await message.reply_text("You're not authorized to use this command.")
        return

    u_start = time.time()
    if message.reply_to_message:
        message = message.reply_to_message
    split_text = message.text.split(" ", maxsplit=1)
    if len(split_text) <= 1:
        await message.reply_text("You need to specify the file or directory to upload after the command.")
        return
    cmd1 = split_text[1]
    replyid = message.id  # changed from .id to .message_id
    if os.path.exists(cmd1):
        status_message = await message.reply_text(f"➣ Uploading the file... 📁")
        try:
            await client.send_document(
                chat_id=message.chat.id,
                document=cmd1,
                caption=cmd1,
                reply_to_message_id=replyid,
            )
        finally:
            await status_message.delete()
    else:
        await message.reply_text("**File Directory Not Found**\n```{}```".format(cmd1))


async def exec_message(client, message):
    if message.from_user.id not in AUTH_USERS:
        await message.reply_text("You're not authorized to use this command.")
        return

    split_text = message.text.split(" ", maxsplit=1)
    if len(split_text) <= 1:
        await message.reply_text("You need to specify the command to execute after /bash.")
        return

    cmd = split_text[1]
    reply_to_id = message.id
    if message.reply_to_message:
        reply_to_id = message.reply_to_message.message_id

    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await process.communicate()
    e = stderr.decode()
    if not e:
        e = "No Error"
    o = stdout.decode()
    if not o:
        o = "No Output"
    else:
        o = o.strip()

    message_text = f"**Command:**\n`{cmd}` \n**PID:**\n`{process.pid}`\n\n**Error:**\n`{e}`\n**Output:**\n{o}"
    if len(message_text) > MAX_MESSAGE_LENGTH:
        with open("exec.txt", "w+", encoding="utf8") as out_file:
            out_file.write(str(message_text))
        await client.send_document(
            chat_id=message.chat.id,
            document="exec.txt",
            caption=f"Output of `{cmd}`",
            reply_to_message_id=reply_to_id
        )
        os.remove("exec.txt")
    else:
        await message.reply_text(message_text)
        
app.run()
