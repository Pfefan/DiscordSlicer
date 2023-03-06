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
from handlers.database_handler import Local_DB_Manager, Cloud_DB_Manager


class Download_Service():
    def __init__(self, use_cloud_database) -> None:
        """
        Initializes the Download_Service class.
        """
        self.logger = ConfigLogger().setup()
        self.local_db_manager = Local_DB_Manager()
        self.local_db_manager.configure_database()
        self.cloud_db_manager = Cloud_DB_Manager()
        self.category_name = "UPLOAD"
        self.use_cloud_database = use_cloud_database


    async def download_files(self, interaction, channel_id):
        filename = ""
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
        if self.use_cloud_database:
            filename = self.cloud_db_manager.find_name_by_channel_id(channel_id)
        else:
            filename = self.local_db_manager.find_name_by_channel_id(channel_id)
        self.logger.info("Downloading %s", filename)
        await interaction.edit_original_response(content=f"Downloading {filename}")
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
        shutil.rmtree(f"files/download/{channel_id}") # remove the downloaded chunk data

    async def get_file_channel_id(self, interaction, file):
        if self.use_cloud_database:
            # Check if file exists in database by ID
            if file.isdigit():
                id_entry = self.cloud_db_manager.find_by_id(file)
                if id_entry is not None:
                    return id_entry
            
            # If file not found by ID, try finding it by basename
            basename = os.path.basename(file)
            basename = os.path.splitext(basename)[0]
            name_entry = self.cloud_db_manager.find_by_filename(basename)
            if name_entry is not None:
                return name_entry
            
            # If file not found by basename, try finding the channel by name
            category_name = "UPLOAD"
            category = discord.utils.get(interaction.guild.categories, name=category_name)
            if category is None:
                category = await interaction.guild.create_category(category_name)
            channel = discord.utils.get(category.channels, name=file)
            if channel is not None:
                channel_entry = self.cloud_db_manager.find_by_channel_name(channel.id)
                if channel_entry is not None:
                    return channel_entry
            
            # If file not found by ID, basename, or channel name, return None
            return None
        else:
            # Check if file exists in database by ID
            id_entry = self.local_db_manager.find_by_id(file)
            if id_entry is not None:
                return id_entry
            
            # If file not found by ID, try finding it by basename
            basename = os.path.basename(file)
            basename = os.path.splitext(basename)[0]
            name_entry = self.local_db_manager.find_by_filename(basename)
            if name_entry is not None:
                return name_entry
            
            # If file not found by basename, try finding the channel by name
            category_name = "UPLOAD"
            category = discord.utils.get(interaction.guild.categories, name=category_name)
            if category is None:
                category = await interaction.guild.create_category(category_name)
            channel = discord.utils.get(category.channels, name=file)
            if channel is not None:
                channel_entry = self.local_db_manager.find_by_channel_name(channel.id)
                if channel_entry is not None:
                    return channel_entry
            
            # If file not found by ID, basename, or channel name, return None
            return None


    async def main(self, interaction, file:str):
        await interaction.response.send_message("Working on Download...")
        os.makedirs("files/download", exist_ok=True)
        file_id = await self.get_file_channel_id(interaction, file)
        if file_id != None:
            self.logger.info("Found file in the channel with the id %s", file_id)
            await self.download_files(interaction, file_id)
            await self.merge_files(interaction, file_id)
        else:
            self.logger.info("Didnt find any file for the input: %s", file)
            await interaction.edit_original_response(content=f"Didnt find any file for the input: {file}")
