POSITIONS = ['C', '1B', '2B', '3B','SS', 'LF', 'RF', 'CF', 'DH', 'SP', 'RP']


class Player:
    def __init__(self, csv_record: str):
        csv_record_parts = csv_record.split(',')
        self.name = csv_record_parts[0]
        self.team = csv_record_parts[1]
        self.positions = Player.get_positions(csv_record)
        self.pts = float(csv_record_parts[-1])

    @staticmethod
    def get_positions(csv_record: str):
        return csv_record[csv_record.find('"') + 1:csv_record.rfind('"')].split(",")


def parse_data():
    data_rows = open("FantasyPros_2022_Projections_H.csv", "r").readlines()
    players = [Player(player) for player in data_rows[1:]]
    print(players)


parse_data()
