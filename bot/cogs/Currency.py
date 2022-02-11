import asyncio
import random
import aiosqlite
import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType
from dotenv import load_dotenv
from .BotConfig import Config

env = load_dotenv()

shop = {
    "watch" : {
        "price" : 200,
        "sale" : 100
    },
    "computer" : {
        "price" : 2000,
        "sale" : 1000
    },
    "apple" : {
        "price" : 100,
        "sale" : 0
    }
}

tasks = {
    "Cats" : {
        "reward" : 100,
        "req" : "Come get your food kitties!",
        "desc" : "Help someone feed their cats!",
        "dialogue" : "While you were walking, an elderly man asks you if you can feed his cats, as he dropped the "
        "cat bowls and cannot bend down to grab them. Type `Come get your food kitties!`",
        "thank" : "Old Man: Thank you sonny. Here's 100 moners for your troubles."
    },
    "Help" : {
        "reward" : 200,
        "req" : "Here, I'll help you up!",
        "desc" : "Help someone who fell back onto their feet!",
        "dialogue" : "As you walk down the street, you see someone trip and fall. Type `Here, I'll help you up!` to "
        "help them back up!",
        "thank" : "Guy: Oh, thank you! Here, take 200 moners for helping me up."
    },
    "Street" : {
        "reward" : "3 apples",
        "rewardnum" : 3,
        "rewarditem" : "apple",
        "req" : "We can cross the street together.",
        "desc" : "Help an old lady cross the street!",
        "dialogue" : "As you walk down the street, you see an elderly lady with her hands full of groceries at a "
        "crosswalk. She looks like she needs help. Type `We can cross the street together.` to help her cross the street!",
        "thank" : "Old Lady: Oh, that was very kind of you, dear. Let me see what I have in my bag for you. Here "
        "you go, three apples. Thanks again!"
    },
    "Technician" : {
    "reward" : "One Computer",
    "rewardnum" : 1,
    "rewarditem" : "computer",
    "req" : "Pick up all the screws! Screws everywhere!",
    "desc" : "Help a technician pick up his screws!",
    "dialogue" : "You go into a tech shop to look for some new tech. As you walk around, you see a technician working "
    "on a new PC build drop all of his screws on the floor! type `Pick up all the screws! Screws everywhere!` to "
    "help him pick up the screws.",
    "thank" : "Technician: Thank you for helping me, may I offer you a new PC for your help?"
    }
}

