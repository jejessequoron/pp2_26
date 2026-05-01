import json

SETTINGS_FILE = "settings.json"
LEADERBOARD_FILE = "leaderboard.json"

default_settings = {
    "sound": True,
    "car_color": "red",
    "difficulty": "normal",
}

def load_settings():
    with open(SETTINGS_FILE) as f:
        settings = json.load(f)
    for key in default_settings:
        if key not in settings:
            settings[key] = default_settings[key]
    return settings

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

def load_leaderboard():
    with open(LEADERBOARD_FILE) as f:
        return json.load(f)

def save_score(leaderboard, name, score, distance, coins):
    leaderboard.append(
        {
            "name": name,
            "score": int(score),
            "distance": int(distance),
            "coins": int(coins),
        }
    )
    leaderboard.sort(key=lambda row: row["score"], reverse=True)
    while len(leaderboard) > 10:
        leaderboard.pop()
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard, f, indent=4)