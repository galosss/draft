import dataclasses
import csv
import time

import data_creation

TEAM_POS = ['C', '1B', '2B', '3B', 'INF', 'UTIL'] + 4 * ['OF'] + 4 * ['P'] + 2 * ['RP'] + 2 * ['SP']
INFIELD = ['1B', '2B', '3B', 'SS']
UTIL = ['C', '1B', '2B', '3B', 'SS', 'INF', 'OF']
PITCHERS = ['SP', 'RP']

DRAFT_PLAYERS = 16
DRAFT_POS = 13


@dataclasses.dataclass
class DraftPlayer:
    name: str
    positions: list
    pts: float

    def __hash__(self):
        return hash(self.name)


def my_pick(players_left, positions_left):
    for player in players_left:
        for position in player.positions:
            if position in positions_left:
                return player
    assert False


def cpu_pick(players_left):
    return players_left.pop(0)


def create_data():
    data_creation.create_data()


def get_data(should_create=True):
    if should_create:
        create_data()
    players = []
    with open('players_data.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for line in reader:
            players.append(DraftPlayer(line['name'], line['positions'].split(','), float(line['pts'])))
    return players


def mock_draft(my_pos=DRAFT_POS, draft_size=DRAFT_PLAYERS, depth=5):
    players_left = get_data(False)
    positions_left = TEAM_POS[:]
    current_pick = 1
    return mock_draft_from_state(current_pick, players_left, positions_left, [], my_pos, draft_size, depth=depth)


def mock_draft_from_state(current_pick, players_left, positions_left, team, my_pos=DRAFT_POS, draft_size=DRAFT_PLAYERS,
                          cache=None, depth=3):
    if cache is None:
        cache = {}
    if (current_pick, tuple(players_left), tuple(positions_left)) in cache:
        return cache[(current_pick, tuple(players_left), tuple(positions_left))]
    while current_pick > my_pos:
        my_pos = next_pick_snake(my_pos, draft_size)

    players_left_dyn = players_left[:]
    # while positions_left:
    while len(positions_left) > (len(TEAM_POS) - depth):
        if current_pick == my_pos:
            if len(positions_left) == (len(TEAM_POS) - depth):
                potential_team_players = []
                scores = []
                for pos_index, position in enumerate(specify_positions_list(positions_left)):
                    player, without_player = get_highest_of_position(players_left_dyn, position)
                    potential_team_players.append(player)
                    selection_score = player.pts
                    scores.append(selection_score)
                chosen_index = scores.index(max(scores))
                return [potential_team_players[chosen_index]]  # end mock draft
            # if len(positions_left) == 1:
            #     return [get_highest_of_position(players_left, positions_left[0])[0]]  # end mock draft
            scores = []
            potential_team_players = []
            potential_without_player = []
            positions_without = []
            for pos_index, position in enumerate(specify_positions_list(positions_left)):
                player, without_player = get_highest_of_position(players_left_dyn, position)
                potential_team_players.append(player)
                potential_without_player.append(without_player)
                position_without = positions_left[:]
                position_without.remove(position)
                positions_without.append(position_without)
                current_team = team[:] + [player]
                # if any(['Kris' in p.name for p in team]):
                #     print('Hello')
                selection_score = player.pts + mock_draft_from_state(current_pick + 1, without_player,
                                                                     position_without, current_team, my_pos,
                                                                     draft_size, cache)[0].pts
                scores.append(selection_score)
            chosen_index = scores.index(max(scores))
            # print(f"adding {players[chosen_index]} to team")
            team.append(potential_team_players[chosen_index])
            positions_left = positions_without[chosen_index]
            players_left_dyn = potential_without_player[chosen_index]
            my_pos = next_pick_snake(my_pos, draft_size)
        else:
            cpu_pick(players_left_dyn)
        current_pick += 1
    cache[(current_pick, tuple(players_left), tuple(positions_left))] = team
    return team


def get_highest_of_position(players_left, position):
    for index, player in enumerate(players_left):
        if position in player.positions:
            return player, players_left[:index] + players_left[index + 1:]


def specify_positions_list(positions):
    filtered_positions = set(positions)
    if 'P' in positions and any([position in positions for position in PITCHERS]):
        filtered_positions.remove('P')
    if 'INF' in positions and any([position in positions for position in INFIELD]):
        filtered_positions.remove('INF')
    if 'UTILS' in positions and any([position in positions for position in UTIL]):
        filtered_positions.remove('UTILS')
    return filtered_positions


def next_pick_snake(current_pick, draft_size=DRAFT_PLAYERS):
    return (((current_pick - 1) // draft_size) + 1) * draft_size * 2 + 1 - current_pick


def get_all_picks_positions(draw_pos=DRAFT_POS, draft_size=DRAFT_PLAYERS):
    num_picks = len(TEAM_POS)
    picks = [draw_pos]
    pos = draw_pos
    while num_picks:
        pos = next_pick_snake(pos, draft_size)
        picks.append(pos)
        num_picks -= 1
    return picks


start = time.time()
print(mock_draft(depth=17, my_pos=13))
end = time.time()
print(f"took {end - start} seconds")
