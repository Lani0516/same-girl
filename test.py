import configparser

config = configparser.ConfigParser()
config.read("config/config.ini", encoding="utf-8")

print(config.get("Voice", "Blacklist").split())
print()
print(type(config.get("Voice", "Blacklist").split()))