import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

load_dotenv()

# ====================== الإعدادات ======================
TOKEN = os.getenv("TOKEN")

# الرتب
MEMBER_ROLE_ID = 1524577434169774140
BOT_ROLE_ID = 1527108181719781526
STAFF_ROLE_ID = 1540513092696277072

# الرومات
WELCOME_CHANNEL_ID = 1524572016274047087
AUTO_CHANNELS = [
    1524572016274047087,  # Channel1
    1524573430358343872,  # Channel2
]

# الرياكشنات
REACTIONS = [
    "<a:emoji:1544873892395618454>",
]

# الصورة الافتراضية
DEFAULT_IMAGE = "https://i.imgur.com/3ZQ3Z3Q.png"

# ======================================================

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.image_url = DEFAULT_IMAGE


# ================== تسجيل أوامر السلاش ==================
@bot.event
async def on_ready():
    print(f"✅ البوت شغال باسم: {bot.user}")
    try:
        await bot.tree.sync()  # يسجل الأوامر في كل السيرفرات (ياخذ ساعة عشان يظهر)
        print("✅ تم تسجيل أوامر السلاش بنجاح!")
    except Exception as e:
        print(f"❌ خطأ في تسجيل السلاش: {e}")


# ================== حدث دخول عضو جديد ==================
@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild

    # رتب تلقائية
    if member.bot:
        role = guild.get_role(BOT_ROLE_ID)
    else:
        role = guild.get_role(MEMBER_ROLE_ID)

    if role:
        try:
            await member.add_roles(role, reason="Auto Role")
        except Exception as e:
            print(f"خطأ في إعطاء الرتبة: {e}")

    # رسالة الترحيب
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        member_count = guild.member_count
        embed = discord.Embed(
            title="Welcome To The Server",
            description=(
                f"**We Hope You Enjoy Here**\n\n"
                f"You Are Member **#{member_count}**"
            ),
            color=0x2b2d31
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"ID: {member.id}")
        try:
            await channel.send(content=f"{member.mention}", embed=embed)
        except Exception as e:
            print(f"خطأ في الترحيب: {e}")


# ================== حدث قراءة الرسائل ==================
@bot.event
async def on_message(message: discord.Message):
    if message.author.bot:
        return

    # حماية الروابط
    content_lower = message.content.lower()
    has_link = any(x in content_lower for x in ["http://", "https://", "www.", "discord.gg/", "discord.com/invite"])

    if has_link:
        has_staff = any(role.id == STAFF_ROLE_ID for role in message.author.roles)
        if not has_staff:
            try:
                await message.delete()
                await message.channel.send(
                    f"{message.author.mention} ممنوع إرسال الروابط.",
                    delete_after=5
                )
            except:
                pass
            return

    # الرد التلقائي + الرياكشن
    if message.channel.id in AUTO_CHANNELS:
        for emoji in REACTIONS:
            try:
                await message.add_reaction(emoji)
            except Exception as e:
                print(f"خطأ في الرياكشن: {e}")

        try:
            await message.reply(bot.image_url, mention_author=False)
        except Exception as e:
            print(f"خطأ في الرد بالصورة: {e}")

    await bot.process_commands(message)


# ================== أوامر البريفكس (النظام القديم) ==================
@bot.command(name="ping")
async def prefix_ping(ctx):
    await ctx.send(f"🏓 Pong! {round(bot.latency * 1000)}ms")


@bot.command(name="setimage")
async def prefix_setimage(ctx: commands.Context, url: str):
    if not any(role.id == STAFF_ROLE_ID for role in ctx.author.roles):
        await ctx.send("ما عندكِ صلاحية.", delete_after=5)
        return

    if not url.startswith("http"):
        await ctx.send("الرابط لازم يبدأ بـ http", delete_after=5)
        return

    bot.image_url = url
    await ctx.send(f"تم تغيير صورة الرد التلقائي بنجاح ✅\n{url}")


# ================== أوامر السلاش (النظام الجديد) ==================
@bot.tree.command(name="ping", description="يعرض سرعة الاتصال بالبوت")
async def slash_ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"🏓 Pong! {round(bot.latency * 1000)}ms")


@bot.tree.command(name="setimage", description="تغيير صورة الرد التلقائي (للمشرفين فقط)")
async def slash_setimage(interaction: discord.Interaction, url: str):
    # التحقق من صلاحية المشرف
    if not any(role.id == STAFF_ROLE_ID for role in interaction.user.roles):
        await interaction.response.send_message("ما عندك صلاحية.", ephemeral=True)
        return

    if not url.startswith("http"):
        await interaction.response.send_message("الرابط لازم يبدأ بـ http", ephemeral=True)
        return

    bot.image_url = url
    await interaction.response.send_message(f"✅ تم تغيير الصورة بنجاح\n{url}")


# ================== تشغيل البوت ==================
bot.run(TOKEN)
