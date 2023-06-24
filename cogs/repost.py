import discord
from discord.ext import commands



class Repost(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cache = []


    async def setup(self):
        await self.cache_reposts()

    async def cache_reposts(self):
        async with self.bot.pool.acquire() as conn:
            query = "SELECT * FROM repost"
            rows = await conn.fetch(query)
            for row in rows:
                post = row["post"]
                self.cache.append(post)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """Saves twitter links to a database, compares if previously posted then automatically removes the message."""
        if message.author.bot:
            return
        if "twitter.com" in message.content:
                link = message.content
                split_message = link.split("?")
                tweet = split_message[0]
                if tweet in self.cache:
                    await message.delete()
                else:
                    self.cache.append(tweet)
                    async with self.bot.pool.acquire() as conn:
                        await conn.execute('INSERT INTO tweet (post) VALUES ($1)', tweet)


async def setup(bot):
    repost_cog = Repost(bot)
    await repost_cog.setup()
    await bot.add_cog(repost_cog)