import asyncio
import os
import time
from datetime import datetime, timedelta
from typing import Union

from pyrogram.types import (InlineKeyboardButton,
                            InlineKeyboardMarkup, Voice)

from Bikash import config
from Bikash.config import MUSIC_BOT_NAME, lyrical
from Bikash import app

from ..utils.formatters import (convert_bytes, get_readable_time,
                                seconds_to_min)

downloader = {}


class TeleAPI:
    def __init__(self):
        self.chars_limit = 4096
        self.sleep = config.TELEGRAM_DOWNLOAD_EDIT_SLEEP

    async def send_split_text(self, message, string):
        n = self.chars_limit
        out = [(string[i : i + n]) for i in range(0, len(string), n)]
        j = 0
        for x in out:
            if j <= 2:
                j += 1
                await message.reply_text(x)
        return True

    async def get_link(self, message):
        if message.chat.username:
            link = f"https://t.me/{message.chat.username}/{message.reply_to_message.message_id}"
        else:
            xf = str((message.chat.id))[4:]
            link = f"https://t.me/c/{xf}/{message.reply_to_message.message_id}"
        return link

    async def get_filename(
        self, file, audio: Union[bool, str] = None
    ):
        try:
            file_name = file.file_name
            if file_name is None:
                file_name = (
                    "🌷 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦 𝐀𝐮𝐝𝐢𝐨 𝐅𝐢𝐥𝐞 🌷"
                    if audio
                    else "🌷 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦 𝐕𝐢𝐝𝐞𝐨 𝐅𝐢𝐥𝐞 🌷"
                )

        except:
            file_name = (
                "🌷 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦 𝐀𝐮𝐝𝐢𝐨 𝐅𝐢𝐥𝐞 🌷"
                if audio
                else "🌷 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦 𝐕𝐢𝐝𝐞𝐨 𝐅𝐢𝐥𝐞 🌷"
            )
        return file_name

    async def get_duration(self, file):
        try:
            dur = seconds_to_min(file.duration)
        except:
            dur = "Unknown"
        return dur

    async def get_filepath(
        self,
        audio: Union[bool, str] = None,
        video: Union[bool, str] = None,
    ):
        if audio:
            try:
                file_name = (
                    audio.file_unique_id
                    + "."
                    + (
                        (audio.file_name.split(".")[-1])
                        if (not isinstance(audio, Voice))
                        else "ogg"
                    )
                )
            except:
                file_name = audio.file_unique_id + "." + ".ogg"
            file_name = os.path.join(
                os.path.realpath("downloads"), file_name
            )
        if video:
            try:
                file_name = (
                    video.file_unique_id
                    + "."
                    + (video.file_name.split(".")[-1])
                )
            except:
                file_name = video.file_unique_id + "." + "mp4"
            file_name = os.path.join(
                os.path.realpath("downloads"), file_name
            )
        return file_name

    async def download(self, _, message, mystic, fname):
        left_time = {}
        speed_counter = {}
        if os.path.exists(fname):
            return True

        async def down_load():
            async def progress(current, total):
                if current == total:
                    return
                current_time = time.time()
                start_time = speed_counter.get(message.message_id)
                check_time = current_time - start_time
                upl = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=" 𝐂𝐚𝐧𝐜𝐞𝐥 ❌",
                                callback_data="stop_downloading",
                            ),
                        ]
                    ]
                )
                if datetime.now() > left_time.get(message.message_id):
                    percentage = current * 100 / total
                    percentage = str(round(percentage, 2))
                    speed = current / check_time
                    eta = int((total - current) / speed)
                    downloader[message.message_id] = eta
                    eta = get_readable_time(eta)
                    if not eta:
                        eta = "0 sec"
                    total_size = convert_bytes(total)
                    completed_size = convert_bytes(current)
                    speed = convert_bytes(speed)
                    text = f"""
🥀 ​ꪜ𝓲ꪶꪶ𝓲ꪖ​ꪀ {MUSIC_BOT_NAME} 𝐓𝐞𝐥𝐞𝐠𝐫𝐚𝐦 𝐌𝐞𝐝𝐢𝐚 𝐃𝐨𝐰𝐧𝐋𝐨𝐝𝐞𝐫 🌷

🥀 𝐄𝐓𝐀 ➪ {eta}

🥀 𝐃𝐎𝐖𝐍𝐋𝐎𝐃𝐄𝐃 ➪ {completed_size}
🥀 𝐅𝐢𝐥𝐞 𝐒𝐈𝐙𝐄 ➪ {total_size}

🥀 𝐒𝐏𝐄𝐄𝐃 ➪ {speed}/s

🥀 𝐏𝐄𝐑𝐂𝐄𝐍𝐓𝐀𝐆𝐄 ➪ {percentage[:10]}%"""
                    try:
                        await mystic.edit_text(text, reply_markup=upl)
                    except:
                        pass
                    left_time[
                        message.message_id
                    ] = datetime.now() + timedelta(seconds=self.sleep)

            speed_counter[message.message_id] = time.time()
            left_time[message.message_id] = datetime.now()

            try:
                await app.download_media(
                    message.reply_to_message,
                    file_name=fname,
                    progress=progress,
                )
                await mystic.edit_text(
                    "🍁 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲  𝐃𝐨𝐰𝐧𝐥𝐨𝐚𝐝𝐞𝐝 𝐓𝐡𝐞 𝐅𝐢𝐥𝐞 ✅"
                )
                downloader.pop(message.message_id)
            except:
                await mystic.edit_text(_["tg_2"])

        if len(downloader) > 10:
            timers = []
            for x in downloader:
                timers.append(downloader[x])
            try:
                low = min(timers)
                eta = get_readable_time(low)
            except:
                eta = "Unknown"
            await mystic.edit_text(_["tg_1"].format(eta))
            return False

        task = asyncio.create_task(down_load())
        lyrical[mystic.message_id] = task
        await task
        downloaded = downloader.get(message.message_id)
        if downloaded:
            downloader.pop(message.message_id)
            return False
        verify = lyrical.get(mystic.message_id)
        if not verify:
            return False
        lyrical.pop(mystic.message_id)
        return True
