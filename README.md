# DiscordSlicer

DiscordSlicer is a program that allows you to easily upload files larger than 25MB to Discord by slicing them up into 25MB parts. Once the files are uploaded, you can download them or delete them.

## Todo's

- Doku
- Better error handling
- Bug fixes & improvements
- implement a folder structure
- In discord database

## Installation

1. Clone this repository.
2. Install the required dependencies using `pip install -r requirements.txt`.
3. Create a new application on [Discord Developer Portal](https://discord.com/developers/applications).
4. Create a bot user for your application and copy the bot token
5. Paste it into the config in the `DISCORD_TOKEN=<your-bot-token>` value
6. Invite the bot to your server
7. Add your discord username with discriminator to the username key in the config

## Usage

To run this bot, run `python main.py`.

If you want to share files with others you can use [MongoDB](https://cloud.mongodb.com), this is a free cloud database service. To use it, you need to change the the use cloud database setting to true and put in your connection string and cluster name.
