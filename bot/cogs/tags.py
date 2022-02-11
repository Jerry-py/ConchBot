import discord
from discord.ext import commands
import aiosqlite
import datetime
import shortuuid
from DiscordUtils import Pagination

class Tags(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.delete_snipes = dict()
        self.edit_snipes = {}
        self.delete_snipes_attachments = {}

    async def get_tag(self, guild_id, tag):
        db = await aiosqlite.connect("./bot/db/tags.db")
        cursor = await db.cursor()

        await cursor.execute(f"SELECT content FROM g{guild_id} WHERE name = '{tag}'")
        result = await cursor.fetchone()

        await cursor.close()
        await db.close()

        return False if result is None else result

    async def create_table(self, id):
        db = await aiosqlite.connect("./bot/db/tags.db")
        cursor = await db.cursor()

        await cursor.execute(f"CREATE TABLE IF NOT EXISTS g{id} (name TEXT, content TEXT, creator_id INT, created_at TEXT"
        ", last_edited TEXT, tag_id TEXT)")

        await db.commit()
        await cursor.close()
        await db.close()

    async def check_existance(self, name, guild):
        db = await aiosqlite.connect("./bot/db/tags.db")
        cursor = await db.cursor()

        await cursor.execute(f"SELECT name FROM g{guild} WHERE name = '{name.lower()}'")
        result = await cursor.fetchone()

        await cursor.close()
        await db.close()        

        return result is not None

    async def edit_info(self, guild, name, info):
        today = datetime.date.today()
        d2 = today.strftime("%B %d, %Y")
        db = await aiosqlite.connect("./bot/db/tags.db")
        cursor = await db.cursor()

        await cursor.execute(f"UPDATE g{guild} SET content = '{info}' WHERE tag_id = '{name}'")
        await cursor.execute(f"UPDATE g{guild} SET last_edited = '{d2}' WHERE tag_id = '{name}'")
        
        await db.commit()
        await cursor.close()
        await db.close()

    async def create_tag(self, author, guild, name, content):
        db = await aiosqlite.connect("./bot/db/tags.db")
        cursor = await db.cursor()

        today = datetime.date.today()
        d2 = today.strftime("%B %d, %Y")
        
        id = shortuuid.uuid()

        await cursor.execute(f"INSERT INTO g{guild.id} (name, content, creator_id, created_at, last_edited, tag_id)"
            f" VALUES ('{name.lower()}', '{content}', {author.id}, '{d2}', '{d2}', '{id}')")

        await db.commit()
        await cursor.close()
        await db.close()

    async def delete_tag(self, guild, id):
        db = await aiosqlite.connect('./bot/db/tags.db')
        cursor = await db.cursor()
        await cursor.execute(f"DELETE FROM g{guild.id} WHERE tag_id = '{id}'")

        await db.commit()
        await cursor.close()
        await db.close()

    async def get_tag_info(self, guild, name):
        db = await aiosqlite.connect('./bot/db/tags.db')
        cursor = await db.cursor()

        await cursor.execute(f"SELECT creator_id, created_at, last_edited, tag_id FROM g{guild.id} WHERE name = '{name}'")

        for row in await cursor.fetchall():
            creator_id = row[0]
            created_at = row[1]
            last_edited = row[2]
            tag_id = row[3]

        await cursor.close()
        await db.close()

        return creator_id, created_at, last_edited, tag_id

    @commands.group(invoke_without_command=True, aliases=['tags'])
    async def tag(self, ctx):
        main = discord.Embed(title="Guide to ConchBot Tags", color=discord.Color.random())
        main.add_field(name="How to Use a Tag", value="To use a tag, you simply have to use ConchBot's prefix followed by the name of the tag. So if you have a tag named `this`, you"
        " would have to use `cb this`.", inline=False)
        main.add_field(name="Create a Tag", value="There are two ways to create a tag. You can either use `cb tag create` to follow the interactive version, or use the quick version"
        "by using `cb tag create [tagname]:;[tagcontent]`.", inline=False)
        main.add_field(name="Delete a Tag", value="To delete a tag, simply get the tag ID via the `cb tag info` comamnd, then use `cb tag delete [id]`.", inline=False)
        main.add_field(name="Edit a Tag", value="There are two ways to edit a tag. The short way, which is `cb tag edit [tagid]:;[tagcontent]`, and the interactive way, which gives"
        " you directions, and is simply `cb tag edit.`", inline=False)
        main.add_field(name="Get Tag Info", value="To get info on a tag, simply use the tag info command, followed by the name. `cb tag info [name]`.", inline=False)
        main.set_footer(text="ConchBot Tag System")

        create = discord.Embed(title="ConchBot Tag System - Create Command", color=discord.Color.random())
        create.add_field(name="How to Use", value="There are two ways to create a tag. The interactive way, which is just `cb tag create`, then there are instructions to help you. There "
        "is also the quick way, which lets you create tags in one command, `cb tag create [name]:;[content].", inline=False)
        create.add_field(name="Why use \":;\" to Split Content?", value="We use the `:;` set of characters to split content because it is a small string that would not commonly be found "
        "in a tag or anywhere, really.", inline=False)
        create.add_field(name="Could I Have an Example?", value="Sure! Lets say I was creating a tag named `cat`, that returned the string \"I like cats.\" when used. To make this "
        "the quick way, you would use `cb tag create cat:;I like cats.`", inline=False)
        create.set_footer(text="ConchBot Tag System")

        delete = discord.Embed(title="ConchBot Tag System - Delete Command", color=discord.Color.random())
        delete.add_field(name="How to Use", value="The delete command is simple. You just have to get the tag ID via `cb tag info`, then use `cb tag delete [ID]`.", inline=False)
        delete.add_field(name="Who Can Delete Tags?", value="Anyone with `manage messages` permissions can delete tags to keep things civil. You can also delete tags if you"
        " are the owner of the tag.", inline=False)
        delete.set_footer(text="ConchBot Tag System")

        edit = discord.Embed(title="ConchBot Tag System - Edit Command", color=discord.Color.random())
        edit.add_field(name="How to Use", value="Just like the create command, the edit command has two ways to use: the interactive way and the short way. They work basically the same, "
        " `cb tag edit [id]:;[content]")
        edit.add_field(name="Why use \":;\" to Split Content?", value="We use the `:;` set of characters to split content because it is a small string that would not commonly be found "
        "in a tag or anywhere, really.", inline=False)
        edit.add_field(name="Could I have an Example?", value="Sure! I just made my tag `cat`, which spits out the phrase \"I like cats.\" What if I decide I don't like cats anymore?"
        " If that's the case, you can simply use something like this to change it (Let's pretend the `cat` tag ID is 12345): `cb tag edit 12345:;I hate cats.`", inline=False)
        edit.set_footer(text="ConchBot Tag System")

        info = discord.Embed(title="ConchBot Tag System - Info Command", color=discord.Color.random())
        info.add_field(name="How to Use", value="It's simple. You can use either the ID or the name, `cb tag info [name/id]`.")
        info.add_field(name="What Info Does This Return?", value="The `info` command returns plenty of info, including who made it, when it was created, when it was last edited, and the "
        "ID of the tag. It also displays the content of the tag, if there is room.", inline=False)
        info.set_footer(text="ConchBot Tag System")

        embeds = [main, create, delete, edit, info]

        paginator = Pagination.CustomEmbedPaginator(ctx, remove_reactions=True)
        paginator.add_reaction("◀", "back")
        paginator.add_reaction("▶", "next")

        await paginator.run(embeds)

    @tag.command(description="Create a tag for your server.\n[val] value is optional. Split values with ':;'")
    async def create(self, ctx, *, val=None):
        id = shortuuid.uuid()
        if val is not None:
            try:
                name, content = val.split(":;")
            except:
                await ctx.send("You must separate your values with `:;`.")
                return

            await self.create_table(ctx.guild.id)

            check = await self.check_existance(name, ctx.guild.id)
            
            if check is True:
                await ctx.send("That tag already exists!")
                return

            await self.create_tag(ctx.author, ctx.guild, name, content)
            
            return await ctx.send(f"Tag {name} successfully created with tag ID {id}")
        else:
            await ctx.send("What do you want your tag's title to be?")
            title = await self.client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60)

            if len(title.content) > 30:
                return await ctx.send("Your title can't be more than thirty characters.")

            await ctx.send("What do you want to be in your tag?")
            content = await self.client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=120)

            await self.create_tag(ctx.author, ctx.guild, title.content, content.content)

            await ctx.send(f"Tag {title.content} created successfully with tag ID {id}")

    @tag.command(description="Delete a tag.")
    async def delete(self, ctx, *, id):
        db = await aiosqlite.connect('./bot/db/tags.db')
        cursor = await db.cursor()
        if id is None:
            await ctx.send("You must provide a valid ID to delete a tag.")
        else:
            await cursor.execute(f"SELECT creator_id FROM g{ctx.guild.id} WHERE tag_id = '{id}'")
            result = await cursor.fetchone()

            await cursor.close()
            await db.close()

            if result is None:
                await ctx.send("Invalid tag ID.")
            elif int(result[0]) == int(ctx.author.id) or ctx.author.has_permissions(manage_messages=True):
                await self.delete_tag(ctx.guild, id)
                await ctx.send(f"Successfully deleted tag `{id}`.")
            else:
                tagcreator = self.client.get_user(result[0])
                await ctx.send(f"You can't delete a tag that isn't yours! This tag belongs to {tagcreator}!")

    @tag.command(description="Edit your tag!\n[vals] value is optional. Split values with ':;'")
    async def edit(self, ctx, *, vals=None):
        db = await aiosqlite.connect('./bot/db/tags.db')
        cursor = await db.cursor()
        if vals is not None:
            
            try:
                id, content = vals.split(':;')
            except:
                await ctx.send("Please give us two values separated by the string \":;\"")
                return
            await cursor.execute(f"SELECT creator_id FROM g{ctx.guild.id} WHERE tag_id = '{id}'")
            result = await cursor.fetchone()
            
            if result is None:
                await cursor.close()
                await db.close()
                return await ctx.send("A tag with that ID doesn't exist in this guild.")

            if int(result[0]) == int(ctx.author.id):
                await cursor.close()
                await db.close()
                await self.edit_info(ctx.guild.id, id, content)
                await ctx.send("Tag successfully edited.")

            else:
                tagcreator = self.client.get_user(result[0])
                await ctx.send(f"You can't edit a tag that isn't yours! This tag belongs to {tagcreator.name}!")
        else:
            await ctx.send("What is the ID of the tag you want to edit?")
            id = await self.client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60)

            await ctx.send("What do you want the new content of that tag to be?")
            content = await self.client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=60)

            await cursor.execute(f"SELECT creator_id FROM g{ctx.guild.id} WHERE tag_id = '{id.content}'")
            result = await cursor.fetchone()

            await cursor.close()
            await db.close()

            if result is None:
                return await ctx.send("A tag with that ID doesn't exist in this guild.")
            
            if int(result[0]) != int(ctx.author.id):
                return await ctx.send(f"You can't edit a tag that isn't yours. It belongs to {self.client.get_user(result[0]).name}!")
   
            await self.edit_info(ctx.guild.id, id.content, content.content)
            await ctx.send("Tag successfully edited.")

    @tag.command(description="Get the info of a tag.")
    async def info(self, ctx, *, tag):
        creator_id, created_at, last_edited, tag_id = await self.get_tag_info(ctx.guild, tag)

        embed = discord.Embed(title=f"{tag} Tag Information", color=discord.Color.random())
        author = self.client.get_user(creator_id)
        embed.set_author(name=author, icon_url=author.avatar_url)
        embed.add_field(name="Owner:", value=author, inline=False)
        embed.add_field(name="Tag ID:", value=tag_id)
        embed.add_field(name="Creation Date:", value=created_at, inline=False)
        embed.add_field(name="Date Last Edited:", value=last_edited)
        embed.set_footer(text="ConchBot Tag System")

        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Tags(client))