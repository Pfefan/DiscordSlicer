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
        self.embed: discord.Embed
        self.elapsed_time = 0

        os.makedirs("files/download", exist_ok=True)

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
        self.embed = discord.Embed(title="Download", description="Working on Download ⏳")
        response_msg = await ctx.reply(embed=self.embed)
        os.makedirs("files/download", exist_ok=True)
        file_id = await self.search_serv.main(ctx, file, self.category_name)
        if file_id:
            self.logger.info("Found file in the channel with the id %s", file_id)
            if await self.download_files(ctx, response_msg, file_id):
                await self.merge_files(file_id)
        else:
            self.logger.info("Didn't find any file for the input: %s", file)
            await response_msg.edit(content=f"Didn't find any file for the input: {file}")


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
        file = self.db_handler.get_file_by_channelid(channel_id)
        file_count = 0
        download_size = 0
        remaining_time = 0
        download_speed = 0
        chunk_size = 0

        Path(f"files/download/{channel_id}").mkdir(parents=True, exist_ok=True)

        category = discord.utils.get(ctx.guild.categories, name=self.category_name)
        if category is None:
            self.logger.warning("No category found with name %s", self.category_name)
            self.embed.description = f"No category found with name {self.category_name}"
            await response_msg.edit(embed=self.embed)
            return False

        text_channel = discord.utils.get(category.channels, id=int(channel_id))
        if text_channel is None:
            self.logger.info("No text channel found with id %s", channel_id)
            self.embed.description = f"No text channel found with id {channel_id}"
            await response_msg.edit(embed=self.embed)
            return False

        self.logger.info("Downloading %s", (f"{file['file_name']}.{file['file_type']}"))

        await response_msg.delete()
        msg_channel = ctx.channel
        self.embed.description = f"Preparing download for {file['file_name']}.{file['file_type']}"
        self.message = await msg_channel.send(embed=self.embed)

        total_files = file["num_files"]
        filesize = file["file_size"]
        bytefilesize = self.convert_to_bytes(filesize)

        starttime = time.time()
        self.embed.title = f"Downloading {file['file_name']}.{file['file_type']}"

        async for message in text_channel.history(limit=None, oldest_first=True):
            if len(message.attachments) > 0:
                for attachment in message.attachments:
                    self.embed.description = (
                        f"📥 File parts: {file_count}/{total_files}\n"
                        f"💾 Remaining: {self.convert_size(download_size)}/{filesize}\n"
                        f"⏳ ETA: {remaining_time}\n"
                        f"🚀 {self.convert_size(download_speed)}/s"
                    )
                    await self.message.edit(embed=self.embed)
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

        self.elapsed_time = self.convert_time(datetime.timedelta(seconds=time.time() - starttime))
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
        file = self.db_handler.get_file_by_channelid(channel_id)
        download_dir = os.path.join("files", "download", str(channel_id))

        input_files = sorted(os.listdir(download_dir), key=lambda x: int(x.split("_")[-1]))

        if not input_files:
            self.logger.info("No Downloaded files found")
            self.embed.description = "No Downloaded files found"
            await self.message.edit(embed=self.embed)
            return False

        output_filename = f"{file['file_name']}.{file['file_type']}"
        output_path = Path("~/Downloads").expanduser() / output_filename

        try:
            with open(output_path, 'wb') as chunk_files:
                for _, input_file in enumerate(input_files):
                    input_path = os.path.join("files", "download", str(channel_id), input_file)
                    with open(input_path, 'rb') as chunk_file:
                        chunk_files.write(chunk_file.read())
        except OSError as error:
            self.logger.error("An error occurred while merging the files: %s", error)
            self.embed.description = f"An error occurred while merging the files: {error}"
            self.message.edit(embed=self.embed)

        self.logger.info("Merged downloaded files and saved it to the users download folder in %s", self.elapsed_time)
        self.embed.title = "Finished Download"
        self.embed.description = f"for {file['file_name']}.{file['file_type']} in {self.elapsed_time}, saved into your downloads folder"
        await self.message.edit(embed=self.embed)

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
        elif size_bytes >= 1024:
            size_kb = size_bytes / 1024
            size = f"{size_kb:.2f} KB"
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

