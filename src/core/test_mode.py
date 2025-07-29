# test_mode.py
import cv2
import sys
import os
from hand_detector import HandDetector
from game import Game  # Para usar o método de desenhar texto
import json

def load_config():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.abspath(os.path.join(base_dir, "..", "config.json"))
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERRO] lendo config: {e}")
        sys.exit(1)

def run_test():
    cfg = load_config()
    cap = cv2.VideoCapture(cfg["camera_index"])
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():
        print("[ERRO] câmera não disponível.")
        sys.exit(1)

    detector = HandDetector(cfg)
    dummy_game = Game(cfg)  # Para usar draw_unicode_text

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        frame, letter = detector.detect(frame)

        h, w, _ = frame.shape
        frame = dummy_game.draw_unicode_text(frame, "Modo de Teste de Gestos", (w // 2, 40), 32, (255, 255, 0), center=True)
        frame = dummy_game.draw_unicode_text(frame, f"Letra detectada: {letter}", (w // 2, h - 60), 36, (0, 255, 0), center=True)
        frame = dummy_game.draw_unicode_text(frame, "Pressione ESC para sair", (w // 2, h - 30), 24, (200, 200, 200), center=True)

        cv2.imshow("Teste de Gestos", frame)
        key = cv2.waitKey(5) & 0xFF
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
