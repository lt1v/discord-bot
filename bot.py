import discord
import asyncio
import aiohttp
import os
from datetime import datetime, timedelta, timezone

# 🔐 TOKEN sécurisé
TOKEN = os.getenv("TOKEN")

CHANNEL_IDS = [
    1499539348666716251,
    1499539354689994844
]

RESET_INTERVAL = 3600

intents = discord.Intents.default()
client = discord.Client(intents=intents)

session = None


async def get_ltc_price():
    global session
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=litecoin&vs_currencies=usd,eur"
        async with session.get(url) as resp:
            data = await resp.json()
            eur = round(data["litecoin"]["eur"], 2)
            usd = round(data["litecoin"]["usd"], 2)
            return eur, usd
    except:
        return "??", "??"


def create_embed(timestamp, eur, usd):
    embed = discord.Embed(
        title="<:settings:1484630585753473054> Channel BOMBED",
        description="This channel gets nuked **every hour** to maintain a clean environment.",
        color=0x6C2BD9
    )

    embed.add_field(
        name="",
        value=(
            "[Learn More About Fluxify Exchange](https://easyexch.org)\n\n"
            "• <:litecoin:1484628704075452467> **Current LTC Rates:**\n"
            f"  ◦ €{eur}\n"
            f"  ◦ ${usd}\n\n"
            f"> Next nuking <t:{timestamp}:R>\n"
            "> This Channel is **not a Marketplace and Advertising is strictly prohibited**\n\n"
            "**Do you know that?**\n"
            "> A signature is called a John Hancock because he signed the Declaration of Independence."
        ),
        inline=False
    )

    embed.set_thumbnail(url="https://media.tenor.com/2roX3uxz_68AAAAC/cat-space.gif")
    embed.timestamp = datetime.now(timezone.utc)
    embed.set_footer(text="Fluxify System – Fast & Safe Support")

    return embed


async def nuke_channel(channel):
    try:
        position = channel.position
        category = channel.category

        new_channel = await channel.clone()
        await channel.delete()

        await new_channel.edit(position=position, category=category)

        print("💣 Nuke OK:", new_channel.name)
        return new_channel

    except Exception as e:
        print("❌ ERREUR NUKE:", e)
        return None


async def main_loop():
    print("🚀 LOOP START")

    new_channels = []
    for cid in CHANNEL_IDS:
        try:
            channel = await client.fetch_channel(cid)
        except:
            print("❌ Channel introuvable:", cid)
            continue

        new_channel = await nuke_channel(channel)

        if new_channel:
            new_channels.append(new_channel.id)

    if new_channels:
        CHANNEL_IDS.clear()
        CHANNEL_IDS.extend(new_channels)

    print("Channels actifs:", CHANNEL_IDS)

    while True:
        next_reset = datetime.now(timezone.utc) + timedelta(seconds=RESET_INTERVAL)
        timestamp = int(next_reset.timestamp())

        eur, usd = await get_ltc_price()

        for cid in CHANNEL_IDS:
            try:
                channel = await client.fetch_channel(cid)
                await channel.send(embed=create_embed(timestamp, eur, usd))
            except Exception as e:
                print("❌ Erreur send:", e)

        await asyncio.sleep(RESET_INTERVAL)

        new_channels = []

        for cid in CHANNEL_IDS:
            try:
                channel = await client.fetch_channel(cid)
            except:
                print("❌ Channel déjà supprimé:", cid)
                continue

            new_channel = await nuke_channel(channel)

            if new_channel:
                new_channels.append(new_channel.id)

        if new_channels:
            CHANNEL_IDS.clear()
            CHANNEL_IDS.extend(new_channels)


@client.event
async def on_ready():
    global session
    session = aiohttp.ClientSession()

    print(f"✅ Connecté en tant que {client.user}")
    client.loop.create_task(main_loop())


# 🔥 protection crash + restart auto
while True:
    try:
        client.run(TOKEN)
    except Exception as e:
        print("Crash détecté:", e)
        asyncio.sleep(5)
