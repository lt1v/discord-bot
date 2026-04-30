import discord
import asyncio
import aiohttp
import os
from datetime import datetime, timedelta, timezone

TOKEN = os.getenv("TOKEN")

CHANNEL_IDS = [
    1499539348666716251,
    1499539354689994844
]

RESET_INTERVAL = 3600

intents = discord.Intents.default()
client = discord.Client(intents=intents)


# 💰 LTC (safe)
async def get_ltc_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=litecoin&vs_currencies=usd,eur"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                return round(data["litecoin"]["eur"], 2), round(data["litecoin"]["usd"], 2)

    except Exception as e:
        print("API error:", e)
        return "??", "??"


# 🎨 EMBED
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


# 💣 NUKE SAFE
async def nuke_channel(channel):
    try:
        position = channel.position
        category = channel.category

        new_channel = await channel.clone()
        await asyncio.sleep(1)

        await channel.delete()
        await asyncio.sleep(1)

        await new_channel.edit(position=position, category=category)

        print("💣 Nuke OK:", new_channel.name)
        return new_channel

    except Exception as e:
        print("NUKE ERROR:", e)
        return None


# 🔁 LOOP PRINCIPALE
async def main_loop():
    print("🚀 LOOP START")

    await asyncio.sleep(5)  # 🔥 anti rate limit au démarrage

    # 💣 NUKE INITIAL
    new_channels = []

    for cid in CHANNEL_IDS:
        channel = client.get_channel(cid)
        if not channel:
            print("Channel introuvable:", cid)
            continue

        await asyncio.sleep(2)
        new_channel = await nuke_channel(channel)

        if new_channel:
            new_channels.append(new_channel.id)

    if new_channels:
        CHANNEL_IDS.clear()
        CHANNEL_IDS.extend(new_channels)

    print("Channels actifs:", CHANNEL_IDS)

    # 🔁 LOOP
    while True:
        next_reset = datetime.now(timezone.utc) + timedelta(seconds=RESET_INTERVAL)
        timestamp = int(next_reset.timestamp())

        eur, usd = await get_ltc_price()

        for cid in CHANNEL_IDS:
            channel = client.get_channel(cid)
            if channel:
                try:
                    await channel.send(embed=create_embed(timestamp, eur, usd))
                    await asyncio.sleep(1)  # anti spam
                except Exception as e:
                    print("SEND ERROR:", e)

        await asyncio.sleep(RESET_INTERVAL)

        # 💣 NUKE CYCLE
        new_channels = []

        for cid in CHANNEL_IDS:
            channel = client.get_channel(cid)
            if not channel:
                continue

            await asyncio.sleep(2)
            new_channel = await nuke_channel(channel)

            if new_channel:
                new_channels.append(new_channel.id)

        if new_channels:
            CHANNEL_IDS.clear()
            CHANNEL_IDS.extend(new_channels)


# 🚀 READY
@client.event
async def on_ready():
    print(f"✅ Connecté en tant que {client.user}")
    asyncio.create_task(main_loop())


# ▶️ START
if not TOKEN:
    print("❌ TOKEN MANQUANT")
else:
    try:
        client.run(TOKEN)
    except Exception as e:
        print("💥 CRASH:", e)
