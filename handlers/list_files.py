import asyncio

import discord
from discord.ext import commands

from handlers.database_handler import FileManager
from logging_formatter import ConfigLogger


class FileList_Service(discord.ui.View):
    def __init__(self, bot: commands.Bot) -> None:
        self.db_handler = FileManager()
        self.logger = ConfigLogger().setup()
        self.bot = bot

    async def get_embed(self, page=1):
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
            return embed, ButtonView(page=page, num_pages=num_pages)
        else:
            return embed, None

    async def embed(self, interaction, page=1):
        embed, view = await self.get_embed(page)
        await interaction.response.send_message(embed=embed, view=view)

    async def main(self, interaction):
        await self.embed(interaction)


class ButtonView(discord.ui.View):
    def __init__(self, page, num_pages):
        super().__init__()
        self.page = page
        self.num_pages = num_pages

        if page < num_pages:
                @discord.ui.button(label="Next", style=discord.ButtonStyle.primary, emoji="➡️")
                async def next_callback(self, button, interaction):
                    print("next")
        if page > 1:
            @discord.ui.button(label="Previous", style=discord.ButtonStyle.primary, emoji="⬅️")
            async def previous_callback(self, button, interaction):
                print("previous")

    async def on_button_click(self, interaction: discord.Interaction, button: discord.ui.Button,):
        if button.custom_id == "next_button":
            self.page += 1
        elif button.custom_id == "previous_button":
            self.page -= 1
        embed, view = await FileList_Service().get_embed(self.page)
        await interaction.response.edit_message(embed=embed, view=view)
