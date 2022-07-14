import disnake
from disnake.ext import commands

disnake.Embed.set_default_color(disnake.Color.blurple())


class Clan(disnake.ui.modal.Modal):
    def __init__(self, bot: commands.InteractionBot):
        self.bot = bot
        super().__init__(title="Рассказать о клане", components=[
            disnake.ui.TextInput(
                label="Название и тег",
                custom_id="name",
                required=True,
                max_length=15
            ),
            disnake.ui.TextInput(
                label="Когда был создан",
                custom_id="date",
                required=True,
                max_length=25,
            ),
            disnake.ui.TextInput(
                label="Основное занятие",
                custom_id="do",
                required=True,
                max_length=50,
            ),
            disnake.ui.TextInput(
                label="Есть база клана?",
                custom_id="base",
                required=True,
                max_length=3,
                min_length=2,
                placeholder='Да/Нет'
            ),
            disnake.ui.TextInput(
                label="Набираете ли учасников?",
                custom_id="find",
                required=True,
                max_length=3,
                min_length=2,
                placeholder='Да/Нет'
            )
        ])

    async def callback(self, inter: disnake.ModalInteraction, /) -> None:
        cnl = self.bot.get_channel(996703770530566214)

        msg = await cnl.send(
            embed=disnake.Embed(
                title=inter.text_values['name'],
                description=(
                    'База есть' if inter.text_values['base']
                    else 'Базы нету'
                ) + '\n' + (
                    'Ищут участников' if inter.text_values['find']
                    else 'Набора на участников нету'
                )
            ).set_author(
                icon_url=inter.author.avatar.url,
                name=inter.author
            ).add_field(
                name='Название и тег',
                value=f"{inter.text_values['name']}"
            ).add_field(
                name='Создан', value=inter.text_values['date']
            ).add_field(
                name='Основное занятие', value=inter.text_values['do']
            )
        )

        thread = await msg.create_thread(name=inter.text_values['name'])

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

        await inter.send("Инфа о клане отправлена", view=view, ephemeral=True)
