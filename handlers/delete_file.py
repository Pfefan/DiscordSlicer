"""
This module provides a DeleteService class that allows for the deletion of files
uploaded to a Discord server.
The class uses a HybridDBhandler object to keep track of file metadata and the Discord API
to delete the associated
channels. The main function of the class is the `main` method, which takes in a file selection
string and attempts to
find the associated channel ID. If a channel is found, the `delete_file` method is called
to delete the channel and
remove its metadata from the database. If a channel is not found, an error message is displayed.

Classes:
    DeleteService: Provides functionality for deleting files uploaded to a Discord server.
"""
import os

import discord
from discord.ext import commands

from logging_formatter import ConfigLogger
from handlers.database_handler import HybridDBhandler


class DeleteService():
    """
    This class provides functionality for deleting files uploaded to a Discord server.
    """
    def __init__(self) -> None:
        """
        Initializes the DeleteService class.
        """
        self.logger = ConfigLogger().setup()
        self.db_handler = HybridDBhandler()
        self.category_name = "UPLOAD"


    async def delete_file(self, ctx:commands.Context, message:discord.Message, channel_id:int):
        """
        Deletes the channel with the specified channel ID
        and removes the corresponding entry from the database.

        Args:
            ctx (discord.ext.commands.Context): The context of the command.
            message (discord.Message): The message to edit after the channel has been deleted.
            channel_id (str): The ID of the channel to delete.

        Returns:
            None
        """
        channel = await ctx.bot.fetch_channel(channel_id)
        await channel.delete()
        result = self.db_handler.delete_by_channel_id(channel_id)
        if result:
            await message.edit(content=f"Deleted {channel.name} with channel_id={channel_id}")
        else:
            await message.edit(content=f"No file with channel_id={channel_id} found")

    async def get_file_channel_id(self, ctx:commands.Context, file:str):
        """
        Returns the channel ID associated with the given file name or ID.

        Parameters
        ----------
        ctx : commands.Context
            The context in which the message was sent.
        file : str
            The name or ID of the file to find the channel ID for.

        Returns
        -------
        str or None
            The channel ID associated with the given file name or ID, or None if not found.
        """
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
        category = discord.utils.get(ctx.guild.categories, name=self.category_name)
        if category is None:
            category = await ctx.guild.create_category(self.category_name)
        channel = discord.utils.get(category.channels, name=file)
        if channel is not None:
            channel_entry = self.db_handler.find_by_channel_id(channel.id)
            if channel_entry is not None:
                return channel_entry


    async def main(self, ctx:commands.Context, file_sel:str):
        """
        Entry point of the DeleteService class. Deletes the channel associated
        with the given file name or ID
        and updates the database, or displays an error message if the file is not found.

        Parameters:
        -----------
        ctx : discord.ext.commands.Context
            The context in which the command was sent.
        file_sel : str
            The name or ID of the file to delete.

        Returns:
        --------
        None
        """
        channel_id = await self.get_file_channel_id(ctx, file_sel)
        if channel_id is not None:
            message = await ctx.send("Preparing deletion")
            self.logger.info("Found file in the channel with the id %s", channel_id)
            await self.delete_file(ctx, message, channel_id)
        else:
            self.logger.info("Didnt find any file for the input: %s", file_sel)
            await message.edit(content=f"Didnt find any file for the input: {file_sel}")