class Currency(commands.Cog):

    '''
    The currency category holds all kinds of commands made to have fun making moners.
    '''

    def __init__(self, client):
        self.client = client

    async def open_account(self, user):
        db = await aiosqlite.connect('./bot/db/currency.db')
        cursor = await db.cursor()
        dbo = await aiosqlite.connect('./bot/db/tasks.db')
        cursoro = await dbo.cursor()
        
        await cursor.execute(f'SELECT user_id FROM main WHERE user_id = {user.id}')
        result1 = await cursor.fetchone()
        if result1 is not None:
            await cursor.execute(f'CREATE TABLE IF NOT EXISTS u{user.id} (item TEXT, amount INT)')
            return False
        else:
            await cursor.execute(f'INSERT INTO main (user_id, wallet, bank, items) VALUES ({user.id}, 0, 0, 0)')
        await cursor.execute(f'CREATE TABLE IF NOT EXISTS u{user.id} (item TEXT, amount INT)')
        await cursoro.execute(f"CREATE TABLE IF NOT EXISTS u{user.id} (task, status)")
        await db.commit()
        await cursor.close()
        await db.close()
        
        await dbo.commit()
        await cursoro.close()
        await dbo.close()

    async def update_bank(self, user, amt):
        db = await aiosqlite.connect('./bot/db/currency.db')
        cursor = await db.cursor()

        
        await cursor.execute(f'SELECT wallet FROM main WHERE user_id = {user.id}')
        oldamt = await cursor.fetchone()

        await cursor.execute(f'UPDATE main SET wallet = {oldamt[0]+amt} WHERE user_id = {user.id}')
        await db.commit()
        await cursor.close()
        await db.close()
    
    async def get_amt(self, user):
        db = await aiosqlite.connect('./bot/db/currency.db')
        cursor = await db.cursor()

        await cursor.execute(f'SELECT wallet FROM main WHERE user_id = {user.id}')
        walamt = await cursor.fetchone()
        
        await cursor.execute(f'SELECT bank FROM main WHERE user_id = {user.id}')
        bankamt = await cursor.fetchone()

        await cursor.close()
        await db.close()

        return walamt, bankamt

    async def item_func(self, user, item, amount=None):
        db = await aiosqlite.connect("./bot/db/currency.db")
        cursor = await db.cursor()
        await cursor.execute(f"SELECT amount FROM u{user.id} WHERE item = '{item}'")
        oldamount = await cursor.fetchone()
        if oldamount is None:
            await cursor.execute(f"INSERT INTO u{user.id} (item, amount) VALUES ('{item}', 0)")
            await cursor.execute(f"SELECT amount FROM u{user.id} WHERE item = '{item}'")
            oldamount = await cursor.fetchone()
        if amount is None:
            return oldamount
        if oldamount is None:
            await cursor.execute(f"UPDATE u{user.id} SET amount = {amount} WHERE item = '{item}'")
        else:
            await cursor.execute(f"UPDATE u{user.id} SET amount = {amount+oldamount[0]} WHERE item = '{item}'")
        await db.commit()
        await cursor.close()
        await db.close()
    
    @commands.command(aliases=['inv', 'bag', 'bal', 'balance'], description="View your items and balance.\n[user] value is optional.")
    async def inventory(self, ctx, user:discord.Member=None):
        db = await aiosqlite.connect('./bot/db/currency.db')
        cursor = await db.cursor()
        if user is None:
            await self.open_account(ctx.author)
            user = ctx.author
        else:
            await self.open_account(user)
        walamt, bankamt = await self.get_amt(user)
        embed = discord.Embed(
            title=f"{user.name}'s Inventory",
            colour=ctx.author.colour
        )
        embed.add_field(name="Wallet Amount:", value=f"{walamt[0]} moners")
        embed.add_field(name="Bank Amount:", value=f"{bankamt[0]} moners")
        embed.add_field(name="Total:", value=f"{bankamt[0]+walamt[0]} moners")
        await cursor.execute(f'SELECT item FROM u{user.id}')
        items = await cursor.fetchall()
        for item in items:
            await cursor.execute(f"SELECT amount FROM u{user.id} WHERE item = '{item[0]}'")
            amount = await cursor.fetchone()
            embed.add_field(name=f"{item[0]}s:", value=amount[0])
        await ctx.send(embed=embed)

        await cursor.close()
        await db.close()
        
    @commands.command(aliases=['dep'], description="Deposit moners from your wallet into your bank!")
    async def deposit(self, ctx, amt):
        db = await aiosqlite.connect('./bot/db/currency.db')
        cursor = await db.cursor()
        walamt, bankamt = await self.get_amt(ctx.author)
        await self.open_account(ctx.author)
        if amt == "all":
            await cursor.execute(f'UPDATE main SET wallet = 0 WHERE user_id = {ctx.author.id}')
            await cursor.execute(f'UPDATE main SET bank = {walamt[0]+bankamt[0]} WHERE user_id = {ctx.author.id}')
            await ctx.send(f"{walamt[0]} moners have been deposited to your bank.")
        elif int(amt)>walamt[0]:
            await ctx.send("You don't have enough moners in your wallet to deposit that much!")
        elif int(amt)<0:
            await ctx.send("You cannot deposit negative numbers!")
        else:
            await cursor.execute(f'UPDATE main SET wallet = {walamt[0]-int(amt)} WHERE user_id = {ctx.author.id}')
            await cursor.execute(f'UPDATE main SET bank = {int(amt)+bankamt[0]} WHERE user_id = {ctx.author.id}')
            await ctx.send(f'{int(amt)} moners have been deposited to your bank.')
        await db.commit()
        await cursor.close()
        await db.close()

    @commands.command(aliases=["with"], description="Withdraw moners from your bank to your wallet!")
    async def withdraw(self, ctx, amt):
        db = await aiosqlite.connect('./bot/db/currency.db')
        cursor = await db.cursor()
        walamt, bankamt = await self.get_amt(ctx.author)
        await self.open_account(ctx.author)
        notenoughmsg = "You don't have enough moners in your bank to withdraw that much!"
        negmsg = "You cannot withdraw negative numbers!"
        if amt == "all":
            await cursor.execute(f'UPDATE main SET bank = 0 WHERE user_id = {ctx.author.id}')
            await cursor.execute(f'UPDATE main SET wallet = {walamt[0]+bankamt[0]} WHERE user_id = {ctx.author.id}')
            successallmsg = "{} moners have been withdrawn your bank."
            await ctx.send(successallmsg.format(bankamt[0]))
        elif int(amt)>bankamt[0]:
            await ctx.send(notenoughmsg)
        elif int(amt)<0:
            await ctx.send(negmsg)
        else:
            await cursor.execute(f'UPDATE main SET wallet = {walamt[0]+int(amt)} WHERE user_id = {ctx.author.id}')
            await cursor.execute(f'UPDATE main SET bank = {bankamt[0]-int(amt)} WHERE user_id = {ctx.author.id}')
            successmsg = "{} moners have been withdrawn from your bank."
            await ctx.send(successmsg.format(int(amt)))
        await db.commit()
        await cursor.close()
        await db.close()

    @commands.command(description="Buy an item from the shop!\n[quantity] value is optional.")
    async def buy(self, ctx, item, quantity=1):
        ff = await Config.check_ff(self, ctx.guild)
        db = await aiosqlite.connect('./bot/db/currency.db')
        cursor = await db.cursor()
        check = shop.get(item)
        await self.open_account(ctx.author)
        if quantity < 1:
            negmsg = "You can't buy a negative quantity of items. Use `cb sell` for that!"
            await ctx.send(negmsg)
            return

        if check is not None:
            price = shop[item].get('price')
            await cursor.execute(f"SELECT amount FROM u{ctx.author.id} WHERE item = '{item}'")
            check1 = await cursor.fetchone()
            walamt, bankamt = await self.get_amt(ctx.author)
            notenough0 = "You need to withdraw some bank money to make this purchase."
            if walamt[0] + bankamt[0] < price*quantity:
                notenough = "You don't have enough money to make that purchase."
                await ctx.send(notenough)
            elif walamt[0] < price*quantity:
                await ctx.send(notenough0)
            else:
                if check1 is not None:
                    await cursor.execute(f"UPDATE u{ctx.author.id} SET amount = {check1[0] + quantity} WHERE item = '{item}'")
                if check1 is None:
                    await cursor.execute(f"INSERT INTO u{ctx.author.id} (item, amount) VALUES ('{item}', {quantity})")
                await cursor.execute(f'UPDATE main SET wallet = {walamt[0] - quantity*price} WHERE user_id = {ctx.author.id}')
                success = "You just bought {} {} for {}! To use one, please use `cb use {}`."
                await ctx.send(success.format(quantity, item, price*quantity, item))
        else:
            await ctx.send("You must specify a valid item or item ID. Use `cb shop` to view all items currently available.")
        await db.commit()
        await cursor.close()
        await db.close()

    @commands.command(description="Sell an item from your inventory.\n[quantity] value is optional.")
    async def sell(self, ctx, item, quantity=1):
        await self.open_account(ctx.author)
        db = await aiosqlite.connect('./bot/db/currency.db')
        cursor = await db.cursor()
        check0 = shop.get(item)
        if check0 is None:
            await ctx.send("That item doesn't exist.")
            return
        sale = shop[item].get('sale')
        await cursor.execute(f"SELECT item FROM u{ctx.author.id} WHERE item = '{item}'")
        check = await cursor.fetchone()
        await cursor.execute(f"SELECT amount FROM u{ctx.author.id} WHERE item = '{item}'")
        check1 = await cursor.fetchone()
        await cursor.execute(f'SELECT wallet FROM main WHERE user_id = {ctx.author.id}')
        oldamt = await cursor.fetchone()
        if check == 0:
            await ctx.send("You don't own that item.")
            return
        else:
            if quantity < 1:
                await ctx.send("You can't sell a negative number of items. Use the buy command for that!")
            elif quantity > check1[0]:
                await ctx.send(f"You don't have that many {item}s to sell.")
            else:
                await cursor.execute(f"UPDATE u{ctx.author.id} SET amount = {check1[0] - quantity} WHERE item = '{item}'")
                await cursor.execute(f'UPDATE main SET wallet = {oldamt[0]+sale} WHERE user_id = {ctx.author.id}')
                await ctx.send(f"You just sold {quantity} {item}s and gained {sale*quantity}")
        await db.commit()
        await cursor.close()
        await db.close()

    @commands.command(description="View the items available for purchase!")
    async def shop(self, ctx):
        embed = discord.Embed(title="ConchBot Shop", colour=ctx.author.colour)
        embed.add_field(name="Watch", value="Give people the time!")
        embed.add_field(name="Computer", value="Play your favorite games!")
        embed.add_field(name="Apple", value="Eat an apple. An apple a day keeps the doctor away!")
        embed.set_footer(text="To buy an item, use 'cb buy {item}.' Item name MUST be lowercase!")
        await ctx.send(embed=embed)

    @commands.command(description="Beg for moners!")
    @commands.cooldown(1, 15, BucketType.user)
    async def beg(self, ctx):
        await self.open_account(ctx.author)
        amt = random.randint(1, 100)
        people = ['Phil Swift', 'Hugh Jass', 'Mike Oxlong', 'UnsoughtConch', 'That bitch stacy',
                    'Your grumpy old neighbor', 'Jerk Mehoff', 'That one kid from school who only showers once a month', 'I',
                    'Jeff Bezos', 'Bobby', 'Garret Bobby Ferguson', "Fay Gott", "Ree Todd", "Totally Not a Burglar", "Bob", "Bill"]

        person = random.choice(people)
        chance = random.randint(0, 2)
    
        if person == "UnsoughtConch":
            namt = random.randint(100, 1000)
            await ctx.send(f"UnsoughtConch ran `cb editmoners` and gave you {namt} moners!")
            await self.update_bank(ctx.author, namt)
        
        elif person == "Totally Not a Burglar":
            namt = random.randint(1, 100)
            await ctx.send(f"Totally Not a Burglar stole {namt} moners from you!")
            await self.update_bank(ctx.author, -namt)
        
        elif person == "Jeff Bezos":
            namt = random.randint(1000, 10000)
            await ctx.send(f"Jeff Bezos stopped by and gave you {namt} moners!")
            await self.update_bank(ctx.author, namt)

        elif chance == 2:
            await ctx.send(f"{person} gave you {amt} moners, but sadly it was stored in the balls.")

        else:
            await self.update_bank(ctx.author, amt)
            await ctx.send(f"{person} gave you {amt} moners!")
    
    @commands.command(aliases=['rob', 'yoink'], description="Steal moners from someone!")
    @commands.cooldown(1, 60, BucketType.user)
    async def steal(self, ctx, victim:discord.Member):
        await self.open_account(victim)
        if victim == ctx.author:
            await ctx.send("You can't steal from yourself.")
            return
        walamt1, bankamt1 = await self.get_amt(ctx.author)
        walamt2, bankamt2 = await self.get_amt(victim)
        if walamt1[0] + bankamt1[0] < 100:
            await ctx.send("You don't have enough moners to rob someone.")
        elif walamt1[0] < 100:
            await ctx.send("You gotta withdraw some moners from your bank first.")
        elif walamt2[0] < 100:
            await ctx.send("They don't have enough moners in their wallet to be robbed.")
        else:
            result = random.randint(1, 2)
            print(result)
            if result == 1:
                win = random.randint(10, walamt2[0])
                print(win)
                print(walamt1[0])
                await self.update_bank(ctx.author, win)
                await self.update_bank(victim, -win)
                await ctx.send(f"You just robbed {victim} of {win} moners!")
            else:
                await self.update_bank(ctx.author, -100)
                await self.update_bank(victim, 100)
                failmsg = "You failed and had to pay 100 moners. That's what you get."
                await ctx.send(failmsg)

    @commands.command(aliases=['gift'], description="Give someone a gift of moners or an item!")
    async def give(self, ctx, user:discord.Member, mode):
        await self.open_account(ctx.author)
        await self.open_account(user)
        db = await aiosqlite.connect('./bot/db/currency.db')
        cursor = await db.cursor()
        if user == ctx.author:
            selfmsg = "You can't give items to yourself."
            await ctx.send(selfmsg)
            return
        if mode == "item":
            await ctx.send(f"What item would you like to give to {user.name}?")
            msg = await self.client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=10)
            check = shop.get(msg.content)
            if check is None:
                await ctx.send("That's not a valid option.")
            else:
                await ctx.send(f"How many {msg.content}s would you like to give to {user.name}?")
                msg0 = await self.client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=10)
                await cursor.execute(f"SELECT amount FROM u{ctx.author.id} WHERE item = '{msg.content}'")
                check0 = await cursor.fetchone()
                if check0 is None:
                    await ctx.send(f"You don't have any {msg.content}s!")
                elif int(msg0.content) > check0[0]:
                    await ctx.send(f"You don't have that many {msg.content}s to give to {user.name}.")
                elif int(msg0.content) < 1:
                    await ctx.send("You can't give someone 0 or less items.")
                else:
                    await cursor.execute(f"SELECT amount FROM u{user.id} WHERE item = '{msg.content}'")
                    useramt = await cursor.fetchone()
                    await cursor.execute(f"UPDATE u{ctx.author.id} SET amount = {check0[0] - int(msg0.content)} WHERE item = '{msg.content}'")
                    try:
                        await cursor.execute(f"UPDATE u{user.id} SET amount = {useramt[0] + int(msg0.content)} WHERE item = '{msg.content}'")
                    except:
                        await cursor.execute(f"INSERT INTO u{user.id} (item, amount) VALUES ('{msg.content}', 0)")
                        useramt = 0
                        await cursor.execute(f"UPDATE u{user.id} SET amount = {useramt + int(msg0.content)} WHERE item = '{msg.content}'")
                    await ctx.send(f"{msg0.content} {msg.content}s delivered! One last thing - would you like to leave"
                    f"{user.name} a message? If so, reply to this with a message. If not, simply reply with 'no'")
                    msg1 = await self.client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=10)
                    if msg1.content == "no":
                        await ctx.send(f"Alright. {user.name} has **not** been notified.")
                    else:
                        await user.send(f"{ctx.author.name} from {ctx.guild.name} has gifted you "
                        f"{int(msg0.content)} {msg.content}s with the message:\n{msg1.content}")
                        await ctx.send(f"{user.name} has been notified of their gift with an accompanying message!")
        elif mode == "moners":
            walamt, bankamt = await self.get_amt(ctx.author)
            await ctx.send(f"How many moners would you like to give to {user.name}?")
            amount = await self.client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=10)
            if int(amount.content) < 1:
                await ctx.send("You can't give someone 0 or less items.")
            elif int(amount.content) > walamt[0] + bankamt[0]:
                await ctx.send(f"You don't have that many moners to give to {user.name}")
            elif int(amount.content) > walamt[0]:
                await ctx.send(f"You must withdraw some moners from your bank to give {user.name} that many moners.")
            else:
                newamount = int(amount.content)
                await self.update_bank(ctx.author, -newamount)
                await self.update_bank(user, newamount)
                await ctx.send(f"{newamount} moners delivered to {user.name}. Would you like to send them a message?"
                " You type a message after this one or reply with `no` to exit.")
                message = await self.client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=10)
                if message.content == "no":
                    await ctx.send(f"{user.name} has **not** been notified.")
                else:
                    await user.send(f"{ctx.author.name} from {ctx.guild.name} has given you {amount.content} moners, with the "
                    f"message:\n{message.content}")
                    await ctx.send(f"{user.name} has been notified of their gift.")
        else:
            await ctx.send("That is an invalid option. Your options are either `item` or `moners.`")
        await db.commit()
        await cursor.close()
        await db.close()

    @commands.command(description="Bet your moners on some slots!")
    @commands.cooldown(1, 20, BucketType.user)
    async def slots(self, ctx, amt):
        # TEMP: 4% chance of getting the mega jackpot!
        await self.open_account(ctx.author)
        walamt, bankamt = await self.get_amt(ctx.author)
        totalamt = walamt[0]+bankamt[0]
        amt = int(amt)

        if amt>totalamt:
            await ctx.send("You don't have that many moners!")

        elif amt>walamt[0]:
            await ctx.send("You need to withdraw some bank money to bet that much on slots!")

        elif amt<0:
            await ctx.send("You can't bet negative moners.")

        else:
            final = []
            for _ in range(3):
                a = random.choice([":fire:","<:Conch:741462553846087721>", ":heart:",":middle_finger:",":smiling_imp:"])
                final.append(a)

            if final[0] == final[1] == final[2] == "<:Conch:741462553846087721>":
                embed = discord.Embed(
                    title=f"{ctx.author.name}'s Slot Game",
                    colour=discord.Colour.gold()
                )
                embed.add_field(name="Result:", value=f"{final[0]} {final[1]} {final[2]}", inline=False)
                embed.add_field(name="Jackpot!", value="You hit the jackpot!", inline=False)
                embed.add_field(name="Amount Won:", value=f"{amt*10} moners!", inline=False)
                await ctx.send(embed=embed)
                await self.update_bank(ctx.author, amt*10)

            elif final[0] == final[1] == final[2]:
                embed = discord.Embed(
                    title=f"{ctx.author.name}'s Slot Game",
                    colour=discord.Colour.green()
                )
                embed.add_field(name="Result:", value=f"{final[0]} {final[1]} {final[2]}", inline=False)
                embed.add_field(name="Three in a row!", value="You got three of the same emoji!", inline=False)
                embed.add_field(name="Amount Won:", value=f"{amt*5} moners!", inline=False)
                await ctx.send(embed=embed)
                await self.update_bank(ctx.author, amt*5)

            elif final[0] == final[1] or final[1] == final[2]:
                embed = discord.Embed(
                    title=f"{ctx.author.name}'s Slot Game",
                    colour=discord.Colour.green()
                )
                embed.add_field(name="Result:", value=f"{final[0]} {final[1]} {final[2]}", inline=False)
                embed.add_field(name="Amount Won:", value=f"{amt*2} moners!", inline=False)
                await ctx.send(embed=embed)
                await self.update_bank(ctx.author, amt*2)

            else:
                embed = discord.Embed(
                    title=f"{ctx.author.name}'s Slot Game",
                    colour=discord.Colour.red()
                )
                embed.add_field(name="Result:", value=f"{final[0]}{final[1]}{final[2]}", inline=False)
                embed.add_field(name="You lost!", value="You did not get any matching emoji that align :(", inline=False)
                embed.add_field(name="Amount Lost:", value=f"{amt} moners.", inline=False)
                await ctx.send(embed=embed)
                await self.update_bank(ctx.author, amt*-1)

    @commands.command(description="Get your daily moners!")
    @commands.cooldown(1, 86400, BucketType.user)
    async def daily(self, ctx):
        await self.open_account(ctx.author)
        await self.update_bank(ctx.author, 200)

        embed = discord.Embed(
            title="Daily Moners",
            colour=ctx.author.colour
        )
        embed.add_field(name="200 moners have been placed in your wallet.", value="Come back tomorrow for more moners.")
        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True, description="Use an item from your inventory!")
    async def use(self, ctx):
        await ctx.send("You need to specify an item to use.")
    
    @use.command()
    @commands.cooldown(1, 15, BucketType.user)
    async def watch(self, ctx):
        await self.open_account(ctx.author)
        amount = await self.item_func(ctx.author, "watch")
        if amount[0] < 1:
            await ctx.send("You can't use a watch that you don't have!")
        else:
            chance = random.randint(0, 3)
            if chance == 1:
                await ctx.send("You tried to give someone the time, but they didn't give a shit.")
            elif chance == 2:
                await ctx.send("Someone got angry at you and smashed your watch.")
                await self.item_func(ctx.author, "watch", -1)
            else:
                tip = random.randint(0, 50)
                await ctx.send(f"You gave someone the time and they gave you a {tip} moner tip!")
                await self.update_bank(ctx.author, tip)

    @use.command()
    @commands.cooldown(1, 30, BucketType.user)
    async def computer(self, ctx):
        await self.open_account(ctx.author)
        amount = await self.item_func(ctx.author, "computer")
        if amount[0] < 1:
            await ctx.send("You can't use a computer that you don't have!")
        else:
            chance = random.randint(0, 3)
            games = ["Rocket League", "Minecraft", "Minceraft", "Call of Duty: Modern Warfare",
            "Call of Duty: Cold War", "Super Mario Bros.", "Super Mario Galaxy", "Mario Kart", "Halo 3", "Doom", 
            "CS:GO", "Overwatch", "Rainbow Six: Siege", "Uno With Friends", "Dark Souls", "Banjo Kazooie", "The Witcher",
            "Snake"]
            if chance == 2:
                await ctx.send(f"You lost {random.choice(games)} and smashed your computer.")
                await self.item_func(ctx.author, "computer", -1)
            elif chance == 1:
                await ctx.send(f"You lost {random.choice(games)} but decided not to lose your temper.")
            else:
                reward = random.randint(1, 2000)
                await ctx.send(f"You won {random.choice(games)} and got rewarded with {reward} moners!")
                await self.update_bank(ctx.author, reward)

    @use.command()
    @commands.cooldown(1, 15, BucketType.user)
    async def apple(self, ctx):
        await self.open_account(ctx.author)
        amount = await self.item_func(ctx.author, "apple")
        if amount[0] < 1:
            await ctx.send("You can't eat an apple you don't have.")
        else:
            chance = random.randint(0, 3)
            if chance == 2:
                await ctx.send("You dropped your apple on the floor and it smashed :(")
                await self.item_func(ctx.author, "apple", -1)
            elif chance == 1:
                debt = random.randint(10, 3000)
                await ctx.send(f"Your apple successfully scared the doctor away, resulting in {debt} moners"
                " in hospital bills you no longer have to pay for.")
                await self.item_func(ctx.author, "apple", -1)
                await self.update_bank(ctx.author, debt)
            else:
                await ctx.send("You ate an apple.")
                await self.item_func(ctx.author, "apple", -1)

    @use.command()
    @commands.cooldown(1, 15, BucketType.user)
    async def bronze(self, ctx):
        await self.open_account(ctx.author)
        amount = await self.item_func(ctx.author, "Bronze Conch")
        if amount[0] < 1:
            await ctx.send("You can't use a Conch Shell you don't have.")
        else:
            items = list(shop)
            reward = random.choice(items)
            await ctx.send(f"You asked your Bronze Conch what you could have as a prize and it gave you a {reward}!")
            await self.item_func(ctx.author, reward, 1)
            await self.item_func(ctx.author, "Bronze Conch", -1)

    @commands.group(aliases=["tasks"], invoke_without_command=True, description="Do a task for a reward of items!")
    async def task(self, ctx):
        await self.open_account(ctx.author)
        db = await aiosqlite.connect('./bot/db/tasks.db')
        cursor = await db.cursor()
        await cursor.execute(f"SELECT task FROM u{ctx.author.id}")
        result = await cursor.fetchall()
        embed = discord.Embed(title="Available tasks", colour=ctx.author.colour)
        for entry in tasks:
            if flag := any(entry in a for a in result):
                embed.add_field(name=f"{entry} ✅", value=f"Description: {tasks[entry].get('desc')}\nReward: {tasks[entry].get('reward')}")
            else:
                embed.add_field(name=entry, value=f"Description: {tasks[entry].get('desc')}\nReward: {tasks[entry].get('reward')}")
        embed.set_footer(text="To do a task, use 'cb task start {task name}' | ✅ means finished task")
        await ctx.send(embed=embed)

        await cursor.close()
        await db.close()

    @task.command(description="Start a task!")
    async def start(self, ctx, task):
        await self.open_account(ctx.author)
        db = await aiosqlite.connect('./bot/db/tasks.db')
        cursor = await db.cursor()
        await cursor.execute(f"CREATE TABLE IF NOT EXISTS u{ctx.author.id} (task, status)")
        await cursor.execute(f"SELECT task FROM u{ctx.author.id} WHERE task = '{task}'")
        result = await cursor.fetchone()
        if result is not None:
            await ctx.send("You have already completed this task!")
            return
        try:
            tasks[task].get('desc')
        except:
            await ctx.send("That's not a valid task.")
            return
        await ctx.send(tasks[task].get('dialogue'))
        msg = await self.client.wait_for('message', check=lambda message: message.author == ctx.author, timeout=30)
        req = tasks[task].get('req')
        if req in msg.content.lower() or msg.content:
            try:
                await self.update_bank(ctx.author, tasks[task].get('reward'))
            except:
                await self.item_func(ctx.author, tasks[task].get('rewarditem'), tasks[task].get('rewardnum'))
            await ctx.send(tasks[task].get('thank'))
            await cursor.execute(f"INSERT INTO u{ctx.author.id} (task) VALUES ('{task}')")
        await db.commit()
        await cursor.close()
        await db.close()

    @commands.command(aliases=["lotto"], disabled=True)
    async def lottery(self, ctx, amount:int):
        await ctx.send(embed=discord.Embed(title=f"You are about to enter the lottery with {amount} moners. Are you sure? `y/n`",  color=discord.Color.gold(), description="If you don't know what you're"
        " doing, I suggest you use the `lottery info` command first."))

        def check(m):
            return m.content.lower() == "y" or m.content.lower() == "n" and m.author == ctx.author

        try:
            conf = await self.client.wait_for('message', check=check, timeout=10)
        except asyncio.TimeoutError:
            return await ctx.send("You must respond with either `y` or `n` in 10 seconds.")

        if conf.content.lower() == "n":
            return await ctx.send("Aborting...")

        walamt, bankamt = await self.get_amt(ctx.author.id)

        if int(walamt[0]) < amount:
            if int(bankamt[0]) < amount:
                return await ctx.send("You don't have that much moners to gamble!")
            
def setup(client):
    client.add_cog(Currency(client))
