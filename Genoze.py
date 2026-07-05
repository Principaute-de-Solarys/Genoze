#   Copyright 2026 Timoh5709 (Timoh de Solarys)
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

import os
import discord
import json
import datetime
from discord import app_commands, ui
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions
from dateutil import tz
from random import randint

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

admin_list = []
ban_list = []
messages_list = []
server_bans = {}
channel_list = {}

facts = []
curFact = -1

bot_id = 1479885378985918515

thumbsup = "\N{THUMBS UP SIGN}"
lol = "😂"

async def send_log(log: str):
    user = await bot.fetch_user(781224979919274014)
    await user.send(log)

class Report(ui.Modal, title="Formulaire de signalement Genoze"):
    report = ui.TextInput(label="Signalement", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        message_id = int(self.custom_id)
        message_idx = 0
        for i in range(len(messages_list)):
            if await check_member_of(message_id, messages_list[i]["messages_published"]):
                message_idx = i
                break
        
        server = await bot.fetch_guild(messages_list[i]["servers_published"][0])
        channel = await server.fetch_channel(channel_list[server.id])
        msg = await channel.fetch_message(messages_list[i]["messages_published"][0])

        message = f"# Un nouveau signalement a été fait :\n> Lien vers le message signalé : {msg.jump_url}\n> Personne à l'origine du signalement : {interaction.user.name} ({interaction.user.id})\n> Contenu du signalement : {self.report}"

        Timoh = await bot.fetch_user(781224979919274014)
        await Timoh.send(content=message, embed=msg.embeds[0])

        await interaction.response.send_message(content="Votre signalement a bien été envoyé !", ephemeral=True)

class ReportBtn(discord.ui.View):
    @discord.ui.button(label="Signaler", style=discord.ButtonStyle.red)
    async def report(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Report(custom_id=str(interaction.message.id)))

async def check_member_of(user_id: int, list: list):
    if user_id in list:
        return True
    else:
        return False

@bot.event
async def on_ready():
    global server_bans, messages_list, facts
    await bot.tree.sync()

    f = open("admin_list.txt", "r")
    for ligne in f.readlines():
        admin_list.append(int(ligne))
    f.close()

    g = open("channels.txt", "r")
    g_list = g.readlines()
    g.close()

    for i in g_list:
        k, v = i.split("/")
        channel_list[int(k)] = int(v)

    h = open("ban_list.txt", "r")
    for ligne in h.readlines():
        ban_list.append(int(ligne))
    h.close()

    i = open("server_bans.json", "r")
    server_bans = json.loads(i.read())
    i.close()

    j = open("messages.json", "r")
    messages_list = json.loads(j.read())
    j.close()
    
    k = open("facts.txt", "r", encoding="UTF-8")
    facts = k.readlines()
    k.close()

    update_status.start()

    print(f'Bot connecté en tant que {bot.user}')
    print("Commandes slash synchronisées.")

@tasks.loop(minutes=5)
async def update_status():
    global curFact
    randomFact = randint(0, len(facts) - 1)
    while randomFact == curFact:
        randomFact = randint(0, len(facts) - 1)
    curFact = randomFact
    
    await bot.change_presence(status=discord.Status.online, activity=discord.Activity(type=discord.ActivityType.watching, name=facts[curFact]))

@bot.tree.command(name="ping", description="Pong !")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("PONG !")

@bot.tree.command(name="help", description="Tu veux de l'aide avec Genoze ?")
async def help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Aide pour Genoze",
        description="-# [ADMIN GENOZE] : Il s'agit d'une commande que seuls les administrateurs Genoze peuvent utiliser.\n-# [ADMIN SERV] : Il ss'agit d'une commande réservée aux administrateurs des serveurs.\n\nVoici la liste des commandes disponibles :",
        color=discord.Color.from_rgb(7, 106, 68)
    )
   
    embed.add_field(name="/help", value="Vous donne ce message.", inline=False)
    embed.add_field(name="/ping", value="Permet de tester la présence du bot.", inline=False)
    embed.add_field(name="/add_bot", value="Vous donne un lien permettant d'ajouter Genoze sur votre serveur. Il vous faudra un administrateur de Genoze pour installer le bot.", inline=False)
    embed.add_field(name="[ADMIN GENOZE] /register_channel (channel:[Salon à enregistrer])", value="Enregistre un salon Genoze.", inline=False)
    embed.add_field(name="[ADMIN GENOZE] /unregister_channel", value="Supprime un salon Genoze.", inline=False)
    embed.add_field(name="[ADMIN GENOZE] /ban user:[L'utilisateur à bannir]", value="Bannit un utilisateur de Genoze.", inline=False)
    embed.add_field(name="[ADMIN GENOZE] /unban user:[L'utilisateur à débannir]", value="Débannit un utilisateur de Genoze.", inline=False)
    embed.add_field(name="[ADMIN GENOZE] /op user:[L'utilisateur à rendre administrateur]", value="Rend un utilisateur administrateur.", inline=False)
    embed.add_field(name="[ADMIN GENOZE] /deop user:[L'utilisateur à dérank]", value="Enlève le rang d'administrateur à un utilisateur.", inline=False)
    embed.add_field(name="[ADMIN GENOZE] /delete_message message_id:[L'identifiant du message à supprimer]", value="Supprime un message.", inline=False)
    embed.add_field(name="[ADMIN SERV] /guild_ban user:[L'utilisateur à bannir]", value="Bannit localement un utilisateur.", inline=False)
    embed.add_field(name="[ADMIN SERV] /guild_unban user:[L'utilisateur à débannir]", value="Débannit un utilisateur banni localement.", inline=False)
   
    embed.set_footer(text="Version : 0.1.1\nSi vous voulez contribuer au développement de Genoze, contactez Timoh de Solarys.")
   
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="add_bot", description="Obtiens un lien pour ajouter Genoze. Contacter un admin Genoze !")
async def add_bot(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Ajoute Genoze",
        description="Clique sur le lien ci-dessous pour ajouter le bot à ton serveur Discord.",
        color=discord.Color.from_rgb(7, 106, 68)
    )
    embed.add_field(
        name="Lien d'invitation",
        value="[Ajouter Genoze](https://discord.com/oauth2/authorize?client_id=1479885378985918515)",
        inline=False
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="register_channel", description="[ADMIN GENOZE] Enregistre un salon Genoze.")
@has_permissions(administrator=True)
@app_commands.describe(channel="Le salon à enregistrer.")
async def register_channel(interaction: discord.Interaction, channel: discord.TextChannel = None):
    if not await check_member_of(interaction.user.id, admin_list):
        await interaction.response.send_message("Seul un administrateur Genoze peut exécuter cette commande.", ephemeral=True)
        return

    await interaction.response.send_message("Enregistre le salon...")

    if channel == None:
        channel = interaction.channel

    for k, v in channel_list.items():
        if k == interaction.guild_id:
            registered_channel = await interaction.guild.fetch_channel(channel_list[interaction.guild_id])
            await interaction.edit_original_response(content=f"Le serveur a déjà un salon enregistré : {registered_channel.jump_url}, un serveur ne peut pas avoir plus d'un salon enregistré. Si vous voulez changer de salon, faites `/unregister_channel`.")
            return

    channel_list[interaction.guild_id] = channel.id

    f = open("channels.txt", "a")
    f.write(f"{interaction.guild_id}/{channel.id}\n")
    f.close()

    await interaction.edit_original_response(content=f"Le salon {channel.jump_url} a bien été enregistré comme salon Genoze pour le serveur {interaction.guild.name}.")

