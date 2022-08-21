import os
import sys
import time
import asyncio
import inspect
import traceback

import aiohttp
import discord

from modules.exception import JustWrong

intents = discord.Intents.all()
intents.typing = False
intents.presences = False

class TestBot(discord.Client):
    def __init__(self):
        # TODO: log it in .ini file
        self.pg_con = None
        self.BOTVERSION = 'v0.1.0'
        self.embed_color = (191, 120, 120)
        self.prefix = '>>'
        self.game = discord.Game("/help || 加入SharkParty")
        self.token = 'MTAwMzkyNzYwMTY3NDQ2MTMwNA.GNkOdj.xQ-b4SwaXRPLYTglCOjZM94OTNgAUyW86h59IM'

        self.vchannel_blacklist = [
            1008422710692565082, # decorator
            1008422750781722716, # decorator
            1008439019731947550
        ]
        self.nchannel = 1010557329579724864

        super().__init__(intents=intents)

        self.colour = discord.Colour(value=000000)

    def cleanup(self):
        self.loop.run_until_complete(asyncio.run(self.close()))
        self.loop.close()

    def run(self):
        try:
            self.loop.run_until_complete(self.start(self.token))
        except discord.errors.LoginFailure:
            print(
                "Client cannot login...\n",
                "Make sure to check whether the bot's token is in the config.ini file.\n",
                "Or your token just unavailable.\n"
            )
        finally:
            self.cleanup()

    async def close(self):
        print("\nClient is shutting down...")
        return await super().close()

    async def on_ready(self):
        # change the presence into .ini
        await self.change_presence(activity=self.game)

        _clear = None

        if sys.platform.startswith('cygwin') or sys.platform.startswith('win32'):
            _clear = lambda: os.system('cls')
        else:
            _clear = lambda: os.system('clear')

        _clear()

        await self.wait_until_ready()

        print("      ___           ___           ___           ___           ___     ",
              "     /\  \         /\__\         /\  \         /\  \         /\__\    ",
              "    /::\  \       /:/  /        /::\  \       /::\  \       /:/  /    ",
              "   /:/\ \  \     /:/__/        /:/\:\  \     /:/\:\  \     /:/__/     ",
              "  _\:\~\ \  \   /::\  \ ___   /::\~\:\  \   /::\~\:\  \   /::\__\____ ",
              " /\ \:\ \ \__\ /:/\:\  /\__\ /:/\:\ \:\__\ /:/\:\ \:\__\ /:/\:::::\__\\",
              " \:\ \:\ \/__/ \/__\:\/:/  / \/__\:\/:/  / \/_|::\/:/  / \/_|:|~~|~   ",
              "  \:\ \:\__\        \::/  /       \::/  /     |:|::/  /     |:|  |    ",
              "   \:\/:/  /        /:/  /        /:/  /      |:|\/__/      |:|  |    ",
              "    \::/  /        /:/  /        /:/  /       |:|  |        |:|  |    ",
              "     \/__/         \/__/         \/__/         \|__|         \|__|    ", sep='\n', end='\n\n')

        print(f'\n{str(self.user)[:-5]} Status | Online\n')

