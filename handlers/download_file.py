"""
Module: download_service.py
Description: This module provides the Download_Service class which can be used to download 
             and merge files from a Discord text channel.
"""
import os
import shutil
from pathlib import Path

import discord

from logging_formatter import ConfigLogger
from handlers.database_handler import FileManager


class Download_Service(discord.ui.View):
    def __init__(self) -> None:
        """
        Initializes the Download_Service class.
        """
        self.category_name = "UPLOAD"
        self.logger = ConfigLogger().setup()
        self.db_manager = FileManager()


    async def download_files(self, interaction, channel_id):
        os.makedirs(f"files/download/{channel_id}", exist_ok=True)
        category = discord.utils.get(interaction.guild.categories, name=self.category_name)
        if category is None:
            self.logger.warning("No category found with name %s", self.category_name)
            await interaction.edit_original_response(
                content=f"No category found with name {self.category_name}"
            )
            return False

        text_channel = discord.utils.get(category.channels, id=int(channel_id))
        if text_channel is None:
            self.logger.info("No text channel found with id %s", channel_id)
            await interaction.edit_original_response(
                content=f"No text channel found with id {channel_id}"
            )
            return False


        self.logger.info("Downloading files...")
        await interaction.edit_original_response(content="Downloading files...")
        async for message in text_channel.history(limit=None):
            if len(message.attachments) > 0:
                for attachment in message.attachments:
                    file_path = f"files/download/{channel_id}/{attachment.filename}"
                    with open(file_path, "wb") as f:
                        await attachment.save(f)

        self.logger.info("All files downloaded successfully")
        await interaction.edit_original_response(content="All files downloaded successfully")

    async def merge_files(self, interaction, channel_id):
        input_files = os.listdir(f"files/download/{channel_id}")
        if not input_files:
            self.logger.info("No input files found")
            await interaction.edit_original_response(content="No input files found")
            return False

        first_file = input_files[0]
        name, extension = os.path.splitext(first_file)
        extension = extension.split("_")[0]
        output_filename = name + extension
        output_path = Path(os.path.expanduser("~/Downloads")) / output_filename

        with open(output_path, "wb") as output_file:
            for input_file in input_files:
                input_path = f"files/download/{channel_id}/{input_file}"
                with open(input_path, "rb") as input_file:
                    shutil.copyfileobj(input_file, output_file)

        self.logger.info("Successfully merged files and saved it in the downloads folder")
        await interaction.edit_original_response(content="Successfully merged files and saved it in the downloads folder")

    async def main(self, interaction, file:str):
        await interaction.response.send_message("Working on Download...")
        os.makedirs("files/download", exist_ok=True)
        await self.download_files(interaction, channel_id)
        await self.merge_files(interaction, channel_id)
        shutil.rmtree(f"files/download/{channel_id}/")
