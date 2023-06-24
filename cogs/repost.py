import discord
from discord.ext import commands
import re


class Repost(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.tweet_cache = []


    async def setup(self):
        await self.cache_tweets()

    async def cache_tweets(self):
        async with self.bot.pool.acquire() as conn:
            query = "SELECT * FROM tweet"
            rows = await conn.fetch(query)
            for row in rows:
                post = row["post"]
                self.tweet_cache.append(post)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Saves twitter links to a database, compares if previously posted then automatically removes the message."""
        if message.author.bot:
            return
        twitter_pattern = r'https?://(www\.)?(fxtwitter|vxtwitter|twitter)\.com/[^\s]+'
        twitter = re.search(twitter_pattern, message.content)

        if twitter:
                link = twitter.group()
                link = link.replace('fxtwitter.com', 'twitter.com')
                link = link.replace('vxtwitter.com', 'twitter.com')
                print(link)
                split_message = link.split("?")
                tweet = split_message[0]
                if tweet in self.tweet_cache:
                    await message.delete()
                else:
                    self.tweet_cache.append(tweet)
                    async with self.bot.pool.acquire() as conn:
                        await conn.execute('INSERT INTO tweet (post) VALUES ($1)', tweet)


async def setup(bot):
    repost_cog = Repost(bot)
    await repost_cog.setup()
    await bot.add_cog(repost_cog)