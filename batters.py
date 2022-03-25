import csv_parser
import espn_api
import common_players_data


def read_fangraphs_data():
    print("getting fangraphs batters...")
    fangraphs_pitchers = csv_parser.CSVParser('batters.csv').lines
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
        common_players_data.enrich_positions(pitcher, espn_positions)  # fix Ohtani positions
        common_players_data.enrich_points(pitcher, calc_points(pitcher))
    return fangraphs_pitchers


def calc_points(batter):
    positive = (batter.H - batter._2B - batter._3B - batter.HR) + 2 * batter._2B + 3 * batter._3B + 4 * batter.HR + \
               batter.R + batter.RBI + batter.HBP + 2 * batter.SB + batter.BB
    negative = 0.5 * batter.SO + batter.CS
    return positive - negative


def write_all_players_to_csv():
    players = read_fangraphs_data()
    return common_players_data.write_all_players_to_csv(players, 'data_b.csv')
