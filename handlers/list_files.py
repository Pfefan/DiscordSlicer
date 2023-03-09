import discord
from discord.ext import commands
from discord.ui import Button, View

from handlers.database_handler import Hybrid_DB_handler
from logging_formatter import ConfigLogger


class FileList_Service():
    def __init__(self, bot: commands.Bot) -> None:
        self.db_handler = Hybrid_DB_handler()
        self.logger = ConfigLogger().setup()
        self.bot = bot
        self.page = 1
        self.message = None


    async def get_embed(self, page, ctx):
        self.logger.info("Getting embed for page %s...", page)
        files = self.db_handler.get_files()

        chunks = [files[i:i+8] for i in range(0, len(files), 8)]
        num_pages = len(chunks)

        if page < 1 or page > num_pages:
            page = 1

        current_chunk = chunks[page-1]
        embed = discord.Embed(title="FILES", description="List of uploaded files", color=discord.Color.blurple())

        for file in current_chunk:
            user = await self.bot.fetch_user(file.user_id)
            channel = self.bot.get_channel(file.channel_id)
            embed.add_field(
                name=f"{file.id}). {file.file_name}.{file.file_type}",
                value=f"Uploader: {user.mention} | Size: {file.file_size} \n Saved in channel: {channel.name}",
                inline=False
            )

        if num_pages > 1:
            embed.set_footer(text=f"Page {page}/{num_pages}")

            previous_btn = Button(label="Previous", style=discord.ButtonStyle.secondary, emoji="⬅️", disabled=(page == 1))
            next_btn = Button(label="Next", style=discord.ButtonStyle.secondary, emoji="➡️", disabled=(page == num_pages))

            async def previous_callback(ctx, page):
                if page > 1:
                    new_page = page - 1
                    embed, view = await self.get_embed(new_page, ctx)
                    await ctx.response.defer()
                    await self.message.edit(embed=embed, view=view)
            
            async def next_callback(ctx, page, num_pages):
                if page < num_pages:
                    new_page = page + 1
                    embed, view = await self.get_embed(new_page, ctx)
                    await ctx.response.defer()
                    await self.message.edit(embed=embed, view=view)

            previous_btn.callback = lambda i: previous_callback(i, page)
            next_btn.callback = lambda i: next_callback(i, page, num_pages)

            view = View()
            view.add_item(previous_btn)
            view.add_item(next_btn)

            self.logger.info("Returning embed and view for page %s", page)
            return embed, view
        else:
            self.logger.info("Returning embed for page %s", page)
            return embed, None


    async def embed(self, ctx, page=1):
        embed, view = await self.get_embed(page, ctx)
        self.message = await ctx.send(embed=embed, view=view)


    async def main(self, ctx):
        await self.embed(ctx)