@bot.tree.command(name="unregister_channel", description="[ADMIN GENOZE] Supprime un salon Genoze.")
@has_permissions(administrator=True)
async def unregister_channel(interaction: discord.Interaction):
    if not await check_member_of(interaction.user.id, admin_list):
        await interaction.response.send_message("Seul un administrateur Genoze peut exécuter cette commande.", ephemeral=True)
        return

    await interaction.response.send_message("Supprime le salon de la liste...")

    for k, v in channel_list.items():
        if k == interaction.guild_id:
            registered_channel = await interaction.guild.fetch_channel(channel_list[interaction.guild_id])
            del channel_list[k]
            f = open("channels.txt", "w")
            for k, v in channel_list.items():
                f.write(f"{k}/{v}\n")
            f.close
            await interaction.edit_original_response(content=f"Le salon enregistré ({registered_channel.jump_url}) a bien été supprimé de la liste de Genoze.")
            return
    
    await interaction.edit_original_response(content=f"Aucun salon Genoze n'a été enregistré pour ce serveur.")

@bot.tree.command(name="ban", description="[ADMIN GENOZE] Bannit un utilisateur.")
@has_permissions(administrator=True)
@app_commands.describe(user="L'utilisateur à bannir.")
async def ban(interaction: discord.Interaction, user: discord.User):
    if not await check_member_of(interaction.user.id, admin_list):
        await interaction.response.send_message("Seul un administrateur Genoze peut exécuter cette commande.", ephemeral=True)
        return
    
    if interaction.user == user:
        await interaction.response.send_message("Vous ne pouvez pas vous bannir.")
        return
    
    await interaction.response.send_message(f"Bannit l'utilisateur {user.global_name} de Genoze...")

    if await check_member_of(user.id, ban_list):
        await interaction.edit_original_response(content=f"{user.global_name} est déjà banni.e.")
        return
    
    ban_list.append(user.id)

    f = open("ban_list.txt", "a")
    f.write(f"{user.id}\n")
    f.close()

    await interaction.edit_original_response(content=f"{user.global_name} est désormais banni.e.")

