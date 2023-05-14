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
import discord
from discord.ext import commands
from discord.ui import Button, View

from logging_formatter import ConfigLogger
from handlers.database_handler import HybridDBhandler
from handlers.search_file import SearchService


class DeleteService():
    """
    This class provides functionality for deleting files uploaded to a Discord server.
    """
    def __init__(self) -> None:
        """
        Initializes the DeleteService class.
        """
        self.logger = ConfigLogger().setup()
        self.search_serv = SearchService()
        self.db_handler = HybridDBhandler()
        self.category_name = "UPLOAD"

    async def delete_file(self, ctx:commands.Context, message:discord.Message, channel_id:int):
        """
        Deletes the file from the Discord server and database.

        Args:
        - ctx (discord.ext.commands.Context): The context of the command.
        - message (discord.Message): The message containing the file to be deleted.
        - channel_id (int): The ID of the channel containing the file.

        Returns:
        - None
        """
        filedata = self.db_handler.get_file_by_channelid(channel_id)
        filename = f"{filedata['file_name']}.{filedata['file_type']}"
        embed = discord.Embed(title="Delete File",
                description="Do you really want to delete this file?",
                color=0x90EE90)
        embed.add_field(name="Selected File", value=filename)
        embed.add_field(name="File Size", value=f"{filedata['file_size']}")
        ok_btn = Button(label="Ok", style=discord.ButtonStyle.secondary,
                                emoji="👍")
        cancel_btn = Button(label="Cancel", style=discord.ButtonStyle.secondary,
                            emoji="❌")

        async def okbtn_callback(btn_ctx: commands.Context):
            """
            Callback function for the OK button.

            Args:
            - btn_ctx (discord.ext.commands.Context): The context of the button click.

            Returns:
            - None
            """
            await btn_ctx.response.defer()
            channel = await ctx.bot.fetch_channel(channel_id)
            await channel.delete()
            result = self.db_handler.delete_by_channel_id(channel_id)
            embed = discord.Embed(title="Delete File")
            if result:
                embed.description = f"Successfully deleted {filename}"
                embed.colour = discord.Colour.green()
                await message.edit(embed=embed, view=None)
            else:
                embed.description = f"No file with channel_id={channel_id} in the database found"
                embed.colour = discord.Colour.red()
                await message.edit(embed=embed, view=None)
                await message.edit(content=f"No file with channel_id={channel_id} in the database found")
            view.stop()

        async def cancelbtn_callback(btn_ctx: commands.Context):
            """
            Callback function for the Cancel button.

            Args:
            - btn_ctx (discord.ext.commands.Context): The context of the button click.

            Returns:
            - None
            """
            await btn_ctx.response.defer()
            embed = discord.Embed(title="Delete File", description="Canceled deletion",
                                  colour=discord.Colour.red())
            await message.edit(embed=embed, view=None)
            view.stop()

        ok_btn.callback = okbtn_callback
        cancel_btn.callback = cancelbtn_callback

        view = View()
        view.add_item(ok_btn)
        view.add_item(cancel_btn)

        await message.edit(embed=embed, view=view)


    async def main(self, ctx:commands.Context, file_sel:str):
        """
        This method is deleting a by the user selected file and then prompting for confirmation
        before deleting the file. It takes in a Discord context object, `ctx`,
        and a string `file_sel`, which is the file selector entered by the user.

        Parameters:
        -----------
        ctx: commands.Context
            A context object representing the invocation context of the command.
        file_sel: str
            The name of the file to be deleted.

        Returns:
        --------
        None
        """
        embed = discord.Embed(title="Delete File", description="Preparing deletion",
                color=0x90EE90)
        channel_id = await self.search_serv.main(ctx, file_sel, self.category_name)
        if channel_id:
            message = await ctx.send(embed=embed)
            self.logger.info("Found file in the channel with the id %s", channel_id)
            await self.delete_file(ctx, message, channel_id)
        else:
            self.logger.info("Didnt find any file for the input: %s", file_sel)
            embed.color = discord.Color.red()
            embed.description = f"Didnt find any file for the input: {file_sel}"
            await ctx.send(embed=embed)
