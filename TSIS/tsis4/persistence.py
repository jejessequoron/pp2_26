import json
import psycopg2
from config import load_config

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "snake_color": [255, 255, 0],
    "grid": True,
    "sound": True,
}

def load_settings():
    with open(SETTINGS_FILE) as f:
        data = json.load(f)
    for key in DEFAULT_SETTINGS:
        if key not in data:
            data[key] = DEFAULT_SETTINGS[key]
    return data

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as file:
        json.dump(settings, file, indent=4)

def connect_db():
    config = load_config()
    conn = psycopg2.connect(**config)
    with conn.cursor() as cur:
        with open("schema.sql") as file:
            cur.execute(file.read())
        conn.commit()
    return conn

def get_player_id(conn, username):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO players(username)
            VALUES (%s)
            ON CONFLICT (username)
            DO UPDATE SET username = EXCLUDED.username
            RETURNING id
            """,
            (username,),
        )
        player_id = cur.fetchone()[0]
        conn.commit()
        return player_id

def save_result(conn, username, score, level):
    player_id = get_player_id(conn, username)
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO game_sessions(player_id, score, level_reached)
            VALUES (%s, %s, %s)
            """,
            (player_id, score, level),
        )
        conn.commit()

def get_personal_best(conn, username):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COALESCE(MAX(gs.score), 0)
            FROM game_sessions gs
            JOIN players p ON p.id = gs.player_id
            WHERE p.username = %s
            """,
            (username,),
        )
        return cur.fetchone()[0]

def get_top_scores(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT p.username, gs.score, gs.level_reached,
                   to_char(gs.played_at, 'YYYY-MM-DD HH24:MI')
            FROM game_sessions gs
            JOIN players p ON p.id = gs.player_id
            ORDER BY gs.score DESC, gs.played_at ASC
            LIMIT 10
            """
        )
        return cur.fetchall()