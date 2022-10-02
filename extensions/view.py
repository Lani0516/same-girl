import discord

from discord import SelectOption
from discord.ext import commands
from discord.ui import View, select

class HelpPrimary(commands.Cog, View):
    def __init__(self, *items, timeout=180, bot, author, channel):
        self.bot = bot
        self.author = author
        self.channel = channel
        super().__init__(*items, timeout=timeout)
        print(self.bot)

    @select(
        placeholder="help command",
        min_values=1, max_values=1,
        options=[
            SelectOption(
                label="General",
                value="docs",
                description="docs for everyone"
            ),
            SelectOption(
                label="Voice",
                value="help",
                description="join a vchannel and enjoy"
            )
        ]
    )
    async def select_callback(self, select, interaction):
        embed = await self.bot.cmd_help(self.author, self.channel, select.values)
        await interaction.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(HelpPrimary(bot))