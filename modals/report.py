import os

import disnake
from disnake.ext import commands

disnake.Embed.set_default_color(disnake.Color.blurple())


class Report(disnake.ui.modal.Modal):
    def __init__(
            self, bot: commands.InteractionBot,
            file: disnake.Attachment,
            db, inter: disnake.CommandInter
    ):
        self.bot = bot
        self.file = file
        self.db = db.db
        with db.db(inter.author.id) as d:
            n = d.json['mc_name']

        super().__init__(title="Отправить жалобу", components=[
            disnake.ui.TextInput(
                label="Твой ник",
                custom_id="my_name",
                value=n,
                required=True,
                max_length=100
            ),
            disnake.ui.TextInput(
                label="Ник нарушителя",
                custom_id="bad_name",
                required=True,
                max_length=100
            ),
            disnake.ui.TextInput(
                label="Какое правило нарушил",
                custom_id="rule",
                required=True,
                max_length=100
            )
        ])

    async def callback(self, inter: disnake.ModalInteraction, /) -> None:
        await inter.response.defer(ephemeral=True)
        await self.file.save(f"tmp/{inter.id}.png")
        with self.db(inter.author.id) as d:
            d.json['mc_name'] = inter.text_values['my_name']

        cnl = self.bot.get_channel(928203029554008145)

        msg = await cnl.send(embed=disnake.Embed(
            title="Жалоба от " + inter.text_values['my_name'],
            description=f"На **{inter.text_values['bad_name']}**\nПричина: **{inter.text_values['rule']}**"
        ).set_author(
            icon_url=inter.author.avatar.url,
            name=inter.author
            ).set_image(file=disnake.File(f"tmp/{inter.id}.png"))
        )

        thread = await msg.create_thread(name="Жалоба от " + inter.text_values['my_name'])

        view = disnake.ui.View()
        view.add_item(disnake.ui.Button(
            style=disnake.ButtonStyle.url,
            label="Перейти к сообщению",
            url=msg.jump_url
        ))

        view.add_item(disnake.ui.Button(
            style=disnake.ButtonStyle.url,
            label="Перейти к ветке",
            url=thread.jump_url
        ))

        await inter.send("Предложение отправлено", view=view, ephemeral=True)
        os.remove(f"tmp/{inter.id}.png")
