# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║                                                                              ║
# ║    ██████╗ ███████╗ █████╗ ████████╗██╗  ██╗██╗  ██╗                        ║
# ║    ██╔══██╗██╔════╝██╔══██╗╚══██╔══╝██║  ██║╚██╗██╔╝                        ║
# ║    ██║  ██║█████╗  ███████║   ██║   ███████║ ╚███╔╝                         ║
# ║    ██║  ██║██╔══╝  ██╔══██║   ██║   ██╔══██║ ██╔██╗                         ║
# ║    ██████╔╝███████╗██║  ██║   ██║   ██║  ██║██╔╝ ██╗                        ║
# ║    ╚═════╝ ╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝                       ║
# ║                                                                              ║
# ║                     [ DISCORD ASSET EXTRACTOR v1.0 ]                        ║
# ║                  [ coded by deathx — not for the weak ]                     ║
# ║                                                                              ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

import discord
from discord import app_commands
import aiohttp
import io
import os
import sys

TOKEN = os.getenv("TOKEN")
CDN   = "https://cdn.discordapp.com"
API   = "https://discord.com/api/v10"
SIZE  = 4096

intents = discord.Intents.default()
client  = discord.Client(intents=intents)
tree    = app_commands.CommandTree(client)

async def fetch_image(url: str) -> discord.File:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.read()
            ext  = url.split(".")[-1].split("?")[0]
            return discord.File(io.BytesIO(data), filename=f"image.{ext}")

@tree.command(name="pfp", description=".")
@app_commands.describe(id="id")
async def pfp(interaction: discord.Interaction, id: str):
    await interaction.response.defer()
    try:
        user = await client.fetch_user(int(id))
        av   = user.avatar or user.default_avatar
        fmt  = "gif" if av.is_animated() else "png"
        url  = av.with_format(fmt).with_size(SIZE).url
        file = await fetch_image(url)
        await interaction.followup.send(file=file)
    except Exception:
        await interaction.followup.send("user not found", ephemeral=True)

@tree.command(name="banner", description=".")
@app_commands.describe(id="id")
async def banner(interaction: discord.Interaction, id: str):
    await interaction.response.defer()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API}/users/{int(id)}", headers={"Authorization": f"Bot {TOKEN}"}) as resp:
                data = await resp.json()
        banner_hash = data.get("banner")
        if not banner_hash:
            await interaction.followup.send("no banner found", ephemeral=True)
            return
        ext  = "gif" if banner_hash.startswith("a_") else "png"
        url  = f"{CDN}/banners/{id}/{banner_hash}.{ext}?size={SIZE}"
        file = await fetch_image(url)
        await interaction.followup.send(file=file)
    except Exception:
        await interaction.followup.send("user not found", ephemeral=True)

@client.event
async def on_ready():
    await tree.sync()
    print(f"  logged in as {client.user} — {round(client.latency * 1000)}ms")

if not TOKEN:
    sys.exit("[ERROR] TOKEN not set")

client.run(TOKEN, log_handler=None)