@bot.tree.command(name="unban", description="[ADMIN GENOZE] Débannit un utilisateur.")
@has_permissions(administrator=True)
@app_commands.describe(user="L'utilisateur à débannir.")
async def unban(interaction: discord.Interaction, user: discord.User):
    if not await check_member_of(interaction.user.id, admin_list):
        await interaction.response.send_message("Seul un administrateur Genoze peut exécuter cette commande.", ephemeral=True)
        return
    
    await interaction.response.send_message(f"Débannit l'utilisateur {user.global_name} de Genoze...")

    if not await check_member_of(user.id, ban_list):
        await interaction.edit_original_response(content=f"{user.global_name} n'est pas banni.e.")
        return
    
    for i in range(len(ban_list)):
        if ban_list[i] == user.id:
            ban_list.pop(i)
            break

    f = open("ban_list.txt", "w")
    for v in ban_list:
        f.write(f"{v}\n")
    f.close()

    await interaction.edit_original_response(content=f"{user.global_name} est désormais débanni.e.")

@bot.tree.command(name="op", description="[ADMIN GENOZE] Rend un utilisateur administrateur.")
@has_permissions(administrator=True)
@app_commands.describe(user="L'utilisateur à rendre administrateur.")
async def op(interaction: discord.Interaction, user: discord.User):
    if not await check_member_of(interaction.user.id, admin_list):
        await interaction.response.send_message("Seul un administrateur Genoze peut exécuter cette commande.", ephemeral=True)
        return
    
    await interaction.response.send_message(f"Rend l'utilisateur {user.global_name} administrateur de Genoze...")

    if await check_member_of(user.id, admin_list):
        await interaction.edit_original_response(content=f"{user.global_name} est déjà administrateur.rice.")
        return
    
    admin_list.append(user.id)

    f = open("admin_list.txt", "a")
    f.write(f"{user.id}\n")
    f.close()

    await interaction.edit_original_response(content=f"{user.global_name} est désormais administrateur.rice.")

@bot.tree.command(name="deop", description="[ADMIN GENOZE] Enlève le rang d'administrateur à un utilisateur.")
@has_permissions(administrator=True)
@app_commands.describe(user="L'utilisateur à dérank.")
async def deop(interaction: discord.Interaction, user: discord.User):
    if not await check_member_of(interaction.user.id, admin_list):
        await interaction.response.send_message("Seul un administrateur Genoze peut exécuter cette commande.", ephemeral=True)
        return
    
    if interaction.user == user:
        await interaction.response.send_message("Vous ne pouvez pas vous dérank.")
        return

    await interaction.response.send_message(f"Dérank l'utilisateur {user.global_name} de Genoze...")

    if not await check_member_of(user.id, admin_list):
        await interaction.edit_original_response(content=f"{user.global_name} n'est pas administrateur.rice.")
        return
    
    for i in range(len(admin_list)):
        if admin_list[i] == user.id:
            admin_list.pop(i)
            break

    f = open("admin_list.txt", "w")
    for v in admin_list:
        f.write(f"{v}\n")
    f.close()

    await interaction.edit_original_response(content=f"{user.global_name} n'est désormais plus administrateur.rice.")

