import os
import sys
import time
import json
import asyncio
import inspect
import traceback

import aiohttp
import discord

from modules.json import Json
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
        self.vprefix = '☕️｜'
        self.game = discord.Game("/help || 加入SharkParty")
        self.token = 'MTAwMzkyNzYwMTY3NDQ2MTMwNA.GNkOdj.xQ-b4SwaXRPLYTglCOjZM94OTNgAUyW86h59IM'

        self.vchannel_create = 1011546109568634902
        self.vchannel_status = 1008425742092214352
        self.vchannel_blacklist = [
            1008422710692565082, # decorator
            1008422750781722716, # decorator
        ]
        self.nchannel = 1010557329579724864
        self.vcategory = 1003922992805449779

        self.admin_commands = [
            'send', 'clear' 
        ]
        self.vchannel_commands = [
            'name', 'whitelist', 'blacklist', 'mute', 'unmute', 'deaf', 'undeaf', 'kick', 'coop'
        ]
        self.vchannel_details = Json('config/vchannel.json')
        
        self.vchannel_details.dump({})
        
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

        print("===========================================================",
              "|      ___           ___           ___           ___      |",
              "|     /\  \         /\  \         /\__\         /\  \     |",
              "|    /::\  \       /::\  \       /::|  |       /::\  \    |",
              "|   /:/\ \  \     /:/\:\  \     /:|:|  |      /:/\:\  \   |",
              "|  _\:\~\ \  \   /::\~\:\  \   /:/|:|__|__   /::\~\:\  \  |",
              "| /\ \:\ \ \__\ /:/\:\ \:\__\ /:/ |::::\__\ /:/\:\ \:\__\\ |",
              "| \:\ \:\ \/__/ \/__\:\/:/  / \/__/~~/:/  / \:\~\:\ \/__/ |",
              "|  \:\ \:\__\        \::/  /        /:/  /   \:\ \:\__\   |",
              "|   \:\/:/  /        /:/  /        /:/  /     \:\ \/__/   |",
              "|    \::/  /        /:/  /        /:/  /       \:\__\     |",
              "|     \/__/         \/__/         \/__/         \/__/     |",
              "|                                                         |",
              "===========================================================", sep='\n', end='\n')

        start_up = f'>>> Your Bot {str(self.user)[:-5]} is now Online' 
        print(start_up)
        print('-' * (len(start_up)+1)) 

##############################################################

    """admin only"""
    async def cmd_send(self, channel, other):
        """
        Usage:
            {command_prefix}send <message_content> [channel_id]
        Example:
            Send Hello in current channel | send Hello
            Send Hello World in Lobby with channel id | send Hello World 1003922992805449780 
        Change:
            None
        Name:
            send
        Return:
            Message Content
        """
        content = None
        
        # other = [message, channel_id[-1]]
        try:
            exp_channel = self.get_channel(int(other[-1]))
        except:
            exp_channel = None

        if not exp_channel:
            exp_channel = channel
        else:
            other.pop(-1)
        
        content = ' '.join(other)

        await self.channel_send(
            response=content,
            type='text', channel=exp_channel
        )

    async def cmd_clear(self, guild, other):
        """
        Usage:
            {command_prefix}clear <object type>
        Example:
            Clear all vchannel which are not in blacklist | clear vchannel
        Change:
            None
        Name:
            clear
        Return:
            None
        """
        if not other:
            raise JustWrong("missing arguments")
        
        type = other[0]

        if type == 'vchannel':
            for channel in guild.voice_channels:
                await self.del_vchannel(channel)
            return
        
        if type == 'message':
            return

        print("Unknown Type\n")

    """global"""
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

        if len(other) <= 1:
            raise JustWrong("please input more than one number")

        check = [self.is_int(i) for i in other]
        if False in check:
            raise JustWrong("invalid input")
        
        num = 0
        for i in other:
            num+=int(i)

        embed.title = f'{emoji_prefix} {num}'
        return embed

