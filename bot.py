import discord
from discord.ext import commands
import requests

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='', intents=intents)

LOG_CHANNEL_ID = 1175807161599791174
WEBHOOK_URL = 'https://discord.com/api/webhooks/1175807301668581448/ycmk6-W2XmWwRBYEI850MQUI4_xkJdpOB5GFKzVlWRpzexJNYG3rhaMdYVU6twAxGdZk'

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_message(message):
    if message.mentions:
        member = message.mentions[0]

        channel_id = 1174433494668148776
        if message.channel.id == channel_id:
            role_name = 'Whitelist'
            role = discord.utils.get(message.guild.roles, name=role_name)

            # ตรวจสอบว่าผู้ถูกแท็กมีบทบาท 'RequiredRole' หรือไม่
            required_role_name = 'กรอกข้อมูลแล้ว'
            required_role = discord.utils.get(message.guild.roles, name=required_role_name)

            # ตรวจสอบว่าไม่มีบทบาท 'Whitelist' ในผู้ใช้
            if role and required_role and required_role in member.roles and role not in member.roles:
                # ตรวจสอบว่าบอทได้ทำการเพิ่มบทบาท "Whitelist" หรือไม่
                added_by_bot = False
                async for entry in message.guild.audit_logs(action=discord.AuditLogAction.role_create, limit=5):
                    if entry.target == member and entry.user == bot.user:
                        added_by_bot = True
                        break

                # ถ้าบอทไม่ได้ทำการเพิ่มบทบาท "Whitelist" ให้
                if not added_by_bot:
                    # ตรวจสอบว่ามีการยืนยันบทบาท Whitelist แล้วหรือไม่
                    confirmed_role_name = 'Whitelist'
                    confirmed_role = discord.utils.get(message.guild.roles, name=confirmed_role_name)

                    if confirmed_role not in member.roles:
                        # เพิ่มบทบาท Whitelist
                        await member.add_roles(role)

                        # ส่งข้อมูลไปยังห้อง log ด้วย Webhook
                        await send_to_log_channel(member, message.author)

                        # ลบบทบาท "กรอกข้อมูลแล้ว" หากบอทได้เพิ่มบทบาท Whitelist ให้แล้ว
                        if required_role in member.roles:
                            await member.remove_roles(required_role)

                        # เพิ่มบทบาทยืนยัน Whitelist
                        await member.add_roles(confirmed_role)

                        # ส่งข้อความยืนยันบทบาท Whitelist
                        confirmation_message = f'ยืนยันยศ {role_name} ให้ {member.mention} สำเร็จแล้ว'
                        await message.channel.send(confirmation_message)
                        return  # ตรวจสอบเพิ่มเติมเพื่อป้องกันการทำงานซ้ำ

            elif required_role not in member.roles and role not in member.roles:
                # ถ้าไม่มีบทบาทที่ต้องการและไม่มีบทบาท Whitelist
                await message.channel.send("กรุณากรอกข้อมูลไวท์ลีสต์ก่อนที่จะทำการยืนยันไวท์ลีสต์")

            elif role in member.roles and required_role not in member.roles:
                # ถ้ามีบทบาท Whitelist อยู่แล้วและไม่มีบทบาท 'กรอกข้อมูลแล้ว'
                if role not in member.roles:  # ตรวจสอบว่าบทบาท Whitelist ไม่ได้ถูกเพิ่มโดยบอท
                    await message.channel.send(f'{member.mention} มียศ Whitelist อยู่แล้ว')

    await bot.process_commands(message)

async def send_to_log_channel(member, author):
    # สร้างข้อความที่จะส่งไปยังห้อง log
    log_message = f'Discord ID: {author.id} ได้ทำการยืนยันบทบาทให้ {member.mention}'

    # สร้าง payload สำหรับ Webhook
    payload = {
        'content': log_message
    }

    # ส่งข้อมูลไปยังห้อง log ผ่าน Webhook
    response = requests.post(WEBHOOK_URL, json=payload)
    print(response.text)  # ให้แสดงข้อมูลที่ได้จากการส่ง Webhook ใน Console

# รัน bot ด้วย TOKEN ของคุณ
bot.run('MTE3NTUwNzYzMzQyMDEwNzgwNg.GD5eJe.TqH-n1LsTyv9mNwCj2mfxyvpDPgn5BY0wCD2AE')
