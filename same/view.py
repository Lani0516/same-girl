from discord import SelectOption
from discord.ext import commands
from discord.ui import View, select

class HelpPrimary(commands.Cog, View):
    def __init__(self, *items, timeout=180, bot, author, channel):
        self.bot = bot
        self.author = author
        self.channel = channel
        super().__init__(*items, timeout=timeout)

    @select(
        placeholder="help command",
        min_values=1, max_values=1,
        options=[
            SelectOption(
                label="🏮 Admin",
                value="gen_admin_cmd_list",
                description="|| maybe join our administators' team someday"
            ),
            SelectOption(
                label="🎏 General",
                value="gen_general_cmd_list",
                description="|| go grab some coco before blaming bad design"
            ),
            SelectOption(
                label="🍻 Voice",
                value="gen_voice_cmd_list",
                description="|| let's sit down and have a long long chat"
            )
        ]
    )
    async def select_callback(self, select, interaction):
        target = getattr(self.bot, select.values[0])
        embed = await target(self.bot)
        await interaction.response.send_message(embed=embed)

class HelpAdmin(commands.Cog, View):
    def __init__(self, *items, timeout=180, bot):
        self.bot = bot
        super().__init__(*items, timeout=timeout)

    @select(
        placeholder="help command",
        min_values=1, max_values=1,
        options=[
            SelectOption(
                label="✉️ Send",
                value=" ",
                description="|| maybe join our administators' team someday"
            ),
            SelectOption(
                label="🪄 Clear",
                value="gen_general_cmd_list",
                description="|| go grab some coco before blaming bad design"
            )
        ]
    )
    async def select_callback(self, select, interaction):
        target = getattr(self.bot, select.values[0])
        embed = await target(self.bot)
        await interaction.response.send_message(embed=embed)

def setup(bot):
    bot.add_cog(HelpPrimary(bot))