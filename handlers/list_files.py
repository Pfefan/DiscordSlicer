"""
This module contains the `FileListService` class that provides functionality for retrieving
 a list of uploaded files.
"""
import discord
from discord.ext import commands
from discord.ui import Button, View

from handlers.database_handler import HybridDBhandler
from logging_formatter import ConfigLogger


class FileListService:
    """
    A class that provides methods to display a list of uploaded files.

    Attributes:
        db_handler (HybridDBhandler): An instance of the HybridDBhandler class
         for database operations.
        logger (ConfigLogger): An instance of the ConfigLogger class for logging.
        bot (commands.Bot): An instance of the discord.ext.commands.Bot class.

    """
    def __init__(self, bot: commands.Bot):
        """
        Constructor for the FileListService class.

        Args:
            bot (commands.Bot): An instance of the discord.ext.commands.Bot class.

        """
        self.db_handler = HybridDBhandler()
        self.logger = ConfigLogger().setup()
        self.bot = bot

    async def get_embed(self, page, ctx):
        """
        A method that gets an Embed object for the given page number.

        Args:
            page (int): The page number to get the Embed object for.
            ctx (commands.Context): The context object for the current command invocation.

        Returns:
            tuple: A tuple containing the Embed object and the View object,
             if it exists, for the given page number.

        """
        self.logger.info("Getting embed for page %s...", page)
        files = self.db_handler.get_files()

        if not files:
            await ctx.send("There are no files stored in the database.")
            return None, None

        chunks = [files[i:i+8] for i in range(0, len(files), 8)]
        num_pages = len(chunks)

        if page < 1 or page > num_pages:
            page = 1

        current_chunk = chunks[page-1]
        embed = discord.Embed(title="FILES", description="List of uploaded files",
                              color=discord.Color.blurple())

        counter = 1
        for file in current_chunk:
            user = await self.bot.fetch_user(file.user_id)
            channel = self.bot.get_channel(file.channel_id)
            if channel:
                embed.add_field(
                    name=f"{counter}). {file.file_name}.{file.file_type}",
                    value=(f"ID: {file.file_id} | Uploader: {user.mention} | Size: {file.file_size}"
                        + f"\nsaved in channel: {channel.name}"),
                    inline=False
                )
            embed.add_field(
                name=f"{counter}). {file.file_name}.{file.file_type}",
                value=(f"ID: {file.file_id} | Uploader: {user.mention} | Size: {file.file_size}"
                    + "\nChannel name not found. It may have been deleted."),
                inline=False
            )

            counter += 1

        if num_pages > 1:
            embed.set_footer(text=f"Page {page}/{num_pages}")

            previous_btn = Button(label="Previous", style=discord.ButtonStyle.secondary,
                                  emoji="⬅️", disabled=page == 1)
            next_btn = Button(label="Next", style=discord.ButtonStyle.secondary,
                              emoji="➡️", disabled=page == num_pages)

            async def previous_callback(ctx: commands.Context, page):
                """
                A method that handles the button click event for the previous button.

                Args:
                    ctx (commands.Context): The context object for the current command invocation.
                    page (int): The current page number.

                """
                if page > 1:
                    new_page = page - 1
                    embed, view = await self.get_embed(new_page, ctx)
                    await ctx.response.defer()
                    await ctx.message.edit(embed=embed, view=view)

            async def next_callback(ctx: commands.Context, page, num_pages):
                """
                A method that handles the button click event for the next button.

                Args:
                    ctx (commands.Context): The context object for the current command invocation.
                    page (int): The current page number.
                """
                if page < num_pages:
                    new_page = page + 1
                    embed, view = await self.get_embed(new_page, ctx)
                    await ctx.response.defer()
                    await ctx.message.edit(embed=embed, view=view)

            previous_btn.callback = lambda i: previous_callback(i, page)
            next_btn.callback = lambda i: next_callback(i, page, num_pages)

            view = View()
            view.add_item(previous_btn)
            view.add_item(next_btn)

            self.logger.info("Returning embed and view for page %s", page)
            return embed, view
        self.logger.info("Returning embed for page %s", page)
        return embed, None


    async def embed(self, ctx, page=1):
        """
        Sends a message indicating that data is being retrieved, retrieves an embed
        with a list of uploaded files, and edits the message with the retrieved embed and view.

        Parameters:
            ctx (commands.Context): The context object of the command invocation.
            page (int, optional): The page number of the embed to retrieve. Defaults to 1.
        """
        message = await ctx.send(content="Getting data..")
        embed, view = await self.get_embed(page, ctx)
        if embed is not None:
            await message.edit(embed=embed, view=view)

    async def main(self, ctx):
        """
        Retrieves an embed with a list of uploaded files and sends the embed as a message.

        Parameters:
            ctx (commands.Context): The context object of the command invocation.
        """
        await self.embed(ctx)
