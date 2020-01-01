from HotukdealV3.Hotukdeal.requests import Hud
from discord.ext import tasks
import discord


class Bot(discord.Client):


    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        print('Message from {0.author}: {0.content}'.format(message))

    async def get_posted_deals(self):

        self.channel = self.get_channel(657687492228546573)

        chat_logs = {}

        msg = await self.channel.history(limit=500).flatten()

        for messages in msg:
            embed_content = messages.embeds
            for content in embed_content:
                title = content.title  # title of the embed
                chat_logs[title] = messages.id

        return chat_logs


bot = Bot()

bot.run('NjUzMjczNjU4MDUxMjY0NTIz.Xfpfkg.xgBC5tO0Qz5ahUZGh3VtsUF74jo')


