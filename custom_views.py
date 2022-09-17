import discord
import operator
from typing import Union
from discord.ui import Button
from discord.ext import commands, pages
from helpers import user_is_mod, move_forward, user_to_string
from league_of_legends import divisions, tiers
from transaction import insert_play_reward, insert_promo_reward_transaction, get_store_items, get_user_coins, insert_item_buy, set_new_balance, create_new_store_item

clancoin_emote = '<:clancoin:974120483693924464>'

class ApproveView(discord.ui.View):
    def __init__(self, ctx, command, division=None, tier=None, play=None):
        super().__init__()

        self.author = ctx.author
        self.command = command
        self.division = division
        self.tier = tier
        self.play = play

        aprove_button = Button(label="Aceptar", style=discord.ButtonStyle.primary, emoji="👍")
        async def aprove_callback(interaction):
            if user_is_mod(interaction):
                if self.command == "recompensa_jugada":
                    aprover_mod = interaction.user.name + '#' + interaction.user.discriminator
                    author_name = self.author.name + '#' + self.author.discriminator
                    if self.play == "TripleKill":
                        print('Recompensa de triple') 
                        insert_play_reward(sent_by=aprover_mod, received_by=author_name, amount=50, transaction_type=self.play.lower())
                        await interaction.response.edit_message(content=f"Aprobado, recibes {clancoin_emote} 50 Clan Coins.", view=None)
                    if self.play == "QuadraKill": 
                        print('Recompensa de quadra')
                        insert_play_reward(sent_by=aprover_mod, received_by=author_name, amount=150, transaction_type=self.play.lower())
                        await interaction.response.edit_message(content=f"Aprobado, recibes {clancoin_emote} 150 Clan Coins.", view=None)
                    if self.play == "PentaKill":
                        print('Recompensa de penta') 
                        insert_play_reward(sent_by=aprover_mod, received_by=author_name, amount=250, transaction_type=self.play.lower())
                        await interaction.response.edit_message(content=f"Aprobado, recibes {clancoin_emote} 250 Clan Coins.", view=None)

                if self.command == "recompensa_promo":
                    for tier in tiers:
                        reward = 0
                        if tier.display_name == self.tier:
                            aprover_mod = interaction.user.name + '#' + interaction.user.discriminator
                            author_name = self.author.name + '#' + self.author.discriminator
                            reward = tier.reward
                            if self.division == "IV":
                                reward = reward * tier.multiplier
                            insert_promo_reward_transaction(sent_by=aprover_mod, received_by=author_name, amount=reward, transaction_type=f'{tier.name}_{self.division}')
                            print('reward sent')
                            await interaction.response.edit_message(content=f"Aprobado, recibes {clancoin_emote} {int(reward)} Clan Coins.", view=None)
                            break
                        # insert_promo_reward_transaction(sent_by=interaction.user, received_by=self.author_id, amount=tier.reward, transaction_type=f'{tier.name}_{self.tier.lower()}')
            else:
                await interaction.response.send_message("Un moderador te dará tu recompensa.", ephemeral=True)
        
        reject_button = Button(label="Rechazar", style=discord.ButtonStyle.red, emoji="👎")
        async def reject_callback(interaction):
            if user_is_mod(interaction):
                await interaction.response.edit_message(content="Revisa tu aporte.", view=None)
            else:
                await interaction.response.send_message("Un moderador te dará tu recompensa.", ephemeral=True)
        
        aprove_button.callback = aprove_callback
        reject_button.callback = reject_callback

        self.add_item(aprove_button)
        self.add_item(reject_button)

class Store():
    def __init__(self, user) -> None:
        self.buy_button = None
        self.cancel_button = None
        self.items = get_store_items()
        self.user = user
        self.index = 0
        self.interaction_buttons = self.view(index=0)
        self.paginator = pages.Paginator(pages=self.embed(), custom_view=self.interaction_buttons, loop_pages=True, use_default_buttons=False)
        self.prev = pages.PaginatorButton(button_type="prev", emoji="⏪", disabled=False, style=discord.ButtonStyle.blurple)
        self.indicator = pages.PaginatorButton(button_type="page_indicator", disabled=True)
        self.next = pages.PaginatorButton(button_type="next", emoji="⏩", style=discord.ButtonStyle.blurple)

        async def next_item(interaction: discord.Interaction):
            self.index = self.paginator.current_page
            self.interaction_buttons.clear_items()
            self.interaction_buttons.add_item(
                BuyButton(
                    index=move_forward(self.items.data, self.paginator.current_page), 
                    user=self.user, 
                    label=f'Comprar por {clancoin_emote} {self.items.data[move_forward(self.items.data, self.paginator.current_page)]["price"]}',
                    store_item=self.items.data[move_forward(self.items.data, self.paginator.current_page)])
            )
            self.interaction_buttons.add_item(discord.ui.Button(label="Cancelar",style=discord.ButtonStyle.red,emoji="✖️",row=1))
            await self.paginator.goto_page(move_forward(self.items.data, self.paginator.current_page), interaction=interaction)
        self.next.callback = next_item

        # self.index = self.paginator.current_page
        self.paginator.add_button(self.prev)
        self.paginator.add_button(self.indicator)
        self.paginator.add_button(self.next)
        # self.paginator.add_item(BuyButton(index=move_forward(self.items.data, self.paginator.current_page), user="MindsetFPS#7717", label="Me siento naruto"))

    def embed(self):
        embeds = []
        for store_item in self.items.data:
            emb = discord.Embed(title=store_item["name"], description=f'{store_item["description"]} {clancoin_emote} ')
            emb.set_image(url=store_item["image_url"])
            # emb.add_field(name=store_item["price"], value="dfsd")
            emb.set_footer(text=f'{store_item["price"]} {clancoin_emote}')
            embeds.append(emb)
        return embeds
    
    def view(self, index):
        view = discord.ui.View()
        self.buy_button = BuyButton(index=move_forward(self.items.data, self.index ), user=self.user, label=f'Comprar por {clancoin_emote} {self.items.data[index]["price"]}', store_item=self.items.data[self.index])
        cancel_button = discord.ui.Button(
            label="Cancelar",
            style=discord.ButtonStyle.red,
            emoji="✖️",
            row=1
        )
        view.add_item(self.buy_button)
        view.add_item(cancel_button)
        return view

