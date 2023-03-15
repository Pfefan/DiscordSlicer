import os

import discord

from logging_formatter import ConfigLogger
from handlers.database_handler import HybridDBhandler


class DeleteService():
    def __init__(self) -> None:
        """
        Initializes the Delete_Service class.
        """
        self.logger = ConfigLogger().setup()
        self.db_handler = HybridDBhandler()
        self.category_name = "UPLOAD"


    async def delete_file(self, ctx, message, channel_id):
        channel = await ctx.bot.fetch_channel(channel_id)
        await channel.delete()
        result = self.db_handler.delete_by_channel_id(channel_id)
        if result:
            await message.edit(content=f"Deleted {channel.name} with channel_id={channel_id}")
        else:
            await message.edit(content=f"No file with channel_id={channel_id} found")

    async def get_file_channel_id(self, interaction, file):
        # Check if file exists in database by ID
        if file.isdigit():
            id_entry = self.db_handler.find_by_id(file)
            if id_entry is not None:
                return id_entry

        # If file not found by ID, try finding it by basename
        basename = os.path.basename(file)
        basename = os.path.splitext(basename)[0]
        name_entry = self.db_handler.find_by_filename(basename)
        if name_entry is not None:
            return name_entry

        # If file not found by basename, try finding the channel by name
        category = discord.utils.get(interaction.guild.categories, name=self.category_name)
        if category is None:
            category = await interaction.guild.create_category(self.category_name)
        channel = discord.utils.get(category.channels, name=file)
        if channel is not None:
            channel_entry = self.db_handler.find_by_channel_id(channel.id)
            if channel_entry is not None:
                return channel_entry


    async def main(self, ctx, file_sel:str):
        channel_id = await self.get_file_channel_id(ctx, file_sel)
        if channel_id != None:
            message = await ctx.send("Preparing deletion")
            self.logger.info("Found file in the channel with the id %s", channel_id)
            await self.delete_file(ctx, message, channel_id)
        else:
            self.logger.info("Didnt find any file for the input: %s", file_sel)
            await message.edit(content=f"Didnt find any file for the input: {file_sel}")