@bot.tree.command(name="delete_message", description="[ADMIN GENOZE] Supprime un message Genoze.")
@has_permissions(administrator=True)
@app_commands.describe(message_id="Le message à supprimer.")
async def delete_message(interaction: discord.Interaction, message_id: str):
    mid = int(message_id)

    if not await check_member_of(interaction.user.id, admin_list):
        await interaction.response.send_message("Seul un administrateur Genoze peut exécuter cette commande.", ephemeral=True)
        return
    
    await interaction.response.send_message("Supprime le message...")
    
    message = await interaction.channel.fetch_message(mid)
    if type(message) == discord.Message:
        if message.author.id == bot_id:
            if len(message.embeds) == 1 and message.embeds[0].author.name == "Genoze":
                message_idx = 0
                for i in range(len(messages_list)):
                    if await check_member_of(mid, messages_list[i]["messages_published"]):
                        message_idx = i
                        break
                
                for i in range(len(messages_list[message_idx]["servers_published"])):
                    server_id = messages_list[message_idx]["servers_published"][i]
                    channel_id = channel_list[server_id]
                    server = await bot.fetch_guild(server_id)
                    channel = await server.fetch_channel(channel_id)
                    bot_message = await channel.fetch_message(messages_list[message_idx]["messages_published"][i])
                    await bot_message.delete()

                messages_list.pop(message_idx)

                f = open("messages.json", "w")
                f.write(json.dumps(messages_list))
                f.close()

                await interaction.edit_original_response(content="Le message a été supprimé.")

@bot.tree.command(name="guild_ban", description="[ADMIN SERV] Bannit localement un utilisateur.")
@has_permissions(administrator=True)
@app_commands.describe(user="L'utilisateur à bannir.")
async def guild_ban(interaction: discord.Interaction, user: discord.User):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("Seul une personne ayant les permissions de bannir quelqu'un peut utiliser cette commande.", ephemeral=True)
        return

    if interaction.user == user:
        await interaction.response.send_message("Vous ne pouvez pas vous bannir.")
        return
    
    await interaction.response.send_message(f"Bannit l'utilisateur {user.global_name} du serveur...")

    if await check_member_of(str(user.id), server_bans.keys()):
        if await check_member_of(interaction.guild.id, server_bans[str(user.id)]):
            await interaction.edit_original_response(content=f"{user.global_name} est déjà banni.e ici.")
            return
        server_bans[str(user.id)].append(interaction.guild.id)
    else:
        server_bans[str(user.id)] = [interaction.guild.id]

    json_str = json.dumps(server_bans)

    f = open("server_bans.json", "w")
    f.write(json_str)
    f.close()

    await interaction.edit_original_response(content=f"{user.global_name} est désormais banni.e ici.")

@bot.tree.command(name="guild_unban", description="[ADMIN SERV] Débannit un utilisateur banni localement.")
@has_permissions(administrator=True)
@app_commands.describe(user="L'utilisateur à débannir.")
async def guild_unban(interaction: discord.Interaction, user: discord.User):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("Seul une personne ayant les permissions de bannir quelqu'un peut utiliser cette commande.", ephemeral=True)
        return
    
    await interaction.response.send_message(f"Débannit l'utilisateur {user.global_name} du serveur...")

    if not await check_member_of(str(user.id), server_bans.keys()):
        await interaction.edit_original_response(content=f"{user.global_name} n'est pas banni.e.")
        return
    
    if not await check_member_of(interaction.guild.id, server_bans[str(user.id)]):
        await interaction.edit_original_response(content=f"{user.global_name} n'est pas banni.e.")
        return

    for i in range(len(server_bans[str(user.id)])):
        if server_bans[str(user.id)][i] == interaction.guild.id:
            server_bans[str(user.id)].pop(i)
            break

    if len(server_bans[str(user.id)]) == 0:
        server_bans.pop(str(user.id))

    json_str = json.dumps(server_bans)

    f = open("server_bans.json", "w")
    f.write(json_str)
    f.close()

    await interaction.edit_original_response(content=f"{user.global_name} est désormais débanni.e du serveur.")

