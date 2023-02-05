import inspect

import discord

from discord.ext import commands
from discord.commands import slash_command, Option

class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(description="Simple manual for using this bot")
    async def help(
        self, ctx,
        command: Option(str, "command", required=False)
    ):
        handler = getattr(self.bot, 'cmd_help', None)
        handler_kwargs = {}
        handler_kwargs["author"] = ctx.author
        handler_kwargs["channel"] = ctx.channel
        handler_kwargs["other"] = [command]

        response = await handler(**handler_kwargs)     

        if isinstance(response, tuple):
            await ctx.send_response(embed=response[0], view=response[1])
            return
        await ctx.send_response(embed=response)

    @slash_command(description="Get client latency")
    async def ping(
        self, ctx, 
    ):
        handler = getattr(self.bot, 'cmd_ping', None)
        response = await handler()
        await ctx.send_response(embed=response)

    @slash_command(description="Get user id")
    async def id(
        self, ctx, 
        user: Option(discord.User, "User", required=False)
    ):
        if not user:
            user = ctx.author

        handler = getattr(self.bot, 'cmd_id', None)
        handler_kwargs = {}
        handler_kwargs["author"] = None
        handler_kwargs["user_mentions"] = [user.id]

        response = await handler(**handler_kwargs)

        await ctx.send_response(embed=response)

def setup(bot):
    bot.add_cog(Slash(bot))