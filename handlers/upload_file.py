"""
This module provides functionality to split a large file into smaller chunks
and upload them to Discord.

Attributes:
logger (logging.Logger): A logger instance to log messages.
dbhandler (HybridDBhandler): An instance of the HybridDBhandler class
to interact with the database.
chunk_size (int): The size of each chunk in bytes.
category_name (str): The name of the category to upload files to.

Functions:
- split_file(path:str, filename:str) -> bool:
Splits a file into smaller chunks.

- async upload_files(ctx:commands.Context, message:discord.Message, path:str, file_name:str
, extension:str) -> bool:
    Uploads the files to Discord.

- convert_size(size_bytes:int) -> str:
    Convert a size in bytes to a human-readable string.

- async main(ctx:commands.Context, path:str):
    Perform the main operation of the upload service.
"""
import os
import re
import shutil

import discord
from discord.ext import commands

from handlers.database_handler import HybridDBhandler
from logging_formatter import ConfigLogger


class UploadService():
    """
    This class provides functionality to split a large file into smaller chunks
    and upload them to Discord.

    Attributes:
        logger (logging.Logger): A logger instance to log messages.
        dbhandler (HybridDBhandler): An instance of the HybridDBhandler class
        to interact with the database.
        chunk_size (int): The size of each chunk in bytes.
        category_name (str): The name of the category to upload files to.
    """

    def __init__(self) -> None:
        """
        Initializes a new instance of the UploadService class.
        """
        self.logger = ConfigLogger().setup()
        self.dbhandler = HybridDBhandler()
        self.chunk_size = 8388608
        self.category_name = "UPLOAD"

    def split_file(self, path, filename):
        """
        Splits a file into smaller chunks.

        Args:
            path (str): The path of the file to split.
            filename (str): The name of the file.

        Returns:
            bool: True if all the chunks were saved successfully, False otherwise.
        """
        file_size = os.stat(path).st_size

        os.makedirs(f"files/upload/{filename}", exist_ok=True)

        num_chunks = file_size // self.chunk_size
        if file_size % self.chunk_size != 0:
            num_chunks += 1

        chunks_saved = 0

        with open(path, 'rb') as file_handle:
            for i in range(num_chunks):
                chunk_data = file_handle.read(self.chunk_size)
                chunk_filename = f'files/upload/{filename}/{filename}_{i}'
                with open(chunk_filename, 'wb') as chunk_file:
                    try:
                        chunk_file.write(chunk_data)
                        chunks_saved += 1
                    except IOError as exception:
                        self.logger.error("IOError while writing chunk %s: %s", i, exception)


        if chunks_saved == num_chunks:
            self.logger.info("All chunks saved successfully")
            return True
        self.logger.error("only %s out of %s chunks were saved", chunks_saved, num_chunks)
        return False

    async def upload_files(self, ctx, message, path, file_name, extension):
        """
        Uploads the files to Discord.

        Args:
            ctx (commands.Context): The context of the command.
            message (discord.Message): The message to edit during the upload process.
            path (str): The path of the file to upload.
            file_name (str): The name of the file.
            extension (str): The extension of the file.

        Returns:
            bool: True if all the files were uploaded successfully, False otherwise.
        """
        category = discord.utils.get(ctx.guild.categories, name=self.category_name)
        if category is None:
            category = await ctx.guild.create_category(self.category_name)

        # Remove any characters that are not allowed in channel names
        channel_name = re.sub(r'[^a-zA-Z0-9_-]', '', file_name)
        # Format the channel name to lowercase
        channel_name = channel_name.lower()

        text_channel = discord.utils.get(category.channels, name=channel_name)

        if text_channel is None:
            text_channel = await category.create_text_channel(channel_name)
        else:
            self.logger.error("File already exists")
            await message.edit(content="File already exists")
            return False

        directory = f'files/upload/{file_name}'
        files = os.listdir(directory)
        total_files = len(files)
        uploaded_files = 0

        self.logger.info("Uploading %s files", total_files)
        await message.edit(content=f"Uploading {total_files} files")

        for file in files:
            with open(os.path.join(directory, file), 'rb') as upload_file:
                chuck_filename = os.path.basename(file)
                discord_file = discord.File(upload_file, filename=chuck_filename)
                await text_channel.send(file=discord_file)
            uploaded_files += 1
            await message.edit(content=f"Uploaded {uploaded_files}/{total_files} files")

        channel_id = text_channel.id
        user_id = ctx.author.id

        file_size = os.stat(path).st_size
        file_type = extension.replace(".", "")
        self.dbhandler.insert_file(
            user_id, channel_id, file_name, self.convert_size(file_size), file_type
            )

        self.logger.info("All files uploaded successfully")
        await message.edit(content="All files uploaded successfully")
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

    async def main(self, ctx:commands.Context, path):
        """
        Perform the main operation of the upload service.

        Args:
            ctx (commands.Context): The context object representing the command invocation.
            path (str): The path to the file to upload.

        Returns:
            bool: True if the upload was successful, False otherwise.

        """
        text_channel = ctx.channel
        message = await text_channel.send("Preparing upload")
        os.makedirs('files/upload', exist_ok=True)
        if os.path.exists(path):
            file_name, extension = os.path.splitext(os.path.basename(path))
            success = self.split_file(path, file_name)
            if success:
                await self.upload_files(ctx, message, path, file_name, extension)
                shutil.rmtree(f"files/upload/{file_name}")
        else:
            self.logger.error("File %s doesnt exist", path)
            await message.edit(content=f"File {path} doesnt exist")
            