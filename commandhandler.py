"""Main command handler to handle slash commands"""
import configparser

import discord
from discord import app_commands
from discord.ext import commands

from handlers.download_file import Download_Service
from handlers.list_files import FileList_Service
from handlers.upload_file import Upload_Service


class Commandhandler(commands.Cog):
    """discord commands"""

    def __init__(self, bot: commands.Bot):
        """init func"""
        self.bot = bot
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        use_cloud_database_str = self.config['DEFAULT'].get('use_cloud_database', 'false')
        self.use_cloud_database = use_cloud_database_str.lower() == 'true'

        self.upload_file = Upload_Service(self.use_cloud_database)
        self.download_file = Download_Service(self.use_cloud_database)
        self.list_files = FileList_Service(bot, self.use_cloud_database)

    @app_commands.command(
        name = "upload-file",
        description = "Uploads a file to discord")

    async def upload(self, interaction: discord.Interaction, filepath:str):
        """command to upload files"""
        await self.upload_file.main(interaction, filepath)

    @app_commands.command(
        name = "download-file",
        description = "Downloads a file from discord with the file-id/channel_name/filename")

    async def download (self, interaction: discord.Interaction, file_selector: str):
        """command to download files"""
        await self.download_file.main(interaction, file_selector)

    @app_commands.command(
        name = "list-files",
        description = "List files which are uploaded")

    async def file_list (self, interaction: discord.Interaction):
        """command to list uploaded files"""
        await self.list_files.main(interaction)


async def setup(bot: commands.Bot) -> None:
    """Cogs setup func"""
    await bot.add_cog(
        Commandhandler(bot)
    )
