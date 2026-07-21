# Genoze 👋

Genoze est un bot Discord d'inter-communication développé en Python par Timoh de Solarys (Timoh5709). Il permet de lier des salons textuels à travers plusieurs serveurs Discord pour créer un espace d'échange unifié, tout en intégrant des outils complets de modération globale et locale pour garder une safe place.

## Fonctionnalités principales

*   **Inter-communication Discord synchrone :** Chaque message envoyé dans un salon Genoze enregistré est automatiquement mis en forme dans un Embed élégant et retransmis en temps réel sur tous les autres serveurs connectés.
*   **Système de réponses :** Vous pouvez répondre aux messages du bot pour répondre au contenu.
*   **Système de suppression :** Vous pouvez supprimer vos messages.
*   **Réactions synchronisées :** Les réactions ajoutées ou retirées sur un serveur sont répercutées instantanément sur l'ensemble des serveurs du réseau.
*   **Comptes virtuels :** Vous pouvez créer des comptes virtuels pour partager vos annonces de mannière officielle sur Genoze.
*   **Signalement (modération) :** Un bouton "Signaler" attaché à chaque message permet aux utilisateurs d'ouvrir un formulaire pour envoyer une alerte directement aux administrateurs de Genoze avec le contexte du message.
*   **Modération à double niveau :**
    *   **Globale (Admin Genoze) :** Bannissement définitif du réseau Genoze.
    *   **Locale (Admin serveur) :** Possibilité pour les administrateurs d'un serveur de bloquer l'affichage des messages d'un utilisateur spécifique uniquement chez eux.
*   **Statut dynamique :** Le bot change automatiquement sa présence toutes les 5 minutes en affichant des faits aléatoires chargés depuis un fichier externe.

## Commandes disponibles

Le bot utilise exclusivement les commandes slash.

### Commandes publiques
*   `/help` : Affiche la liste des commandes et les informations de version.
*   `/ping` : Teste la présence du bot.
*   `/leaderboard` : Affiche le classement des réactions.
*   `/add_bot` : Fournit le lien d'invitation OAuth2 du bot.

### Commandes administrateurs Genoze (Global)
*   `/register_channel [salon]` : Enregistre le salon actuel (ou celui spécifié) comme le salon Genoze officiel du serveur (limité à 1 par serveur).
*   `/unregister_channel` : Supprime le salon du réseau Genoze.
*   `/ban [utilisateur]` : Bannit un utilisateur de l'intégralité du réseau Genoze.
*   `/unban [utilisateur]` : Débannit un utilisateur du réseau global.
*   `/op [utilisateur]` : Donne les droits d'administration Genoze à un utilisateur.
*   `/deop [utilisateur]` : Retire les privilèges d'administration Genoze.
*   `/delete_message [message_id]` : Supprime un message.

### Commandes administrateurs serveur (Local)
*   `/guild_ban [utilisateur]` : Bannit localement un utilisateur pour qu'il n'apparaisse plus sur votre serveur.
*   `/guild_unban [utilisateur]` : Annule le bannissement local d'un utilisateur.
*   `/register_virtual_account [nom] [URL pour la photo de profil (vous pouvez envoyer l'image sur Discord et copier son lien)] [salon]` : Crée un compte virtuel.
*   `/unregister_virtual_account [identifiant du compte virtuel]` : Supprime le compte virtuel.

### Commandes membres d'un compte virtuel (et administrateurs serveur)
*   `/add_va_member [utilisateur] [identifiant du compte virtuel]` : Ajoute un membre au compte virtuel.
*   `/remove_va_member [utilisateur] [identifiant du compte virtuel]` : Retire un membre au compte virtuel.

## Prérequis et installation

### Fichiers de configuration requis
Le bot repose sur un stockage local simple. Avant de le lancer, assurez-vous que les fichiers suivants existent à la racine du projet :
*   `admin_list.txt` : Contient les IDs Discord des administrateurs Genoze (un ID par ligne).
*   `ban_list.txt` : Contient les IDs des utilisateurs bannis globalement.
*   `channels.txt` : Fichier de mapping des salons enregistrés (`ID_SERVEUR/ID_SALON`).
*   `facts.txt` : Liste de phrases/faits pour le statut du bot (une phrase par ligne, encodé en UTF-8).
*   `server_bans.json` : Structure JSON gérant les exclusions locales par serveur (initialiser avec `{}`).
*   `messages.json` : Historique et compteur des messages transférés (initialiser avec `[]`).
*   `custom_account_channel.json` : Fichier de mapping des comptes virtuels enregistrés (initialiser avec `{}`).
*   `virtual_ids.json` : Contient les comptes virtuels (initialiser avec `{}`).

### Variable d'environnement
Le bot requiert un jeton Discord sécurisé passé via une variable d'environnement :
```bash
export TWEET_TOKEN="VOTRE_TOKEN_DISCORD"