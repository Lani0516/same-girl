import os
import sys
import time
import asyncio
import inspect
import traceback

import aiohttp
import discord

from discord.ext import commands

from modules.json import Json
from modules.exception import JustWrong

intents = discord.Intents.all()
intents.typing = False
intents.presences = False

class TestBot(commands.Bot):
    def __init__(self):
        # TODO: log it in .ini file
        self.pg_con = None
        self.BOTVERSION = 'v0.1.0'
        self.embed_color = (150, 194, 208)
        self.prefix = '>>'
        self.vprefix = '☕️｜'
        self.game = discord.Game("/help || 加入SharkParty")
        self.token = 'MTAwMzkyNzYwMTY3NDQ2MTMwNA.GNkOdj.xQ-b4SwaXRPLYTglCOjZM94OTNgAUyW86h59IM'
        self.colour = discord.Colour(value=000000)

        self.vchannel_create = 1011546109568634902
        self.vchannel_status = 1008425742092214352
        self.vchannel_blacklist = [
            1008422710692565082, # decorator
            1012416432790839367, # decorator
        ]
        self.nchannel = 1008422710692565082
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

        self.remove_command('help')
        
    def cleanup(self):
        try:
            self.loop.run_until_complete(self.logout())
            self.loop.run_until_complete(self.aiosession.close())

            pending = asyncio.all_tasks()
            gathered = asyncio.gather(*pending)

            gathered.cancel()
            self.loop.run_until_complete(gathered)
            gathered.exception()

        except:
            pass

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

    async def logout(self):
        print("\nClient is shutting down...\n")
        await self.cmd_clear()
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

        await self.bg_task()

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

        if not content:
            raise JustWrong("missing content")

        await self.channel_send(
            response=content,
            type='text', channel=exp_channel
        )

    async def cmd_clear(self, guild, other, channel=None):
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
            raise JustWrong("missing argument")
        
        type = other[0]

        if type == 'vchannel':
            if channel:
                await self.channel_send(
                    "Clearing all vchannel...",
                    type='text', channel=channel
                )
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

    async def cmd_docs(self, channel, other):
        """
        Usage:
            {command_prefix}docs <comand>
        Example:
            Getting docs of command ping | docs ping
        Change:
            None
        Name:
            docs
        Return:
            Docs of Input Command
        """
        if other:
            command = other[0]
        else:
            raise JustWrong("missing argument")

        try:
            target = getattr(self, 'cmd_' + command)
        except:
            raise JustWrong("unknown command")

        docs = getattr(target, '__doc__', None)
        docs = [line.strip() for line in docs.strip().split('\n')]

        args = docs[-3], docs[-1], docs[1][16:], docs[3].split(' | ')
        if not docs[4].startswith('Change'):
            args = docs[-3], docs[-1], docs[1][16:], docs[3].split(' | '), docs[4].split(' | ')

        embed = self.gen_embed(
            args,
            style='docs', color=(150, 194, 208), imp=True, err=False
        )
        return embed

    """vchannel only"""
    async def cmd_whitelist(self, guild, channel, user_mention, other):
        if not other:
            raise JustWrong("missing argument")

    async def cmd_blacklist(self, guild, channel, user_mentions, other):
        """
        Usage:
            {command_prefix}blacklist < + | - | add | remove > <@User>
        Example:
            Add @LandedWriter to blacklist | blacklist add @LandedWriter
            Remove @LandedWriter from blacklist | blacklist - @LandedWriter
        Change:
            None
        Name:
            blacklist
        Return:
            Blacklisted User
        """
        if user_mentions:
            member_list = [guild.get_member(user) for user in user_mentions]
        else:
            raise JustWrong("missing user mention")

        embed = self.gen_embed()

        if not other:
            raise JustWrong("missing argument")

        np = []

        if (
            other[0] == '+'
            or other[0] == 'add'
        ):
            for member in member_list:
                if not channel.permissions_for(member).connect:
                    member_list.remove(member)
                    np.append(member)
                    continue
                if getattr(member.voice, 'channel', None) == channel:
                    await member.move_to(None)
                await channel.set_permissions(member, connect=False, send_messages=False)
            if member_list:
                embed.add_field(
                    name='Blacklist Member',
                    value=f"> {', '.join([member.mention for member in member_list])}", inline=False
                )
            if np:
                embed.add_field(
                    name='Already Blacklisted',
                    value=f"> {', '.join([member.mention for member in np])}", inline=False
                )
            await self.channel_send(
                embed,
                type='embed', channel=channel
            )
            return

        if (
            other[0] == '-'
            or other[0] == 'remove'
        ):
            for member in member_list:
                if channel.permissions_for(member).connect:
                    member_list.remove(member)
                    np.append(member)
                    continue
                await channel.set_permissions(member, connect=True, send_messages=True)
            if member_list:
                embed.add_field(
                    name='Unblacklist Member',
                    value=f"> {', '.join([member.mention for member in member_list])}", inline=False
                )
            if np:
                embed.add_field(
                    name='Not Blacklisted',
                    value=f"> {', '.join([member.mention for member in np])}", inline=False
                )
            await self.channel_send(
                embed,
                type='embed', channel=channel
            )
            return

        raise JustWrong("invalid arguments")

    async def cmd_mute(self, author, guild, channel, user_mentions):
        """
        Usage:
            {command_prefix}mute [@User]
        Example:
            Mute yourself | mute
            Mute @LandedWriter | mute @LandedWriter
        Change:
            None
        Name:
            mute
        Return:
            Mute User
        """
        if user_mentions:
            member_list = [guild.get_member(user) for user in user_mentions]
        else:
            member_list = [author]
        
        m = await self.change_voice_state(
            member_list,
            type='mute', channel=channel
        )
        n = self.gen_embed(
            style='empty'
        )
        if not m: return

        if m[0]:
            n.add_field(
                name='Mute Member',
                value=f"> {', '.join([member.mention for member in m[0]])}", inline=False
            )
        if m[1]:
            n.add_field(
                name='Different Channel',
                value=f"> {', '.join([member.mention for member in m[1]])}", inline=False
            )
        if m[2]:
            n.add_field(
                name='Already Muted',
                value=f"> {', '.join([member.mention for member in m[2]])}", inline=False
            )
        await self.channel_send(
            n,
            type='embed', channel=channel
        )
        return

    async def cmd_unmute(self, author, guild, channel, user_mentions):
        """
        Usage:
            {command_prefix}unmute [@User]
        Example:
            Unmute yourself | unmute
            Unmute @LandedWriter | unmute @LandedWriter
        Change:
            None
        Name:
            unmute
        Return:
            Unmute User
        """
        if user_mentions:
            member_list = [guild.get_member(user) for user in user_mentions]
        else:
            member_list = [author]
        
        m = await self.change_voice_state(
            member_list,
            type='unmute', channel=channel
        )
        n = self.gen_embed(
            style='empty'
        )
        if not m: return

        if m[0]:
            n.add_field(
                name='Unmute Member',
                value=f"> {', '.join([member.mention for member in m[0]])}", inline=False
            )
        if m[1]:
            n.add_field(
                name='Different Channel',
                value=f"> {', '.join([member.mention for member in m[1]])}", inline=False
            )
        if m[2]:
            n.add_field(
                name='Already Unmuted',
                value=f"> {', '.join([member.mention for member in m[2]])}", inline=False
            )
        await self.channel_send(
            n,
            type='embed', channel=channel
        )
        return

    async def cmd_deaf(self, author, guild, channel, user_mentions):
        """
        Usage:
            {command_prefix}deaf [@User]
        Example:
            Deafen yourself | deaf
            Deafen @LandedWriter | deaf @LandedWriter
        Change:
            None
        Name:
            deaf
        Return:
            Deafen User
        """
        if user_mentions:
            member_list = [guild.get_member(user) for user in user_mentions]
        else:
            member_list = [author]
        
        m = await self.change_voice_state(
            member_list,
            type='deaf', channel=channel
        )
        n = self.gen_embed(
            style='empty'
        )
        if not m: return

        if m[0]:
            n.add_field(
                name='Deafen Member',
                value=f"> {', '.join([member.mention for member in m[0]])}", inline=False
            )
        if m[1]:
            n.add_field(
                name='Different Channel',
                value=f"> {', '.join([member.mention for member in m[1]])}", inline=False
            )
        if m[2]:
            n.add_field(
                name='Already Deafened',
                value=f"> {', '.join([member.mention for member in m[2]])}", inline=False
            )
        await self.channel_send(
            n,
            type='embed', channel=channel
        )
        return

    async def cmd_undeaf(self, author, guild, channel, user_mentions):
        """
        Usage:
            {command_prefix}undeaf [@User]
        Example:
            Undeafen yourself | undeaf
            Undeafen @LandedWriter | undeaf @LandedWriter
        Change:
            None
        Name:
            undeaf
        Return:
            Undeafen User
        """
        if user_mentions:
            member_list = [guild.get_member(user) for user in user_mentions]
        else:
            member_list = [author]
        
        m = await self.change_voice_state(
            member_list,
            type='undeaf', channel=channel
        )
        n = self.gen_embed(
            style='empty'
        )
        if not m: return

        if m[0]:
            n.add_field(
                name='Undeafen Member',
                value=f"> {', '.join([member.mention for member in m[0]])}", inline=False
            )
        if m[1]:
            n.add_field(
                name='Different Channel',
                value=f"> {', '.join([member.mention for member in m[1]])}", inline=False
            )
        if m[2]:
            n.add_field(
                name='Already Undeafened',
                value=f"> {', '.join([member.mention for member in m[2]])}", inline=False
            )
        await self.channel_send(
            n,
            type='embed', channel=channel
        )
        return

    async def cmd_kick(self, guild, channel, user_mentions):
        """
        Usage:
            {command_prefix}kick <@User>
        Example:
            Kick @LandedWriter from this channel | kick @LandedWriter
        Change:
            None
        Name:
            kick
        Return:
            Kicked User
        """
        if user_mentions:
            member_list = [guild.get_member(user) for user in user_mentions]
        else:
            raise JustWrong("missing user mention")

        m = await self.change_voice_state(
            member_list,
            type='kick', channel=channel
        )
        n = self.gen_embed(
            style='empty'
        )
        if not m: return

        if m[0]:
            n.add_field(
                name='Kick Member',
                value=f"> {', '.join([member.mention for member in m[0]])}", inline=False
            )
        if m[1]:
            n.add_field(
                name='Different Channel',
                value=f"> {', '.join([member.mention for member in m[1]])}", inline=False
            )
        await self.channel_send(
            n,
            type='embed', channel=channel
        )
        return
            
    async def cmd_coop(self, guild, channel, user_mentions):
        """
        Usage:
            {command_prefix}coop <@User>
        Example:
            Give @LandedWriter this channel's admin role | coop @LandedWriter
        Change:
            None
        Name:
            coop
        Return:
            Added User
        """
        if user_mentions:
            member_list = [guild.get_member(user) for user in user_mentions]
        else:
            raise JustWrong("missing user mention")

        details = self.vchannel_details.data
        for user in member_list:
            details[str(channel.id)]['coop'].append(str(user))

        self.vchannel_details.dump(details)
        await self.channel_send(
            f"Added {', '.join([member.mention for member in member_list])} to this channel coop.",
            type='text', channel=channel
        )
        return

