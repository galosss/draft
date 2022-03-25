import csv
import json
import requests

## REST API DEFINITIONS
URL = 'https://fantasy.espn.com/apis/v3/games/flb/seasons/2022/segments/0/leaguedefaults/' \
      '1?scoringPeriodId=0&view=kona_player_info'

REST_API_FILTERS = {
    "players":
        {
            "useFullProjectionTable": {"value": True},
            "sortDraftRanks": {"sortPriority": 3, "sortAsc": True, "value": "STANDARD"},
            "sortPercOwned": {"sortPriority": 4, "sortAsc": False},
            "limit": 0,
            "offset": 50,
        }
}

# ESPN FANTASY DEFINITIONS
ESPN_POSITIONS = [
    'C',  # 0
    '1B',  # 1
    '2B',  # 2
    '3B',  # 3
    'SS',  # 4
    'OF',  # 5
    'MID_INF',  # 6
    'COR_INF',  # 7
    'LF',  # 8
    'CF',  # 9
    'RF',  # 10
    'DH',  # 11
    'UTIL',  # 12
    'P',  # 13
    'SP',  # 14
    'RP',  # 15
    'BE',  # 16
    'IL',  # 17
    'UNK',  # 18
    'INF',  # 19
]

MY_ESPN_POSITIONS = ['C', '1B', '2B', '3B', 'SS', 'OF', 'INF', 'UTIL', 'P', 'SP', 'RP']


class ESPNPlayer:
    def __init__(self, name, player_id, positions):
        self.name = name
        self.player_id = player_id
        self._positions = positions
        if 18 in positions or any([i > 19 for i in positions]):
            return
        self.positions = [ESPN_POSITIONS[i] for i in positions if ESPN_POSITIONS[i] in MY_ESPN_POSITIONS]

    def __repr__(self):
        return f"{self.name}: {','.join(self.positions)}"


def get_players(offset=0, limit=-1):
    REST_API_FILTERS["players"]["offset"] = offset
    REST_API_FILTERS["players"]["limit"] = limit
    headers = {'x-fantasy-filter': json.dumps(REST_API_FILTERS)}
    r = requests.get(URL, headers=headers)
    data = json.loads(r.content)
    players = data['players']  # list of players
    for player in players:
        if 22 in player['player']['eligibleSlots']:  # these are minor leaguers or something
            # return  # it is sorted per ranking, so it's safe to leave here
            player['player']['eligibleSlots'].remove(22)
        yield ESPNPlayer(player['player']['fullName'], player['id'], player['player']['eligibleSlots'])


def write_all_players_to_csv():
    with open('espn_map.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'name', 'positions'])
        for player in get_players():
            writer.writerow([player.player_id, player.name, ','.join(player.positions)])


# write_all_players_to_csv()
