import discord
from discord.ext import commands
from discord import app_commands
from discord.utils import get
import asyncio
import random
import aiosqlite
from easy_pil import *
import re


ROLE = "⌁﹒member"

ADMIN_ROLES = [1007673373851140146, 1000887595724705844, 1001089149236949023, 1001088961529266199] # insert numerical IDs of admin roles here - bot will ignore changes made by these users
BOT_ROLE_ID = 1052616862032199695 # numerical ID of the role given to this bot - changes made by this role will be ignored
STATIC_NICKNAME_ROLE_ID = 1052649002635628704 # numerical ID - bot will revert changes made by these users
PLACEHOLDER_NICKNAME = "Moderated Nickname"
NICKNAME_PATTERNS = [
    r'(discord\.gg/)',  # invite links
    r'(nigg|fag|\bnazi\b)',  # banned words - \bword\b is exact match only
    r'(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)'  # hyperlinks
]

class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.all())
        self.synced = False
    
    async def on_ready(self):
        setattr(bot, "db", await aiosqlite.connect('levelDatabase.db'))
        await asyncio.sleep(3)

        async with bot.db.cursor() as cursor:
            await cursor.execute("CREATE TABLE IF NOT EXISTS levels (level INTEGER, xp INTEGER, user INTEGER, guild INTEGER)")

        channel = bot.get_channel(1052610265063112774)

        await channel.purge()

        with open('images/roles.png', 'rb') as f:
            picture = discord.File(f)
            await channel.send(file=picture)

        embed=discord.Embed(title="__** Roles Information**__", color=0xc7f2f5)
        embed.add_field(name="Staff Roles", value="Staff Members of the discord. \n<@&1007673373851140146>, <@&1000887595724705844>, <@&1001089149236949023>, <@&1001088961529266199>", inline=True)
        embed.add_field(name="Special Role's (Booster or Custom)", value="<@&1009467926207799448> \nObtain by boosting the discord with Nitro! \n\n<@&1016813324593278988> \nMust have been such a weirdo for getting this role!", inline=False)
        embed.add_field(name="Level Roles", value="**Level 5 ** - <@&1052625291882790962>\nAbility to use external emotes\nAbility to stream in voice channels\n**Level 10 ** - <@&1052625295666073641>\nAbility to add reactions in chats\nAbility to use external stickers\n**Level 15 ** - <@&1052625298660790293>\nAbility to change nickname\n**Level 20 ** - <@&1052625300606947328>\nAttach files permission\n**Level 25** - <@&1052625301814911006>\nAbility to use /AFK command\n**Level 30** - <@&1052625303052238919>\nAbility to attach GIF links\n**Level 35** - <@&1052625304100810762>\nNo Rewards yet!\n**Level 40 ** - <@&1052625311713480744>\nNo Rewards yet!\n**Level 45 ** - <@&1052625523479695380>\nNo Rewards yet!\n**Level 50 ** - <@&1052625527409750106>\nNo Rewards yet!\n**Level 55 ** - <@&1052625528911310868>\nNo Rewards yet!\n**Level 60 ** - <@&1052625531532755066>\nNo Rewards yet!", inline=False)
        await channel.send(embed=embed)

        with open('images/channels.png', 'rb') as f:
            picture = discord.File(f)
            await channel.send(file=picture)

        embed=discord.Embed(title="__** Fast Travel**__", color=0xc7f2f5)
        embed.add_field(name="Important Server Channels", value="Reaction Roles: <#1052645130076700702> \nServer Rules: <#1052610292737126501> \nServer News: <#1052643618315305001> \nSupport Tickets: <#1052645257017303075> \nMinecraft Server: <#1052645938340053072>", inline=False)
        await channel.send(embed=embed)

        channel = bot.get_channel(1052610292737126501)

        await channel.purge()

        with open('images/rules.png', 'rb') as f:
            picture = discord.File(f)
            await channel.send(file=picture)

        embed=discord.Embed(title="__** Server Rules**__", color=0xc7f2f5)
        embed.add_field(name="**Be polite.**", value="Chatting is fine - keep toxicity to a certain level. No excessively outrageous hostile language either. Excessive toxicity and drama will result in a ban.", inline=False)
        embed.add_field(name="**No advertisement.**", value="This will not be tolerated and will lead to an instant ban. Any types of external links are not allowed in the server.", inline=False)
        embed.add_field(name="**No harassment.**", value="Do not post information or pictures of other people without their permission. Any type of serious harassment (blackmailing, doxxing, hate speech) will lead to a permanent ban.", inline=False)
        embed.add_field(name="**No NSFW content.**", value="NSFW (Not Safe For Work) content is strictly not allowed in any of the channels, and if posted will result in a ban. Keep things safe for work in all channels. This includes, but is not limited to, emotes, profile pictures, and images.", inline=False)
        embed.add_field(name="**English only.**", value="This is an English server and all messages should be in English. Failure to speak English will result in warnings and then mutes.", inline=False)

        await channel.send(embed=embed)
        await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="Still need help? do /help for more help!"))