##############################################################

    async def on_voice_state_update(self, member, before, after):
        join = leave = False

        if before.channel:
            leave = True
        
        if after.channel:
            join = True

        content = str()
        
        if join and not leave: # join only
            content, color = f'{member.display_name} | 加入 {str(after.channel)[len(self.vprefix)-1:]}', (150, 194, 208)
            
        elif not join and leave: # change
            content, color = f'{member.display_name} | 離開 {str(before.channel)[len(self.vprefix)-1:]}', None

        else: # leave only
            content, color = f'{member.display_name} | {str(before.channel)[len(self.vprefix)-1:]} 移到 {str(after.channel)[len(self.vprefix)-1:]}', (216, 176, 107)

        print(f'{member.guild} | {content}')

        args = content, member.display_avatar

        embed = self.gen_embed(
            args,
            style='line', color=color
        )

        await self.channel_send(response=embed, type='embed', channel=self.get_channel(self.vchannel_status))
        await self.del_vchannel(before.channel)

    async def on_guild_channel_create(self, channel):
        if str(channel.type) != 'voice':
            return

        guild_id = channel.guild.id
        channel_id = channel.id
        author = self.get_channel(self.vchannel_create).last_message.author
        
        details = self.vchannel_details.data
        details[str(channel_id)] = {'author': str(author), 'guild_id': guild_id}

        # channel id: str, author: str, guild_id: int
        self.vchannel_details.dump(details)
    
    async def on_guild_channel_delete(self, channel):
        if str(channel.type) != 'voice':
            return

        guild = channel.guild
        
        details = self.vchannel_details.data
        try:
            details.pop(str(channel.id))
        except KeyError:
            print("| Could not find channel, clearing all channel in current guild.")  

            for key in list(details):
                if details[key]['guild_id'] == guild.id:
                    del details[key]
            await self.cmd_clear(guild, ['vchannel'])

        self.vchannel_details.dump(details)

    async def on_message(self, message):
        await self.wait_until_ready()

        if message.author.bot:
            return

        message_content = message.content.strip()

        """Nhentai Translator"""
        # build it into a function for better returning
        stop = None

        stop = await self.n_translator(
            message_content,
            channel=message.channel,
        )

        if stop:
            print(f'{message.guild} | {message.author} | generating n_number >> {int(message_content)}')
            await message.delete()
            return

        """Vchannel Creator"""
        # create | [name] < | [limit] >
        # 1. message.author -> highest perm. of this vchannel
        # make this into a function
        # 2. use vchannel private channel to set perm.
        # | log vchannel into a file
        # | send usage when created
        # | json ? 
        if message.channel == self.get_channel(self.vchannel_create):
            stop = await self.gen_vchannel(
                message_content, 
                guild=message.guild, channel=message.channel, author=message.author
            )
        
        if stop:
            print(f'{message.guild} | {message.author} | generating vchannel >> {stop[len(self.vprefix):]}')
            return

        """Command Reader"""
        # Change the prefix to config someday
        if not message.content.startswith(self.prefix):
            return

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

        is_admin = message.author.guild_permissions.administrator

        argspec = inspect.signature(target)
        params = argspec.parameters.copy()

        if (
            command in self.admin_commands
            and not is_admin
        ):
            await self.channel_send(
                "This is an admin only command.",
                type='text', channel=message.channel
            )
            return

        if (
            command in self.vchannel_commands
            and str(message.channel.type) != 'voice'
        ):
            await self.channel_send(
                "This is a vchannel command.",
                type='text', channel=message.channel
            )
            return

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
                style='error', imp=True
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
                response,
                type=response_type, channel=message.channel
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

    async def gen_vchannel(self, vchannel, guild, channel, author):
        # use catergory.create_voice_channel
        # category -> self.vcategory
        category = discord.utils.get(guild.categories, id=self.vcategory)
        vchannel = [i.strip() for i in vchannel.split('|')]

        if not category:
            print("invalid vcategory\n")
            return
            
        if not vchannel[0] == "create":
            return

        name = f'{self.vprefix}{vchannel[1]}'
        
        try:
            limit = vchannel.pop(2)
        except IndexError:
            limit = 0

        # cannot use if limit: because 0 also equals to false
        if limit == '':
            await self.channel_send(
                "再多一個 | 我就幫你折蓮花",
                type='text', channel=channel
            )
            return

        await category.create_voice_channel(name, user_limit=limit, bitrate=self.get_bitrate(guild), position=1)

        args = f'{author.display_name} | 創建了 {name[len(self.vprefix):]}', author.display_avatar

        embed = self.gen_embed(
            args,
            style='line', color=(144, 202, 144),
        )
        await self.channel_send(
            response=embed,
            type='embed', channel=self.get_channel(self.vchannel_status)
        )
        return name

    async def del_vchannel(self, vchannel):
        if not vchannel:
            return

        if vchannel.id in self.vchannel_blacklist:
            return

        if vchannel.members:
            return

        print(f'{vchannel.guild} | delete vchannel | {str(vchannel)[len(self.vprefix)-1:]}') 

        args = f'{str(vchannel)[len(self.vprefix)-1:]} | 成為了回憶', 'https://cdn-icons-png.flaticon.com/512/1978/1978026.png'

        embed = self.gen_embed(
            args,
            style='line',
            color=(124, 124, 124),
        )
        await self.channel_send(
            response=embed,
            type='embed',
            channel=self.get_channel(self.vchannel_status)
        )
        await vchannel.delete()

    def gen_embed(self, *args, style='empty', color=None, imp=False):
        """Provides a basic template for embeds."""
        embed = discord.Embed()

        if args:
            args = args[0]

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
            return embed

        if style == 'line':
            embed.set_author(name=args[0], icon_url=args[1])
            return embed
        
        if style == 'error':
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
                return embed
            except:
                print("Creating author only error embed\n")
                return embed

        print("Unknown embed style. Returning back empty one.\n")

        return embed

    async def n_translator(self, number, channel):
        if not channel.id == self.nchannel:
            return

        if not self.is_int(number):
            return

        if not len(number) == 6:
            return

        await self.channel_send(
            response=f'https://nhentai.net/g/{int(number)}',
            type='text',
            channel=channel
            )
        return "Done!"

##############################################################

    def is_int(self, object) -> bool:
        try:
            int(object)
        except:
            return False
        return True

    def is_exist(self, list: list, index: int) -> bool:
        try:
            list[index]
        except:
            return False
        return True

    def get_bitrate(self, guild) -> int:
        tier = guild.premium_tier

        if tier == 0:
            return 96000
        if tier == 1:
            return 128000
        if tier == 2:
            return 256000
        if tier == 3:
            return 384000
