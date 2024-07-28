import discord
from discord.ext import commands
from discord.ui import Button, View
import json
import os
from cryptography.fernet import Fernet

CONFIG_FILE = 'config.json'
KEY_FILE = 'key.key'
BANNED_USERS_FILE = 'banned_users.txt'
TOKEN = 'YOUR_DISCORD_BOT_TOKEN'  # Substitua pelo token do seu bot

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

def generate_key():
    key = Fernet.generate_key()
    with open(KEY_FILE, 'wb') as key_file:
        key_file.write(key)

def load_key():
    return open(KEY_FILE, 'rb').read()

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

class AdminPanel(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label='Banir Usuário', style=discord.ButtonStyle.danger, custom_id='ban_user')
    async def ban_user_button(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_message("Digite o nome do usuário a ser banido:", ephemeral=True)
        await interaction.client.wait_for('message', check=lambda m: m.author == interaction.user)
        username = interaction.message.content
        with open(BANNED_USERS_FILE, 'a') as f:
            f.write(username + '\n')
        await interaction.followup.send(f"Usuário {username} foi banido.", ephemeral=True)

    @discord.ui.button(label='Resetar Chave', style=discord.ButtonStyle.primary, custom_id='reset_key')
    async def reset_key_button(self, button: Button, interaction: discord.Interaction):
        generate_key()
        await interaction.response.send_message("Chave foi resetada.", ephemeral=True)

    @discord.ui.button(label='Resetar UUID', style=discord.ButtonStyle.secondary, custom_id='reset_uuid')
    async def reset_uuid_button(self, button: Button, interaction: discord.Interaction):
        # Implement UUID reset logic here
        await interaction.response.send_message("UUID foi resetado.", ephemeral=True)

    @discord.ui.button(label='Resetar Nome de Usuário', style=discord.ButtonStyle.success, custom_id='reset_username')
    async def reset_username_button(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_message("Digite o antigo nome de usuário:", ephemeral=True)
        old_username_message = await interaction.client.wait_for('message', check=lambda m: m.author == interaction.user)
        old_username = old_username_message.content

        await interaction.followup.send("Digite o novo nome de usuário:", ephemeral=True)
        new_username_message = await interaction.client.wait_for('message', check=lambda m: m.author == interaction.user)
        new_username = new_username_message.content

        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
            if data['username'] == old_username:
                data['username'] = new_username
                with open(CONFIG_FILE, 'w') as f:
                    json.dump(data, f)
                await interaction.followup.send(f"Nome de usuário {old_username} foi alterado para {new_username}.", ephemeral=True)
            else:
                await interaction.followup.send(f"Nome de usuário {old_username} não encontrado.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"Erro: {str(e)}", ephemeral=True)

@bot.command()
async def admin_panel(ctx):
    view = AdminPanel()
    await ctx.send("Painel Administrativo:", view=view)

if __name__ == '__main__':
    if not os.path.exists(KEY_FILE):
        generate_key()
    bot.run(TOKEN)