bot = aclient()
tree = app_commands.CommandTree(bot)


async def on_member_update(memberBefore, memberAfter):
    # get corresponding audit log entry to find who initiated member change
    corresponding_audit_entry = None
    # get all audit log entries for Member Updated
    async for entry in bot.guilds[0].audit_logs(action=discord.AuditLogAction.member_update):
        # if this entry was to the user in question, and was this specific nickname change
        if (entry.target == memberBefore and entry.after.nick == memberAfter.nick):
            corresponding_audit_entry = entry
            print(entry.user)
            print(entry.user.roles)
            break

    if corresponding_audit_entry is not None:  # successfully found audit log entry before
        # user changed their own nickname; ignore if admin/bot changed it
        admin_role_check = (corresponding_audit_entry.user.top_role.id in ADMIN_ROLES)
        bot_role_check = (corresponding_audit_entry.user.top_role.id == BOT_ROLE_ID)
        if not(admin_role_check or bot_role_check):
            for i in memberAfter.roles:
                print(i.id)
                if i.id == STATIC_NICKNAME_ROLE_ID:  # user has Static Name role
                    await memberAfter.edit(nick=memberBefore.display_name)  # revert nickname
                    return
                else:  # check for bad words
                    new_nickname = memberAfter.display_name
                    if checkName(new_nickname):  # bad display name
                        if not checkName(memberAfter.name):  # username is okay
                            await memberAfter.edit(nick=None)  # reset nickname
                        else:
                            # assign placeholder nickname
                            await memberAfter.edit(nick=PLACEHOLDER_NICKNAME)

@bot.event
async def on_member_join(member):
    role = get(member.guild.roles, name=ROLE)
    await member.add_roles(role)
    
def checkName(nick):
    result = False
    for i in NICKNAME_PATTERNS:
        if re.match(i, nick, re.IGNORECASE):
            result = True
            break

    return result

@bot.event
async def on_member_update(memberBefore, memberAfter):
    # get corresponding audit log entry to find who initiated member change
    corresponding_audit_entry = None
    # get all audit log entries for Member Updated
    async for entry in bot.guilds[0].audit_logs(action=discord.AuditLogAction.member_update):
        # if this entry was to the user in question, and was this specific nickname change
        if (entry.target == memberBefore and entry.after.nick == memberAfter.nick):
            corresponding_audit_entry = entry
            print(entry.user)
            print(entry.user.roles)
            break

    if corresponding_audit_entry is not None:  # successfully found audit log entry before
        # user changed their own nickname; ignore if admin/bot changed it
        admin_role_check = (corresponding_audit_entry.user.top_role.id in ADMIN_ROLES)
        bot_role_check = (corresponding_audit_entry.user.top_role.id == BOT_ROLE_ID)
        if not(admin_role_check or bot_role_check):
            for i in memberAfter.roles:
                print(i.id)
                if i.id == STATIC_NICKNAME_ROLE_ID:  # user has Static Name role
                    await memberAfter.edit(nick=memberBefore.display_name)  # revert nickname
                    return
                else:  # check for bad words
                    new_nickname = memberAfter.display_name
                    if checkName(new_nickname):  # bad display name
                        if not checkName(memberAfter.name):  # username is okay
                            await memberAfter.edit(nick=None)  # reset nickname
                        else:
                            # assign placeholder nickname
                            await memberAfter.edit(nick=PLACEHOLDER_NICKNAME)

                            
