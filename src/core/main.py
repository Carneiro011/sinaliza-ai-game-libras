import json
import sys
import cv2
import os
import sqlite3
from datetime import datetime
import time
from hand_detector import HandDetector
from game import Game


def load_config():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(base_dir, "..", "config.json"))
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERRO] lendo config: {e}")
        sys.exit(1)


def salvar_ranking_db(nome, pontos, tempo):
    db_path = os.path.abspath(os.path.join("data", "ranking.db"))
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
    game = Game(cfg)

    # Configura callback de clique
    cv2.namedWindow("Soletrador - LIBRAS")
    import game as game_module
    cv2.setMouseCallback("Soletrador - LIBRAS", game_module.mouse_click)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        key = cv2.waitKey(5) & 0xFF

        if not game.check_finished():
            frame, letter = detector.detect(frame)
            if letter:
                game.update(letter)
            result = game.render(frame, letter, key=key)
        else:
            result = game.render_final(frame, key=key)

        # Verifica se retornou ao menu
        if isinstance(result, str) and result == "menu":
            vencedor_idx = 0 if game.scores[0] >= game.scores[1] else 1
            salvar_ranking_db(
                game.nomes[vencedor_idx],
                game.scores[vencedor_idx],
                round(time.time() - game.session_start)
            )
            cap.release()
            cv2.destroyAllWindows()
            return  # <-- Apenas retorna, não cria nova janela!
        else:
            frame = result

        cv2.imshow("Soletrador - LIBRAS", frame)

        if key == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_game(tempo_por_letra=10, jogadores=1, nomes=["Jogador 1", "Jogador 2"])
