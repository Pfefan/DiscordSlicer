import os
import shutil
from pathlib import Path

import discord
from discord.ext import commands

from logging_formatter import ConfigLogger
from handlers.database_handler import HybridDBhandler


class DownloadService:
    def __init__(self) -> None:
        """
        Initializes the Download_Service class.
        """
        self.logger = ConfigLogger().setup()
        self.db_handler = HybridDBhandler()
        self.category_name = "UPLOAD"

        os.makedirs("files/download", exist_ok=True)

    async def download_files(self, ctx: commands.Context, message: discord.Message, channel_id: str) -> bool:
        filename = ""
        Path(f"files/download/{channel_id}").mkdir(parents=True, exist_ok=True)
        category = discord.utils.get(ctx.guild.categories, name=self.category_name)
        if category is None:
            self.logger.warning("No category found with name %s", self.category_name)
            await message.edit(content=f"No category found with name {self.category_name}")
            return False

        text_channel = discord.utils.get(category.channels, id=int(channel_id))
        if text_channel is None:
            self.logger.info("No text channel found with id %s", channel_id)
            await message.edit(content=f"No text channel found with id {channel_id}")
            return False

        filename = self.db_handler.find_name_by_channel_id(channel_id)
        self.logger.info("Downloading %s", filename)
        await message.edit(content=f"Downloading {filename}")

        async for message in text_channel.history(limit=None):
            if len(message.attachments) > 0:
                for attachment in message.attachments:
                    file_path = os.path.join("files", "download", str(channel_id), attachment.filename)
                    with open(file_path, "wb") as f:
                        await attachment.save(f)

        self.logger.info("All files downloaded successfully")
        await message.edit(content="All files downloaded successfully")
        return True

    async def merge_files(self, message: discord.Message, channel_id: str) -> bool:
        input_files = sorted(os.listdir(os.path.join("files", "download", str(channel_id))), key=lambda x: int(x.split("_")[-1]))
        if not input_files:
            self.logger.info("No input files found")
            await message.edit(content="No input files found")
            return False

        output_filename = self.db_handler.find_fullname_by_channel_id(channel_id)
        output_path = Path("~/Downloads").expanduser() / output_filename

        with open(output_path, 'wb') as f:
            for i, input_file in enumerate(input_files):
                input_path = os.path.join("files", "download", str(channel_id), input_file)
                with open(input_path, 'rb') as chunk_file:
                    f.write(chunk_file.read())

        self.logger.info("Successfully merged files and saved it in the downloads folder")
        await message.edit(content="Successfully merged files and saved it in the downloads folder")
        shutil.rmtree(os.path.join("files", "download", str(channel_id))) # remove the downloaded chunk data
        return True

    async def get_file_channel_id(self, ctx: commands.Context, file: str) -> str:
        # Check if file exists in database by ID
        if file.isdigit():
            id_entry = self.db_handler.find_by_id(file)
            if id_entry is not None:
                return id_entry
        
        # If file not found by ID, try finding it by basename
        basename = os.path.basename(file)
        basename = os.path.splitext(basename)[0]
        name_entry = self.db_handler.find_by_filename(basename)
        if name_entry is not None:
            return name_entry
        
        # If file not found by basename, try finding the channel by name
        category = discord.utils.get(ctx.guild.categories, name=self.category_name)
        if category is None:
            category = await ctx.guild.create_category(self.category_name)
        channel = discord.utils.get(category.channels, name=file)
        if channel is not None:
            channel_entry = self.db_handler.find_by_channel_id(channel.id)
            if channel_entry is not None:
                return channel_entry
        return None


    async def main(self, ctx: commands.Context, file: str):
        first_msg = await ctx.send("Working on Download ↓")
        os.makedirs("files/download", exist_ok=True)
        file_id = await self.get_file_channel_id(ctx, file)
        if file_id:
            text_channel = ctx.channel
            message = await text_channel.send("Preparing download")
            self.logger.info("Found file in the channel with the id %s", file_id)
            await self.download_files(ctx, message, file_id)
            await self.merge_files(message, file_id)
        else:
            self.logger.info("Didn't find any file for the input: %s", file)
            await first_msg.edit(content=f"Didn't find any file for the input: {file}")
