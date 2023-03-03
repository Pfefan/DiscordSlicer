import os
import discord

class Download_Service():
    def __init__(self) -> None:
        self.category_name = "UPLOAD"

    async def download_files(self, interaction, text_channel_name):
        category = discord.utils.get(interaction.guild.categories, name=self.category_name)
        if category is None:
            await interaction.edit_original_response(content=f"No category found with name {self.category_name}")
            return False

        text_channel = discord.utils.get(category.channels, name=text_channel_name)
        if text_channel is None:
            await interaction.edit_original_response(content=f"No text channel found with name {text_channel_name}")
            return False

        await interaction.edit_original_response(content="Downloading files...")
        async for message in text_channel.history(limit=None):
            if len(message.attachments) > 0:
                for attachment in message.attachments:
                    file_path = os.path.join('downloads', attachment.filename)
                    with open(file_path, 'wb') as f:
                        await attachment.save(f)

        await interaction.edit_original_response(content="All files downloaded successfully")

    async def main(self, interaction, text_channel_name):
        await interaction.response.send_message("Working on Download...")
        os.makedirs('downloads', exist_ok=True)
        await self.download_files(interaction, text_channel_name)
