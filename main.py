import os
import random

import disnake
from disnake.ext import commands

import db
import time
from modals.clan import Clan
from modals.report import Report
from modals.suggest import Suggest
from json import dumps as tostr

bot = commands.InteractionBot(test_guilds=[927860273388343306], intents=disnake.Intents.all())
disnake.Embed.set_default_color(disnake.Color.blurple())


async def check_file(
        inter: disnake.CommandInter,
        file: disnake.Attachment = None
):
    if not file: return
    if file.size >= (1024 ** 3) * 8:
        return await inter.send('Скриншот слишком большой', ephemeral=True) or True
    if not file.filename.endswith('.png'):
        return await inter.send('Поддерживается только .png', ephemeral=True) or True


def profile_embed(user: disnake.User):
    emb = disnake.Embed(color=user.accent_color or user.color or disnake.Color.blurple())

    try:
        emb.set_image(file=disnake.File(f'image_db/{user.id}.png'))
    except:
        pass

    with db.db(user.id) as d:
        data = d.json

    if data['bio']:
        emb.add_field('О себе', data['bio'], inline=False)

    if data['name']:
        emb.add_field('Имя', data['name'], inline=True)

    if data['age']:
        emb.add_field('Возраст', data['age'], inline=True)

    if data['gender']:
        emb.add_field('Пол', data['gender'], inline=True)

    emb.add_field('В руках', data['bal'], inline=True)
    emb.add_field('В банке', data['dep'], inline=True)
    emb.add_field('Уровень', f"{data['lvl']} [{data['xp']}/{(data['lvl'] * 200) or 100}]", inline=True)

    emb.set_author(name=user, icon_url=user.display_avatar.url)

    return emb


from modals.profile_edit import PEdit


@bot.event
async def on_message(msg: disnake.Message):
    if (
            msg.guild is None or
            msg.author.bot
    ):
        return

    with db.db(msg.author.id) as d:
        d.json['msg_amt'] += 1
        if time.time() > d.json['last_msg'] + 15:
            d.json['last_msg'] = time.time()
            d.json['xp'] += 1
            d.json['bal'] += random.randint(1, 5)
            if d.json['xp'] >= d.json['lvl'] * 200:
                d.json['xp'] -= d.json['lvl'] * 200
                d.json['lvl'] += 1
                d.json['bal'] += random.randint(5, 10)
                await bot.get_channel(940884092386430986).send(
                    f'У {msg.author.mention} {d.json["lvl"]} уровень :tada:',
                    allowed_mentions=disnake.AllowedMentions(users=[])
                )


@bot.event
async def on_ready():
    print('Ready')
    await bot.change_presence(activity=disnake.Activity(
        name='мурчание котиков', type=disnake.ActivityType.listening
    ))


@bot.slash_command(description='Отправить предложение')
async def suggest(inter: disnake.CommandInter):
    await inter.response.send_modal(Suggest(bot))


@bot.slash_command(description="Жалоба на майнкрафт игрока")
async def report(
        inter: disnake.CommandInter,
        file: disnake.Attachment
):
    await inter.response.send_modal(Report(bot, file, db, inter))


@bot.slash_command(description='Рассказать о своём клане')
async def clan(inter: disnake.CommandInter):
    await inter.response.send_modal(Clan(bot))


@bot.slash_command(description='')
async def profile(_): pass


@profile.sub_command(description="Посмотреть профиль")
async def show(
        inter: disnake.CommandInter,
        user: disnake.User = None
):
    user = user or inter.author
    if user.bot:
        return await inter.send('У ботяр нету профилей', ephemeral=True)

    await inter.send(embed=profile_embed(user))


@profile.sub_command(description='Редактировать свой профиль')
async def edit(
        inter: disnake.CommandInter,
        banner: disnake.Attachment = None
):
    if await check_file(inter, banner):
        return

    if banner:
        await inter.response.defer()
        await banner.save(f"image_db/{inter.author.id}.png")
        await inter.edit_original_message(embed=profile_embed(inter.author))
    else:
        await inter.response.send_modal(PEdit(bot, inter.author.id))


