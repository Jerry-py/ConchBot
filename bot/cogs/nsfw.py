import discord
from discord.ext import commands
from dotenv import load_dotenv
import asyncpraw
import os
import random
import rule34
from hentai import Hentai, Format, Utils
import DiscordUtils

load_dotenv('.env')

rule34 = rule34.Rule34()
reddit = asyncpraw.Reddit(client_id = os.getenv("redditid"),
            client_secret = os.getenv("redditsecret"),
            username = "UnsoughtConch",
            password = os.getenv('redditpassword'),
            user_agent = "ConchBotPraw")

class NSFW(commands.Cog):

    '''
    ConchBot has one of the best NSFW categories on Discord, while not even being its main focus.
    '''

    def __init__(self, client):
        self.client = client

    @commands.group(invoke_without_command=True, description="Get a hentai image from r/hentai.")
    async def hentai(self, ctx):
        msg = await ctx.send("Getting your porn...")
        subreddit = await reddit.subreddit('hentai')
        top = subreddit.top(limit=50)
        all_subs = []

        async for submission in top:
            all_subs.append(submission)
        
        ransub = random.choice(all_subs)

        embed = discord.Embed(title=ransub.title, colour=ctx.author.colour, url=ransub.url)
        embed.set_image(url=ransub.url)
        embed.set_footer(text=f"Posted by {ransub.author} on Reddit. | ❤ {ransub.ups} | 💬 {ransub.num_comments}")
        await msg.delete()
        await ctx.send(embed=embed)

    @commands.command(description="Use a sauce code to find a hentai comic from nhentai.net.\n[id] value is optional. Returns random NHentai comic when none.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def sauce(self, ctx, id=None):
        await ctx.send("Getting your porn...")
        doujin = Utils.get_random_hentai() if id is None else Hentai(id)
        if not Hentai.exists(doujin.id):
            await ctx.send("Nothing found.")

        else:
            try:
                artist = doujin.artist[0].name
            except:
                artist = "No artist"
            embeds = []
            for num, url in enumerate(doujin.image_urls, start=1):
                embed = discord.Embed(title=doujin.title(Format.Pretty), color=ctx.author.color, url=doujin.url)
                embed.set_image(url=url)
                embed.set_footer(text=f"Author: {artist} | Upload date: {doujin.upload_date} | Page {num} of {len(doujin.image_urls)}")
                embeds.append(embed)

            paginator = DiscordUtils.Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
            paginator.add_reaction('⏪', "back")
            paginator.add_reaction('⏩', "next")

            await paginator.run(embeds)

    @commands.command(description="Get porn from Reddit r/porn.")
    @commands.cooldown(1, 5, commands.BucketType.user) 
    async def porn(self, ctx):
        msg = await ctx.send("Getting your porn...")
        subreddit = await reddit.subreddit('porn')
        top = subreddit.top(limit=50)
        all_subs = []

        async for submission in top:
            all_subs.append(submission)
        
        ransub = random.choice(all_subs)

        embed = discord.Embed(title=ransub.title, colour=ctx.author.colour, url=ransub.url)
        embed.set_image(url=ransub.url)
        embed.set_footer(text=f"Posted by {ransub.author} on Reddit. | ❤ {ransub.ups} | 💬 {ransub.num_comments}")
        await msg.delete()
        await ctx.send(embed=embed)

    @commands.command(aliases=["tits", "boob", "tit"], description="Get a picture of boobs via r/boobs.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def boobs(self, ctx):
        msg = await ctx.send("Getting your porn...")
        subreddit = await reddit.subreddit('boobs')
        top = subreddit.top(limit=50)
        all_subs = []

        async for submission in top:
            all_subs.append(submission)
        
        ransub = random.choice(all_subs)

        embed = discord.Embed(title=ransub.title, colour=ctx.author.colour, url=ransub.url)
        embed.set_image(url=ransub.url)
        embed.set_footer(text=f"Posted by {ransub.author} on Reddit. | ❤ {ransub.ups} | 💬 {ransub.num_comments}")
        
        await msg.edit(embed=embed)
    
    @commands.command(aliases=["tittydrop", "titdrop"], description="Get a boobdrop from r/tittydrop. [MOST GIFS MAY NOT SHOW]")
    @commands.cooldown(1, 5, commands.BucketType.user) 
    async def boobdrop(self, ctx):
        msg = await ctx.send("Getting your porn...")
        subreddit = await reddit.subreddit('tittydrop')
        top = subreddit.top(limit=50)
        all_subs = []

        async for submission in top:
            all_subs.append(submission)
        
        ransub = random.choice(all_subs)

        embed = discord.Embed(title=ransub.title, colour=ctx.author.colour, url=ransub.url, type="link")
        embed.set_image(url=ransub.url)
        embed.set_footer(text=f"Posted by {ransub.author} on Reddit. | ❤ {ransub.ups} | 💬 {ransub.num_comments}")
        await msg.delete()
        await ctx.send(embed=embed)

    @commands.command(description="What the fuck?")
    @commands.cooldown(1, 5, commands.BucketType.user) 
    async def feet(self, ctx):
        await ctx.send("What the fuck is wrong with you? Fucking toe gobbling fuck.")
        await self.client.get_channel(793927796354449459).send("Some degenerate just tried to use the feet command.")
        
    @commands.command(description="Get gay porn from r/gayporn.")
    @commands.cooldown(1, 5, commands.BucketType.user) 
    async def gay(self, ctx):
        msg = await ctx.send("Getting your porn...")
        subreddit = await reddit.subreddit('gayporn')
        top = subreddit.top(limit=50)
        all_subs = []

        async for submission in top:
            all_subs.append(submission)
        
        ransub = random.choice(all_subs)

        embed = discord.Embed(title=ransub.title, colour=ctx.author.colour, url=ransub.url)
        embed.set_image(url=ransub.url)
        embed.set_footer(text=f"Posted by {ransub.author} on Reddit. | ❤ {ransub.ups} | 💬 {ransub.num_comments}")
        await msg.delete()
        await ctx.send(embed=embed)

    @commands.command(aliases=["lesbo"], description="Get a lesbian porn image from r/lesbians.")
    @commands.cooldown(1, 5, commands.BucketType.user) 
    async def lesbian(self, ctx):
        msg = await ctx.send("Getting your porn...")
        subreddit = await reddit.subreddit('lesbians')
        top = subreddit.top(limit=50)
        all_subs = []

        async for submission in top:
            all_subs.append(submission)
        
        ransub = random.choice(all_subs)

        embed = discord.Embed(title=ransub.title, colour=ctx.author.colour, url=ransub.url)
        embed.set_image(url=ransub.url)
        embed.set_footer(text=f"Posted by {ransub.author} on Reddit. | ❤ {ransub.ups} | 💬 {ransub.num_comments}")
        await msg.delete()
        await ctx.send(embed=embed)

    @commands.command(description="Get Overwatch porn from r/overwatch_porn.")
    @commands.cooldown(1, 5, commands.BucketType.user) 
    async def overwatch(self, ctx):
        msg = await ctx.send("Getting your porn...")
        subreddit = await reddit.subreddit('overwatch_porn')
        top = subreddit.top(limit=50)
        all_subs = []

        async for submission in top:
            all_subs.append(submission)
        
        ransub = random.choice(all_subs)

        embed = discord.Embed(title=ransub.title, colour=ctx.author.colour, url=ransub.url)
        embed.set_image(url=ransub.url)
        embed.set_footer(text=f"Posted by {ransub.author} on Reddit. | ❤ {ransub.ups} | 💬 {ransub.num_comments}")
        await msg.delete()
        await ctx.send(embed=embed)

    @commands.command(description="Get an SFM piece of porn from r/sfmcompileclub.")
    @commands.cooldown(1, 5, commands.BucketType.user) 
    async def sfm(self, ctx):
        msg = await ctx.send("Getting your porn...")
        subreddit = await reddit.subreddit('sfmcompileclub')
        top = subreddit.top(limit=50)
        all_subs = []

        async for submission in top:
            all_subs.append(submission)
        
        ransub = random.choice(all_subs)

        embed = discord.Embed(title=ransub.title, colour=ctx.author.colour, url=ransub.url)
        embed.set_image(url=ransub.url)
        embed.set_footer(text=f"Posted by {ransub.author} on Reddit. | ❤ {ransub.ups} | 💬 {ransub.num_comments}")
        await msg.delete()
        await ctx.send(embed=embed)

    @commands.command(aliases=["vagina"], description="Get pussy pics from r/pussy.")
    @commands.cooldown(1, 5, commands.BucketType.user) 
    async def pussy(self, ctx):
        msg = await ctx.send("Getting your porn...")
        subreddit = await reddit.subreddit('pussy')
        top = subreddit.top(limit=50)
        all_subs = []

        async for submission in top:
            all_subs.append(submission)
        
        ransub = random.choice(all_subs)

        embed = discord.Embed(title=ransub.title, colour=ctx.author.colour, url=ransub.url)
        embed.set_image(url=ransub.url)
        embed.set_footer(text=f"Posted by {ransub.author} on Reddit. | ❤ {ransub.ups} | 💬 {ransub.num_comments}")
        await msg.delete()
        await ctx.send(embed=embed)

    @commands.command(description="Get a waifu from r/waifusgonewild.")
    @commands.cooldown(1, 5, commands.BucketType.user) 
    async def waifu(self, ctx):
        msg = await ctx.send("Getting your porn...")
        subreddit = await reddit.subreddit('waifusgonewild')
        top = subreddit.top(limit=50)
        all_subs = []

        async for submission in top:
            all_subs.append(submission)
        
        ransub = random.choice(all_subs)

        embed = discord.Embed(title=ransub.title, colour=ctx.author.colour, url=ransub.url)
        embed.set_image(url=ransub.url)
        embed.set_footer(text=f"Posted by {ransub.author} on Reddit. | ❤ {ransub.ups} | 💬 {ransub.num_comments}")
        await msg.delete()
        await ctx.send(embed=embed)

    @commands.command(aliases=["r34"], description="Get Rule34 images!\n[query] value is optional - defaults to r/rule34 when none.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def rule34(self, ctx, *, query=None):
        if query is None:
            msg = await ctx.send("Getting your porn...")
            subreddit = await reddit.subreddit('rule34')
            top = subreddit.top(limit=50)
            all_subs = []

            async for submission in top:
                all_subs.append(submission)

            ransub = random.choice(all_subs)

            embed = discord.Embed(title=ransub.title, colour=ctx.author.colour, url=ransub.url)
            embed.set_image(url=ransub.url)
            embed.set_footer(text=f"Posted by {ransub.author} on Reddit. | ❤ {ransub.ups} | 💬 {ransub.num_comments}")

            await msg.edit("", embed=embed)
        else:
            try:
                query = query.replace(" ", "_")

                msg = await ctx.send("Grabbing your porn...")
                images = await rule34.getImages(tags=query)
                total = []

                try:
                    total.extend(iter(images))
                except:
                    return await ctx.send(f"No images were found on Rule34 with the tag `{query}`")

                finalimg = random.choice(total)

                embed = discord.Embed(
                    title=f'ID: {finalimg.id}',
                    colour=ctx.author.colour,
                    url=finalimg.file_url,
                )

                embed.set_image(url=finalimg.file_url)
                embed.set_footer(text=f"Posted by {finalimg.creator_ID} on Rule 34. | Score: {finalimg.score}")

                await msg.edit(embed=embed)
            except:
                return await ctx.send("Hmmm. API has sent something strange. Please try again later.")

    @commands.command(aliases=["futa"], description="Is futanari considered gay? Get a Futa image from r/futanari.")
    @commands.cooldown(1, 5, commands.BucketType.user) 
    async def futanari(self, ctx):
        msg = await ctx.send("Getting your porn...")
        subreddit = await reddit.subreddit('futanari')
        top = subreddit.top(limit=50)
        all_subs = []

        async for submission in top:
            all_subs.append(submission)
        
        ransub = random.choice(all_subs)

        embed = discord.Embed(title=ransub.title, colour=ctx.author.colour, url=ransub.url)
        embed.set_image(url=ransub.url)
        embed.set_footer(text=f"Posted by {ransub.author} on Reddit. | ❤ {ransub.ups} | 💬 {ransub.num_comments}")
        await msg.delete()
        await ctx.send(embed=embed)

    @commands.command(description="See images of naked people in pain. Images from r/bdsm.")
    @commands.cooldown(1, 5, commands.BucketType.user) 
    async def bdsm(self, ctx):
        msg = await ctx.send("Getting your porn...")
        subreddit = await reddit.subreddit('bdsm')
        top = subreddit.top(limit=50)
        all_subs = []

        async for submission in top:
            all_subs.append(submission)
        
        ransub = random.choice(all_subs)

        embed = discord.Embed(title=ransub.title, colour=ctx.author.colour, url=ransub.url)
        embed.set_image(url=ransub.url)
        embed.set_footer(text=f"Posted by {ransub.author} on Reddit. | ❤ {ransub.ups} | 💬 {ransub.num_comments}")
        await msg.delete()
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(NSFW(client))
