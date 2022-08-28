import json

class Json:
    def __init__(self, json_file):
        self.file = json_file
        self.data = self.parse()

    def parse(self):
        with open(self.file, encoding="utf-8") as data:
            try:
                parsed = json.load(data)
            except Exception:
                parsed = {}
        return parsed

    def get(self, item, default=None):
        try:
            data = self.data[item]
        except KeyError:
            print(f'| Could not get {item} in {self.file}')
            data = default
        return data

    def dump(self, obj):
        with open(self.file, encoding="utf-8", mode='w') as file:
            json.dump(obj, file, indent=2)
        self.data = self.parse()