@bot.event
async def on_user_update(memberBefore, memberAfter):
    newUsername = memberAfter.name
    if checkName(newUsername):  # bad username
        # assign placeholder nickname
        await memberAfter.edit(nick=PLACEHOLDER_NICKNAME)


# check if new members' usernames need filtering
@bot.event
async def on_member_join(member):
    username = member.name
    if checkName(username):  # bad username
        # assign placeholder nickname
        await member.edit(nick=PLACEHOLDER_NICKNAME)
                            
@bot.event
async def on_message(message):
    if bot.user.mentioned_in(message):
        await message.channel.send('You are so smelly omg')

        
@bot.event
async def on_message(message):

    channel = 1052647329234165770

    if message.author.bot:
        return
    author = message.author
    guild = message.guild
    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT xp FROM levels WHERE user = ? AND guild = ?", (author.id, guild.id))
        xp = await cursor.fetchone()
        await cursor.execute("SELECT level FROM levels WHERE user = ? AND guild = ?", (author.id, guild.id))
        level = await cursor.fetchone()

        if not xp or not level:
            await cursor.execute("INSERT INTO levels (level, xp, user, guild) VALUES (?, ?, ?, ?)", (1, 0, author.id, guild.id,))
            await bot.db.commit()
        
        try:
            xp = xp[0]
            level = level[0]
        except TypeError:
            xp = 0
            level = 0

        if level < 5:
            xp += random.randint(1, 3)
            await cursor.execute("UPDATE levels SET xp = ? WHERE user = ? AND guild = ?", (xp, author.id, guild.id))
        else:
            rand = random.randint(1, level//4)
            if rand == 1:
                xp += random.randint(1, 3)
                await cursor.execute("UPDATE levels SET xp = ? WHERE user = ? AND guild = ?", (xp, author.id, guild.id))
        if xp >= 100:
            level += 1
            await cursor.excute("UPDATE levels SET level = ? WHERE user = ? AND guild = ?", (level, author.id, guild.id))
            await cursor.execute("UPDATE levels SET xp = ? WHERE user = ? AND guild = ?", (0, author.id, guild.id))
            await channel.send(f"{author.mention} has leveled up to level **{level}** GG!!")
        await bot.db.commit()

@tree.command(name="level", description="Displays your level", guild=discord.Object(id = 1000881534259187823))
async def self(interaction: discord.Interaction):
    if member is None:
        member = interaction.user.id
        
        print(f"{member.id}")

    async with bot.db.cursor() as cursor:
        await cursor.execute("SELECT xp FROM levels WHERE user = ? AND guild = ?", (member.id, guild))
        xp = await cursor.fetchone()
        await cursor.execute("SELECT level FROM levels WHERE user = ? AND guild = ?", (member.id, guild.id))
        level = await cursor.fetchone()

        if not xp or not level:
            await cursor.execute("INSERT INTO levels (level, xp, user, guild) VALUES (?, ?, ?, ?", (1, 0, member.id, ctx.guild.id,))
            await bot.commit()
        
        try:
            xp = xp[0]
            level = level[0]
        except TypeError:
            xp = 0
            level = 0



bot.run("MTA1MjYxNjY4MTYwNTgzMjcxNQ.GVJq9I.IWhL_F3SpPxHqtgSj-GDS8vvQpKw-cyui17Y20")
