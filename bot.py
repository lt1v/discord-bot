import discord
import asyncio
import aiohttp
import os
from datetime import datetime, timedelta, timezone

TOKEN = os.getenv("TOKEN")

CHANNEL_IDS = [
    1499549229121667155,
    1499549243482968064
]

RESET_INTERVAL = 3600

intents = discord.Intents.default()
client = discord.Client(intents=intents)

# 🔒 sécurité
started = False
nuking = False


# 💰 LTC
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
        ),
        inline=False
    )

    embed.timestamp = datetime.now(timezone.utc)
    embed.set_footer(text="Fluxify System")

    return embed


# 💣 NUKE SAFE
async def nuke_channel(channel):
    try:
        position = channel.position
        category = channel.category
        name = channel.name

        new_channel = await channel.clone()
        await asyncio.sleep(1)

        try:
            await channel.delete()
        except Exception as e:
            print("DELETE FAIL:", e)

        await asyncio.sleep(1)

        await new_channel.edit(position=position, category=category)

        print("💣 Nuke OK:", name)
        return new_channel

    except Exception as e:
        print("NUKE ERROR:", e)
        return None


# 🔁 LOOP
async def main_loop():
    global nuking

    print("🚀 LOOP START")

    await asyncio.sleep(5)

    while True:
        if nuking:
            await asyncio.sleep(2)
            continue

        nuking = True

        next_reset = datetime.now(timezone.utc) + timedelta(seconds=RESET_INTERVAL)
        timestamp = int(next_reset.timestamp())

        eur, usd = await get_ltc_price()

        # 📤 envoi embed
        for cid in CHANNEL_IDS:
            channel = client.get_channel(cid)
            if channel:
                try:
                    await channel.send(embed=create_embed(timestamp, eur, usd))
                    await asyncio.sleep(1)
                except Exception as e:
                    print("SEND ERROR:", e)

        await asyncio.sleep(RESET_INTERVAL)

        # 💣 NUKE
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

        nuking = False


# 🚀 READY
@client.event
async def on_ready():
    global started

    if started:
        return

    started = True

    print(f"✅ Connecté en tant que {client.user}")
    asyncio.create_task(main_loop())


# ▶️ START
if not TOKEN:
    print("❌ TOKEN MANQUANT")
else:
    try:
        client.run(TOKEN)
    except Exception as e:
        print("CRASH:", e)
