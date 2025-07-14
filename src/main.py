import json, sys, cv2, os
from hand_detector import HandDetector
from game         import Game

def load_config(path="config.json"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERRO] lendo config: {e}")
        sys.exit(1)

def main():
    cfg = load_config(os.path.join(os.path.dirname(__file__),"config.json"))
    cap = cv2.VideoCapture(cfg["camera_index"])
    if not cap.isOpened():
        print("[ERRO] câmera não disponível.")
        sys.exit(1)

    detector = HandDetector(cfg)
    game     = Game(cfg)

    while True:
        ret, frame = cap.read()
        if not ret: break

        frame = cv2.flip(frame, 1)
        frame, letter = detector.detect(frame)
        if letter:
            game.update(letter)
        frame = game.render(frame, letter)

        cv2.imshow("Herói do Alfabeto", frame)
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