@bot.event
async def on_message(message: discord.Message):
    if message.guild and not message.author.bot:
        if message.channel.id == channel_list.get(message.guild.id):
            if not await check_member_of(message.author.id, ban_list):
                message_data = {
                    "author_id": message.author.id,
                    "servers_published": [],
                    "messages_published": [],
                    "likes": 0,
                    "lol": 0
                }
                embed = discord.Embed(
                    title=message.author.display_name,
                    description=f"-# *{message.author.name} ({message.author.id})*\n---\n{message.content}",
                    color=discord.Color.from_rgb(7, 106, 68),
                    timestamp=datetime.datetime.now(tz.gettz("Europe/Paris"))
                )
                embed.set_author(
                    name="Genoze"
                )
                embed.set_footer(
                    text=message.guild.name,
                    icon_url=message.guild.icon.url
                )
                embed.set_thumbnail(url=message.author.avatar.url)
                if len(message.attachments) >= 1:
                    firstImage = False
                    for i in message.attachments:
                        if not firstImage and i.content_type.split("/")[0] == "image":
                            embed.set_image(url=i.url)
                            firstImage = True
                            continue
                        embed.add_field(name=i.title, value=i.url, inline=False)
                else:
                    await message.delete()
                embed.add_field(name="Likes", value="0", inline=True)
                embed.add_field(name="Lol", value="0", inline=True)
                needCheck = False
                if type(message.reference) is discord.MessageReference:
                    reply = message.reference.resolved
                    if reply.author.id == bot_id:
                        reply_msgs = reply.embeds[0].description.split("\n---\n")
                        reply_msg = reply_msgs[len(reply_msgs) - 1]
                        embed.description = f"-# *{message.author.name} ({message.author.id})*\n---\n{reply.embeds[0].title} (dans {reply.embeds[0].footer.text} à {reply.embeds[0].timestamp.strftime('%d/%m/%Y')}, {(reply.embeds[0].timestamp.hour + 2) % 24}:{reply.embeds[0].timestamp.minute}) : \"{reply_msg}\"\n---\n{message.content}"
                if await check_member_of(str(message.author.id), server_bans.keys()):
                    needCheck = True
                for server_id, channel_id in channel_list.items():
                    server = await bot.fetch_guild(server_id)
                    channel = await server.fetch_channel(channel_id)
                    if needCheck:
                        if await check_member_of(server_id, server_bans[str(message.author.id)]):
                            await message.author.send(content=f"Votre [message]({message.channel.jump_url}) n'a pas été transféré sur {server.name} car vous y êtes banni.e.")
                            continue
                    bot_message = await channel.send(embed=embed, view=ReportBtn())
                    await bot_message.add_reaction(thumbsup)
                    await bot_message.add_reaction(lol)
                    message_data["servers_published"].append(server_id)
                    message_data["messages_published"].append(bot_message.id)
                messages_list.append(message_data)

                f = open("messages.json", "w")
                f.write(json.dumps(messages_list))
                f.close()
            else:
                await message.author.send(content=f"Votre [message]({message.channel.jump_url}) n'a pas été transféré sur les autres serveurs car vous êtes banni.e.")
                await message.delete()
    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payLoad: discord.RawReactionActionEvent):
    if payLoad.user_id != bot_id:
        if str(payLoad.emoji) == thumbsup or str(payLoad.emoji) == lol:
            message_idx = 0
            for i in range(len(messages_list)):
                if await check_member_of(payLoad.message_id, messages_list[i]["messages_published"]):
                    message_idx = i
                    break

            server = await bot.fetch_guild(payLoad.guild_id)
            channel = await server.fetch_channel(payLoad.channel_id)
            msg = await channel.fetch_message(payLoad.message_id)
            embed = discord.Embed(
                title=msg.embeds[0].title,
                description=msg.embeds[0].description,
                color=discord.Color.from_rgb(7, 106, 68),
                timestamp=msg.embeds[0].timestamp
            )
            embed.set_author(name=msg.embeds[0].author.name)
            embed.set_footer(text=msg.embeds[0].footer.text, icon_url=msg.embeds[0].footer.icon_url)
            embed.set_thumbnail(url=msg.embeds[0].thumbnail.url)
            if len(msg.embeds[0].fields) - 2 > 0:
                for i in range(len(msg.embeds[0].fields) - 2):
                    embed.add_field(name=msg.embeds[0].fields[i].name, value=msg.embeds[0].fields[i].value, inline=False)
            prev_like = messages_list[message_idx]["likes"]
            prev_lol = messages_list[message_idx]["lol"]
            if str(payLoad.emoji) == thumbsup:
                embed.add_field(name="Likes", value=f"{prev_like + 1}", inline=True)
                messages_list[message_idx]["likes"] += 1
            else:
                embed.add_field(name="Likes", value=f"{prev_like}", inline=True)
            if str(payLoad.emoji) == lol:
                embed.add_field(name="Lol", value=f"{prev_lol + 1}", inline=True)
                messages_list[message_idx]["lol"] += 1
            else:
                embed.add_field(name="Lol", value=f"{prev_lol}", inline=True)
            await msg.edit(embed=embed)

            for i in range(len(messages_list[message_idx]["servers_published"])):
                server_id = messages_list[message_idx]["servers_published"][i]
                channel_id = channel_list[server_id]
                server = await bot.fetch_guild(server_id)
                channel = await server.fetch_channel(channel_id)
                bot_message = await channel.fetch_message(messages_list[message_idx]["messages_published"][i])
                await bot_message.edit(embed=embed)

            f = open("messages.json", "w")
            f.write(json.dumps(messages_list))
            f.close()

