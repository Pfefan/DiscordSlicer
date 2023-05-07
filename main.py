"""Main class to initialize the program."""
import configparser
import os
import sys

import discord
from discord.ext import commands

from logging_formatter import ConfigLogger

logger = ConfigLogger().setup()

def get_config():
    """Return the configuration file as a dictionary or exit the program if the file is not found.

    If the `config.ini` file is not found, a default configuration will be created
    and saved to the file.
    Otherwise, the file will be read and the contents will be returned as a dictionary.
    The dictionary will contain the configuration values from the `DEFAULT` section
    of the config file.

    Returns:
        dict: The configuration values as a dictionary.

    Raises:
        SystemExit: If the `config.ini` file is not found and a default configuration
        cannot be created.
    """
    if not os.path.isfile("config.ini"):
        config = configparser.ConfigParser()

        config['BOT'] = {
            'token': 'your-discord-bot-token-here',
            'application_id': 'your-applicationid-here',
        }

        config['DATABASE'] = {
            'use_cloud_database': 'False',
            'connection_string': 'your-connection-string-here',
            'cluster_name': 'your-cluster-name-here'
        }
        config['AUTH'] = {
            'usernames': "your usernames here seperated by commas"
        }
        with open('config.ini', 'w+', encoding="utf-8") as configfile:
            config.write(configfile)
        logger.warning("No Config file")
        sys.exit(1)
    else:
        config = configparser.ConfigParser()
        config.read('config.ini')
        return config


class Botserver(commands.Bot):
    """
    Bot setup function.

    Attributes:
        None.
    """
    def __init__(self) -> None:
        self.config = get_config()
        super().__init__(command_prefix = "-", intents = discord.Intents.all(),
                         application_id = self.config['BOT']["application_id"], help_command=None)

    async def setup_hook(self) -> None:
        """Loads the commandhandler extension and syncs the slash commands tree
        with Discord's API."""
        await self.load_extension("commandhandler")
        await bot.tree.sync()

    async def on_ready(self):
        """
        Called when the bot has connected to Discord.

        Sets the user activity and prints the bot's user name.

        Args:
            None.

        Returns:
            None.
        """
        logger.info('Logged in as: %s Ready!', self.user)
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,
                                                            name="-help"),
                                                            status=discord.Status.do_not_disturb)

if __name__ == "__main__":
    config_json = get_config()
    os.makedirs('files', exist_ok=True)
    bot = Botserver()
    bot.run(config_json['BOT']["token"])
