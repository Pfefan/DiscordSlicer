"""Main command handler to handel slash commands"""
import discord
from discord import app_commands
from discord.ext import commands

from handlers.upload_file import Upload_Service
from handlers.download_file import Download_Service


class Commandhandler(commands.Cog):
    """discord commands"""

    def __init__(self, bot: commands.Bot):
        """init func"""
        self.bot = bot
        self.upload_file = Upload_Service()
        self.download_file = Download_Service()

    @app_commands.command(
        name = "upload-file",
        description = "Uploads a file to discord")

    async def upload(self, interaction: discord.Interaction, filepath:str):
        """command to List specific servers"""
        await self.upload_file.main(interaction, filepath)

    @app_commands.command(
        name = "download-file",
        description = "Downloads a file from discord")

    async def download (self, interaction: discord.Interaction, filedest:str):
        """command to get servers with players online"""
        print("download")


async def setup(bot: commands.Bot) -> None:
    """Cogs setup func"""
    await bot.add_cog(
        Commandhandler(bot)
    )