class BuyButton(discord.ui.Button):
        def __init__(
            self,
            label: str = None,
            emoji: Union[str, discord.Emoji, discord.PartialEmoji] = None,
            style: discord.ButtonStyle = discord.ButtonStyle.green,
            disabled: bool = False,
            custom_id: str = None,
            row: int = 0,
            user: str = None,
            index: int = 0,
            store_item: dict = None
        ):
            super().__init__(
                emoji=emoji,
                style=style,
                disabled=disabled,
                custom_id=custom_id,
                row=row,
                label=label
            )
            self.emoji: Union[str, discord.Emoji, discord.PartialEmoji] = emoji
            self.style = style
            self.disabled = disabled
            self.paginator = None
            self.user = user
            self.store_item = store_item

        async def callback(self, interaction):
            price = self.store_item["price"]
            coins = get_user_coins(self.user)
            print("price: ", price, "user clancoins: ", coins.data[0]['coins'])
            print(price > coins.data[0]['coins'])

            if coins.data[0]["coins"] < price:
                await interaction.response.send_message("No tienes suficientes Clan Coins.")
            else:
                if self.store_item["code"] != None:
                    if self.store_item["amount"] > 0:
                        embed = discord.Embed(title=f'Compraste {self.store_item["name"]}.', description="En un momento recibiras tu objeto.", color=discord.Colour.blurple())
                        embed.set_image(url=self.store_item["image_url"])

                        transaction_name = f"buy_item_{str(self.store_item['id'])}"
                        insert_item_buy(sent_by=user_to_string(interaction.guild.owner), received_by=user_to_string(interaction), amount=self.store_item['price'], transaction_type=transaction_name) 
                        set_new_balance(user=self.user, price=self.store_item["price"], operation=operator.sub)
                        await interaction.user.send(f"Tu codigo para masterclass es {self.store_item['code']}")
                        await interaction.response.edit_message(content=f'Compraste {self.store_item["name"]}.', view=None, embed=embed)
                    else:
                        await interaction.response.edit_message(content="Nos hemos quedado sin codigos, por favor vuelve a intentarlo despues.", view=None, embed=None)
                        await interaction.guild.owner.send(f'Nos hemos quedado el codigo {self.store_item["code"]} para {self.store_item["name"]}, considera añadir mas unidades o crear un nuevo objeto.')
                else:
                    
                    # await interaction.response.send_message()
                    transaction_name = f"buy_item_{str(self.store_item['id'])}"
                    insert_item_buy(sent_by=user_to_string(interaction.guild.owner), received_by=self.user, amount=self.store_item['price'], transaction_type=transaction_name)
                    set_new_balance(user=self.user, price=self.store_item["price"], operation=operator.sub)
                    await interaction.response.edit_message(content=f'Compraste {self.store_item["name"]}', view=None, embed=None)
                    await interaction.followup.send(content=f"<@{interaction.user.id}> compró {self.store_item['name']}. En un momento <@{interaction.guild.owner_id}> se contactará para entregar el premio.")

class Create_add_item_view(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="Nombre"))
        self.add_item(discord.ui.InputText(label="Precio"))
        self.add_item(discord.ui.InputText(label="Descripcion", style=discord.InputTextStyle.long))
        self.add_item(discord.ui.InputText(label="Image URL"))
        self.add_item(discord.ui.InputText(label="Codigo - Cantidad", required=False))

    async def callback(self, interaction: discord.Interaction):

        payload = {
            "name": self.children[0].value,
            "price": self.children[1].value,
            "description": self.children[2].value,
            "image_url": self.children[3].value,
        }

        embed = discord.Embed(title="Nuevo objeto")

        if len(self.children[4].value) > 0:
            code_and_amount = self.children[4].value.split(" ")

            payload["code"] = code_and_amount[0]
            payload["amount"] = code_and_amount[1]

            embed.add_field(name="Codigo", value=code_and_amount[0])
            embed.add_field(name="Cantidad", value=code_and_amount[1])

        create_new_store_item(payload=payload)

        embed.add_field(name="Nombre", value=self.children[0].value)
        embed.add_field(name="Precio", value=self.children[1].value)
        embed.add_field(name="Descripcion", value=self.children[2].value)
        embed.set_image(url=self.children[3].value)

        await interaction.response.send_message(embeds=[embed], ephemeral=True)