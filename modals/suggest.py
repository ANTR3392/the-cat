import disnake
from disnake.ext import commands

disnake.Embed.set_default_color(disnake.Color.blurple())


class Suggest(disnake.ui.modal.Modal):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot
        super().__init__(title="Отправить предложение", components=[
            disnake.ui.TextInput(
                label="Заголовок",
                custom_id="title",
                required=True,
                max_length=100
            ),
            disnake.ui.TextInput(
                label="Описание",
                custom_id="text",
                required=True,
                max_length=4000,
                style=disnake.TextInputStyle.paragraph
            )
        ])

    async def callback(self, inter: disnake.ModalInteraction, /) -> None:
        cnl = self.bot.get_channel(927943232829145129)

        msg = await cnl.send(embed=disnake.Embed(
            title=inter.text_values['title'],
            description=inter.text_values['text']
        ).set_author(
            icon_url=inter.author.avatar.url,
            name=inter.author
            )
        )

        thread = await msg.create_thread(name=inter.text_values['title'])

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
