"""
This module contains the DownloadService class which is used for downloading
 and merging files from a Discord channel.
"""
import os
import shutil
from pathlib import Path

import discord
from discord.ext import commands

from handlers.database_handler import HybridDBhandler
from handlers.search_file import SearchService
from logging_formatter import ConfigLogger


class DownloadService:
    """
    A class used to download and merge files from a Discord channel.

    Methods
    -------
    __init__()
        Initializes the Download_Service class.

    download_files(ctx, message, channel_id)
        Downloads files from the given channel id and saves them to the local storage.

    merge_files(message, channel_id)
        Merges the downloaded files into a single file and saves it in the downloads folder.

    get_file_channel_id(ctx, file)
        Returns the channel ID associated with the given file name or ID.

    main(ctx, file)
        The main function to be executed when downloading and merging files.
    """

    def __init__(self) -> None:
        """
        Initializes the Download_Service class by setting up a logger and database handler.
        """
        self.logger = ConfigLogger().setup()
        self.search_serv = SearchService()
        self.db_handler = HybridDBhandler()
        self.category_name = "UPLOAD"

        os.makedirs("files/download", exist_ok=True)

    async def download_files(
        self, ctx: commands.Context, message: discord.Message, channel_id: str
    ) -> bool:

        """
        Downloads files from the given channel ID and saves them to the local storage.

        Parameters
        ----------
        ctx : commands.Context
            The context in which the message was sent.
        message : discord.Message
            The message object that triggered the download.
        channel_id : str
            The ID of the channel to download files from.

        Returns
        -------
        bool
            True if the files were downloaded successfully, False otherwise.
        """

        filename = ""
        edit_message:discord.Message = None

        Path(f"files/download/{channel_id}").mkdir(parents=True, exist_ok=True)
        category = discord.utils.get(ctx.guild.categories, name=self.category_name)
        if category is None:
            self.logger.warning("No category found with name %s", self.category_name)
            edit_message = await message.edit(content=f"No category found with name {self.category_name}")
            return False

        text_channel = discord.utils.get(category.channels, id=int(channel_id))
        if text_channel is None:
            self.logger.info("No text channel found with id %s", channel_id)
            edit_message = await message.edit(content=f"No text channel found with id {channel_id}")
            return False

        filename = self.db_handler.find_name_by_channel_id(channel_id)
        self.logger.info("Downloading %s", filename)
        edit_message = await message.edit(content=f"Downloading {filename}")

        async for message in text_channel.history(limit=None):
            if len(message.attachments) > 0:
                for attachment in message.attachments:
                    file_path = os.path.join(
                        "files", "download", str(channel_id), attachment.filename
                        )
                    with open(file_path, "wb") as down_file:
                        await attachment.save(down_file)

        self.logger.info("All files downloaded successfully")
        await edit_message.edit(content="All files downloaded successfully")
        return True

    async def merge_files(self, message: discord.Message, channel_id: str) -> bool:
        """
        Merges the downloaded files into a single file and saves it in the downloads folder.

        Parameters
        ----------
        message : discord.Message
            The message object that triggered the merge.
        channel_id : str
            The ID of the channel to merge files from.

        Returns
        -------
        bool
            True if the files were merged and saved successfully, False otherwise.
        """
        download_dir = os.path.join("files", "download", str(channel_id))
        input_files = sorted(os.listdir(download_dir), key=lambda x: int(x.split("_")[-1]))
        if not input_files:
            self.logger.info("No input files found")
            await message.edit(content="No input files found")
            return False

        output_filename = self.db_handler.find_fullname_by_channel_id(channel_id)
        output_path = Path("~/Downloads").expanduser() / output_filename

        with open(output_path, 'wb') as chunk_files:
            for _, input_file in enumerate(input_files):
                input_path = os.path.join("files", "download", str(channel_id), input_file)
                with open(input_path, 'rb') as file:
                    chunk_files.write(file.read())

        self.logger.info("Successfully merged files and saved it in the downloads folder")
        await message.edit(content="Successfully merged files and saved it in the downloads folder")
        shutil.rmtree(os.path.join("files", "download", str(channel_id)))
        return True

    async def main(self, ctx: commands.Context, file: str):
        """
        The main function to be executed when downloading and merging files.

        Parameters
        ----------
        ctx : commands.Context
            The context in which the message was sent.
        file : str
            The name or ID of the file to download and merge.
        """
        first_msg = await ctx.send("Working on Download ↓")
        os.makedirs("files/download", exist_ok=True)
        file_id = await self.search_serv.main(ctx, file, self.category_name)
        if file_id:
            text_channel = ctx.channel
            message = await text_channel.send("Preparing download")
            self.logger.info("Found file in the channel with the id %s", file_id)
            await self.download_files(ctx, message, file_id)
            await self.merge_files(message, file_id)
        else:
            self.logger.info("Didn't find any file for the input: %s", file)
            await first_msg.edit(content=f"Didn't find any file for the input: {file}")
