import discord
import asyncio
import aiohttp
import os
from datetime import datetime, timedelta, timezone

# 🔐 TOKEN sécurisé (Render)
TOKEN = os.getenv("TOKEN")

CHANNEL_IDS = [
    1502239386627084369,
    1502239382789165058
]

RESET_INTERVAL = 3600  # secondes

intents = discord.Intents.default()
client = discord.Client(intents=intents)

session = None


# 💰 LTC LIVE
async def get_ltc_price():
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=litecoin&vs_currencies=usd,eur"
        async with session.get(url) as resp:
            data = await resp.json()
            eur = round(data["litecoin"]["eur"], 2)
            usd = round(data["litecoin"]["usd"], 2)
            return eur, usd
    except Exception as e:
        print("❌ API error:", e)
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
            "[Learn More About Fluxify Exchange](https://fluxify.space)\n\n"
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


# 💣 NUKE + garde position
async def nuke_channel(channel):
    try:
        position = channel.position
        category = channel.category
        name = channel.name
        new_channel = await channel.clone()
        await channel.delete()
        await new_channel.edit(position=position, category=category)
        print("💣 Nuke OK:", name)
        return new_channel
    except Exception as e:
        print("❌ ERREUR NUKE:", e)
        return None


# 🔁 LOOP PRINCIPALE
async def main_loop():
    print("🚀 LOOP START")

    # 🔥 nuke initial
    new_channels = []
    for cid in CHANNEL_IDS:
        try:
            channel = await client.fetch_channel(cid)
            new_channel = await nuke_channel(channel)
            if new_channel:
                new_channels.append(new_channel.id)
        except Exception as e:
            print("❌ Channel error:", e)

    if new_channels:
        CHANNEL_IDS.clear()
        CHANNEL_IDS.extend(new_channels)

    print("Channels actifs:", CHANNEL_IDS)

    # 🔁 boucle infinie
    while True:
        next_reset = datetime.now(timezone.utc) + timedelta(seconds=RESET_INTERVAL)
        timestamp = int(next_reset.timestamp())

        eur, usd = await get_ltc_price()

        # 📤 envoi embed
        for cid in CHANNEL_IDS:
            try:
                channel = await client.fetch_channel(cid)
                await channel.send(embed=create_embed(timestamp, eur, usd))
            except Exception as e:
                print("❌ Send error:", e)

        await asyncio.sleep(RESET_INTERVAL)

        # 💣 nuke cycle
        new_channels = []
        for cid in CHANNEL_IDS:
            try:
                channel = await client.fetch_channel(cid)
                new_channel = await nuke_channel(channel)
                if new_channel:
                    new_channels.append(new_channel.id)
            except Exception as e:
                print("❌ Nuke loop error:", e)

        if new_channels:
            CHANNEL_IDS.clear()
            CHANNEL_IDS.extend(new_channels)


# 🚀 READY
@client.event
async def on_ready():
    global session
    session = aiohttp.ClientSession()
    print(f"✅ Connecté en tant que {client.user}")
    client.loop.create_task(main_loop())


# ▶️ LANCEMENT
client.run(TOKEN)
