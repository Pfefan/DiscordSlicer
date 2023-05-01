"""
This module defines a Commandhandler cog that handles slash commands to
upload, download, delete, and list files.

Classes:

    Commandhandler: A Discord Cog that defines slash commands to
    upload, download, delete, and list files.

Functions:

    setup: A function that sets up the Commandhandler cog.

"""

import discord
from discord.ext import commands

from handlers.download_file import DownloadService
from handlers.list_files import FileListService
from handlers.upload_file import UploadService
from handlers.delete_file import DeleteService


class Commandhandler(commands.Cog):
    """A Discord Cog that defines slash commands to upload, download, delete, and list files."""

    def __init__(self, bot: commands.Bot):
        """Initializes the Commandhandler cog.

        Args:
        - bot (commands.Bot): A Discord bot object.
        """
        self.bot = bot

        self.upload_file = UploadService()
        self.download_file = DownloadService()
        self.delete_file = DeleteService()
        self.list_files = FileListService(bot)

        self.config = bot.config

    async def userauth(self, ctx: commands.Context):
        """
        Checks if the user which send a command is authenticated in the config file
        
        Args:
        - ctx (commands.context): Message context
        
        Returns:
        - bool: True if the user is authenticated, False if not
        """
        usernames = self.config["AUTH"]["usernames"]
        usernames = [username.strip() for username in usernames.split(", ")]
        
        if str(ctx.author) in usernames:
            return True
        else:
            embed = discord.Embed(title="Authentication Error",
                              description="You are not authorized to use this command.",
                              color=discord.Color.red())
            await ctx.reply(embed=embed)
            return False

    @commands.hybrid_command(
        name = "upload-file",
        description = "Uploads a file to discord",
        with_app_command = True)

    async def upload(self, ctx: commands.Context, filepath: str):
        """A Discord slash command to upload files.

        Args:
        - ctx (commands.Context): A context object that represents the invocation
        context of the command.
        - filepath (str): A string that represents the path of the file to be uploaded.
        """
        if await self.userauth(ctx):
            await self.upload_file.main(ctx, filepath)

    @commands.hybrid_command(
        name = "download-file",
        description = "Downloads a file from discord with the file-id/channel_name/filename",
        with_app_command = True)

    async def download (self, ctx: commands.Context, file_selector: str):
        """A Discord slash command to download files.

        Args:
        - ctx (commands.Context): A context object that represents the invocation
        context of the command.
        - file_selector (str): A string that represents the file identifier
        or the file name to be downloaded.
        """
        if await self.userauth(ctx):
            await self.download_file.main(ctx, file_selector)

    @commands.hybrid_command(
        name = "delete-file",
        description = "Deletes a selected file from Discord",
        with_app_command = True)

    async def delete (self, ctx: commands.Context, file_selector: str):
        """A Discord slash command to delete files.

        Args:
        - ctx (commands.Context): A context object that represents the invocation context
        of the command.
        - file_selector (str): A string that represents the file identifier or the file name
        to be deleted.
        """
        if await self.userauth(ctx):
            await self.delete_file.main(ctx, file_selector)

    @commands.hybrid_command(
        name = "list-files",
        description = "List files which are uploaded",
        with_app_command = True)

    async def file_list (self, ctx: commands.Context):
        """A Discord slash command to list uploaded files.

        Args:
        - ctx (commands.Context): A context object that represents the invocation context
        of the command.
        """
        await self.list_files.main(ctx)

    @commands.hybrid_command(
        name = "help",
        description = "Displays an embed that shows all possible commands.",
        with_app_command = True)

    async def help(self, ctx: commands.Context):
        """A Discord slash command that displays an embed of all possible commands.

        Args:
        - ctx (commands.Context): A context object that represents the invocation
        context of the command.
        """
        embed = discord.Embed(title="Available Commands", color=0xff69b4)
        embed.add_field(
            name="upload-file",
            value="Uploads a file to Discord",
            inline=False
        )
        embed.add_field(
            name="download-file",
            value="Downloads a file from Discord with the file-id/channel_name/filename",
            inline=False
        )
        embed.add_field(
            name="delete-file",
            value="Deletes a selected file from Discord",
            inline=False
        )
        embed.add_field(
            name="list-files",
            value="Lists files that have been uploaded",
            inline=False
        )

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot) -> None:
    """Cogs setup func"""
    await bot.add_cog(
        Commandhandler(bot)
    )