##############################################################

    async def cmd_help(self):
        pass

    async def cmd_ping(self):
        """
        Usage:
            {command_prefix}ping
        Example:    
            Getting Client Latency | ping
        Change:
            None
        Name:
            ping
        Return:
            Client Latency (ms)
        """
        emoji_prefix = '<:announcement:1005815395967565834>'

        embed = self.gen_embed(style='empty')
        embed.title = f'{emoji_prefix} {int(round(self.latency, 3)*1000)}ms'
        
        return embed

    async def cmd_avatar(self, author, other):
        """
        Usage:
            {command_prefix}avatar [@User]
        Example:
            Getting your own avatar | avatar
            Getting @LandedWriter's avatar | avatar @LandedWriter
        Change:
            None
        Name:
            avatar
        Return:
            User Avatar
        """
        emoji_prefix = '<:announcement:1005815395967565834>'

        if other:
            try:
                author = self.get_user(int(other[0][2:-1]))
            except ValueError:
                author = None

        if not author:
            raise JustWrong("invalid user mention")

        embed = self.gen_embed(style='empty', imp=True)
        embed.title = f'{emoji_prefix} {author}'
        embed.set_image(url=author.avatar.url)

        return embed

    async def cmd_sum(self, other):
        """
        Usage:
            {command_prefix}sum
        Example:
            Getting the sum of 2 nums | sum 1 2
            Getting the sum of multiple nums | sum 1 5 10 15 20
        Change:
            None
        Name:
            sum
        Return:
            Sum of Input Nums
        """
        emoji_prefix = '<:announcement:1005815395967565834>'

        embed = self.gen_embed(style='empty')
        signal = False

        if len(other) <= 1:
            raise JustWrong("please input more than one number")

        try:
            num = 0
            for i in other:
                num+=int(i)
        except:
            signal = True

        if signal:
            raise JustWrong("wrong input")

        embed.title = f'{emoji_prefix} {num}'

        return embed

    async def cmd_send(self, other):
        """
        Usage:
            {command_prefix}send <message_content> <channel_id>
        Example:
            Send Hello World in Lobby with channel id | send Hello World 1003922992805449780 
        Change:
            None
        Name:
            send
        Return:
            Message Content
        """
        content = channel = None
        
        if len(other) <= 2:
            raise JustWrong("invalid input")

        # other = [message, channel_id[-1]]
        try: channel = self.get_channel(int(other.pop(-1)))  
        except: raise JustWrong("invalid channel id")
        
        if not channel: raise JustWrong("invalid channel id")

        content = ' '.join(other)

        await self.channel_send(
            response=content,
            type='text',
            channel=channel
        )

    # first step for making {command_prefix}help
    async def cmd_docs(self):
        print([i.strip() for i in self.cmd_ping.__doc__.strip().split('\n')])

##############################################################

    async def on_voice_state_update(self, member, before, after):
        join = leave = False

        if before.channel:
            leave = True
        
        if after.channel:
            join = True

        content = str()

        del_signal = False
        
        if join and not leave: # join only
            content, color = f'{member.display_name} 進入了 {str(after.channel)[3:]}', (150, 194, 208)
            
        elif not join and leave: # change
            content, color = f'{member.display_name} 離開了 {str(before.channel)[3:]}', None
            if not before.channel.members:
                del_signal = True

        else: # leave only
            content, color = f'{member.display_name} 由 {str(before.channel)[3:]} 進入了 {str(after.channel)[3:]}', (216, 176, 107)
            if not before.channel.members:
                del_signal = True

        if before.channel.id in self.vchannel_blacklist:
            del_signal = False

        print(f'{member.guild} | {content}')

        embed = self.gen_embed(style='empty', color=color)
        try:
            embed.set_author(name=content, icon_url=member.display_avatar)
        except:
            embed.set_author(name=content, icon_url=member.display_avatar_url)
            print("Try to upgrade your Pycord or Discord.py version.\n")

        if del_signal:
            print(f'{member.guild} | Delete Vchannel | {before.channel}')
            await before.channel.delete()

        await self.channel_send(response=embed, type='embed', channel=self.get_channel(1008425742092214352))

    async def on_message(self, message):
        await self.wait_until_ready()

        if message.author.bot:
            return

        """Nhentai translator"""
        if message.channel.id == self.nchannel:
            kami_no_kotoba = message.content.strip()
            if len(kami_no_kotoba) == 6:
                try:
                    kami_no_kotoba = int(kami_no_kotoba)
                    await self.channel_send(
                        response=f'https://nhentai.net/g/{kami_no_kotoba}',
                        type='text',
                        channel=message.channel
                    )
                    print(f'{message.guild} | {message.author} | generating kami_no_kotoba >> {kami_no_kotoba}')

                    await message.delete()
                    
                    return
                except ValueError:
                    pass

        """Command Reader"""
        # Change the prefix to config someday
        if not message.content.startswith(self.prefix):
            return

        message_content = message.content.strip()

        command, *args = message_content.split(' ')
        command = command[len(self.prefix):].lower().strip()

        if args:
            args = ' '.join(args).lstrip(' ').split(' ')
        else:
            args = []

        if command == 'h': command = "help"

        try:
            target = getattr(self, 'cmd_' + command)
            print(f'{message.guild} | {message.author} | raising command >> {command}')
            if not args == []:
                argsln = ' '.join(args)
                print(f'| {argsln}')

        except AttributeError:
            print(f'{message.guild} | {message.author} | unknown command >> {command}')
            return

        except:
            print()
            traceback.print_exc()
            print("\nRaised unknown error on getting command.\n")

        argspec = inspect.signature(target)
        params = argspec.parameters.copy()
        
        target_kwargs = {}
        if params.pop('message', None):
            target_kwargs['message'] = message
        
        if params.pop('channel', None):
            target_kwargs['channel'] = message.channel

        if params.pop('author', None):
            target_kwargs['author'] = message.author

        if params.pop('guild', None):
            target_kwargs['guild'] = message.guild

        if params.pop('user_mention', None):
            target_kwargs['user_mention'] = message.raw_mentions

        if params.pop('other', None):
            target_kwargs['other'] = [i.strip() for i in args]

        response = None

        try:
            if '--error' in [i.strip() for i in args]:
                raise JustWrong("--testing error")

            response = await target(**target_kwargs)

        except JustWrong as error:
            docs = getattr(target, '__doc__', None)
            docs = [line.strip() for line in docs.strip().split('\n')]

            args = docs[-3], docs[-1], docs[1][16:], docs[3].split(' | ')
            if not docs[4].startswith('Change'):
                args = docs[-3], docs[-1], docs[1][16:], docs[3].split(' | '), docs[4].split(' | ')

            response = self.gen_embed(
                args,
                style='error',
                imp=True
            )

            response.description = f'> {error.message}'

        except ValueError:
            traceback.print_exc()
            print("Command missing type.\n")
            return

        except TypeError:
            traceback.print_exc()
            print("No return gotten.\n")
            return

        response_type = 'embed'

        if not response:
            print("| Command has no return")
            return

        try:
            await self.channel_send(
                response=response,
                type=response_type,
                channel=message.channel
            )
        except TypeError:
            print("You make set somewhere.\n")

