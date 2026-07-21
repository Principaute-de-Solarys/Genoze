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
import aiofiles
import validators
from discord import app_commands, ui
from discord.ext import commands, tasks
from dateutil import tz
from random import randint

intents = discord.Intents.default()
intents.messages = True
intents.reactions = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

admin_list = set()
ban_list = set()
messages_list = []
leaderboard = {}
server_bans = {}
channel_list = {}
custom_account_channel_list = {}
virtual_ids = {}
virtual_ids_idx = 9999999999999999999

facts = []
curFact = -1

bot_id = 1479885378985918515

thumbsup = "\N{THUMBS UP SIGN}"
lol = "😂"

class Report(ui.Modal, title="Formulaire de signalement Genoze"):
    report = ui.TextInput(label="Signalement", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        message_id = int(self.custom_id)
        message_idx = -1
        for i in range(len(messages_list)):
            if check_member_of(message_id, messages_list[i]["messages_published"]):
                message_idx = i
                break
        
        msg = None

        if message_idx < 0:
            await interaction.response.send_message(content="Une erreur est survenue lors du signalement.", ephemeral=True)
            return

        server = bot.get_guild(messages_list[message_idx]["servers_published"][0]) or await bot.fetch_guild(messages_list[message_idx]["servers_published"][0])
        channel = server.get_channel(channel_list[messages_list[message_idx]["servers_published"][0]]) or await server.fetch_channel(channel_list[messages_list[message_idx]["servers_published"][0]])
        msg = await channel.fetch_message(messages_list[message_idx]["messages_published"][0])

        message = f"# Un nouveau signalement a été fait :\n> Lien vers le message signalé : {msg.jump_url}\n> Personne à l'origine du signalement : {interaction.user.name} ({interaction.user.id})\n> Contenu du signalement : {self.report}"

        Timoh = bot.get_user(781224979919274014) or await bot.fetch_user(781224979919274014)
        await Timoh.send(content=message, embed=msg.embeds[0])

        await interaction.response.send_message(content="Votre signalement a bien été envoyé !", ephemeral=True)

class MessageBtns(discord.ui.View):
    @discord.ui.button(label="Signaler", style=discord.ButtonStyle.red)
    async def reportbtn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(Report(custom_id=str(interaction.message.id)))

    @discord.ui.button(label="Supprimer", style=discord.ButtonStyle.gray)
    async def deletebtn(self, interaction: discord.Interaction, button: discord.ui.Button):
        og_id = int(interaction.message.embeds[0].description.split("(")[1].split(")")[0])
        if interaction.user.id != og_id and not check_member_of(interaction.user.id, admin_list):
            if og_id > 9999999999999999999:
                og_id = str(og_id)
                pala = 0
                for uid in virtual_ids[og_id]["users"]:
                    if interaction.user.id != uid:
                        pala += 1

                if pala == len(virtual_ids[og_id]["users"]):
                    await interaction.response.send_message(content="Vous ne pouvez pas supprimer un message qui ne vous appartient pas.", ephemeral=True)
                    return
            else:
                await interaction.response.send_message(content="Vous ne pouvez pas supprimer un message qui ne vous appartient pas.", ephemeral=True)
                return
        
        await interaction.response.send_message(content="Supprime le message...", ephemeral=True)
    
        message_idx = -1
        for i in range(len(messages_list)):
            if check_member_of(interaction.message.id, messages_list[i]["messages_published"]):
                message_idx = i
                break

        if message_idx < 0:
            await interaction.response.send_message(content="Une erreur est survenue lors de la suppression.")
            return
        
        for i in range(len(messages_list[message_idx]["servers_published"])):
            server_id = messages_list[message_idx]["servers_published"][i]
            channel_id = channel_list[server_id]
            server = bot.get_guild(server_id) or await bot.fetch_guild(server_id)
            channel = server.get_channel(channel_id) or await server.fetch_channel(channel_id)
            bot_message = channel.get_partial_message(messages_list[message_idx]["messages_published"][i]) or await channel.fetch_message(messages_list[message_idx]["messages_published"][i])
            await bot_message.delete()

        messages_list.pop(message_idx)

        f = open("messages.json", "w")
        f.write(json.dumps(messages_list))
        f.close()

        await interaction.edit_original_response(content="Le message a été supprimé.")

def check_member_of(id: int, set: set):
    return id in set

@bot.event
async def on_ready():
    global server_bans, messages_list, facts, custom_account_channel_list, virtual_ids, virtual_ids_idx
    await bot.tree.sync()

    if os.path.exists("admin_list.txt"):
        async with aiofiles.open("admin_list.txt", "r", encoding="utf-8") as f:
            content = await f.read()
            for ligne in content.splitlines():
                if ligne.strip():
                    admin_list.add(int(ligne.strip()))

    if os.path.exists("channels.txt"):
        async with aiofiles.open("channels.txt", "r", encoding="utf-8") as f:
            content = await f.read()
            for i in content.splitlines():
                if "/" in i:
                    k, v = i.split("/")
                    channel_list[int(k)] = int(v)

    if os.path.exists("ban_list.txt"):
        async with aiofiles.open("ban_list.txt", "r", encoding="utf-8") as f:
            content = await f.read()
            for ligne in content.splitlines():
                if ligne.strip():
                    ban_list.add(int(ligne.strip()))

    if os.path.exists("server_bans.json"):
        async with aiofiles.open("server_bans.json", "r", encoding="utf-8") as f:
            server_bans = json.loads(await f.read())

    if os.path.exists("messages.json"):
        async with aiofiles.open("messages.json", "r", encoding="utf-8") as f:
            messages_list = json.loads(await f.read())
    
    if os.path.exists("facts.txt"):
        async with aiofiles.open("facts.txt", "r", encoding="UTF-8") as f:
            content = await f.read()
            facts = content.splitlines()

    if os.path.exists("custom_account_channels.json"):
        async with aiofiles.open("custom_account_channels.json", "r", encoding="utf-8") as f:
            custom_account_channel_list = json.loads(await f.read())
                    
    if os.path.exists("virtual_ids.json"):
        async with aiofiles.open("virtual_ids.json", "r", encoding="utf-8") as f:
            virtual_ids = json.loads(await f.read())

    if len(virtual_ids.keys()) > 0:
        virtual_ids_idx = int(sorted(virtual_ids.keys())[-1])

    for msg in messages_list:
        if leaderboard.get(msg["author_id"]) == None:
            leaderboard[msg["author_id"]] = [msg["likes"], msg["lol"]]
        else:
            leaderboard[msg["author_id"]] = [leaderboard[msg["author_id"]][0] + msg["likes"], leaderboard[msg["author_id"]][1] + msg["lol"]]

    update_status.start()

    print(f'Bot connecté en tant que {bot.user}')

@tasks.loop(minutes=5)
async def update_status():
    global curFact
    if not facts:
        update_status.stop()
        return
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
    embed.add_field(name="/leaderboard", value="Donne le classement des likes et des lol.", inline=False)
    embed.add_field(name="/delete_message message_id:[L'identifiant du message à supprimer]", value="Supprime votre message.", inline=False)
    embed.add_field(name="/report message_id:[L'identifiant du message à signaler]", value="Signale un message.", inline=False)
    embed.add_field(name="/add_bot", value="Vous donne un lien permettant d'ajouter Genoze sur votre serveur. Il vous faudra un administrateur de Genoze pour installer le bot.", inline=False)
    embed.add_field(name="[ADMIN GENOZE] /register_channel (channel:[Salon à enregistrer])", value="Enregistre un salon Genoze.", inline=False)
    embed.add_field(name="[ADMIN GENOZE] /unregister_channel", value="Supprime un salon Genoze.", inline=False)
    embed.add_field(name="[ADMIN GENOZE] /ban user:[L'utilisateur à bannir]", value="Bannit un utilisateur de Genoze.", inline=False)
    embed.add_field(name="[ADMIN GENOZE] /unban user:[L'utilisateur à débannir]", value="Débannit un utilisateur de Genoze.", inline=False)
    embed.add_field(name="[ADMIN GENOZE] /op user:[L'utilisateur à rendre administrateur]", value="Rend un utilisateur administrateur.", inline=False)
    embed.add_field(name="[ADMIN GENOZE] /deop user:[L'utilisateur à dérank]", value="Enlève le rang d'administrateur à un utilisateur.", inline=False)
    embed.add_field(name="[ADMIN SERV] /guild_ban user:[L'utilisateur à bannir]", value="Bannit localement un utilisateur.", inline=False)
    embed.add_field(name="[ADMIN SERV] /guild_unban user:[L'utilisateur à débannir]", value="Débannit un utilisateur banni localement.", inline=False)
    embed.add_field(name="[ADMIN SERV] /register_virtual_account name:[Le nom du compte virtuel] pp_url:[Le lien vers la photo de profil] (channel:[Le salon où enregistrer])", value="Crée un compte virtuel.", inline=False)
    embed.add_field(name="[ADMIN SERV] /unregister_virtual_account virtual_id:[L'identifiant du compte virtuel]", value="Supprime le compte virtuel.", inline=False)
    embed.add_field(name="[MEMBRE COMPTE VIRTUEL/ADMIN SERV] /add_va_member user:[L'utilisateur à ajouter] virtual_id:[L'identifiant du compte virtuel]", value="Ajoute un membre au compte virtuel.", inline=False)
    embed.add_field(name="[MEMBRE COMPTE VIRTUEL/ADMIN SERV] /remove_va_member user:[L'utilisateur à retirer] virtual_id:[L'identifiant du compte virtuel]", value="Retire un membre au compte virtuel.", inline=False)
   
    embed.set_footer(text="Version : 0.3\nSi vous voulez contribuer au développement de Genoze, contactez Timoh de Solarys.")
   
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

@bot.tree.command(name="leaderboard", description="Fait un classement des 5 premières personnes ayant le plus de réactions.")
async def leaderboardfn(interaction: discord.Interaction):
    await interaction.response.send_message("Charge les données du leaderboard...")

    embed = discord.Embed(
        title="Classement Genoze",
        description="## Likes :\n",
        color=discord.Color.from_rgb(7, 106, 68)
    )

    likesLeaderboard = {}
    lolLeaderboard = {}
    posidx = 1
    maxId = 5
    posUserLikes = 0
    posUserLol = 0

    if len(leaderboard) < maxId:
        maxId = len(leaderboard)

    for k, v in leaderboard.items():
        likesLeaderboard[k] = v[0]
        lolLeaderboard[k] = v[1]

    likesLeaderboard = dict(sorted(likesLeaderboard.items(), key=lambda item: item[1], reverse=True))
    lolLeaderboard = dict(sorted(lolLeaderboard.items(), key=lambda item: item[1], reverse=True))

    for k, v in likesLeaderboard.items():
        if k > 9999999999999999999:
            curUser = virtual_ids[str(k)]["name"]
        else:
            curUser = bot.get_user(k) or await bot.fetch_user(k)
        if isinstance(curUser, str):
            embed.description = f"{embed.description}{posidx}. {curUser} (compte virtuel) : {v} likes\n"
        elif k == interaction.user.id and curUser:
            embed.description = f"{embed.description}{posidx}. **{curUser.mention} (vous) : {v} likes**\n"
            posUserLikes = posidx
        elif posidx < 6 and curUser:
            embed.description = f"{embed.description}{posidx}. {curUser.mention} : {v} likes\n"
        elif posidx <6 and not curUser:
            embed.description = f"{embed.description}{posidx}. {k} : {v} likes\n"
        elif posidx == 6:
            embed.description = f"{embed.description}\n"

        posidx += 1

        if posidx > maxId and (posUserLikes != 0 or not check_member_of(interaction.user.id, likesLeaderboard.keys())):
            break
        
    posidx = 1
    embed.description = f"{embed.description}## Lol :\n"

    for k, v in lolLeaderboard.items():
        if k > 9999999999999999999:
            curUser = virtual_ids[str(k)]["name"]
        else:
            curUser = bot.get_user(k) or await bot.fetch_user(k)
        if isinstance(curUser, str):
            embed.description = f"{embed.description}{posidx}. {curUser} (compte virtuel) : {v} lol\n"
        elif k == interaction.user.id and curUser:
            embed.description = f"{embed.description}{posidx}. **{curUser.mention} (vous) : {v} lol**\n"
            posUserLol = posidx
        elif posidx < 6 and curUser:
            embed.description = f"{embed.description}{posidx}. {curUser.mention} : {v} lol\n"
        elif posidx < 6 and not curUser:
            embed.description = f"{embed.description}{posidx}. {k} : {v} lol\n"
        elif posidx == 6:
            embed.description = f"{embed.description}\n"
        
        posidx += 1

        if posidx > maxId and (posUserLol != 0 or not check_member_of(interaction.user.id, lolLeaderboard.keys())):
            break

    await interaction.edit_original_response(content="", embed=embed)

@bot.tree.command(name="delete_message", description="Supprime un message Genoze.")
@app_commands.describe(message_id="Le message à supprimer.")
async def delete_message(interaction: discord.Interaction, message_id: str):
    mid = int(message_id)
    message = await interaction.channel.fetch_message(mid)

    if isinstance(message, discord.Message) and message.author.id == bot_id:
        og_id = int(message.embeds[0].description.split("(")[1].split(")")[0])

        if interaction.user.id != og_id and not check_member_of(interaction.user.id, admin_list):
            if og_id > 9999999999999999999:
                og_id = str(og_id)
                pala = 0
                for uid in virtual_ids[og_id]["users"]:
                    if interaction.user.id != uid:
                        pala += 1

                if pala == len(virtual_ids[og_id]["users"]):
                    await interaction.response.send_message(content="Vous ne pouvez pas supprimer un message qui ne vous appartient pas.", ephemeral=True)
                    return
            else:
                await interaction.response.send_message(content="Vous ne pouvez pas supprimer un message qui ne vous appartient pas.", ephemeral=True)
                return
        
        await interaction.response.send_message("Supprime le message...")
        
        if len(message.embeds) == 1 and message.embeds[0].author.name == "Genoze":
            message_idx = -1
            for i in range(len(messages_list)):
                if check_member_of(mid, messages_list[i]["messages_published"]):
                    message_idx = i
                    break
            
            if message_idx != -1:
                for i in range(len(messages_list[message_idx]["servers_published"])):
                    server_id = messages_list[message_idx]["servers_published"][i]
                    channel_id = channel_list[server_id]
                    server = bot.get_guild(server_id) or await bot.fetch_guild(server_id)
                    channel = server.get_channel(channel_id) or await server.fetch_channel(channel_id)
                    bot_message = channel.get_partial_message(messages_list[message_idx]["messages_published"][i]) or await channel.fetch_message(messages_list[message_idx]["messages_published"][i])
                    await bot_message.delete()

                messages_list.pop(message_idx)

                async with aiofiles.open("messages.json", "w", encoding="utf-8") as f:
                    await f.write(json.dumps(messages_list, indent=4))

                await interaction.edit_original_response(content="Le message a été supprimé.")
            else:
                await interaction.response.send_message(content="Une erreur est survenue lors de la suppression.")

@bot.tree.command(name="report", description="Signale un message Genoze.")
@app_commands.describe(message_id="Le message à signaler.")
async def reportfn(interaction: discord.Interaction, message_id: str):
    mid = int(message_id)

    message = await interaction.channel.fetch_message(mid)
    if isinstance(message, discord.Message) and message.author.id == bot_id:
        if len(message.embeds) == 1 and message.embeds[0].author.name == "Genoze":
            await interaction.response.send_modal(Report(custom_id=str(mid)))

@bot.tree.command(name="register_channel", description="[ADMIN GENOZE] Enregistre un salon Genoze.")
@app_commands.describe(channel="Le salon à enregistrer.")
async def register_channel(interaction: discord.Interaction, channel: discord.TextChannel = None):
    if not check_member_of(interaction.user.id, admin_list):
        await interaction.response.send_message("Seul un administrateur Genoze peut exécuter cette commande.", ephemeral=True)
        return

    await interaction.response.send_message("Enregistre le salon...")

    if channel == None:
        channel = interaction.channel

    if interaction.guild_id in channel_list.keys():
        registered_channel = interaction.guild.get_channel(channel_list[interaction.guild_id]) or await interaction.guild.fetch_channel(channel_list[interaction.guild_id])
        await interaction.edit_original_response(content=f"Le serveur a déjà un salon enregistré : {registered_channel.jump_url}, un serveur ne peut pas avoir plus d'un salon enregistré. Si vous voulez changer de salon, faites `/unregister_channel`.")
        return

    channel_list[interaction.guild_id] = channel.id

    async with aiofiles.open("channels.txt", "a", encoding="utf-8") as f:
        await f.write(f"{interaction.guild_id}/{channel.id}\n")

    await interaction.edit_original_response(content=f"Le salon {channel.jump_url} a bien été enregistré comme salon Genoze pour le serveur {interaction.guild.name}.")

@bot.tree.command(name="unregister_channel", description="[ADMIN GENOZE] Supprime un salon Genoze.")
async def unregister_channel(interaction: discord.Interaction):
    if not check_member_of(interaction.user.id, admin_list):
        await interaction.response.send_message("Seul un administrateur Genoze peut exécuter cette commande.", ephemeral=True)
        return

    await interaction.response.send_message("Supprime le salon de la liste...")

    if interaction.guild_id in channel_list.keys():
        registered_channel = interaction.guild.get_channel(channel_list[interaction.guild_id]) or await interaction.guild.fetch_channel(channel_list[interaction.guild_id])
        del channel_list[interaction.guild_id]
        async with aiofiles.open("channels.txt", "w", encoding="utf-8") as f:
            for k, v in channel_list.items():
                await f.write(f"{k}/{v}\n")
        await interaction.edit_original_response(content=f"Le salon enregistré ({registered_channel.jump_url}) a bien été supprimé de la liste de Genoze.")
    else:
        await interaction.edit_original_response(content=f"Aucun salon Genoze n'a été enregistré pour ce serveur.")

@bot.tree.command(name="ban", description="[ADMIN GENOZE] Bannit un utilisateur.")
@app_commands.describe(user="L'utilisateur à bannir.", user_id="L'identifiant de l'utilisateur à bannir (pour les comptes virtuels).")
async def ban(interaction: discord.Interaction, user: discord.User = None, user_id: str = None):
    if not check_member_of(interaction.user.id, admin_list):
        await interaction.response.send_message("Seul un administrateur Genoze peut exécuter cette commande.", ephemeral=True)
        return

    if user == None and user_id == None:
        await interaction.response.send_message("Vous devez préciser l'utilisateur à bannir.", ephemeral=True)
        return
    
    user_id = int(user_id)
    if user == None and user_id <= 9999999999999999999:
        user = bot.get_user(user_id) or await bot.fetch_user(user_id)

    if interaction.user == user:
        await interaction.response.send_message("Vous ne pouvez pas vous bannir.", ephemeral=True)
        return
    
    if user_id == 0:
        user_id = user.id

    user_name = user_id
    if user_id <= 9999999999999999999:
        user_name = user.global_name
    else:
        user_name = virtual_ids[str(user_id)]["name"]

    await interaction.response.send_message(f"Bannit l'utilisateur {user_name} de Genoze...")

    if check_member_of(user_id, ban_list):
        await interaction.edit_original_response(content=f"{user_name} est déjà banni.e.")
        return
    
    ban_list.add(user_id)

    async with aiofiles.open("ban_list.txt", "a", encoding="utf-8") as f:
        await f.write(f"{user_id}\n")

    await interaction.edit_original_response(content=f"{user_name} est désormais banni.e.")

@bot.tree.command(name="unban", description="[ADMIN GENOZE] Débannit un utilisateur.")
@app_commands.describe(user="L'utilisateur à débannir.", user_id="L'identifiant de l'utilisateur à débannir (pour les comptes virtuels).")
async def unban(interaction: discord.Interaction, user: discord.User = None, user_id: str = None):
    if not check_member_of(interaction.user.id, admin_list):
        await interaction.response.send_message("Seul un administrateur Genoze peut exécuter cette commande.", ephemeral=True)
        return
    
    if user == None and user_id == None:
        await interaction.response.send_message("Vous devez préciser l'utilisateur à débannir.", ephemeral=True)
        return
    
    user_id = int(user_id)
    if user == None and user_id <= 9999999999999999999:
        user = bot.get_user(user_id) or await bot.fetch_user(user_id)

    if user_id == 0:
        user_id = user.id

    user_name = user_id
    if user_id <= 9999999999999999999:
        user_name = user.global_name
    else:
        user_name = virtual_ids[str(user_id)]["name"]

    await interaction.response.send_message(f"Débannit l'utilisateur {user_name} de Genoze...")

    if not check_member_of(user_id, ban_list):
        await interaction.edit_original_response(content=f"{user_name} n'est pas banni.e.")
        return
    
    ban_list.remove(user_id)

    async with aiofiles.open("ban_list.txt", "w", encoding="utf-8") as f:
        for v in ban_list:
            await f.write(f"{v}\n")

    await interaction.edit_original_response(content=f"{user_name} est désormais débanni.e.")

@bot.tree.command(name="op", description="[ADMIN GENOZE] Rend un utilisateur administrateur.")
@app_commands.describe(user="L'utilisateur à rendre administrateur.")
async def op(interaction: discord.Interaction, user: discord.User):
    if not check_member_of(interaction.user.id, admin_list):
        await interaction.response.send_message("Seul un administrateur Genoze peut exécuter cette commande.", ephemeral=True)
        return
    
    await interaction.response.send_message(f"Rend l'utilisateur {user.global_name} administrateur de Genoze...")

    if check_member_of(user.id, admin_list):
        await interaction.edit_original_response(content=f"{user.global_name} est déjà administrateur.rice.")
        return
    
    admin_list.add(user.id)

    async with aiofiles.open("admin_list.txt", "a", encoding="utf-8") as f:
        await f.write(f"{user.id}\n")

    await interaction.edit_original_response(content=f"{user.global_name} est désormais administrateur.rice.")

@bot.tree.command(name="deop", description="[ADMIN GENOZE] Enlève le rang d'administrateur à un utilisateur.")
@app_commands.describe(user="L'utilisateur à dérank.")
async def deop(interaction: discord.Interaction, user: discord.User):
    if not check_member_of(interaction.user.id, admin_list):
        await interaction.response.send_message("Seul un administrateur Genoze peut exécuter cette commande.", ephemeral=True)
        return
    
    if interaction.user == user:
        await interaction.response.send_message("Vous ne pouvez pas vous dérank.", ephemeral=True)
        return

    await interaction.response.send_message(f"Dérank l'utilisateur {user.global_name} de Genoze...")

    if not check_member_of(user.id, admin_list):
        await interaction.edit_original_response(content=f"{user.global_name} n'est pas administrateur.rice.")
        return
    
    admin_list.remove(user.id)
    async with aiofiles.open("admin_list.txt", "w", encoding="utf-8") as f:
        for v in admin_list:
            await f.write(f"{v}\n")

    await interaction.edit_original_response(content=f"{user.global_name} n'est désormais plus administrateur.rice.")

@bot.tree.command(name="register_virtual_account", description="[ADMIN SEV] Enregistre un compte virtuel Genoze.")
@app_commands.describe(name="Le nom du compte virtuel.", pp_url="Le lien vers la photo de profil.", channel="Le salon où enregistrer.")
async def register_virtual_account(interaction: discord.Interaction, name: str, pp_url: str, channel: discord.TextChannel = None):
    global virtual_ids_idx

    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("Seul une personne ayant les permissions d'administrateur peut utiliser cette commande.", ephemeral=True)
        return
    
    if not validators.url(pp_url):
        await interaction.response.send_message(f"L'adresse précisée est invalide : {pp_url}", ephemeral=True)
        return

    await interaction.response.send_message("Enregistre le compte virtuel...")

    if channel == None:
        channel = interaction.channel

    if str(interaction.guild_id) in custom_account_channel_list.keys():
        if str(channel.id) in custom_account_channel_list[str(interaction.guild_id)].keys():
            await interaction.edit_original_response(content=f"Le salon a déjà un compte virtuel enregistré : {virtual_ids[str(custom_account_channel_list[str(interaction.guild_id)][str(channel.id)])]['name']}, un salon ne peut pas avoir plus d'un compte virtuel enregistré.")
            return

    virtual_ids_idx += 1

    if custom_account_channel_list.get(str(interaction.guild_id)) == None:
        custom_account_channel_list[str(interaction.guild_id)] = {}

    custom_account_channel_list[str(interaction.guild_id)][str(channel.id)] = virtual_ids_idx
    
    virtual_ids[str(virtual_ids_idx)] = {
        "name": name,
        "pp_url": pp_url,
        "users": [interaction.user.id]
    }

    async with aiofiles.open("custom_account_channels.json", "w", encoding="utf-8") as f:
        await f.write(json.dumps(custom_account_channel_list, indent=4))

    async with aiofiles.open("virtual_ids.json", "w", encoding="utf-8") as f:
        await f.write(json.dumps(virtual_ids, indent=4))

    await interaction.edit_original_response(content=f"Le compte virtuel {name} a bien été enregistré à l'identifiant {virtual_ids_idx}.")

@bot.tree.command(name="unregister_virtual_account", description="[ADMIN SERV] Supprime un compte virtuel Genoze.")
@app_commands.describe(virtual_id="L'identifiant du compte virtuel.")
async def unregister_virtual_account(interaction: discord.Interaction, virtual_id: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Seul une personne ayant les permissions d'administrateur peut utiliser cette commande.", ephemeral=True)
        return

    await interaction.response.send_message("Supprime le compte virtuel...")

    if str(interaction.guild_id) in custom_account_channel_list.keys():
        if int(virtual_id) in custom_account_channel_list[str(interaction.guild_id)].values():
            for cid, vid in custom_account_channel_list[str(interaction.guild_id)].items():
                if vid == int(virtual_id):
                    break

            old_name = virtual_ids[virtual_id]["name"]
            del virtual_ids[virtual_id]
            del custom_account_channel_list[str(interaction.guild_id)][cid]
            async with aiofiles.open("custom_account_channels.json", "w", encoding="utf-8") as f:
                await f.write(json.dumps(custom_account_channel_list, indent=4))
            async with aiofiles.open("virtual_ids.json", "w", encoding="utf-8") as f:
                await f.write(json.dumps(virtual_ids, indent=4))
            await interaction.edit_original_response(content=f"Le compte virtuel {old_name} a bien été supprimé de Genoze.")
            return

    await interaction.edit_original_response(content=f"Aucun compte virtuel Genoze n'est enregistré avec cet identifiant.")

@bot.tree.command(name="guild_ban", description="[ADMIN SERV] Bannit localement un utilisateur.")
@app_commands.describe(user="L'utilisateur à bannir.", user_id="L'identifiant de l'utilisateur à bannir (pour les comptes virtuels).")
async def guild_ban(interaction: discord.Interaction, user: discord.User = None, user_id: str = None):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("Seul une personne ayant les permissions de bannir quelqu'un peut utiliser cette commande.", ephemeral=True)
        return

    if user == None and user_id == None:
        await interaction.response.send_message("Vous devez préciser l'utilisateur à bannir.", ephemeral=True)
        return
    
    user_id = int(user_id)
    if user == None and user_id <= 9999999999999999999:
        user = bot.get_user(user_id) or await bot.fetch_user(user_id)

    if user_id == 0:
        user_id = user.id

    if interaction.user == user:
        await interaction.response.send_message("Vous ne pouvez pas vous bannir.", ephemeral=True)
        return
    
    user_name = user_id
    if user_id <= 9999999999999999999:
        user_name = user.global_name
    else:
        user_name = virtual_ids[str(user_id)]["name"]
    
    await interaction.response.send_message(f"Bannit l'utilisateur {user_name} du serveur...")

    if check_member_of(str(user_id), server_bans.keys()):
        if check_member_of(interaction.guild.id, server_bans[str(user_id)]):
            await interaction.edit_original_response(content=f"{user_name} est déjà banni.e ici.")
            return
        server_bans[str(user_id)].append(interaction.guild.id)
    else:
        server_bans[str(user_id)] = [interaction.guild.id]

    async with aiofiles.open("server_bans.json", "w", encoding="utf-8") as f:
        await f.write(json.dumps(server_bans, indent=4))

    await interaction.edit_original_response(content=f"{user_name} est désormais banni.e ici.")

@bot.tree.command(name="guild_unban", description="[ADMIN SERV] Débannit un utilisateur banni localement.")
@app_commands.describe(user="L'utilisateur à débannir.", user_id="L'identifiant de l'utilisateur à débannir (pour les comptes virtuels).")
async def guild_unban(interaction: discord.Interaction, user: discord.User = None, user_id: str = None):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("Seul une personne ayant les permissions de bannir quelqu'un peut utiliser cette commande.", ephemeral=True)
        return
    
    if user == None and user_id == None:
        await interaction.response.send_message("Vous devez préciser l'utilisateur à débannir.", ephemeral=True)
        return
    
    user_id = int(user_id)
    if user == None and user_id <= 9999999999999999999:
        user = bot.get_user(user_id) or await bot.fetch_user(user_id)

    if user_id == 0:
        user_id = user.id

    user_name = user_id
    if user_id <= 9999999999999999999:
        user_name = user.global_name
    else:
        user_name = virtual_ids[str(user_id)]["name"]

    await interaction.response.send_message(f"Débannit l'utilisateur {user_name} du serveur...")

    if not check_member_of(str(user_id), server_bans.keys()):
        await interaction.edit_original_response(content=f"{user_name} n'est pas banni.e.")
        return
    
    if not check_member_of(interaction.guild.id, server_bans[str(user_id)]):
        await interaction.edit_original_response(content=f"{user_name} n'est pas banni.e.")
        return

    for i in range(len(server_bans[str(user_id)])):
        if server_bans[str(user_id)][i] == interaction.guild.id:
            server_bans[str(user_id)].pop(i)
            break

    if len(server_bans[str(user_id)]) == 0:
        server_bans.pop(str(user_id))

    async with aiofiles.open("server_bans.json", "w", encoding="utf-8") as f:
        await f.write(json.dumps(server_bans, indent=4))

    await interaction.edit_original_response(content=f"{user_name} est désormais débanni.e du serveur.")

@bot.tree.command(name="add_va_member", description="[MEMBRE COMPTE VIRTUEL/ADMIN SERV] Ajoute un membre au compte virtuel.")
@app_commands.describe(user="L'utilisateur à ajouter.", virtual_id="L'identifiant du compte virtuel.")
async def add_va_member(interaction: discord.Interaction, user: discord.User, virtual_id: str):
    if not check_member_of(interaction.user.id, virtual_ids[virtual_id]["users"]) and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Seul un membre du compte virtuel ou un administrateur peut ajouter d'autres membres au compte.", ephemeral=True)
        return
    
    await interaction.response.send_message(f"Ajoute {user.global_name} au compte virtuel {virtual_ids[virtual_id]['name']}...")

    if check_member_of(user.id, virtual_ids[virtual_id]["users"]):
        await interaction.edit_original_response(content=f"{user.global_name} est déjà membre du compte virtuel.")
        return
    
    virtual_ids[virtual_id]["users"].append(user.id)

    async with aiofiles.open("virtual_ids.json", "w", encoding="utf-8") as f:
        await f.write(json.dumps(virtual_ids, indent=4))

    await interaction.edit_original_response(content=f"{user.global_name} est désormais membre du compte virtuel.")

@bot.tree.command(name="remove_va_member", description="[MEMBRE COMPTE VIRTUEL/ADMIN SERV] Retire un membre au compte virtuel.")
@app_commands.describe(user="L'utilisateur à retirer.", virtual_id="L'identifiant du compte virtuel.")
async def remove_va_member(interaction: discord.Interaction, user: discord.User, virtual_id: str):
    if not check_member_of(interaction.user.id, virtual_ids[virtual_id]["users"]) and not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("Seul un membre du compte virtuel ou un administrateur peut retirer d'autres membres au compte.", ephemeral=True)
        return
    
    if interaction.user == user:
        await interaction.response.send_message("Vous ne pouvez pas vous retirer.", ephemeral=True)
        return
    
    await interaction.response.send_message(f"Retire {user.global_name} au compte virtuel {virtual_ids[virtual_id]['name']}...")

    if not check_member_of(user.id, virtual_ids[virtual_id]["users"]):
        await interaction.edit_original_response(content=f"{user.global_name} n'est pas membre du compte virtuel.")
        return
    
    virtual_ids[virtual_id]["users"].remove(user.id)

    async with aiofiles.open("virtual_ids.json", "w", encoding="utf-8") as f:
        await f.write(json.dumps(virtual_ids, indent=4))

    await interaction.edit_original_response(content=f"{user.global_name} n'est plus membre du compte virtuel.")

async def messagefn(message: discord.Message, author: dict):
    if not check_member_of(author["id"], ban_list):
        message_data = {
            "author_id": author["id"],
            "servers_published": [],
            "messages_published": [],
            "likes": 0,
            "lol": 0
        }
        embed = discord.Embed(
            title=author["display_name"],
            description=f"-# *{author['name']} ({author['id']})*\n---\n{message.content}",
            color=discord.Color.from_rgb(7, 106, 68),
            timestamp=datetime.datetime.now(tz.gettz("Europe/Paris"))
        )
        if author["id"] > 9999999999999999999:
            embed.color=discord.Color.from_rgb(249, 163, 6)
            embed.title=f"{author['name']} *(compte virtuel)*"
        embed.set_author(
            name="Genoze"
        )
        embed.set_footer(
            text=message.guild.name,
            icon_url=message.guild.icon.url
        )
        embed.set_thumbnail(url=author["avatar_url"])
        if len(message.attachments) >= 1:
            firstImage = False
            for i in message.attachments:
                if not firstImage and i.content_type.split("/")[0] == "image":
                    embed.set_image(url=i.url)
                    firstImage = True
                    continue
                embed.add_field(name=i.filename, value=i.url, inline=False)
        elif author["id"] <= 9999999999999999999:
            await message.delete()
        embed.add_field(name="Likes", value="0", inline=True)
        embed.add_field(name="Lol", value="0", inline=True)
        needCheck = False
        if message.reference and isinstance(message.reference.resolved, discord.Message):
            reply = message.reference.resolved
            if reply.author.id == bot_id:
                reply_msgs = reply.embeds[0].description.split("\n---\n")
                reply_msg = reply_msgs[len(reply_msgs) - 1]
                embed.description = f"-# *{author['name']} ({author['id']})*\n---\n{reply.embeds[0].title} (dans {reply.embeds[0].footer.text} à {reply.embeds[0].timestamp.strftime('%d/%m/%Y')}, {(reply.embeds[0].timestamp.hour + 2) % 24}:{reply.embeds[0].timestamp.minute}) : \"{reply_msg}\"\n---\n{message.content}"
        if check_member_of(str(author["id"]), server_bans.keys()):
            needCheck = True
        for server_id, channel_id in channel_list.items():
            server = bot.get_guild(server_id) or await bot.fetch_guild(server_id)
            channel = server.get_channel(channel_id) or await server.fetch_channel(channel_id)
            if needCheck:
                if check_member_of(server_id, server_bans[str(author["id"])]):
                    real_sender = message.guild.get_member(author["sender_id"]) or await message.guild.fetch_member(author["sender_id"])
                    await real_sender.send(content=f"Votre [message]({message.channel.jump_url}) n'a pas été transféré sur {server.name} car vous y êtes banni.e.")
                    continue
            bot_message = await channel.send(embed=embed, view=MessageBtns(timeout=None))
            await bot_message.add_reaction(thumbsup)
            await bot_message.add_reaction(lol)
            message_data["servers_published"].append(server_id)
            message_data["messages_published"].append(bot_message.id)
        
        messages_list.append(message_data)

        async with aiofiles.open("messages.json", "w", encoding="utf-8") as f:
            await f.write(json.dumps(messages_list, indent=4))
    else:
        try:
            real_sender = message.guild.get_member(author["sender_id"]) or await message.guild.fetch_member(author["sender_id"])
            await real_sender.send(content=f"Votre [message]({message.channel.jump_url}) n'a pas été transféré sur les autres serveurs car vous êtes banni.e.")
        except discord.Forbidden:
            pass
        if author["id"] <= 9999999999999999999:
            await message.delete()

@bot.event
async def on_message(message: discord.Message):
    if message.guild and not message.author.bot:
        if message.channel.id == channel_list.get(message.guild.id):
            author = {
                "id": message.author.id,
                "display_name": message.author.display_name,
                "name": message.author.name,
                "avatar_url": message.author.display_avatar.url,
                "sender_id": message.author.id
            }
            await messagefn(message, author)
        elif str(message.channel.id) in custom_account_channel_list.get(str(message.guild.id)).keys():
            vid = str(custom_account_channel_list[str(message.guild.id)][str(message.channel.id)])

            pala = 0
            for uid in virtual_ids[vid]["users"]:
                if message.author.id != uid:
                    pala += 1

            if pala == len(virtual_ids[vid]["users"]):
                await message.author.send(content="Vous ne pouvez pas envoyer un message dans un compte virtuel dont vous n'êtes pas membre.")
            else:
                author = {
                    "id": int(vid),
                    "display_name": virtual_ids[vid]["name"],
                    "name": str.lower(virtual_ids[vid]["name"]),
                    "avatar_url": virtual_ids[vid]["pp_url"],
                    "sender_id": message.author.id
                }
                await messagefn(message, author)
    await bot.process_commands(message)

async def update_message_reactions(payLoad: discord.RawReactionActionEvent, value: int):
    if payLoad.user_id != bot_id:
        if str(payLoad.emoji) == thumbsup or str(payLoad.emoji) == lol:
            message_idx = -1
            for i in range(len(messages_list)):
                if check_member_of(payLoad.message_id, messages_list[i]["messages_published"]):
                    message_idx = i
                    break

            if message_idx == -1:
                return

            server = bot.get_guild(payLoad.guild_id) or await bot.fetch_guild(payLoad.guild_id)
            channel = server.get_channel(payLoad.channel_id) or await server.fetch_channel(payLoad.channel_id)
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
            if msg.embeds[0].image.url != None:
                embed.set_image(url=msg.embeds[0].image.url)
            if len(msg.embeds[0].fields) - 2 > 0:
                for i in range(len(msg.embeds[0].fields) - 2):
                    embed.add_field(name=msg.embeds[0].fields[i].name, value=msg.embeds[0].fields[i].value, inline=False)
            prev_like = messages_list[message_idx]["likes"]
            prev_lol = messages_list[message_idx]["lol"]
            if str(payLoad.emoji) == thumbsup:
                embed.add_field(name="Likes", value=f"{prev_like + value}", inline=True)
                messages_list[message_idx]["likes"] += value
                if leaderboard.get(messages_list[message_idx]["author_id"]) == None:
                    leaderboard[messages_list[message_idx]["author_id"]] = [value, 0]
                else:
                    leaderboard[messages_list[message_idx]["author_id"]] = [leaderboard[messages_list[message_idx]["author_id"]][0] + value, leaderboard[messages_list[message_idx]["author_id"]][1]]
            else:
                embed.add_field(name="Likes", value=f"{prev_like}", inline=True)
            if str(payLoad.emoji) == lol:
                embed.add_field(name="Lol", value=f"{prev_lol + value}", inline=True)
                messages_list[message_idx]["lol"] += value
                if leaderboard.get(messages_list[message_idx]["author_id"]) == None:
                    leaderboard[messages_list[message_idx]["author_id"]] = [0, value]
                else:
                    leaderboard[messages_list[message_idx]["author_id"]] = [leaderboard[messages_list[message_idx]["author_id"]][0], leaderboard[messages_list[message_idx]["author_id"]][1] + value]
            else:
                embed.add_field(name="Lol", value=f"{prev_lol}", inline=True)
            
            for i, server_id in enumerate(messages_list[message_idx]["servers_published"]):
                channel_id = channel_list.get(server_id)
                server = bot.get_guild(server_id) or await bot.fetch_channel(server_id)
                if server and channel_id:
                    channel = server.get_channel(channel_id) or await server.fetch_channel(channel_id)
                    try:
                        target_msg = channel.get_partial_message(messages_list[message_idx]["messages_published"][i])
                        await target_msg.edit(embed=embed)
                    except discord.HTTPException:
                        pass

            async with aiofiles.open("messages.json", "w", encoding="utf-8") as f:
                await f.write(json.dumps(messages_list, indent=4))

@bot.event
async def on_raw_reaction_add(payLoad: discord.RawReactionActionEvent):
    await update_message_reactions(payLoad, 1)

@bot.event
async def on_raw_reaction_remove(payLoad: discord.RawReactionActionEvent):
    await update_message_reactions(payLoad, -1)

token = str(os.getenv("TWEET_TOKEN"))

bot.run(token)