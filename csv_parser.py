import csv


# Turns a dictionary into a class
class Dict2Class(object):
    def __init__(self, my_dict):
        for key in my_dict:
            val = my_dict[key]
            if val.isnumeric():
                val = int(val)
            else:
                try:
                    val = float(val)
                except ValueError:
                    pass
            if key[0].isnumeric():
                key = '_' + key
            setattr(self, key, val)


class CSVParser:
    def __init__(self, filename):
        self.name = filename
        self.keys = []
        self.lines = []
        self.parse()

    def parse(self):
        with open(self.name, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            self.keys = reader.fieldnames
            for line in reader:
                self.lines.append(Dict2Class(line))
