import discord
from discord.ext import commands
from discord import app_commands
import json
import random
import asyncio
from pathlib import Path
import os

with open("token.json", "r", encoding="utf-8") as f:
    BotToken = json.load(f)["BotToken"]

DataFile = "quotes_data.json"
Intents = discord.Intents.default()
Intents.message_content = True
Intents.members = True
Bot = commands.Bot(command_prefix = "!",intents = Intents)
def LoadData()->dict:
    if Path(DataFile).exists():
        with open(DataFile, "r",encoding = "utf-8") as f:
            return json.load(f)
    return {}

def SaveData(Data:dict):
    with open(DataFile,"w", encoding = "utf-8") as f:
        json.dump(Data, f, ensure_ascii = False, indent = 2)

def GetGulidConfig(Data:dict,GuildID:int)->dict:
    Key=str(GuildID)
    if Key not in Data:
        Data[Key]={"TargetUserID" : None,
                   "Probability": 0.3,
                   "Minchar":1,
                   "Quote":[],
                   "Enable":True
                   }
    return Data[Key]

@Bot.event
async def on_ready():
    Data=LoadData()
    for guild in Bot.guilds:
        Config = GetGulidConfig(Data, guild.id)        
        if Config["TargetUserID"] is not None:
            TargetUser = guild.get_member(Config["TargetUserID"])
            name = TargetUser.display_name if TargetUser else "古人"
        else:
            name = "去設定復活對象"    

        print(f"{name} 正在復活")
        
    try:
        synced = await Bot.tree.sync()
        print(f"111復活成功111")
    except Exception as e:
        print(f"復活失敗請扣雪鯊")

@Bot.event
async def on_message(Message:discord.Message):
    if Message.author.bot:
        return 
    Data = LoadData()
    GulidID = str(Message.guild.id) if Message.guild else None
    if not GulidID:
        return
    Config = GetGulidConfig(Data, Message.guild.id)
    if Config["TargetUserID"] and Message.author.id  == Config["TargetUserID"] and len(Message.content) >= Config["Minchar"] and not Message.content.startswith("/") and not Message.content.startswith("!") :
        Quote=Message.content
        Config["Quote"].append(Quote)
        SaveData(Data)
    elif Config["Enable"] and Config["Quote"] and Config["TargetUserID"] and random.random()<=Config["Probability"] :
        Quote = random.choice(Config["Quote"])
        TargetUser = Message.guild.get_member(Config["TargetUserID"])
        if TargetUser is not None :
            name = TargetUser.display_name
        else :
            name = "古人"
        Embed = discord.Embed(description = f"{Quote}",color = 0x707bf4)
        Embed.set_footer(text = "不知填啥")
        if TargetUser is not None and TargetUser.display_avatar is not None :
            Embed.set_thumbnail(url = TargetUser.display_avatar.url)
        await asyncio.sleep(0.5)
        await Message.channel.send(embed = Embed)
    await Bot.process_commands(Message)

@Bot.tree.command(name = "SetTarget", description = "取對象復活")

@app_commands.describe(member = "復活對象")

@app_commands.checks.has_permissions(manage_guild = True)

async def set_target(interaction: discord.Interaction, member: discord.Member):
    Data = LoadData()
    Config = GetGulidConfig(Data, interaction.guild.id)
    Config["TargetUserID"] = member.id
    SaveData(Data)
    await interaction.response.send_message("取到對象", ephemeral = True)

@Bot.tree.error
async def on_app_command_error(interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("沒有力量", ephemeral=True)
    else:
        await interaction.response.send_message(f"寄", ephemeral=True)

@Bot.command()
async def GetHistory(ctx, 目標成員: discord.Member):
    StatusMSG = await ctx.send(f"復活 {目標成員.display_name} 中")   
    Data = LoadData()
    Config = GetGulidConfig(Data, ctx.guild.id)
    count = 0
    async for Message in ctx.channel.history(limit=1000):
        if Message.author == 目標成員 :
            if Message.content not in Config["Quote"]:
                Config["Quote"].append(Message.content) 
                count += 1
    SaveData(Data)
    if count > 0:
        await StatusMSG.edit(content=f"收集復活對象資料完成")
    else:
        await StatusMSG.edit(content=f"是不是復活過")


# ──啟動───────────────────────────────────────────────

if __name__ == "__main__":
    Bot.run(BotToken)



