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


class Download_Service:
    """
    A class used to download and merge files from a Discord text channel.

    Attributes:
        category_name (str): The name of the category to search for in the server.
        logger (logging.Logger): The logger object used to log messages.

    Methods:
        download_files: Downloads all files from a Discord text channel.
        merge_files: Merges all downloaded files into a single file and saves it to the user's downloads folder.
        main: Main method used to download and merge files from a Discord text channel.
    """

    def __init__(self) -> None:
        """
        Initializes the Download_Service class.
        """
        self.category_name = "UPLOAD"
        self.logger = ConfigLogger().setup()

    async def download_files(self, interaction, text_channel_name):
        """
        Downloads all files from a Discord text channel.

        Args:
            interaction (discord.Interaction): The interaction object for the command.
            text_channel_name (str): The name of the text channel to download files from.

        Returns:
            bool: True if files were downloaded successfully, False otherwise.
        """
        os.makedirs(f"files/download/{text_channel_name}", exist_ok=True)
        category = discord.utils.get(interaction.guild.categories, name=self.category_name)
        if category is None:
            self.logger.warning("No category found with name %s", self.category_name)
            await interaction.edit_original_response(
                content=f"No category found with name {self.category_name}"
            )
            return False

        text_channel = discord.utils.get(category.channels, name=text_channel_name)
        if text_channel is None:
            self.logger.info("No text channel found with name %s", text_channel_name)
            await interaction.edit_original_response(
                content=f"No text channel found with name {text_channel_name}"
            )
            return False

        self.logger.info("Downloading files...")
        await interaction.edit_original_response(content="Downloading files...")
        async for message in text_channel.history(limit=None):
            if len(message.attachments) > 0:
                for attachment in message.attachments:
                    file_path = f"files/download/{text_channel_name}/{attachment.filename}"
                    with open(file_path, "wb") as f:
                        await attachment.save(f)

        self.logger.info("All files downloaded successfully")
        await interaction.edit_original_response(content="All files downloaded successfully")

    async def merge_files(self, interaction, text_channel_name):
        """
        Merges all downloaded files into a single file and saves it to the user's downloads folder.

        Args:
            interaction (discord.Interaction): The interaction object for the command.
            text_channel_name (str): The name of the text channel to download files from.

        Returns:
            bool: True if files were merged and saved successfully, False otherwise.
        """
        input_files = os.listdir(f"files/download/{text_channel_name}")
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
                input_path = f"files/download/{text_channel_name}/{input_file}"
                with open(input_path, "rb") as input_file:
                    shutil.copyfileobj(input_file, output_file)

        self.logger.info("Successfully merged files and saved it in the downloads folder")
        await interaction.edit_original_response(content="Successfully merged files and saved it in the downloads folder")

    async def main(self, interaction, text_channel_name: str):
        """
        The main method to download and merge files from a Discord text channel.

        Parameters:
        -----------
        interaction: discord.Interaction
            The Discord interaction object.
        text_channel_name: str
            The name of the text channel from which to download and merge files.

        Returns:
        --------
        None
        """
        await interaction.response.send_message("Working on Download...")
        os.makedirs("files/download", exist_ok=True)
        channel_name = text_channel_name.replace(" ", "-")
        await self.download_files(interaction, channel_name)
        await self.merge_files(interaction, channel_name)
        shutil.rmtree(f"files/download/{text_channel_name}/")