@bot.slash_command()
async def top(
        inter: disnake.CommandInter,
        criteria: str = commands.param(choices={
            'Войс': 'voice',
            'Сообщения': 'msg_amt',
            'Уровень': 'lvl',
            'Монеты': 'bal'
        })
):
    users = [
                int(id.split('.')[0])
                for id in os.listdir('db/')
                if 'server' not in id
            ][:25]

    def sort(id):
        with db.db(id) as user:
            match criteria:
                case 'voice':
                    return user.json['voice']
                case 'msg_amt':
                    return user.json['msg_amt']
                case 'lvl':
                    tmp = user.json['xp']
                    for x in range(user.json['lvl'] - 1):
                        x += 1
                        tmp += x * 200

                    return tmp
                case 'bal':
                    return user.json['bal'] + user.json['dep']

    def show_data(id):
        with db.db(id) as user:
            match criteria:
                case 'voice':
                    def r(i):
                        return int(str(i).split('.')[0])

                    total = user.json['voice']

                    hour = r(total / 3600)
                    sec = total % 3600
                    minutes = r(sec / 60)
                    seconds = sec % 60
                    return f'{hour} час.  {minutes} мин.  {seconds} сек.'
                case 'msg_amt':
                    return str(user.json['msg_amt']) + ' сообщений'
                case 'lvl':
                    return f"{user.json['lvl']} [{user.json['xp']}/{(user.json['lvl'] * 200) or 100}]"
                case 'bal':
                    return f'''{user.json['bal']} в руках
{user.json['dep']} в банке
{user.json['bal'] + user.json['dep']} всего'''

    users = [u for u in users if sort(u)]
    users.sort(key=sort, reverse=True)
    c = {
        'voice': 'сиденью в войсе',
        'msg_amt': 'сообщениям',
        'lvl': 'уровню',
        'bal': 'балансу'
    }
    emb = disnake.Embed(title=f'Топ по {c[criteria]}')

    for x in range(len(users)):
        emb.add_field(
            name=f'{x + 1}. {bot.get_user(users[x])}',
            value=show_data(users[x]), inline=True
        )

    await inter.send(embed=emb)


@bot.slash_command(description='Вложить деньги в банк')
async def deposit(
        inter: disnake.CommandInter,
        amount: int = commands.param(
            min_value=1,
            default=None
        )
):
    with db.db(inter.author.id) as d:
        if amount is None:
            amount = d.json['bal']

        if amount > d.json['bal']:
            return await inter.send(f'У тебя слишком мало денег ({d.json["bal"]} / {amount})', ephemeral=True)

        d.json['dep'] += amount
        d.json['bal'] -= amount

        await inter.send(f'Ты положил {amount} монет в банк', ephemeral=True)


@bot.slash_command(description='Вытащить деньги из банка')
async def withdraw(
        inter: disnake.CommandInter,
        amount: int = commands.param(
            min_value=1,
            default=None
        )
):
    with db.db(inter.author.id) as d:
        if amount is None:
            amount = d.json['dep']

        if amount > d.json['dep']:
            return await inter.send(f'У тебя слишком мало денег в банке ({d.json["dep"]} / {amount})', ephemeral=True)

        d.json['bal'] += amount
        d.json['dep'] -= amount

        await inter.send(f'Ты вытащил {amount} монет из банка', ephemeral=True)


@bot.slash_command(
    description='Изменить баланс',
    default_permission=False,
    name='set-money'
)
async def set_money(
        inter: disnake.CommandInter,
        user: disnake.User,
        amount: int,
        action: str = commands.param(
            choices={
                'Добавить': '+',
                'Забрать': '-'
            }, default=None
        )
):
    with db.ServerData() as d:
        d.json['audit'].append({
            'user': inter.author.id,
            'action': db.Const.audit_change_bal,
            'target': user.id,
            'value': (action or '=') + ' ' + str(amount),
            'timestamp': time.time()
        })

    with db.db(user.id) as d:
        match action:
            case '+':
                d.json['bal'] += amount
            case '-':
                d.json['bal'] -= amount
            case None:
                d.json['bal'] = amount

        await inter.send(
            f'Теперь у {user.mention} {d.json["bal"]} монет',
            allowed_mentions=disnake.AllowedMentions(users=[])
        )


@bot.slash_command(
    description='Просмотр действий',
    default_permission=False
)
async def audit(
        inter: disnake.CommandInter,
        admin: disnake.User = None,
        target: disnake.User = None,
        action: str = commands.param(
            choices={
                'Изменение кол-ва монет': '0',
                'Создание предмета': '1',
                'Удаление предмета': '2',
                'Изменение предмета': '3',
                'Передача денег': '4',
                'Воровство': '5'
            }, default=None
        )
):
    acts = [
                'Изменение кол-ва монет',
                'Создание предмета',
                'Удаление предмета',
                'Изменение предмета',
                'Передача денег',
                'Воровство'
            ]
    data = []

    with db.ServerData() as d:
        unsorted = d.json['audit']

    if action:
        action = int(action)

    if admin:
        admin = admin.id

    if target:
        target = target.id

    for x in unsorted:
        if (x['action'] == action or action is None) and \
                (x['user'] == admin or admin is None) and \
                (x['target'] == target or target is None):
            data.append(x)
    data = data[:25]
    emb = disnake.Embed()
    for x in data:
        emb.add_field(
            name='‌',
            value=(
                f'Админ: <@{x["user"]}>\n'
                f'Действие: {acts[int(x["action"])]}\n'
                f'Юзер: <@{x["target"]}>\n'
                f'Время: <t:{round(x["timestamp"])}:R>'
            ), inline=True
        )
    await inter.send(embed=emb)



bot.run(open('token.txt').read())
