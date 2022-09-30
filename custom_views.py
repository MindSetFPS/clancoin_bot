import discord
import operator
from typing import Union
from discord.ui import Button
from discord.ext import commands, pages
from helpers import user_is_mod, move_forward, user_to_string
from league_of_legends import divisions, tiers
from transaction import insert_play_reward, insert_promo_reward_transaction, get_store_items, get_user_coins, insert_item_buy, set_new_balance, create_new_store_item, create_new_prediction, create_users_prediction_pick, set_prediction_correct_answer, user_has_already_picked, get_predictors, set_prediction_transaction, create_prediction_entry_transaction

clancoin_emote = '<:clancoin:974120483693924464>'

class BetView(discord.ui.View):
    def __init__(self, ctx=discord.ApplicationContext, teamOption0=str, teamOption1=str, question=str, prediction_id=int, prize=int, entry_cost=int):
        super().__init__(
            timeout=43200
        )

        self.question = question
        self.prediction_id = prediction_id
        self.prize = prize
        self.entry_cost = entry_cost

        self.teamOption0 = teamOption0
        self.display_name0 = teamOption0.replace("_", " ")
        self.display_name0 = self.display_name0.title()
        self.emoji0 = None

        self.teamOption1 = teamOption1
        self.display_name1 = teamOption1.replace("_", " ")
        self.display_name1 = self.display_name1.title()
        self.emoji1 = None

        for emoji in ctx.guild.emojis:
                if emoji.name == self.teamOption0:
                    self.emoji0 = emoji
                    break

        for emoji in ctx.guild.emojis:
                if emoji.name == self.teamOption1:
                    self.emoji1 = emoji
                    break

        #crear prediccion en db
        team1_Button = BetOptionButton(question=self.question, options=(self.display_name0, self.display_name0), selection=0 ,style=discord.ButtonStyle.gray, emoji=self.emoji0, button=1, prediction_id=self.prediction_id, prize=self.prize, entry_cost=self.entry_cost)
        team2_Button = BetOptionButton(question=self.question, options=(self.display_name0, self.display_name1), selection=1 ,style=discord.ButtonStyle.gray, emoji=self.emoji1, button=1, prediction_id=self.prediction_id, prize=self.prize, entry_cost=self.entry_cost)

        self.add_item(team1_Button)
        self.add_item(team2_Button)

class BetOptionButton(discord.ui.Button):
        def __init__(
            self,
            options: tuple,
            emoji: Union[str, discord.Emoji, discord.PartialEmoji] = None,
            style: discord.ButtonStyle = discord.ButtonStyle.green,
            disabled: bool = False,
            custom_id: str = None,
            button: int=0,
            row: int = 0,
            prediction_id: int=None,
            prize: int=None,
            entry_cost: int=None, 
            selection: int=None,
            question: str=None,
        ):
            super().__init__(
                emoji=emoji,
                style=style,
                disabled=disabled,
                custom_id=custom_id,
                row=row,
                label=options[selection]
            )
            # self.emoji: Union[str, discord.Emoji, discord.PartialEmoji] = emoji
            self.style = style
            self.disabled = disabled
            self.label = options[selection]
            self.button = button
            self.prediction_id = prediction_id
            self.prize = prize
            self.entry_cost = entry_cost
            self.selection = selection
            self.options = options
            self.question = question

        async def callback(self, interaction: discord.Interaction ):
            await interaction.response.defer()
            if user_is_mod(interaction):
                # cuando el mod da click, se entiende que ese fue el ganador
                    #actualizar db con el ganador
                set_prediction_correct_answer(winner=self.selection, prediction_id=self.prediction_id)

                # traer de la db a los jugadores que votaron por esta opcion
                print(f'prediction_id: {self.prediction_id}')
                predictors = get_predictors(prediction_id=self.prediction_id, pick=self.selection)

                for prediction in predictors:
                    # a cada uno, crearles una transaccion por el valor dado 
                    set_prediction_transaction(transaction_type=f'prediction_{str(self.prediction_id)}', amount=self.prize, sent_by=user_to_string(ctx=interaction.guild.owner), received_by=prediction["user"])
                    #editar el balance con el nuevo 
                    set_new_balance(user=prediction["user"], price=self.prize, operation=operator.add)

                # eliminar botones, y poner el resultadoHa ganado X."
                embed = discord.Embed(title=self.question, description=f'Respuesta correcta: {self.emoji} {self.label}')
                await interaction.followup.edit_message(content=None, view=None, embed=embed, message_id=interaction.message.id)
            else:
                confirmation_view = ConfirmationView(selection=self.selection, option=self.options[self.selection],  emoji=self.emoji, prediction_id=self.prediction_id, prize=self.prize, entry_cost=self.entry_cost)
                await interaction.followup.send(content=None, view=confirmation_view, ephemeral=True)