@bot.event
async def on_raw_reaction_remove(payLoad: discord.RawReactionActionEvent):
    if payLoad.user_id != bot_id:
        if str(payLoad.emoji) == thumbsup or str(payLoad.emoji) == lol:
            message_idx = 0
            for i in range(len(messages_list)):
                if await check_member_of(payLoad.message_id, messages_list[i]["messages_published"]):
                    message_idx = i
                    break

            server = await bot.fetch_guild(payLoad.guild_id)
            channel = await server.fetch_channel(payLoad.channel_id)
            msg = await channel.fetch_message(payLoad.message_id)
            embed = discord.Embed(
                title=msg.embeds[0].title,
                description=msg.embeds[0].description,
                color=discord.Color.from_rgb(7, 106, 68),
                timestamp=msg.embeds[0].timestamp
            )
            embed.set_author(name=msg.embeds[0].author.name)
            embed.set_footer(text=msg.embeds[0].footer.text, icon_url=msg.embeds[0].footer.icon_url)
            embed.set_thumbnail(url=msg.embeds[0].thumbnail.url)
            if len(msg.embeds[0].fields) - 2 > 0:
                for i in range(len(msg.embeds[0].fields) - 2):
                    embed.add_field(name=msg.embeds[0].fields[i].name, value=msg.embeds[0].fields[i].value, inline=False)
            prev_like = messages_list[message_idx]["likes"]
            prev_lol = messages_list[message_idx]["lol"]
            if str(payLoad.emoji) == thumbsup:
                embed.add_field(name="Likes", value=f"{prev_like - 1}", inline=True)
                messages_list[message_idx]["likes"] -= 1
            else:
                embed.add_field(name="Likes", value=f"{prev_like}", inline=True)
            if str(payLoad.emoji) == lol:
                embed.add_field(name="Lol", value=f"{prev_lol - 1}", inline=True)
                messages_list[message_idx]["lol"] -= 1
            else:
                embed.add_field(name="Lol", value=f"{prev_lol}", inline=True)
            await msg.edit(embed=embed)
            
            for i in range(len(messages_list[message_idx]["servers_published"])):
                server_id = messages_list[message_idx]["servers_published"][i]
                channel_id = channel_list[server_id]
                server = await bot.fetch_guild(server_id)
                channel = await server.fetch_channel(channel_id)
                bot_message = await channel.fetch_message(messages_list[message_idx]["messages_published"][i])
                await bot_message.edit(embed=embed)

            f = open("messages.json", "w")
            f.write(json.dumps(messages_list))
            f.close()

token = str(os.getenv("TWEET_TOKEN"))

bot.run(token)
