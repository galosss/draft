import json
import requests

URL = 'https://fantasy.espn.com/apis/v3/games/flb/seasons/2022/segments/0/leaguedefaults/' \
      '1?scoringPeriodId=0&view=kona_player_info'

OFFSET = 0
LIMIT = 50

FILTERS = {
    "players":
        {
            "useFullProjectionTable": {"value": True},
            "sortDraftRanks": {"sortPriority": 3, "sortAsc": True, "value": "STANDARD"},
            "sortPercOwned": {"sortPriority": 4, "sortAsc": False},
            "limit": LIMIT,
            "offset": OFFSET,
        }
}

headers = {'x-fantasy-filter': json.dumps(FILTERS)}
r = requests.get(URL, headers=headers)
data = json.loads(r.content)
players = data['players']  # list of players
print(players[0])