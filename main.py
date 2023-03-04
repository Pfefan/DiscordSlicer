"""Main class to initialize the programm"""
import os
import sys

import discord
from discord.ext import commands

from logging_formatter import ConfigLogger
logger = ConfigLogger().setup()

def get_config():
    if not os.path.isfile("config.txt"):
        with open("config.txt", "w+", encoding="utf8") as conf:
            conf.write("TOKEN=your-discord-bot-token-here\nAPPLICATION_ID=your-applicationid-here")
            logger.info("Invalid Token")
            sys.exit(1)
    else:
        with open("config.txt", "r", encoding="utf8") as conf:
            content = conf.readlines()
            content = [line.strip() for line in content]
            config_dict = dict(line.split("=") for line in content)
            return config_dict


class MCservers(commands.Bot):
    """Bot setup function"""
    def __init__(self) -> None:
        config = get_config()
        super().__init__(command_prefix = "-", intents = discord.Intents.all(),
                         application_id = config["APPLICATION_ID"])

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
    bot.run(config_json["TOKEN"])
