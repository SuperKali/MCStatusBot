import nextcord
import json
import sys
import os
from nextcord.ext import commands

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils'))

class Commands(commands.Cog):
    def __init__(self, client):
        self.client = client

        with open('config.json') as config:
            self.config = json.load(config)


    @commands.command()
    async def createstatusmsg(self, ctx):
        if ctx.message.author.id == self.config['owner_id']:
            with open('data.json') as data:
                self.data = json.load(data)

            embed = nextcord.Embed(
                title="MCStatusBot Configured 🎉", 
                description=f"This message will be updated with the status message automatically.", 
                color=nextcord.Colour.blue())

            message = await ctx.send(embed=embed)
            await ctx.message.delete()

            self.data['pinger_message_id'] = message.id
            data_save = open("data.json", "w")
            json.dump(self.data, data_save)
            data_save.close() 
        else:
           await ctx.send("MCStatusBot: You don't have the permission for use this command, only the owner can do this command.")   


    @commands.command()
    async def update(self, ctx):
        """Checks for updates and updates the bot if available"""
        if ctx.message.author.id != self.config['owner_id']:
            return await ctx.send("MCStatusBot: You don't have the permission to use this command, only the owner can do this.")
            
        from update import check_for_update, download_and_install_update
        
        await ctx.send("Checking for updates...")
        update_available, data = check_for_update()
        
        if update_available:
            await ctx.send(f"Update available! Current version: `{data['current_version']}`, Latest version: `{data['latest_version']}`")
            confirmation_msg = await ctx.send("Do you want to install this update? (React with ✅ to confirm)")
            await confirmation_msg.add_reaction("✅")
            
            def check(reaction, user):
                return user == ctx.author and str(reaction.emoji) == "✅" and reaction.message.id == confirmation_msg.id
                
            try:
                await self.client.wait_for('reaction_add', timeout=60.0, check=check)
                
                status_msg = await ctx.send("Installing update...")
                success = download_and_install_update(data)
                
                if success:
                    await status_msg.edit(content="✅ Update installed successfully! Please restart the bot to apply changes.")
                else:
                    await status_msg.edit(content="❌ Update failed. Check logs for more details.")
            except:
                await ctx.send("Update cancelled or timed out.")
        else:
            await ctx.send("You're already running the latest version!")


    @commands.command()
    async def help(self, ctx):
        embed = nextcord.Embed(
            title="Commands of MCStatusBot",
            description=f"",
            color=nextcord.Colour.dark_blue())

        embed.add_field(
            name="User Commands", 
            value=f"`{self.config['bot_prefix']}status` - Get real-time status of all Minecraft servers\n"
                  f"`{self.config['bot_prefix']}help` - Shows this help message",
            inline=False
        )
        
        if ctx.author.id == self.config['owner_id']:
            embed.add_field(
                name="Admin Commands", 
                value=f"`{self.config['bot_prefix']}createstatusmsg` - Create a message that will be updated with server status\n"
                      f"`{self.config['bot_prefix']}update` - Check for and install bot updates",
                inline=False
            )

        embed.set_footer(text="Bot developed by SuperKali#8716")    
        
        await ctx.send(embed=embed)

async def setup(client):
   await client.add_cog(Commands(client))