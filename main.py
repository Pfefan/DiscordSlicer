"""Main class to initialize the programm"""
import configparser
import os
import sys

import discord
from discord.ext import commands

from logging_formatter import ConfigLogger

logger = ConfigLogger().setup()

def get_config():
    if not os.path.isfile("config.ini"):
        config = configparser.ConfigParser()

        config['DEFAULT'] = {
            'token': 'your-discord-bot-token-here',
            'application_id': 'your-applicationid-here',
            'use_cloud_database': 'False',
            'connection_string': 'your-connection-string-here',
            'cluster_name': 'your-cluster-name-here'
        }
        with open('config.ini', 'w+', encoding="utf-8") as configfile:
            config.write(configfile)
        logger.warning("No Config file")
        sys.exit(1)
    else:
        config = configparser.ConfigParser()
        config.read('config.ini')
        return config['DEFAULT']


class MCservers(commands.Bot):
    """Bot setup function"""
    def __init__(self) -> None:
        config = get_config()
        super().__init__(command_prefix = "-", intents = discord.Intents.all(),
                         application_id = config["application_id"], help_command=None)

    async def setup_hook(self) -> None:
        await self.load_extension("commandhandler")
        await bot.tree.sync()

    async def on_ready(self):
        """called when the bot has connected to discord
        sets user activity and prints bot user name"""
        logger.info('Logged in as: %s Ready!', self.user)
        await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,
                                                            name="-help"),
                                                            status=discord.Status.do_not_disturb)

if __name__ == "__main__":
    config_json = get_config()
    os.makedirs('files', exist_ok=True)
    bot = MCservers()
    bot.run(config_json["token"])
