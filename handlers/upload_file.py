import os
import shutil

import discord
from handlers.database_handler import FileManager

from logging_formatter import ConfigLogger


class Upload_Service():
    def __init__(self) -> None:
        self.chunk_size = 8388608
        self.category_name = "UPLOAD"
        self.logger = ConfigLogger().setup()
        self.db_handler = FileManager()

    def split_file(self, path):
        filename = os.path.basename(path)
        file_size = os.stat(path).st_size

        os.makedirs(f'files/upload/{filename}')

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

    async def upload_files(self, interaction, filename, path):
        base_name, extension = os.path.splitext(filename)
        category_name = "UPLOAD"
        category = discord.utils.get(interaction.guild.categories, name=category_name)
        if category is None:
            category = await interaction.guild.create_category(category_name)
        text_channel = discord.utils.get(category.channels, name=filename)

        if text_channel is None:
            text_channel = await category.create_text_channel(base_name)
        else:
            self.logger.error("File already exists")
            await interaction.edit_original_response(content="File already exists")
            return False

        directory = f'files/upload/{filename}'
        files = os.listdir(directory)
        total_files = len(files)
        uploaded_files = 0
        
        self.logger.info("Uploading files %s", total_files)
        await interaction.edit_original_response(content=f"Uploading files {total_files}")

        for file in files:
            with open(os.path.join(directory, file), 'rb') as f:
                filename = os.path.basename(file)
                discord_file = discord.File(f, filename=filename)
                await text_channel.send(file=discord_file)
            uploaded_files += 1
            await interaction.edit_original_response(content=f"Uploaded {uploaded_files}/{total_files} files")

        channel_id = text_channel.id
        user_id = interaction.user.id

        file_name = base_name
        file_size = os.stat(path).st_size
        file_type = extension.replace(".", "")
        self.db_handler.add_file(user_id, channel_id, file_name, self.convert_size(file_size), file_type)

        self.logger.info("All files uploaded successfully")
        await interaction.edit_original_response(content="All files uploaded successfully")

    def convert_size(self, size_bytes):
        if size_bytes >= 1024*1024*1024:
            size_GB = size_bytes / (1024*1024*1024)
            return f"{size_GB:.2f} GB"
        elif size_bytes >= 1024*1024:
            size_MB = size_bytes / (1024*1024)
            return f"{size_MB:.2f} MB"
        else:
            return f"{size_bytes} bytes"

    async def main(self, interaction, path):
        await interaction.response.send_message("Working on Upload...")
        os.makedirs('files/upload', exist_ok=True)
        if os.path.exists(path):
            success = self.split_file(path)
            if success:
                filename = os.path.basename(path)
                await self.upload_files(interaction, filename, path)
                shutil.rmtree(f"files/upload/{filename}")
        else:
            self.logger.error("File %s doesnt exist", path)
            await interaction.edit_original_response(content=f"File {path} doesnt exist")
            