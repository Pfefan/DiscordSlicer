"""
Module for searching for saved files with one of these Properties: id, filename or channel name.

This module provides a Search_Service class that can be used to search for saved files using their
properties such as ID, filename or channel name.
"""
import os

import discord
from discord.ext import commands

from handlers.database_handler import HybridDBhandler
from logging_formatter import ConfigLogger


class SearchService:
    """
    Class to search for saved files using their properties such as ID, filename or channel name.

    Attributes
    ----------
    db_handler : HybridDBhandler
        The handler for database queries.
    logger : logging.Logger
        The logger for logging messages.

    Methods
    -------
    __init__(self)
        Initializes the `Search_Service` class.
    async def main(self, ctx: commands.context, file:str)
        Searches for the channel ID associated with the given file name or ID.
    async def get_file_channel_id(self, ctx:commands.Context, file:str)
        Returns the channel ID associated with the given file name or ID.
    """

    def __init__(self) -> None:
        """Initializes the `Search_Service` class."""
        self.db_handler = HybridDBhandler()
        self.logger = ConfigLogger().setup()

    async def main(self, ctx: commands.context, file:str, category_name:str):
        """
        Searches for the channel ID associated with the given file name or ID.

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
        self.logger.info("Getting channel_id from file with input %s", file)
        file_channel = await self.get_file_channel_id(ctx, file, category_name)
        return file_channel

    async def get_file_channel_id(self, ctx:commands.Context, file:str, category_name:str):
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
        category = discord.utils.get(ctx.guild.categories, name=category_name)
        if category is None:
            category = await ctx.guild.create_category(category_name)
        channel = discord.utils.get(category.channels, name=file)
        if channel is not None:
            channel_entry = self.db_handler.find_by_channel_id(channel.id)
            if channel_entry is not None:
                return channel_entry