class ConfirmationView(discord.ui.View):
        def __init__(
            self, 
            prediction_id: int, 
            prize: int, 
            entry_cost: int,
            option: str=None,
            emoji: Union[str, discord.Emoji, discord.PartialEmoji] = None,
            selection: int=None,
        ):
            super().__init__(
                timeout=43200
            )

            self.prediction_id = prediction_id
            self.prize = prize
            self.entry_cost = entry_cost
            self.emoji = emoji
            self.option = option
            self.selection = selection

            self.add_item(
                ConfirmVote(
                    label=f'Confirmar voto por {self.option}', 
                    emoji=self.emoji, 
                    prediction_id=self.prediction_id,
                    entry_cost=self.entry_cost,
                    prize=self.prize,
                    selection=self.selection
                ), 
            )

class ConfirmVote(discord.ui.Button):
        def __init__(
            self,
            label: str = None,
            emoji: Union[str, discord.Emoji, discord.PartialEmoji] = None,
            style: discord.ButtonStyle = discord.ButtonStyle.green,
            disabled: bool = False,
            custom_id: str = None,
            button: int=0,
            row: int = 0,
            prediction_id: int=0,
            prize: int=None,
            entry_cost: int=None,
            selection: int=None
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
            self.label = label
            self.button = button
            self.prediction_id = prediction_id
            self.prize = prize
            self.entry_cost = entry_cost
            self.selection = selection

        async def callback(self, interaction: discord.Interaction ):
                #al dar click, revisar si ya voto
                if user_has_already_picked(user=user_to_string(interaction.user), prediction_id=self.prediction_id):
                    await interaction.response.send_message(content=f'Tu voto ya no se puede alterar.', ephemeral=True)
                else:
                    #    si no crear una entrada con su respuesta en la db
                    pick = create_users_prediction_pick(pick=self.selection, prediction_id=self.prediction_id, user=user_to_string(interaction.user))
                    create_prediction_entry_transaction(
                        transaction_type=f'prediction_entry_{str(self.prediction_id)}', 
                        amount=-self.entry_cost, 
                        sent_by=user_to_string(ctx=interaction.guild.owner), 
                        received_by=user_to_string(ctx=interaction.user)
                    )
                    
                    #    si ya tiene, mandar un mensaje diciendo que ya voto y por quien
                    await interaction.response.send_message(content=f'Votaste por {self.emoji} {self.label}', ephemeral=True)

class ApproveView(discord.ui.View):
    def __init__(self, ctx, command, division=None, tier=None, play=None):
        super().__init__(
            timeout=None
        )

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
                    label=f'Comprar por {self.items.data[move_forward(self.items.data, self.paginator.current_page)]["price"]} Clan Coins.',
                    emoji=clancoin_emote,
                    row=1,
                    store_item=self.items.data[move_forward(self.items.data, self.paginator.current_page)])
            )
            self.interaction_buttons.add_item(CancelButton())
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
        self.buy_button = BuyButton(index=move_forward(self.items.data, self.index ), user=self.user, emoji=clancoin_emote , label=f'Comprar por {self.items.data[index]["price"]} Clan Coins.', store_item=self.items.data[self.index], row=1)
        cancel_button = CancelButton()
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
                        insert_item_buy(sent_by=user_to_string(interaction.guild.owner), received_by=user_to_string(interaction), amount=-self.store_item['price'], transaction_type=transaction_name) 
                        await interaction.user.send(f"Tu codigo para masterclass es {self.store_item['code']}")
                        await interaction.response.edit_message(content=f'Compraste {self.store_item["name"]}.', view=None, embed=embed)
                    else:
                        await interaction.response.edit_message(content="Nos hemos quedado sin codigos, por favor vuelve a intentarlo despues.", view=None, embed=None)
                        await interaction.guild.owner.send(f'Nos hemos quedado el codigo {self.store_item["code"]} para {self.store_item["name"]}, considera añadir mas unidades o crear un nuevo objeto.')
                else:
                    
                    # await interaction.response.send_message()
                    transaction_name = f"buy_item_{str(self.store_item['id'])}"
                    insert_item_buy(sent_by=user_to_string(interaction.guild.owner), received_by=self.user, amount=-self.store_item['price'], transaction_type=transaction_name)
                    await interaction.response.edit_message(content=f'Compraste {self.store_item["name"]}', view=None, embed=None)
                    await interaction.followup.send(content=f"<@{interaction.user.id}> compró {self.store_item['name']}. En un momento <@{interaction.guild.owner_id}> se contactará para entregar el premio.")

class CancelButton(discord.ui.Button):
        def __init__(
            self,
        ):
            super().__init__(
                emoji="✖️",
                style=discord.ButtonStyle.red,
                disabled=False,
                custom_id=None,
                row=1,
                label="Cancelar"
            )

        async def callback(self, interaction):
            await interaction.response.edit_message(content="Hasta luego 👋.", view=None, embed=None)

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