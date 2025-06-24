
import discord
from discord.ext import commands
import json
import os

# تحميل الداتا
if os.path.exists("data.json"):
    with open("data.json", encoding="utf-8") as f:
        user_data = json.load(f)
else:
    user_data = {}

def save_data():
    with open("data.json", "w", encoding="utf-8") as f:
        json.dump(user_data, f, ensure_ascii=False, indent=2)

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user} جاهز 🔥")

@bot.command()
async def create(ctx, roadmap_name: str, *, args=None):
    if roadmap_name in user_data:
        await ctx.send("⚠️ الرودماب دي موجودة بالفعل.")
        return

    import re
    access_roles = re.findall(r"role:@(\w+)", args or "")
    add_roles = re.findall(r"add:@(\w+)", args or "")
    edit_roles = re.findall(r"edit:@(\w+)", args or "")

    user_data[roadmap_name] = {
        "tasks": {},
        "members": {},
        "permissions": {
            "access": access_roles,
            "add": add_roles,
            "edit": edit_roles
        }
    }

    save_data()
    await ctx.send(
        f"✅ تم إنشاء الرودماب **{roadmap_name}**\n"
        f"👥 access: {', '.join(access_roles) or '❌'}\n"
        f"➕ add: {', '.join(add_roles) or '❌'}\n"
        f"🛠️ edit: {', '.join(edit_roles) or '❌'}"
    )

@bot.command()
async def myroadmaps(ctx):
    member_roles = [role.name.lower() for role in ctx.author.roles]
    matched_roadmaps = []

    for roadmap_name, info in user_data.items():
        access_roles = [r.lower() for r in info["permissions"].get("access", [])]
        if any(role in access_roles for role in member_roles):
            matched_roadmaps.append(roadmap_name)

    if not matched_roadmaps:
        await ctx.send("❌ مفيش رودماب متاحة ليك.")
    else:
        msg = "📌 الرودمابات اللي تقدر تشتغل عليها:\n"
        for name in matched_roadmaps:
            msg += f"• {name}\n"
        await ctx.send(msg)

@bot.command()
async def showroadmap(ctx, roadmap_name: str):
    roadmap = user_data.get(roadmap_name)
    if not roadmap:
        await ctx.send("❌ الرودماب دي مش موجودة.")
        return

    user_roles = [r.name.lower() for r in ctx.author.roles]
    perms = roadmap["permissions"]
    allowed_roles = [
        *perms.get("access", []),
        *perms.get("add", []),
        *perms.get("edit", [])
    ]
    allowed_roles = [r.lower() for r in allowed_roles]

    if not any(role in allowed_roles for role in user_roles):
        await ctx.send("⛔ معندكش صلاحية تشوف الرودماب دي.")
        return

    tasks = roadmap["tasks"]
    if not tasks:
        await ctx.send("📭 الرودماب دي لسه فاضية.")
        return

    msg = f"📋 المهام في **{roadmap_name}**:\n"
    for num, task in tasks.items():
        msg += f"{num}️⃣ {task}\n"

    await ctx.send(msg)

bot.run("YOUR_BOT_TOKEN")
