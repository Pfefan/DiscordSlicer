"""Main command handler to handel slash commands"""
import discord
from discord import app_commands
from discord.ext import commands


class Commandhandler(commands.Cog):
    """discord commands"""

    def __init__(self, bot: commands.Bot):
        """init func"""
        self.bot = bot
        self.onlookup = serverlookup_on.Lookup()
        self.onlinecmd = showembed_on.OnEmbed()
        self.detailscmd = details.Details()
        self.watchserver = playeraktivitycmd.Main()
        self.autorun = autorun.Autorun()
        self.listcmd = liston.Listserver()

    @app_commands.command(
        name = "upload-file",
        description = "Uploads a file to discord")

    async def upload(self, interaction: discord.Interaction, filepath:str):
        """command to List specific servers"""
        await self.listcmd.main(interaction, filepath)

    @app_commands.command(
        name = "download-file",
        description = "Downloads a file from discord")

    async def download (self, interaction: discord.Interaction, filedest:str):
        """command to get servers with players online"""
        await self.onlinecmd.sortdata(interaction, filedest)


async def setup(bot: commands.Bot) -> None:
    """Cogs setup func"""
    await bot.add_cog(
        Commandhandler(bot)
    )
