# bot.py

import os
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
API_BASE = os.getenv("API_BASE", "http://127.0.0.1:5000/api")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

async def fetch_json(session, method, url, **kwargs):
    async with session.request(method, url, **kwargs) as resp:
        if resp.status >= 400:
            text = await resp.text()
            raise Exception(f"API error: {resp.status} {text}")
        return await resp.json()

# ---------------- MENU ----------------
@tree.command(name="menu", description="Show menu (optionally provide category)")
@app_commands.describe(category="Optional category like Tacos, Burritos")
async def menu(interaction: discord.Interaction, category: str = None):
    await interaction.response.defer() 
    params = {"limit": 8}  # fetch only 8 items by default
    if category:
        params['category'] = category

    async with aiohttp.ClientSession() as session:
        try:
            data = await fetch_json(session, "GET", f"{API_BASE}/menu", params=params)
        except Exception as e:
            await interaction.followup.send(f"Error fetching menu: {e}")
            return

    if not data:
        await interaction.followup.send("No items found.")
        return

    embed = discord.Embed(title=f"Menu{(' - ' + category) if category else ''}")
    for it in data:
        name = it.get("name")
        desc = it.get("description") or "No description"
        price = it.get("price", 0.0)
        embed.add_field(name=f"{name} — ${price:.2f}", value=desc, inline=False)

    await interaction.followup.send(embed=embed)

# ---------------- ITEM ----------------
@tree.command(name="item", description="Get details for a menu item")
@app_commands.describe(item_name="Name of the menu item (e.g., Crunchwrap Supreme)")
async def item(interaction: discord.Interaction, item_name: str):
    await interaction.response.defer()
    async with aiohttp.ClientSession() as session:
        try:
            data = await fetch_json(session, "GET", f"{API_BASE}/menu/item/{item_name}")
        except Exception as e:
            await interaction.followup.send(f"Item not found or error: {e}")
            return

    embed = discord.Embed(title=data.get("name"))
    embed.add_field(name="Category", value=data.get("category"), inline=True)
    embed.add_field(name="Price", value=f"${data.get('price', 0.0):.2f}", inline=True)
    embed.add_field(name="Calories", value=str(data.get("calories") or "N/A"), inline=True)
    if data.get("description"):
        embed.description = data.get("description")

    await interaction.followup.send(embed=embed)

# ---------------- DEALS ----------------
@tree.command(name="deals", description="Show active deals")
async def deals(interaction: discord.Interaction):
    await interaction.response.defer()
    async with aiohttp.ClientSession() as session:
        try:
            data = await fetch_json(session, "GET", f"{API_BASE}/deals")
        except Exception as e:
            await interaction.followup.send(f"Error fetching deals: {e}")
            return

    if not data:
        await interaction.followup.send("No active deals right now.")
        return

    embed = discord.Embed(title="Active Deals")
    for d in data:
        embed.add_field(name=d.get("title"), value=d.get("details") or "No details", inline=False)

    await interaction.followup.send(embed=embed)

# ---------------- ORDER ----------------
@tree.command(name="order_add", description="Add an item to your simulated order")
@app_commands.describe(item_name="Menu item name", quantity="Quantity to add")
async def order_add(interaction: discord.Interaction, item_name: str, quantity: int = 1):
    await interaction.response.defer()
    payload = {"discord_user_id": str(interaction.user.id), "item_name": item_name, "quantity": quantity}

    async with aiohttp.ClientSession() as session:
        try:
            res = await fetch_json(session, "POST", f"{API_BASE}/order/add", json=payload)
        except Exception as e:
            await interaction.followup.send(f"Error adding to order: {e}")
            return

    await interaction.followup.send(f"Added {quantity} x {item_name} to your order.")

@tree.command(name="order_view", description="View your current simulated order")
async def order_view(interaction: discord.Interaction):
    await interaction.response.defer()
    params = {"discord_user_id": str(interaction.user.id)}

    async with aiohttp.ClientSession() as session:
        try:
            data = await fetch_json(session, "GET", f"{API_BASE}/order/view", params=params)
        except Exception as e:
            await interaction.followup.send(f"Error viewing order: {e}")
            return

    items = data.get("items", [])
    if not items:
        await interaction.followup.send("Your order is empty.")
        return

    embed = discord.Embed(title="Your Order")
    for it in items:
        embed.add_field(
            name=f"{it['name']} x{it['quantity']}",
            value=f"Subtotal: ${it['subtotal']:.2f}",
            inline=False
        )
    embed.add_field(name="Total", value=f"${data.get('total', 0.0):.2f}")
    await interaction.followup.send(embed=embed)

@tree.command(name="order_checkout", description="Checkout your current simulated order")
async def order_checkout(interaction: discord.Interaction):
    await interaction.response.defer()
    payload = {"discord_user_id": str(interaction.user.id)}

    async with aiohttp.ClientSession() as session:
        try:
            res = await fetch_json(session, "POST", f"{API_BASE}/order/checkout", json=payload)
        except Exception as e:
            await interaction.followup.send(f"Error checking out: {e}")
            return

    await interaction.followup.send("Checked out your order. (Simulation only — no payment processed)")

# ---------------- FEEDBACK ----------------
@tree.command(name="feedback", description="Send feedback about the bot")
@app_commands.describe(message="Your feedback message")
async def feedback(interaction: discord.Interaction, message: str):
    await interaction.response.defer()
    payload = {"discord_user_id": str(interaction.user.id), "message": message}

    async with aiohttp.ClientSession() as session:
        try:
            res = await fetch_json(session, "POST", f"{API_BASE}/feedback", json=payload)
        except Exception as e:
            await interaction.followup.send(f"Error sending feedback: {e}")
            return

    await interaction.followup.send("Thanks for your feedback!")

# ---------------- BOT READY ----------------
@bot.event
async def on_ready():
    try:
        await tree.sync()
        print(f"Logged in as {bot.user} (id: {bot.user.id}) — Slash commands synced.")
        print(f"API base: {API_BASE}")
    except Exception as e:
        print("Failed to sync commands:", e)

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("Please set DISCORD_TOKEN in the environment.")
        exit(1)
    bot.run(DISCORD_TOKEN)

