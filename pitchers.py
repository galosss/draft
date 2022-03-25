import csv_parser
import espn_api
import common_players_data


def read_fangraphs_data():
    print("getting fangraphs pitchers...")
    fangraphs_pitchers = csv_parser.CSVParser('pitchers.csv').lines
    print("getting players map...")
    players_map = csv_parser.CSVParser('players_map.csv').lines
    print("getting espn players...")
    espn_players = list(espn_api.get_players())
    print("enriching data..")
    for pitcher in fangraphs_pitchers:
        espn_id = common_players_data.convert_fangraphs_to_espn_id(players_map, pitcher.playerid)
        if not espn_id:
            # print(f'not finding espn id of {pitcher.Name}')
            espn_positions = common_players_data.get_espn_positions_by_name(espn_players, pitcher.Name)
        else:
            espn_positions = common_players_data.get_espn_positions_by_id(espn_players, espn_id)
        if not espn_positions:
            common_players_data.enrich_points(pitcher, 0)
            common_players_data.enrich_positions(pitcher, [])
            print(f'not finding espn positions.. setting {pitcher.Name} points to 0')
            continue
        enrich_blown_saves(pitcher, calc_blown_saves(pitcher))
        common_players_data.enrich_positions(pitcher, espn_positions)  # fix Ohtani positions
        common_players_data.enrich_points(pitcher, calc_points(pitcher))
    return fangraphs_pitchers


def enrich_blown_saves(player, blown_saves):
    setattr(player, 'BS', blown_saves)


def calc_points(pitcher):
    positive = 1.98 * pitcher.IP + 7 * pitcher.W + 7 * pitcher.HLD + 7 * pitcher.SV + 5 * pitcher.QS + pitcher.SO
    negative = 5 * pitcher.L + 5 * pitcher.BS + pitcher.ER + 0.5 * pitcher.H + 0.5 * pitcher.BB
    return positive - negative


def calc_blown_saves(player):
    return (player.HLD + player.SV) // 5  # this should be fixed to match other stats. just temporary calculation


def write_all_players_to_csv():
    players = read_fangraphs_data()
    return common_players_data.write_all_players_to_csv(players, 'data_p.csv')