##############################################################

    async def channel_send(self, response, type, channel):
        if type == 'text':
            await channel.send(
                content=response
            )
        elif type == 'embed':
            await channel.send(
                embed=response
            )
        else:
            print("Send unknown type.")

    def gen_embed(self, *args, style=None, color=None, imp=False):
        """Provides a basic template for embeds."""
        embed = discord.Embed()

        if args:
            args = args[0]

        if not style:
            print("Embed got no style.\n")
            return

        if color:
            try:
                r, g, b = color
            except TypeError:
                print("You need a rgb tuple for the embed color.")
        else:
            r, g, b = self.embed_color
        
        embed.color = self.colour.from_rgb(r, g, b)

        if imp:
            embed.set_footer(text=f'LandedWriter ∙ TestBot {self.BOTVERSION}', icon_url='https://cdn.discordapp.com/attachments/771941194207985694/1005882566580113558/3980-blonde-neko-scared.png')

        # add some style
        if style == 'empty':
            pass
        
        elif style == 'error':
            embed.set_author(name=' | Error Raised', icon_url='https://cdn-icons-png.flaticon.com/512/5219/5219070.png')
            try:
                embed.title = f'Error of using {args[0].capitalize()}'

                value = None
                
                try: args[4]
                except: value = f'1. {args[3][0]}\n```{self.prefix}{args[3][1]}```'

                if not value: value = f'1. {args[3][0]}\n```{self.prefix}{args[3][1]}```\n2. {args[4][0]}\n```{self.prefix}{args[4][1]}```'

                embed.add_field(
                    name='Usage',
                    value=f'- <imp> - [n-imp] -\n```{args[2]}```',
                    inline=False
                )

                embed.add_field(
                    name='Example',
                    value=value,
                    inline=False
                )

                embed.add_field(
                    name='Return',
                    value=f'```{args[1]}```',
                    inline=False
                )
            except:
                print("Creating author only error embed\n")

        else:
            print("Unknown embed style. Returning back empty one.\n")

        return embed

##############################################################

    def get_vchannel_blacklist(self):
        """Return all dec. or blacklisted vchannel."""
        return self.vchannel_blacklist