##############################################################

    async def on_voice_state_update(self, member, before, after):
        join = leave = False

        if before.channel:
            leave = True
        
        if after.channel:
            join = True

        content = str()
        
        if join and not leave: # join only
            content, color = f'{member.display_name} | 加入 {str(after.channel)[len(self.vprefix)-1:]}', None
            
        elif not join and leave: # change
            content, color = f'{member.display_name} | 離開 {str(before.channel)[len(self.vprefix)-1:]}', (191, 120, 120)
        
        elif join and leave:
            return # other voice state update

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
        details[str(channel_id)] = {'author': str(author), 'coop': [], 'guild_id': guild_id}

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
            await self.cmd_clear(channel.guild, ['vchannel', ])

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

        details = None

        if command in self.vchannel_commands:
            details = self.vchannel_details.get(str(message.channel.id))

        master_signal = False
        if details:
            for key in list(details):
                if key == 'author':
                    if str(message.author) == details[key]:
                        master_signal = True
                if key == 'coop':
                    if str(message.author) in details[key]:
                        master_signal = True
                if master_signal:
                    break
        
            if not master_signal:
                await self.channel_send(
                    "You are not one of the vchannel administrator.",
                    type='text', channel=message.channel
                )
                return

        args = [i.strip() for i in args]

        for mention in message.raw_mentions:
            args.remove('<@'+str(mention)+'>')

        target_kwargs = {}
        if params.pop('message', None):
            target_kwargs['message'] = message
        
        if params.pop('channel', None):
            target_kwargs['channel'] = message.channel

        if params.pop('author', None):
            target_kwargs['author'] = message.author

        if params.pop('guild', None):
            target_kwargs['guild'] = message.guild

        if params.pop('user_mentions', None):
            target_kwargs['user_mentions'] = message.raw_mentions

        if params.pop('other', None):
            target_kwargs['other'] = args

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
                style='docs', imp=True, err=True
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

    async def channel_send(self, response, channel, type='text'):
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

    async def change_voice_state(self, members, type, channel):
        if type.endswith('mute'):
            _type = ['mute', 'mute']
        elif type.endswith('deaf'):
            _type = ['deaf', 'deafen']
        elif type.endswith('kick'):
            _type = ['kick', 'kick']
        else:
            return

        p = []
        np = []

        if type.startswith('un'):
            _type.append(False)
        else:
            _type.append(True)

        target_kwargs = {_type[1]: _type[2]}

        for member in members:
            if getattr(member.voice, 'channel', None) != channel:
                members.remove(member)
                np.append(member)
            else:
                if type == 'kick':
                    await member.move_to(None)
                    continue
                if getattr(member.voice, _type[0]) == _type[2]:
                    members.remove(member)
                    p.append(member)
                else:
                    target = getattr(member, 'edit')
                    await target(**target_kwargs)         
        return [members, np, p]

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
            style='line', color=(124, 124, 124),
        )
        await self.channel_send(
            embed,
            type='embed', channel=self.get_channel(self.vchannel_status)
        )
        await vchannel.delete()

    def gen_embed(self, *args, style='empty', color=None, imp=False, err=False):
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
        
        if style == 'docs':
            embed.title = f'Help of using {args[0].capitalize()}'
            embed.description = "> hope this helps you out"
            embed.set_author(name='| How To Command', icon_url='https://cdn-icons-png.flaticon.com/512/305/305098.png')

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
            if err:
                embed.title = f'Error of using {args[0].capitalize()}'
                embed.set_author(name='| Error Raised', icon_url='https://cdn-icons-png.flaticon.com/512/5219/5219070.png')
                embed.color = self.colour.from_rgb(191, 120, 120)
            return embed

        print("| Unknown embed style. Returning back empty one.\n")

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

    async def bg_task(self):
        c = 1
        while False:
        # while not self.is_closed():
            print(f'I\'m running at {c} times.')
            c += 1
            await asyncio.sleep(5)

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
