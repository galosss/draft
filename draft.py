import dataclasses
import csv
import time
import typing

import data_creation

TEAM_POS = ['C', '1B', '2B', '3B', 'SS', 'INF', 'UTIL'] + 4 * ['OF'] + 4 * ['P'] + 2 * ['RP'] + 2 * ['SP']
INFIELD = ['1B', '2B', '3B', 'SS']
# UTIL = ['C', '1B', '2B', '3B', 'SS', 'INF', 'OF', 'DH']
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
    positions_left_mat = [TEAM_POS[:] for _ in range(draft_size)]
    current_pick = 1
    return mock_draft_from_state(current_pick, players_left, positions_left_mat, [], TEAM_POS, my_pos, depth=depth)


def mock_draft_from_state(current_pick, players_left, positions_left_mat, team, team_format, my_pos=DRAFT_POS,
                          depth=3, cache=None):
    draft_size = len(positions_left_mat)
    if cache is None:
        cache = {}

    my_positions_left = positions_left_mat[my_pos - 1]
    if (tuple(players_left), tuple(my_positions_left)) in cache:
        return cache[(tuple(players_left), tuple(my_positions_left))]
    positions_left_mat = positions_left_mat[:]
    while who_picks_snake(current_pick) != my_pos:
        _, players_left, positions_left = dumb_pick(
            players_left, positions_left_mat[who_picks_snake(current_pick, draft_size) - 1])
        positions_left_mat[who_picks_snake(current_pick, draft_size) - 1] = positions_left
        current_pick += 1

    if len(positions_left_mat[my_pos - 1]) == 1:  # end condition
        return team[:] + [get_highest_of_position(players_left, my_positions_left.pop())[0]]  # end mock draft

    if len(team_format) - len(positions_left_mat[my_pos - 1]) >= depth:  # compromise
        player, players_left, positions_left = dumb_pick(players_left, my_positions_left)
        positions_left_mat[my_pos - 1] = positions_left
        return mock_draft_from_state(current_pick + 1, players_left, positions_left_mat, team[:] + [player],
                                     team_format, my_pos, depth, cache)
    team = smart_pick(current_pick, players_left, positions_left_mat, team[:], team_format, my_pos, depth, cache)
    cache[(tuple(players_left), tuple(my_positions_left))] = team
    return team
    # return team[:depth] + mock_draft_from_state(current_pick, players_left, positions_left_mat, [],
    #                                             positions_left_mat[my_pos - 1],
    #                                             DRAFT_POS, depth, cache)


def smart_pick(current_pick, players_left, positions_left_mat, team, team_format, my_pos, depth, cache):
    positions_left = positions_left_mat[my_pos - 1]
    scores = []
    potential_team_players = []
    potential_without_player = []
    positions_without = []
    potential_teams = []
    for pos_index, position in enumerate(specify_positions_list(positions_left)):
        player, all_players_without_chosen = get_highest_of_position(players_left, position)
        potential_team_players.append(player)
        potential_without_player.append(all_players_without_chosen)
        positions_without_chosen = positions_left[:]
        positions_without_chosen.remove(position)
        positions_without.append(positions_without_chosen)
        positions_left_mat = positions_left_mat[:]
        positions_left_mat[my_pos - 1] = positions_without_chosen
        potential_teams.append(mock_draft_from_state(current_pick + 1, all_players_without_chosen, positions_left_mat,
                                                     team[:] + [player], team_format, my_pos, depth, cache))
        scores.append(get_total_team_points(potential_teams[-1]))
    chosen_index = scores.index(max(scores))
    return potential_teams[chosen_index]


def dumb_pick(players_left, positions_left):
    for player_index, player in enumerate(players_left):
        for position in player.positions:  # order is from specific to general
            if position in positions_left:
                positions_left = positions_left[:]
                positions_left.remove(position)
                return player, players_left[:player_index] + players_left[player_index + 1:], positions_left


def get_highest_of_position(players_left, position):
    for index, player in enumerate(players_left):
        if position in player.positions:
            return player, players_left[:index] + players_left[index + 1:]


def specify_positions_list(positions: typing.List[str]) -> typing.Set[str]:
    filtered_positions = set(positions)
    if 'P' in positions and sub_array_included(positions, PITCHERS):
        filtered_positions.remove('P')
    # if 'UTILS' in positions and sub_array_included(positions, UTIL):
    #     filtered_positions.remove('UTILS')
    if 'INF' in positions and sub_array_included(positions, INFIELD):
        filtered_positions.remove('INF')
    return filtered_positions


def sub_array_included(arr, sub_arr) -> bool:
    return all([member in arr for member in sub_arr])


def next_pick_snake(current_pick, draft_size=DRAFT_PLAYERS):
    return (((current_pick - 1) // draft_size) + 1) * draft_size * 2 + 1 - current_pick


def who_picks_snake(current_pick, draft_size=DRAFT_PLAYERS):
    is_reverse = ((current_pick - 1) // 16) % 2
    pick = current_pick % draft_size if not is_reverse else ((draft_size + 1 - current_pick) % draft_size)
    return pick if pick else draft_size


def get_all_picks_positions(draw_pos=DRAFT_POS, draft_size=DRAFT_PLAYERS):
    num_picks = len(TEAM_POS)
    picks = [draw_pos]
    pos = draw_pos
    while num_picks:
        pos = next_pick_snake(pos, draft_size)
        picks.append(pos)
        num_picks -= 1
    return picks


def get_total_team_points(team: typing.List[DraftPlayer]) -> float:
    return sum([selected_player.pts for selected_player in team])


# for depth in range(0, 5):
#     start = time.time()
#     select_team = mock_draft(depth=depth, my_pos=13)
#     print(f"depth {depth}")
#     print(f"selected team: {select_team}")
#     print(f"total points: {get_total_team_points(select_team)}")
#     end = time.time()
#     print(f"took {end - start} seconds")
# for pos in range(1, 17):
#     start = time.time()
#     select_team = mock_draft(depth=3, my_pos=pos)
#     print(f"pos {pos}")
#     print(f"selected team: {select_team}")
#     print(f"total points: {get_total_team_points(select_team)}")
#     end = time.time()
#     print(f"took {end - start} seconds")
start = time.time()
select_team = mock_draft(depth=3, my_pos=13)
print(f"selected team: {select_team}")
print(f"total points: {get_total_team_points(select_team)}")
end = time.time()
print(f"took {end - start} seconds")
