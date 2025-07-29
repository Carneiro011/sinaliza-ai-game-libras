import json
import sys
import cv2
import os
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
            frame = game.render(frame, letter, key=key)
        else:
            result = game.render_final(frame, key=key)
            if result == "menu":
                cap.release()
                cv2.destroyAllWindows()
                import gui
                gui.ConfigScreen().mainloop()
                return

        cv2.imshow("Soletrador - LIBRAS", frame)

        if key == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_game(tempo_por_letra=10, jogadores=1, nomes=["Jogador 1", "Jogador 2"])
