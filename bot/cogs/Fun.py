import json
import urllib.request
import random
import os
import dbl
import aiohttp
import asyncpraw
import discord
from discord.ext.commands.cooldowns import BucketType
import httpx
from discord.ext import commands
from dotenv import load_dotenv
import os
import urllib
import aiosqlite
from bot.cogs.utils.embed import Embeds
import datetime
import randomstuff
import requests as req
import asyncio

load_dotenv('.env')

reddit = asyncpraw.Reddit(client_id = os.getenv("redditid"),
                    client_secret = os.getenv("redditsecret"),
                    username = "UnsoughtConch",
                    password = os.getenv('redditpassword'),
                    user_agent = "ConchBotPraw")

rs = randomstuff.AsyncClient(api_key = os.getenv("aiapikey"))
dbltoken = os.getenv('DBLTOKEN')

class Fun(commands.Cog):
    '''
    The fun category is where most fun commands are. ConchBot is all about its fun commands, so most commands will be here.
    '''

    def __init__(self, client):
        self.client = client
        self.dbl = dbl.DBLClient(self.client, dbltoken)
        self.time = datetime.datetime.utcnow().strftime('%Y:%m:%d %H:%M')
        
    async def category_convert(self, category):
        cat = category.lower()
        categories = ['education', 'diy', 'recreational', 'social', 'charity', 'cooking', 'relaxation', 'music', 'busywork']
        alias1 = ['edu', '', 'recreation', '', '', 'baking', 'relax', '', 'work']
        alias2 = ['educational', 'rec', '', '', '', 'relaxational', '', '']

        if cat in categories:
            return cat
        elif cat in alias1:
            index = alias1.index(cat)
            return categories[index]
        elif cat in alias2:
            index = alias2.index(cat)
            return categories[index]
        else:
            return False
            
    async def create_gofile_folder(self, user_id):
        db = await aiosqlite.connect('./bot/db/config.db')
        cursor = await db.cursor()

        await cursor.execute(f"SELECT user_id FROM gofile WHERE user_id = {user_id}")
        result = await cursor.fetchone()

        if result is not None:
            await cursor.close()
            await db.close()
            return True

        else:
            await cursor.execute(f"INSERT INTO gofile (user_id) VALUES ({user_id})")
            await db.commit()
            await cursor.close()
            await db.close()

            folderid = os.getenv("GOFILE_FOLDER_ID")
            token = os.getenv("GOFILE_TOKEN")

            async with aiohttp.ClientSession() as session:
                async with session.put("https://api.gofile.io/createFolder", data=f'parentFolderId={folderid}&token={token}&folderName={user_id}') as resp:
                    data = json.loads(await resp.read())
                    status = data['status']
                    dat = str(data['data']) + "ee"

            if str(status) == "ok":
                print(dat)
                print(data)
                return True

            else:
                print(status)
                return False
            
    @property
    def _session(self):
        return self.client.http._HTTPClient__session

    async def get_data(self, data_type: str = "json", url : str = None):
        response = await self._session.get(url)
        datatype = data_type.lower()
        if datatype == "json":
            return await response.json()
        elif 'text' in data_type:
            return await response.text()
        else:
            return 400

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if message.channel.name == "conchchat":
            try:
                votes = await self.dbl.get_bot_upvotes()
                flag = any(int(item['id']) == int(message.author.id) for item in votes)
                await message.channel.trigger_typing()
                aimsg = rs.get_ai_response(message.content)
                message = aimsg["message"]
                if flag:
                    await message.reply(message)
                else:
                    await message.reply(f"{message}\n\n*Consider voting for me on Top.gg! (<https://bit.ly/2PiLbwh>) "
                    "It only takes a second of your time and you won't see this message anymore!*")
            except AttributeError:
                await message.channel.trigger_typing()
                aimsg = await rs.get_ai_response(message.content)
                message = aimsg
                await message.reply(message)
            except httpx.ReadTimeout:
                await message.channel.send("It seems my API has timed out. Please give me a few minutes, and if the problem "
                "continues, please contact UnsoughtConch via my `cb support` command.")
        try:
            if (
                message.guild.id == 724050498847506433
                and "retard" in message.content.lower()
            ):
                await message.add_reaction("☹")
        except:
            pass

        if message.content == f"<@!{self.client.user.id}>":
            await message.channel.send("My prefix is `cb `")

    @commands.command(aliases=["chatbot"], description="Set up an AI chat channel in your server!")
    @commands.has_permissions(manage_guild=True)
    async def ai(self, ctx):
        await ctx.send("You can set up a chatbot channel by naming any channel 'conchchat,' or I can do it for you! "
        "would you like me to do it for you? `Yes` or `no`.")
        msg = await self.client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30)
        if "yes" in msg.content.lower():
            await ctx.send("What category would you like this channel in? Channel categories ***must be the exact "
            "name, capitalization and all.***")
            msg0 = await self.client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30)
            category = discord.utils.get(ctx.guild.categories, name=msg0.content)
            try:
                channel = await ctx.guild.create_text_channel('conchchat', category=category)
            except:
                await ctx.send("I'm sorry, but I do not have the `manage guild` requirement needed to create channels.")
                return
            await ctx.send(f"Done! The channel `conchchat` was created in the category `{msg0.content}`")
        elif "no" in msg.content.lower():
            await ctx.send("Okay. Cancelling...")
        else:
            await ctx.send("That's not a valid option.")

    @commands.command(description="Shorten a link!")
    @commands.cooldown(1, 5, BucketType.user)
    async def shorten(self, ctx, *, url):
        o = urllib.parse.quote(url, safe='/ :')

        e = await self.get_data('json', f'https://is.gd/create.php?format=json&url={o}')

        return await ctx.send(f"<{e['result_url']}>")

    @commands.command(description="Get a meme from (almost) any Reddit subreddit!")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def reddit(self, ctx, subreddit):
        message = await ctx.send("This may take a hot minute... Sit tight!")
        try:
            subreddit = await reddit.subreddit(subreddit)
            top = subreddit.top(limit=50)
            all_subs = []

            async for submission in top:
                all_subs.append(submission)

            ransub = random.choice(all_subs)
            if ransub.over_18 and ctx.channel.is_nsfw() != True:
                await ctx.send("Looks like that post is marked over 18, meaning you need to be in an NSFW marked"
                " channel to look at that post.")
                return
            if ransub.is_self:
                embed = discord.Embed(title=f"{ransub.author}'s Post", colour=ctx.author.colour)
                embed.add_field(name=ransub.title, value=ransub.selftext)
                embed.set_footer(text=f"❤ {ransub.ups} | 💬 {ransub.num_comments}")
            else:
                embed = discord.Embed(title=ransub.title, colour=ctx.author.colour, url=ransub.url)
                embed.set_footer(text=f"Posted by {ransub.author} on Reddit. | ❤ {ransub.ups} | 💬 {ransub.num_comments}")
                embed.set_image(url=ransub.url)
            await message.delete()
            await ctx.send(embed=embed)
        except:
            await ctx.send("Something went wrong. This may be the fact that the subreddit does not exist or is locked.")

    @commands.command(description="It's This for That is a fun API and website! It gives startup ideas.")
    @commands.cooldown(1, 10, commands.BucketType.user) 
    async def itft(self, ctx):
        thing = await self.get_data('json', 'https://itft.io/api/v1/random')
        try:
            embed = discord.Embed(title="Wait, what does your startup do?", colour=ctx.author.colour)
            embed.add_field(name="So, basically, it's like a", value=f"**{thing['this']}**", inline=False)
            embed.add_field(name="For", value=f"**{thing['that']}**", inline=False)
            embed.set_footer(text="ItsThisForThat API | itsthisforthat.com")
            await ctx.send(embed=embed)
        except:
            await ctx.send("Woops! Something went wrong.")

    @commands.command(description="View COVID statistics for any country!")
    @commands.cooldown(1, 10, commands.BucketType.user) 
    async def covid(self, ctx, *, country):
        data = await self.get_data('json', f"https://corona.lmao.ninja/v2/countries/{country}")
        try:
            embed = discord.Embed(title=f"COVID-19 in {country}", colour=discord.Colour.gold(),)
            embed.add_field(name="Cases:", value=data[country]['All']['confirmed'])
            embed.add_field(name="Recovered Cases:", value=data[country]['All']['recovered'])
            embed.add_field(name="Deaths:", value=data[country]['All']['deaths'])
            embed.add_field(name="Country Population:", value=data[country]['All']['population'])
            embed.add_field(name="Life Expectancy:", value=data[country]['All']['life_expectancy'])
            embed.set_footer(text="Stats brought to you by M-Media-Group's COVID-19 API")
            await ctx.send(embed=embed)
        except:
            await ctx.send("Country not found. Country names ***are case-sensitive***.")

    @commands.command(description="Get a joke from the r/jokes subreddit!")
    @commands.cooldown(1, 10, commands.BucketType.user) 
    async def joke(self, ctx):
        msg = await ctx.send("Grabbing your joke...")
        subreddit = await reddit.subreddit("jokes")
        top = subreddit.top(limit=50)
        all_subs = []

        async for submission in top:
            all_subs.append(submission)
        
        ransub = random.choice(all_subs)

        embed = discord.Embed(name=f"{ransub.author}'s Joke", colour=ctx.author.colour)
        embed.add_field(name=ransub.title, value=ransub.selftext)
        embed.set_footer(text=f"❤ {ransub.ups} | 💬 {ransub.num_comments}")
        await msg.delete()
        await ctx.send(embed=embed)

    @commands.command(aliases=['repeat'], description="Make the bot repeat a word or phrase.")
    @commands.cooldown(1, 3, commands.BucketType.user) 
    async def echo(self, ctx, channel:discord.TextChannel, *, msg):
        if channel is None:
            await ctx.send(msg)
        else:
            await channel.send(msg)

    @commands.command(name='8ball', description="Ask the 8-ball a question and receive an answer!")
    @commands.cooldown(1, 5, commands.BucketType.user) 
    async def _8ball(self, ctx, *, msg):
        responses = ['As I see it, yes.',
                        'Ask again later.',
                        'Better not tell you now.',
                        'Cannot predict now.',
                        'Concentrate and ask again.',
                        'Don’t count on it.',
                        'It is certain.',
                        'It is decidedly so.',
                        'Most likely.',
                        'My reply is no.',
                        'My sources say no.',
                        'Outlook not so good.',
                        'Outlook good.',
                        'Reply hazy, try again.',
                        'Signs point to yes.',
                        'Very doubtful.',
                        'Without a doubt.',
                        'Yes.',
                        'Yes – definitely.',
                        'You may rely on it.']
        embed = discord.Embed(
            title="Magic 8 Ball",
            colour=discord.Colour.blurple()
        )
        embed.add_field(name="Question:", value=msg)
        embed.add_field(name="Answer:", value=random.choice(responses))
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def hehewed(self, ctx):
        embed = discord.Embed(title="**__Ping and Access Roles__**", description="Get your roles by reacting to the corresponding reaction.", color=discord.Color.red())
        embed.add_field(name="**Announcement Ping**", value="React with 📣 to get pings for server announcements!", inline=False)
        embed.add_field(name="**Vote Ping**", value=f"React with 🗳 to get pings when there's a new vote in {self.client.get_channel(726098004708163594).mention}!", inline=False)
        embed.add_field(name="**Revive Ping**", value="React with 💀 to get pinged when the chat is dead!", inline=False)
        embed.add_field(name="**NSFW Access**", value=f"React with 🔞 to get access to {self.client.get_channel(814256958806556723).mention}!", inline=False)
        embed.set_footer(text="React with a listed reaction to get that role.")
        await ctx.send(embed=embed)

        embed = discord.Embed(title="**__Color Roles__**", color=discord.Color.teal(), description="Make your name a pretty color!")
        embed.add_field(name="**Red**", value=f"React with 🔴 to get a {ctx.guild.get_role(857816667190198282).mention} name!", inline=False)
        embed.add_field(name="**Orange**", value=f"React with 🟠 to get an {ctx.guild.get_role(857816821242789929).mention} name!", inline=False)
        embed.add_field(name="**Yellow**", value=f"React with 🟡 to get a {ctx.guild.get_role(857816873848012820).mention} name!", inline=False)
        embed.add_field(name="**Green**", value=f"React with 🟢 to get a {ctx.guild.get_role(857816937152380948).mention} name!", inline=False)
        embed.add_field(name="**Blue**", value=f"React with 🔵 to get a {ctx.guild.get_role(857816980887044157).mention} name!", inline=False)
        embed.add_field(name="**Purple**", value=f"React with 🟣 to get a {ctx.guild.get_role(857817018039009290).mention} name!", inline=False)
        embed.add_field(name="**White**", value=f"React with ⚪ to get a {ctx.guild.get_role(857817054706663494).mention} name!", inline=False)
        embed.add_field(name="**Black**", value=f"React with ⚫ to get a {ctx.guild.get_role(857817144989712434).mention} name!", inline=False)
        embed.set_footer(text="React with a listed reaction to get that color name.")
        await ctx.send(embed=embed)

    @commands.command(aliases=["LMGTFY"], description="Make a Google link with the specified query.")
    @commands.cooldown(1, 3, commands.BucketType.user) 
    async def google(self, ctx, *, query):
        nquery = query.replace(' ', '+').lower()
        await ctx.send(f"https://www.google.com/search?q={nquery}")

    @commands.command(aliases=['chances', 'odds', 'odd'], description="Rate the chances of something happening!")
    @commands.cooldown(1, 5, commands.BucketType.user) 
    async def chance(self, ctx, *, msg):
        chancenum = random.randint(0, 10)
        embed = discord.Embed(
            title="What are the Chances?",
            colour = ctx.author.colour
        )
        embed.add_field(name="Question:", value=msg)
        embed.add_field(name="The chances are...", value=chancenum)
        await ctx.send(embed=embed)

    @commands.command(aliases=['avatar'], description="Show someone's profile picture!\n[member] value is optional.")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def pfp(self, ctx, member: discord.Member=None):
        if member is None:
            embed = discord.Embed(
                title=f"{ctx.author}'s Avatar",
                colour=ctx.author.colour
            )
            embed.set_image(url=ctx.author.avatar.url)
        else:
            embed = discord.Embed(
                title=f"{member}'s Avatar",
                colour=member.colour
            )
            embed.set_image(url=member.avatar.url)

        await ctx.send(embed=embed)
    
    @commands.group(invoke_without_command=True, description="Returns a random activity for when you're bored!")
    @commands.cooldown(1, 5, BucketType.user)
    async def bored(self, ctx):
        json = await self.get_data('json', 'https://www.boredapi.com/api/activity/')
        embed = discord.Embed(title="I'm Bored", color=discord.Color.random())
        embed.add_field(name="If you're bored, you should...", value=json["activity"])
        if json['link']:
            embed.add_field(name="I can find a link to this project at...", value=json['link'], inline=False)
        if int(json['participants']) == 1:
            people = "1 person."
        else:
            people = f"{json['participants']}"
        embed.add_field(name="This might cost...", value="$" + str(int(json['price'])*10), inline=False)
        embed.add_field(name="The amount of people needed for this project is...", value=people, inline=False)
        embed.set_footer(text=f"Type: {json['type']} | Key: {json['key']} | Provided by BoredAPI")

        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True, description="Make a QR code!")
    async def qr(self, ctx, value = None):
        
        if value is None:
            o = ctx.message.attachments[0].url
        o = urllib.parse.quote(value)

        await ctx.send(f'https://api.qrserver.com/v1/create-qr-code/?data={o}')

    @qr.command(description="Read a QR Code!")
    async def read(self, ctx, image=None):
        if image is not None:
            url = urllib.parse.quote(image)

        else:
            if len(ctx.message.attachments) > 1:
                return await ctx.send("We can only decode one QR code at a time.")
            
            elif len(ctx.messsage.attachments) < 1:
                return await ctx.send("You have to add some type of QR code for us to decode.")

            url = urllib.parse.quote(ctx.message.attachments[0].url)

        try:
            res = await self.get_data('json', f'https://api.qrserver.com/v1/read-qr-code/?fileurl={url}')
        except:
            return await ctx.send("I couldn't find any QR codes in that image.")

        await ctx.send(res[0]['symbol'][0]['data'])

    @bored.command(description="Search for a specific activity via an activity key.")
    @commands.cooldown(1, 5, BucketType.user)
    async def key(self, ctx, key):
        json = await self.get_data('json', f'https://www.boredapi.com/api/activity/{key}')
        try:
            embed = discord.Embed(title="I'm Bored", color=discord.Color.random())
            embed.add_field(name="If you're bored, you should...", value=json["activity"])
            if json['link']:
                embed.add_field(name="I can find a link to this project at...", value=json['link'], inline=False)
            if int(json['participants']) == 1:
                people = "1 person."
            else:
                people = f"{json['participants']}"
            embed.add_field(name="This might cost...", value="$" + str(int(json['price'])*10), inline=False)
            embed.add_field(name="The amount of people needed for this project is...", value=people, inline=False)
            embed.set_footer(text=f"Type: {json['type']} | Key: {json['key']} | Provided by BoredAPI")

            await ctx.send(embed=embed)
        except KeyError:
            await ctx.send("No activity found with that key.")

    @bored.command(description="Search for activities by category.\n[category] value is optional, returns a list of categories if none.")
    @commands.cooldown(1, 5, BucketType.user)
    async def category(self, ctx, category=None):
        if not category:
            embed = discord.Embed(title="List of Categories", color=discord.Color.random(), description="Education\nRecreational\nSocial\nDIY\nCharity\nCooking\nRelaxation\nMusic\nBusywork")
            return await ctx.send(embed=embed)
        
        category = await self.category_convert(category)

        if not category:
            return await ctx.send("That category does not exist.")

        json = await self.get_data('json', f'https://www.boredapi.com/api/activity?type={category}')

        try:
            embed = discord.Embed(title="I'm Bored", color=discord.Color.random())
            embed.add_field(name="If you're bored, you should...", value=json["activity"])
            if json['link']:
                embed.add_field(name="I can find a link to this project at...", value=json['link'], inline=False)
            if int(json['participants']) == 1:
                people = "1 person."
            else:
                people = f"{json['participants']}"
            embed.add_field(name="This might cost...", value="$" + str(int(json['price'])*10), inline=False)
            embed.add_field(name="The amount of people needed for this project is...", value=people, inline=False)
            embed.set_footer(text=f"Type: {json['type']} | Key: {json['key']} | Provided by BoredAPI")

            await ctx.send(embed=embed)
        except KeyError:
            return await ctx.send("That category does not exist.")


    @commands.group()
    async def gofile(self, ctx):
        pass

    @gofile.command(disabled=True)
    async def upload(self, ctx, url):
        status = await self.create_gofile_folder(ctx.author.id)
        return await ctx.send(status)

    @commands.command(aliases=["encoder"], description="Encode something into binary or base64.")
    async def encode(self, ctx, type, *, code):
        types = ["binary", "base64"]
        type = type.lower()
        if type in types:
            if type == "binary":
                encoder = await self.get_data('json', f'https://some-random-api.ml/binary?encode={code}')
                try:
                    encoded = encoder["binary"]
                    embed = discord.Embed(title="Binary Encoder", colour=discord.Color.green())
                    embed.add_field(name="Input", value=f"```{code}```", inline=False)
                    embed.add_field(name="Output", value=f"```{encoded}```", inline=False)
                    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)
                except:
                    embed = Embeds().OnApiError(command_name=ctx.command.qualified_name, status=400)
            else:
                encoder = await self.get_data('json', f'https://some-random-api.ml/base64?encode={code}')
                try:                            
                    encoded = encoder["base64"]
                    embed = discord.Embed(title="Base64 Encoder", colour=discord.Color.green())
                    embed.add_field(name="Input", value=f"```{code}```", inline=False)
                    embed.add_field(name="Output", value=f"```{encoded}```", inline=False)
                    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)
                except:
                    embed = Embeds().OnApiError(command_name=ctx.command.qualified_name, status=400)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Use binary or base64")

    @commands.command(aliases=["decoder"], description="Decode a binary or base64 string.")
    async def decode(self, ctx, type, *, code):
        types = ["binary", "base64"]
        type = type.lower()
        if type in types:
            if type == "binary":
                decoder = await self.get_data('json', 'https://some-random-api.ml/binary?decode={}'.format(code))
                try:
                    decoded = decoder["text"]
                    embed = discord.Embed(title="Binary Decoder")
                    embed.add_field(name="Input", value=f"```{code}```", inline=False)
                    embed.add_field(name="Output", value=f"```{decoded}```", inline=False)
                    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)
                except:
                    embed = Embeds().OnApiError(command_name=ctx.command.qualified_name, status=decoder.status)
                    await ctx.send(embed=embed)
            else:
                decoder = await self.get_data('json', 'https://some-random-api.ml/base64?decode={}'.format(code))
                try:
                    decoded = decoder["text"]
                    embed = discord.Embed(title="Base64 Decoder")
                    embed.add_field(name="Input", value=f"```{code}```", inline=False)
                    embed.add_field(name="Output", value=f"```{decoded}```", inline=False)
                    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)
                except:
                    embed = Embeds().OnApiError(command_name=ctx.command.qualified_name, status=400)
                await ctx.send(embed=embed)
        else:
            await ctx.send("Use binary or base64")

    @commands.command(description="Get lyrics of a specific song!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def lyrics(self, ctx, *, search):
        search = search.replace(' ', '%20')
        search_web = f"https://some-random-api.ml/lyrics?title={search}"

        await ctx.channel.trigger_typing()
        api = await self.get_data('json', search_web)
        try:
            title = api["title"]
            author = api["author"]
            lyrics = api["lyrics"]

            embed = discord.Embed(title=f"{title} by {author}", description=lyrics)
            try:
                await ctx.send(embed=embed)
            except:
                embeds = []

                page_count = lyrics / 4096

                if '.' in str(page_count):
                    page_count = int(page_count) + 1

                num = 4096
                for i in range(page_count):
                    embed = discord.Embed(title=f"{title} by {author}", description=lyrics[:num])
                    embed.set_footer(text=f"Page {i}/{page_count}")
                    embeds.append(embed)
                    num += 4096


                paginator = menus.Paginator(pages=embeds, show_disabled=False, show_indicator=True)

                paginator.customize_button("next", button_label=">", button_style=discord.ButtonStyle.green)
                paginator.customize_button("prev", button_label="<", button_style=discord.ButtonStyle.green)
                paginator.customize_button("first", button_label="<<", button_style=discord.ButtonStyle.blurple)
                paginator.customize_button("last", button_label=">>", button_style=discord.ButtonStyle.blurple)

                await paginator.send(ctx, ephemeral=False)



        except:
            embed = Embeds().OnApiError(command_name=ctx.command.qualified_name, status=400)
            await ctx.send(embed=embed)

    @commands.command(description="Define a word!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def define(self, ctx, word):
        word_lowered = word.lower()
        word_link = f"https://some-random-api.ml/dictionary?word={word_lowered}"

        api = await self.get_data('json', word_link)
        try:
            embeds = []
            word_name = api["word"]
            word_definition = api["definition"]
    
            page_count = word_definition / 4096
            num = 4096        
            for i in range(page_count):
                embed = discord.Embed(title=f"{word_name} Definition", description=word_definition[:num])
                embed.set_footer(text=f"Page {i}/{page_count}")
                embeds.append(embed)
                num += 4096

            await ctx.defer()

            paginator = menus.Paginator(pages=embeds, show_disabled=False, show_indicator=True)

            paginator.customize_button("next", button_label=">", button_style=discord.ButtonStyle.green)
            paginator.customize_button("prev", button_label="<", button_style=discord.ButtonStyle.green)
            paginator.customize_button("first", button_label="<<", button_style=discord.ButtonStyle.blurple)
            paginator.customize_button("last", button_label=">>", button_style=discord.ButtonStyle.blurple)

            await paginator.send(ctx, ephemeral=False)
        except:
            embed = Embeds().OnApiError(command_name=ctx.command.qualified_name, status=400)
            await ctx.send(embed=embed)

    @commands.command(description="Returns a real-looking Discord bot token.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def token(self, ctx):
        token_web = "https://some-random-api.ml/bottoken"

        response = await self.get_data('json', token_web)
        try:
            bottoken = response["token"]
        except:
            embed = Embeds().OnApiError(command_name=ctx.command.qualified_name, status=400)
            return await ctx.send(embed=embed)
        await ctx.send(bottoken)
        
        
    @commands.command()
    async def ttsobama(self, ctx, *, text : str = None):
        if text is None:
            return await ctx.send("You need to enter text!")

        if len(text) > 280:
            return await ctx.send("Text is too long!")

        await ctx.send('Your video is loading... Might take up to 5-12 seconds', delete_after=12)

        response = req.post(url='http://talkobamato.me/synthesize.py', data={
                "input_text": text
            })
        await asyncio.sleep(12)
        url = response.url.replace('http://talkobamato.me/synthesize.py?speech_key=', '')

        url = f'http://talkobamato.me/synth/output/{url}/obama.mp4'

        await asyncio.sleep(1)

        urllib.request.urlretrieve(url, 'obama.mp4')

        file = discord.File('obama.mp4')

        await ctx.send(file=file)

        os.remove('obama.mp4')
        

def setup(client):
    client.add_cog(Fun(client))
