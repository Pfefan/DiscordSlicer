"""
This module contains the DownloadService class which is used for downloading
 and merging files from a Discord channel.
"""
import os
import shutil
from pathlib import Path
import time
import datetime

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
        self.message: discord.Message
        self.elapsed_time = 0

        os.makedirs("files/download", exist_ok=True)

    async def download_files(
        self, ctx: commands.Context, response_msg: discord.Message, channel_id: str
    ) -> bool:

        """
        Downloads files from the given channel ID and saves them to the local storage.

        Parameters
        ----------
        ctx : commands.Context
            The context in which the message was sent.
        response_msg : discord.Message
            The message object that triggered the download.
        channel_id : str
            The ID of the channel to download files from.

        Returns
        -------
        bool
            True if the files were downloaded successfully, False otherwise.
        """

        filename = ""
        file_count = 0
        download_size = 0
        remaining_time = 0
        download_speed = 0
        chunk_size = 0

        Path(f"files/download/{channel_id}").mkdir(parents=True, exist_ok=True)
        category = discord.utils.get(ctx.guild.categories, name=self.category_name)
        if category is None:
            self.logger.warning("No category found with name %s", self.category_name)
            await response_msg.edit(content=f"No category found with name {self.category_name}")
            return False

        text_channel = discord.utils.get(category.channels, id=int(channel_id))
        if text_channel is None:
            self.logger.info("No text channel found with id %s", channel_id)
            await response_msg.edit(content=f"No text channel found with id {channel_id}")
            return False

        filename = self.db_handler.find_name_by_channel_id(channel_id)
        self.logger.info("Downloading %s", filename)

        await response_msg.delete()
        msg_channel = ctx.channel
        self.message = await msg_channel.send(f"Preparing download for {filename}")

        total_files = self.db_handler.get_numfiles(channel_id)
        filesize = self.db_handler.get_filesize(channel_id)
        bytefilesize = self.convert_to_bytes(filesize)


        starttime = time.time()
        async for message in text_channel.history(limit=None):
            if len(message.attachments) > 0:
                for attachment in message.attachments:
                    await self.message.edit(content=f"📥 Downloading {file_count}/{total_files}\n"
                                                    f"💾 {self.convert_size(download_size)}/{filesize}\n"
                                                    f"⏳ ETA: {remaining_time}\n"
                                                    f"🚀 {self.convert_size(download_speed)}/s")
                    chunck_starttime = time.time()
                    file_path = os.path.join(
                        "files", "download", str(channel_id), attachment.filename
                        )
                    with open(file_path, "wb") as down_file:
                        await attachment.save(down_file)
                        chunk_size = os.path.getsize(file_path)
                    file_count += 1
                    download_size += chunk_size

                    elapsed_time = time.time() - chunck_starttime
                    download_speed = chunk_size / elapsed_time

                    remaining_size = bytefilesize - download_size
                    remaining_time = remaining_size / download_speed


                    remaining_time = datetime.timedelta(seconds=remaining_time)

                    if remaining_time.seconds > 0:
                        remaining_time = self.convert_time(remaining_time)
                    else:
                        remaining_time = "0 seconds"

        elapsed_time = datetime.timedelta(seconds=(time.time() - starttime))
        elapsed_time = self.convert_time(elapsed_time)
        self.elapsed_time = elapsed_time
        self.logger.info("All files downloaded successfully in %s", elapsed_time)
        return True

    async def merge_files(self, channel_id: str) -> bool:
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
            await self.message.edit(content="No input files found")
            return False

        output_filename = self.db_handler.find_fullname_by_channel_id(channel_id)
        output_path = Path("~/Downloads").expanduser() / output_filename

        with open(output_path, 'wb') as chunk_files:
            for _, input_file in enumerate(input_files):
                input_path = os.path.join("files", "download", str(channel_id), input_file)
                with open(input_path, 'rb') as file:
                    chunk_files.write(file.read())

        self.logger.info("Finished Downloading and merged files into your download folder in %s", self.elapsed_time)
        await self.message.edit(content=f"Finished Downloading and merged files into your download folder in {self.elapsed_time}")
        shutil.rmtree(os.path.join("files", "download", str(channel_id)))
        return True
    
    def convert_size(self, size_bytes):
        """
        Convert a size in bytes to a human-readable string.

        Args:
            size_bytes (int): The size in bytes to convert.

        Returns:
            str: A human-readable string representation of the size.

        """
        if size_bytes >= 1024*1024*1024:
            size_gb = size_bytes / (1024*1024*1024)
            size = f"{size_gb:.2f} GB"
        elif size_bytes >= 1024*1024:
            size_mb = size_bytes / (1024*1024)
            size = f"{size_mb:.2f} MB"
        else:
            size = f"{size_bytes} bytes"

        return size

    def convert_to_bytes(self, size_str):
        """
        Converts a size string in GB or MB into bytes.
        
        Args:
            size_str (str): The size string to convert. The format should be a number followed by 'GB', 'MB', or nothing for bytes.
        
        Returns:
            int: The size in bytes.
        """
        if size_str.endswith("GB"):
            size = float(size_str[:-2]) * 1024 ** 3
        elif size_str.endswith("MB"):
            size = float(size_str[:-2]) * 1024 ** 2
        else:
            size = float(size_str)
        return int(size)

    def convert_time(self, timeval:float):
        """converts a parsed timedelta into a better readable format
        
        Args:
            timeval(float): the value to convert
        
        Returns:
            str: formated value
        """

        days = timeval.days
        hours = timeval.seconds // 3600
        minutes = (timeval.seconds // 60) % 60
        seconds = timeval.seconds % 60

        formatted_time = ""
        if days > 0:
            formatted_time += f"{days} days, "
        if hours > 0:
            formatted_time += f"{hours} hours, "
        if minutes > 0:
            formatted_time += f"{minutes} minutes, "
        if seconds > 0:
            formatted_time += f"{seconds} seconds"

        formatted_time = formatted_time.rstrip(", ")

        return formatted_time

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
        response_msg = await ctx.reply(content="Working on Download ⏳")
        os.makedirs("files/download", exist_ok=True)
        file_id = await self.search_serv.main(ctx, file, self.category_name)
        if file_id:
            self.logger.info("Found file in the channel with the id %s", file_id)
            await self.download_files(ctx, response_msg, file_id)
            await self.merge_files(file_id)
        else:
            self.logger.info("Didn't find any file for the input: %s", file)
            await response_msg.edit(content=f"Didn't find any file for the input: {file}")
