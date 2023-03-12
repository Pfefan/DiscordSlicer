"""Main command handler to handle slash commands"""

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

        self.upload_file = Upload_Service()
        self.download_file = Download_Service()
        self.list_files = FileList_Service(bot)

    @commands.hybrid_command(
        name = "upload-file",
        description = "Uploads a file to discord",
        with_app_command = True)

    async def upload(self, ctx: commands.Context, filepath: str):
        """command to upload files"""
        await ctx.reply("Working on Upload ↓")
        await self.upload_file.main(ctx, filepath)

    @commands.hybrid_command(
        name = "download-file",
        description = "Downloads a file from discord with the file-id/channel_name/filename",
        with_app_command = True)

    async def download (self, ctx: commands.Context, file_selector: str):
        """command to download files"""
        await self.download_file.main(ctx, file_selector)

    @commands.hybrid_command(
        name = "list-files",
        description = "List files which are uploaded",
        with_app_command = True)

    async def file_list (self, ctx: commands.Context):
        """command to list uploaded files"""
        await self.list_files.main(ctx)


async def setup(bot: commands.Bot) -> None:
    """Cogs setup func"""
    await bot.add_cog(
        Commandhandler(bot)
    )
