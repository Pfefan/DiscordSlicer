import discord
from discord.ext import commands
from discord.ui import Button, View

from handlers.database_handler import FileManager
from logging_formatter import ConfigLogger


class FileList_Service():
    def __init__(self, bot: commands.Bot) -> None:
        self.db_handler = FileManager()
        self.logger = ConfigLogger().setup()
        self.bot = bot
        self.page = 1

    async def get_embed(self, page, msg_interaction):
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

            previous_btn = Button(label="Previous", style=discord.ButtonStyle.primary, emoji="⬅️", disabled=(page == 1))
            next_btn = Button(label="Next", style=discord.ButtonStyle.primary, emoji="➡️", disabled=(page == num_pages))

            async def previous_callback(interaction, page):
                if page > 1:
                    new_page = page - 1
                    embed, view = await self.get_embed(new_page, msg_interaction)
                    await interaction.response.defer()
                    await msg_interaction.edit_original_response(embed=embed, view=view)
            
            async def next_callback(interaction, page, num_pages):
                if page < num_pages:
                    new_page = page + 1
                    embed, view = await self.get_embed(new_page, msg_interaction)
                    await interaction.response.defer()
                    await msg_interaction.edit_original_response(embed=embed, view=view)

            previous_btn.callback = lambda i: previous_callback(i, page)
            next_btn.callback = lambda i: next_callback(i, page, num_pages)

            view = View()
            view.add_item(previous_btn)
            view.add_item(next_btn)

            return embed, view
        else:
            return embed, None


    async def embed(self, interaction, page=1):
        embed, view = await self.get_embed(page, interaction)
        await interaction.response.send_message(embed=embed, view=view)

    async def main(self, interaction):
        await self.embed(interaction)
