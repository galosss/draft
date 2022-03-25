import csv

import batters
import pitchers


def create_data():
    batters_data = batters.write_all_players_to_csv()
    pitchers_data = pitchers.write_all_players_to_csv()
    assert batters_data[0].keys() == pitchers_data[0].keys()
    with open('players_data.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, list(batters_data[0].keys()))
        writer.writeheader()
        rows = sorted(batters_data + pitchers_data, key=lambda player: player["pts"], reverse=True)
        for row in rows:
            writer.writerow(row)
    return rows
