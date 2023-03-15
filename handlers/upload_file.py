import os
import re
import shutil

import discord
from discord.ext import commands

from handlers.database_handler import HybridDBhandler
from logging_formatter import ConfigLogger


class UploadService():
    def __init__(self) -> None:
        self.logger = ConfigLogger().setup()
        self.dbhandler = HybridDBhandler()
        self.chunk_size = 8388608
        self.category_name = "UPLOAD"

    def split_file(self, path, filename):
        file_size = os.stat(path).st_size

        os.makedirs(f"files/upload/{filename}", exist_ok=True)

        num_chunks = file_size // self.chunk_size
        if file_size % self.chunk_size != 0:
            num_chunks += 1

        chunks_saved = 0

        with open(path, 'rb') as f:
            for i in range(num_chunks):
                chunk_data = f.read(self.chunk_size)
                chunk_filename = f'files/upload/{filename}/{filename}_{i}'
                with open(chunk_filename, 'wb') as chunk_file:
                    try:
                        chunk_file.write(chunk_data)
                        chunks_saved += 1
                    except Exception as e:
                        self.logger.error("Error while writing chunk %s: %s", i, e)

        if chunks_saved == num_chunks:
            self.logger.info("All chunks saved successfully")
            return True
        else:
            self.logger.error("only %s out of %s chunks were saved", chunks_saved, num_chunks)
            return False

    async def upload_files(self, ctx, message, path, file_name, extension):
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
            with open(os.path.join(directory, file), 'rb') as f:
                chuck_filename = os.path.basename(file)
                discord_file = discord.File(f, filename=chuck_filename)
                await text_channel.send(file=discord_file)
            uploaded_files += 1
            await message.edit(content=f"Uploaded {uploaded_files}/{total_files} files")

        channel_id = text_channel.id
        user_id = ctx.author.id

        file_size = os.stat(path).st_size
        file_type = extension.replace(".", "")
        self.dbhandler.insert_file(user_id, channel_id, file_name, self.convert_size(file_size), file_type)

        self.logger.info("All files uploaded successfully")
        await message.edit(content="All files uploaded successfully")
        return True

    def convert_size(self, size_bytes):
        if size_bytes >= 1024*1024*1024:
            size_GB = size_bytes / (1024*1024*1024)
            return f"{size_GB:.2f} GB"
        elif size_bytes >= 1024*1024:
            size_MB = size_bytes / (1024*1024)
            return f"{size_MB:.2f} MB"
        else:
            return f"{size_bytes} bytes"

    async def main(self, ctx:commands.Context, path):
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
            