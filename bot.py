import code
from peewee import *
import datetime
from db import db
from Models import Person, Transaction
from dotenv import load_dotenv
import discord
from discord.ui import Modal, View, InputText
import os

load_dotenv()
bot = discord.Bot(intents=discord.Intents.all())
db.connect()
db.create_tables([Person, Transaction])

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

@bot.slash_command(name="get_coins", description = "Get your 10 coins of the day.")
async def get_coins(ctx):
    username = ctx.author.name
    user_in_db = Person.get_or_create(name=username, birthday=datetime.date(2009, 3, 13))
    transaction = Transaction(user=username, transaction="daily", amount=10, sent_by=bot.user.name, received_by=username)
    transaction.save()

    # user = bot.get_user(user_id) or await bot.fetch_user(user_id)
    await ctx.respond("Ya recibiste tus monedas diarias.", ephemeral=True)

@bot.slash_command(name = "hello", description = "Say hello to the bot")
async def hello(ctx):
    # print(ctx.guild.members)
    user_id = ctx.author.id
    user = bot.get_user(user_id) or await bot.fetch_user(user_id)
    await user.send('whatever')

class MyModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="Nombre"))
        self.add_item(discord.ui.InputText(label="Precio"))
        self.add_item(discord.ui.InputText(label="Descripcion", style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Image Link"))
        self.add_item(discord.ui.InputText(label="Codigo - Cantidad"))

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Nuevo objeto")
        embed.add_field(name="Nombre", value=self.children[0].value)
        embed.add_field(name="Precio", value=self.children[1].value)
        embed.add_field(name="Descripcion", value=self.children[2].value)
        embed.set_image(url=self.children[3].value)

        code_and_amount = self.children[4].value.split(" ")
        print(code_and_amount)
        embed.add_field(name="Codigo", value=code_and_amount[0])
        embed.add_field(name="Cantidad", value=code_and_amount[1])

        await interaction.response.send_message(embeds=[embed], ephemeral=True)

@bot.slash_command(name = "add_new_item", description = "Add a new item to the store.")
async def add_new_item(ctx):
    user_roles = ctx.author.roles
    guild_roles = ctx.guild.roles

    highest_user_rol = user_roles[len(user_roles) - 1].name
    highest_guild_rol = guild_roles[len(guild_roles) - 1].name
    
    if highest_guild_rol == highest_user_rol:
        print("User is in the highest role, he is authorized to use this command")
        modal = MyModal(title="Modal via Slash Command")
        await ctx.send_modal(modal)
    else:
        await ctx.respond("No tienes el rol necesario para usar este comando.", ephemeral=True)

bot.run(os.getenv('TOKEN'))
db.close()  