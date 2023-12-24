from pyrogram import Client, filters
import os
import time
import asyncio
import traceback
import sys
import math  

AUTH_USERS = [6452498126] 
TEMP_DOWNLOAD_DIRECTORY = 'temp/'
os.makedirs(TEMP_DOWNLOAD_DIRECTORY, exist_ok=True)
MAX_MESSAGE_LENGTH = 4096
FINISHED_PROGRESS_STR = "✅"
UN_FINISHED_PROGRESS_STR = "❎"

api_id = '19975263'
api_hash = 'c06e6a449ce68bbc5b30160a05ab8fdb'
bot_token = '6613656845:AAEeQwKrWZVAj7_GRTvEf2P0kRP9CoSTECo'

# Initialize the Client
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)


@app.on_message(filters.incoming & filters.command(["upload"]))
async def upload_message(client, message):
    await upload_dir(client, message)


@app.on_message(filters.incoming & filters.command(["download"]))
async def download_message(client, message):
    await download_dir(client, message)


@app.on_message(filters.incoming & filters.command(["bash"]))
async def bash_message(client, message):
    await exec_message(client, message)


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
    replyid = message.message_id  # changed from .id to .message_id
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


async def download_dir(client, message):
    if message.reply_to_message:
        reply = await message.reply_text("➣ Downloading the file... 🚴‍♀️")

        downloaded_file_path = await client.download_media(
            message=message.reply_to_message,
            file_name=TEMP_DOWNLOAD_DIRECTORY,
        )
        await reply.edit(f"Downloaded to `{downloaded_file_path}`")
    else:
        await message.reply_text("**Reply to a file to download it.**")

async def exec_message(client, message):
    if message.from_user.id not in AUTH_USERS:
        await message.reply_text("You're not authorized to use this command.")
        return

    cmd = message.text.split(" ", maxsplit=1)[1]
    reply_to_id = message_id
    if message.reply_to_message:
        reply_to_id = message.reply_to_message_id

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
        o = "\n".join(o.split("\n"))

    output = f"**Query:**\n__Command:__\n`{cmd}` \n__PID:__\n`{process.pid}`\n\n**STDERR:** \n`{e}`\n**OUTPUT:**\n{o}"

    if len(output) > MAX_MESSAGE_LENGTH:
        with open("exec.txt", "w+", encoding="utf8") as out_file:
            out_file.write(str(output))
        await client.send_document(
            chat_id=message.chat.id,
            document="exec.txt",
            caption=cmd,
            reply_to_message_id=reply_to_id
        )
        os.remove("exec.txt")
    else:
        await message.reply_text(output)

app.run()
