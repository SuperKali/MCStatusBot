import asyncio
import nextcord
import time
import json
import os

from nextcord.ext import commands
from mcstatus import JavaServer, BedrockServer
from colorama import init, Fore, Style, Back
from apscheduler.schedulers.asyncio import AsyncIOScheduler

with open('config.json') as config_file:
    config = json.load(config_file)

client = commands.Bot(command_prefix=config["bot_prefix"], help_command=None, intents=nextcord.Intents.all())

bot_token = config['bot_token']

count_all_servers = {}

@client.event
async def on_ready():

    # initializing terminal text color
    init(autoreset=True)

    # Initialize the status of the bot in the presence
    await client.change_presence(status=nextcord.Status.online, activity=nextcord.Activity(type=nextcord.ActivityType.playing, name="...loading"))


    # Check if you have configured the discord server id
    server_id = client.get_guild(int(config['server_id']))
    if server_id is None:
        print(f"[{time.strftime('%d/%m/%y %H:%M:%S')}] ERROR: The server_id set in the configuration file is invalid!")
        return 0

    # Check if you have configured the channel id where it will write the status
    check_channel_status = server_id.get_channel(int(config['channel_status_id']))
    if check_channel_status is None:
        print(f"[{time.strftime('%d/%m/%y %H:%M:%S')}] ERROR: The channel_status_id set in the configuration file is invalid!")


    # Check if you have configured the owner id
    owner_id = client.get_user(int(config['owner_id']))
    if owner_id is None:
        print(f"[{time.strftime('%d/%m/%y %H:%M:%S')}] ERROR: The owner_id set in the configuration file is invalid!")

    global enabled_cogs
    # Search all cogs
    for i in os.listdir('./cogs'):
        if i.endswith('.py'):
            client.load_extension(f'cogs.{i[:-3]}')
            enabled_cogs = i


    print(Style.NORMAL + Fore.LIGHTMAGENTA_EX + "╔═══════════════════╗")
    print(Style.NORMAL + Fore.GREEN + "Name: " + Fore.RESET + Fore.RED + "MCStatusBot")
    print(Style.NORMAL + Fore.GREEN + "Version: " + Fore.RESET + Fore.RED + "v1.3")
    print(Style.NORMAL + Fore.GREEN + "Refresh Time: " + Fore.RESET + Fore.RED + str(config["refresh_time"]) + " seconds")
    print(Style.NORMAL + Fore.GREEN + "Bot Status: " + Fore.RESET + Fore.RED + "Online")
    print(Style.NORMAL + Fore.GREEN + "Enabled Cogs: " + Fore.RESET + Fore.RED + str(enabled_cogs.replace('.py', '')))
    print(Style.NORMAL + Fore.GREEN + "Support: " + Fore.RESET + Fore.RED + "https://discord.superkali.me")
    print(Style.NORMAL + Fore.LIGHTMAGENTA_EX + "╚═══════════════════╝")



async def update_servers_status():
    if config["is_maintenance_status"] == False:
        server_id = client.get_guild(config['server_id'])
        if server_id is not None:
            channel_message = server_id.get_channel(config['channel_status_id'])
            if channel_message is not None:

                txt = nextcord.Embed(title=config['message_title'], description=f"{config['message_description']}\n", colour=nextcord.Colour.orange())

                with open('data.json') as data_file:
                    data = json.load(data_file)

                with open('config.json') as server_list:
                    data_list = json.load(server_list)
                try:

                    pinger_message = await channel_message.fetch_message(int(data['pinger_message_id']))
                    checking = nextcord.Embed(description=config["message_checking_embed"], colour=nextcord.Colour.orange())
                    await pinger_message.edit(embed=checking)

                except nextcord.errors.NotFound:
                    return print(Style.NORMAL + Fore.RED + "[MCStatusBot] " + Fore.RESET + Fore.CYAN + f"The bot is not configured yet.. missing the command {config['bot_prefix']}createstatusmsg on the text channel")
                    

                for servers in data_list["servers_to_ping"]:
                    if servers["is_maintenance"] == False:
                        try:
                            if servers["is_bedrock"]:
                                check = BedrockServer.lookup(f"{servers['server_ip']}:{servers['port']}").status().players.online
                                txt.add_field(name=servers['server_name'], value=f"🟢 ONLINE ({check} players)", inline=False)
                                count_all_servers[servers['server_name']] = {"online": check, "count_on_presence": servers["count_on_presence"], "status": True}
                            else:
                                check = JavaServer.lookup(f"{servers['server_ip']}:{servers['port']}").status().players.online
                                txt.add_field(name=servers['server_name'], value=f"🟢 ONLINE ({check} players)", inline=False)  
                                count_all_servers[servers['server_name']] = {"online": check, "count_on_presence": servers["count_on_presence"], "status": True}
                        except:
                            txt.add_field(name=servers['server_name'], value=f"🔴 OFFLINE", inline=False)
                            count_all_servers[servers['server_name']] = {"online": 0, "count_on_presence": servers["count_on_presence"], "status": False}
                    else:
                        txt.add_field(name=servers['server_name'], value=f"🟠 MAINTENANCE", inline=False)

                server_list.close()

                if config["message_field"] and config["message_field_link"] is not None:
                    txt.add_field(name=config["message_field"], value=config["message_field_link"], inline=False)

                txt.set_footer(text=config["message_footer"].format(date=time.strftime('%d/%m/%y'), time=time.strftime('%H:%M:%S')))

                await pinger_message.edit(embed=txt)
                await send_console_status()
                await update_presence_status()

            else:
                print(f"[{time.strftime('%d/%m/%y %H:%M:%S')}] I could not find the servers status channel")
                return 0
        else:
            print(f"[{time.strftime('%d/%m/%y %H:%M:%S')}] I could not find the indicated discord server.")
            return 0
    else:            
        await client.change_presence(status=nextcord.Status.idle, activity=nextcord.Activity(type=nextcord.ActivityType.playing, name="🟠 Maintenance"))

async def update_presence_status():
    servers = count_all_servers.values()
    status = []
    for value in servers:
        if value.get("count_on_presence", False):
            status.append(int(value.get('online', 0)))

    await client.change_presence(status=nextcord.Status.online, activity=nextcord.Activity(type=nextcord.ActivityType.playing, name=config["presence_name"].format(players=sum(status))))
    count_all_servers.clear()

async def send_console_status():
    servers = count_all_servers.values()
    status = []
    for value in servers:
        status.append(int(value.get("status")))
            
    print(Style.NORMAL + Fore.RED + "[MCStatusBot] " + Fore.RESET + Fore.CYAN + f"Current Status of Servers:")
    print(Style.NORMAL + Fore.RED + "[MCStatusBot] " + Fore.RESET + Fore.CYAN + f"{status.count(True)} Online servers")
    print(Style.NORMAL + Fore.RED + "[MCStatusBot] " + Fore.RESET + Fore.CYAN + f"{status.count(False)} Offline servers")

scheduler = AsyncIOScheduler()
scheduler.add_job(update_servers_status, "interval", seconds=config["refresh_time"])
scheduler.start()


client.run(bot_token)