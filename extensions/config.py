import os
import discord
import configparser

class Config:
    def __init__(self, config_file):
        self.config_file = config_file

        config = configparser.ConfigParser(interpolation=None)
        config.read(config_file, encoding='utf-8')

        self._token = config.get(
            "Essential", "Token", fallback=ConfigDefaults.token
        )

        self._command_prefix = config.get(
            "Command", "Prefix", fallback=ConfigDefaults.command_prefix
        )
        self._admin_commands = config.get(
            "Commnad", "AdminCommand", fallback=ConfigDefaults.admin_commands
        )
        if not isinstance(self._admin_commands, (list, tuple, set)):
            try:
                self._admin_commands.split()
            except:
                self._admin_commands = [self._admin_commands]

        self._vchannel_commands = config.get(
            "Command", "VoiceCommand", fallback=ConfigDefaults.vchannel_commands
        )
        if not isinstance(self._vchannel_commands, (list, tuple, set)):
            try:
                self._vchannel_commands.split()
            except:
                self._vchannel_commands = [self._vchannel_commands]

        self._vcategory = config.get(
            "Voice", "Category", fallback=ConfigDefaults.vcategory
        )
        self._vchannel_prefix = config.get(
            "Voice", "Prefix", fallback=ConfigDefaults.vchannel_prefix
        )
        self._vchannel_create = config.get(
            "Voice", "Create", fallback=ConfigDefaults.vchannel_create
        )
        self._vchannel_status = config.get(
            "Voice", "Status", fallback=ConfigDefaults.vchannel_status
        )
        self._vchannel_blacklist = config.get(
            "Voice", "Blacklist", fallback=ConfigDefaults.vchannel_blacklist
        )
        if not isinstance(self._vchannel_blacklist, (list, tuple, set)):
            try:
                self._vchannel_blacklist.split()
            except:
                self._vchannel_blacklist = [self._vchannel_blacklist]

        self._nchannel = config.get(
            "Constant", "Nhentai", fallback=ConfigDefaults.nchannel
        )
        self._activity = config.get(
            "Constant", "Activity", fallback=ConfigDefaults.activity
        )
        self._default_color = config.get(
            "Constant", "Color", fallback=ConfigDefaults.default_color
        ).split()

class ConfigDefaults:
    token = None

    command_prefix = '>>'
    admin_commands = [
        'send', 'clear', 'server_state_setup'
    ]
    vchannel_commands = [
        'name', 'whitelist', 'blacklist', 'mute', 'unmute', 'deaf', 'undeaf', 'kick', 'coop'
    ]

    vcategory = None
    vchannel_prefix = '☕️｜'
    vchannel_create = None
    vchannel_status = None  
    vchannel_blacklist = []

    nchannel = None
    activity = "/help || 加入SharkParty"
    default_color = (150, 194, 208)

    config_file = "config/config.ini"