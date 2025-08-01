import sys
import os
import json
import cv2
import sqlite3
import time
from datetime import datetime

from . import db
from . import game
from .hand_detector import HandDetector
from .utils import get_path 


def load_config():
    try:
        config_path = get_path("src/config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERRO] lendo config: {e}")
        sys.exit(1)


def salvar_ranking_db(nome, pontos, tempo):
    db_path = get_path("data/ranking.db")  
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS ranking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            pontos INTEGER NOT NULL,
            tempo INTEGER NOT NULL,
            data TEXT NOT NULL
        )
    """)
    c.execute("INSERT INTO ranking (nome, pontos, tempo, data) VALUES (?, ?, ?, ?)",
              (nome, pontos, tempo, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()


def run_game(tempo_por_letra, jogadores=1, nomes=None):
    cfg = load_config()
    cfg["letter_timer"] = tempo_por_letra
    cfg["jogadores"] = jogadores
    cfg["nomes"] = nomes if nomes and len(nomes) >= 2 else ["Jogador 1", "Jogador 2"]

    cap = cv2.VideoCapture(cfg["camera_index"])
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("[ERRO] câmera não disponível.")
        sys.exit(1)

    detector = HandDetector(cfg)  
    game_instance = game.Game(cfg)

    cv2.namedWindow("Soletrador - LIBRAS")
    cv2.setMouseCallback("Soletrador - LIBRAS", game.mouse_click)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        key = cv2.waitKey(5) & 0xFF

        if not game_instance.check_finished():
            frame, letter = detector.detect(frame)
            if letter:
                game_instance.update(letter)
            result = game_instance.render(frame, letter, key=key)
        else:
            result = game_instance.render_final(frame, key=key)

        if isinstance(result, str) and result == "menu":
            vencedor_idx = 0 if game_instance.scores[0] >= game_instance.scores[1] else 1
            salvar_ranking_db(
                game_instance.nomes[vencedor_idx],
                game_instance.scores[vencedor_idx],
                round(time.time() - game_instance.session_start)
            )
            cap.release()
            cv2.destroyAllWindows()
            return
        else:
            frame = result

        cv2.imshow("Soletrador - LIBRAS", frame)

        if key == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_game(tempo_por_letra=10, jogadores=1, nomes=["Jogador 1", "Jogador 2"])
