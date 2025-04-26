import nextcord
import json
import time
from nextcord.ext import commands
from mcstatus import JavaServer, BedrockServer

class Status(commands.Cog):
    def __init__(self, client):
        self.client = client
        with open('config.json') as config:
            self.config = json.load(config)

    @commands.command()
    async def status(self, ctx):
        """Shows the current status of all servers in real-time"""
        await ctx.message.add_reaction('⏳')
        
        embed = nextcord.Embed(
            title=f"{self.config['message_title']} - Real-time status",
            description=self.config['message_description'],
            color=nextcord.Colour.blue()
        )

        for server in self.config["servers_to_ping"]:
            if server["is_maintenance"]:
                embed.add_field(name=server['server_name'], value=f"🟠 MAINTENANCE", inline=False)
                continue
                
            try:
                if server["is_bedrock"]:
                    status = BedrockServer.lookup(f"{server['server_ip']}:{server['port']}").status()
                    players_online = status.players.online
                    embed.add_field(name=server['server_name'], 
                                    value=f"🟢 ONLINE ({players_online} players)", 
                                    inline=False)
                else:
                    status = JavaServer.lookup(f"{server['server_ip']}:{server['port']}").status()
                    players_online = status.players.online
                    embed.add_field(name=server['server_name'], 
                                    value=f"🟢 ONLINE ({players_online} players)", 
                                    inline=False)
                    
                # Add player list if available and players are online
                if players_online > 0 and hasattr(status.players, 'sample') and status.players.sample:
                    player_names = [player.name for player in status.players.sample]
                    if player_names:
                        embed.add_field(
                            name=f"Players on {server['server_name']}",
                            value="• " + "\n• ".join(player_names[:10]) + 
                                  (f"\n*...and {players_online - 10} more*" if players_online > 10 else ""),
                            inline=True
                        )
            except Exception as e:
                embed.add_field(name=server['server_name'], value=f"🔴 OFFLINE", inline=False)
        
        embed.set_footer(text=f"Requested by {ctx.author} • {time.strftime('%d/%m/%y %H:%M:%S')}")
        await ctx.message.remove_reaction('⏳', self.client.user)
        await ctx.message.add_reaction('✅')
        await ctx.send(embed=embed)

async def setup(client):
    await client.add_cog(Status(client))