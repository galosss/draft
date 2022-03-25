import csv


def enrich_positions(player, positions):
    setattr(player, 'POS', positions)


def enrich_points(player, pts):
    setattr(player, 'PTS', pts)


def convert_fangraphs_to_espn_id(players_map, fangraphs_id):
    for player in players_map:
        if player.IDFANGRAPHS == fangraphs_id:
            return player.ESPNID
    return 0


def get_espn_positions_by_id(espn_players, player_id):
    for player in espn_players:
        if player.player_id == player_id:
            return player.positions
    return ""


def get_espn_positions_by_name(espn_players, name):
    for player in espn_players:
        if player.name == name:
            return player.positions
    return ""


def write_all_players_to_csv(players, filename):
    rows = []
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, ["name", "pts", "positions"])
        writer.writeheader()
        for player in sorted(players, key=lambda pitcher: pitcher.PTS, reverse=True):
            if not hasattr(player, "POS") or not hasattr(player, "PTS"):
                print(f"bypassing {player.Name}")
                continue
            row = {"name": player.Name, "pts": player.PTS, "positions": ",".join(player.POS)}
            writer.writerow(row)
            rows.append(row)
    return rows