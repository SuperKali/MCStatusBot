import discord
import json
from discord.ext import commands

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

            embed = discord.Embed(
                title="MCStatusBot Configured 🎉", 
                description=f"This message will be updated with the status message automatically.", 
                color=discord.Colour.blue())

            message = await ctx.send(embed=embed)
            await ctx.message.delete()

            self.data['pinger_message_id'] = message.id
            data_save = open("data.json", "w")
            json.dump(self.data, data_save)
            data_save.close() 
        else:
            ctx.send("MCStatusBot: You don't have the permission for use this command, only the owner can do this command.")   


    @commands.command()
    async def help(self, ctx):
        embed = discord.Embed(
            title="Commands of MCStatusBot",
            description=f"{self.config['bot_prefix']}createstatusmsg - allow you to create a message where will be configured the status message.",
            color=discord.Colour.dark_blue())

        embed.set_footer(text="Bot developed by SuperKali#8716")    
        
        await ctx.send(embed=embed)

def setup(client):
    client.add_cog(Commands(client))