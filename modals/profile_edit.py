import os
from __main__ import profile_embed, db

import disnake
from disnake.ext import commands

disnake.Embed.set_default_color(disnake.Color.blurple())


class PEdit(disnake.ui.modal.Modal):
    def __init__(self, bot: commands.InteractionBot, id):
        with db.db(id) as d:
            data = d.json

        self.bot = bot

        super().__init__(
            title="Редактирование профиля",
            components=[
                disnake.ui.TextInput(
                    custom_id='name',
                    value=data['name'],
                    label='Имя',
                    required=False,
                    max_length=15
                ),

                disnake.ui.TextInput(
                    custom_id='age',
                    value=data['age'],
                    label='Возраст',
                    required=False,
                    max_length=2
                ),

                disnake.ui.TextInput(
                    custom_id='gender',
                    value=data['gender'],
                    label='Пол',
                    required=False,
                    max_length=25,
                ),

                disnake.ui.TextInput(
                    custom_id='bio',
                    value=data['bio'],
                    label='О себе',
                    required=False,
                    max_length=1024,
                    style=disnake.TextInputStyle.paragraph
                )
            ]
        )

    async def callback(self, inter: disnake.ModalInteraction) -> None:
        with db.db(inter.author.id) as d:
            d.json = {**d.json, **inter.text_values}
            try:
                d.json['age'] = int(d.json['age'])
            except:
                d.json['age'] = ''

        await inter.send(embed=profile_embed(inter.author))
