#
# Copyright (C) 2023 Sebastiano Barezzi
#
# SPDX-License-Identifier: MIT
#

from humanize import naturalsize
from liblineage.constants.versions import LINEAGEOS_TO_ANDROID_VERSION
from liblineage.updater.v2 import AsyncV2Api
from liblineage.updater.v2.build import Build
from sebaubuntu_libs.libexception import format_exception
from telegram import Bot
from telegram.constants import ParseMode
from telegram.helpers import escape_markdown
from typing import Union

from lineageos_updates_bot.utils.logging import log

class Poster:
	async def post(self, codename: str, update: Build, bot: Bot, chat_id: Union[str, int]):
		chat = await bot.get_chat(chat_id=chat_id)
		device_data = await AsyncV2Api.get_device(codename)
		lineageos_version = update.version

		text = (
			f"{escape_markdown(f'#{codename}', 2)} {escape_markdown(f'#{LINEAGEOS_TO_ANDROID_VERSION[lineageos_version].version_short.lower()}', 2)}\n"
			f"*LMODroid {escape_markdown(lineageos_version, 2)} for {escape_markdown(f'{device_data.oem} {device_data.name} ({codename})', 2)}*\n"
			f"\n"
			f"Device informations: [Here]({escape_markdown(device_data.info_url, 2)})\n"
			f"\n"
			f"Date: {escape_markdown(update.date, 2)}\n"
			f"Type: {escape_markdown(update.build_type, 2)}\n"
			#f"OS patch level: `{escape_markdown(update.os_patch_level, 2)}`\n"
			f"Download: [{escape_markdown(update.ota_zip.filename, 2)}]({escape_markdown(update.ota_zip.url, 2)}) {escape_markdown(f'({naturalsize(update.ota_zip.size)})', 2)}\n"
		)

		additional_files = update.files[1:]

		if additional_files:
			text += (
				"\n"
				"Additional files:\n"
			)

		for file in additional_files:
			text += (
				f"[{escape_markdown(file.filename, 2)}]({escape_markdown(file.url, 2)}) {escape_markdown(f'({naturalsize(file.size)})', 2)}\n"
			)

		if chat.username:
			text += (
				"\n"
				f"@{escape_markdown(chat.username, 2)}\n"
			)

		try:
			await chat.send_message(text, parse_mode=ParseMode.MARKDOWN_V2)
		except Exception as e:
			await log(
				bot,
				"\n".join([
					f"Failed to send message to chat {chat_id}:",
					f"{format_exception(e)}",
					"",
					"Message to send:",
					f"{text}"
				])
			)
			# Reraise exception
			raise e
