import re
import discord
import sqlite3

client = discord.Client()

commands = {}
settings = {}


def run():
    load_db()
    client.run(settings['token'])


@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
async def on_member_join(member):
    await client.send_message(
        client.get_channel(settings['main_ch']),
        (settings['greeting']).format(member.mention))


@client.event
async def on_message(message):
    if message.author.name == 'MiEIBot':
        return
    for expression in commands:
        if expression.search(message.content):
            await commands[expression](message)


def load_db():
    populate_settings()
    populate_parser_data()


def populate_settings():
    db_connnection = sqlite3.connect('discord.db')
    db_cursor = db_connnection.cursor()
    db_cursor.execute(
        'SELECT name, value'
        ' FROM Settings')
    for row in db_cursor.fetchall():
        settings[row[0]] = row[1]
    db_connnection.close()


def populate_parser_data():
    db_connnection = sqlite3.connect('discord.db')
    db_cursor = db_connnection.cursor()
    db_cursor.execute(
        'SELECT Expressions.regex, Expressions.message, Embeds.url'
        ' FROM Expressions'
        ' LEFT JOIN Embeds ON Expressions.embed_name = Embeds.name')

    for row in db_cursor.fetchall():
        if row[2] is None and row[1] is not None:
            commands[re.compile(row[0])] = lambda message, text=row[1]: client.send_message(message.channel, text)
        elif row[1] is None and row[2] is not None:
            embed = discord.Embed()
            embed.set_image(url=row[2])
            commands[re.compile(row[0])] = lambda message, embed=embed: client.send_message(message.channel,
                                                                                            embed=embed)
        else:
            raise ("Invalid row: " + str(row))
    db_connnection.close()
