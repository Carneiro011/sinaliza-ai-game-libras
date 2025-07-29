import cv2
import numpy as np
import mediapipe as mp
from collections import deque
import pickle
import os

def load_labels(path):
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

class HandDetector:
    def __init__(self, config):
        self.mp_hands = mp.solutions.hands
        self.mp_draw = mp.solutions.drawing_utils
        self.hands = self.mp_hands.Hands(
            static_image_mode=config.get("static_image_mode", False),
            max_num_hands=config.get("max_num_hands", 1),
            min_detection_confidence=config.get("min_detection_confidence", 0.7),
            min_tracking_confidence=config.get("min_tracking_confidence", 0.5)
        )

        # Caminhos absolutos para modelo e labels
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        model_path = os.path.join(project_root, config["model_path"])
        labels_path = os.path.join(project_root, config["labels_file"])

        print(f">>> Carregando modelo de: {model_path}")
        with open(model_path, "rb") as f:
            self.model = pickle.load(f)

        self.labels = load_labels(labels_path)
        print("→ Labels:", self.labels)

        self.history = deque(maxlen=config.get("smoothing_window", 7))
        self.threshold = config.get("prediction_threshold", 0.6)
        self.margin_threshold = config.get("margin_threshold", 0.15)

    def _extract_landmarks(self, hand_landmarks):
        base = np.array([hand_landmarks[0].x, hand_landmarks[0].y, hand_landmarks[0].z])
        pontos = []
        for lm in hand_landmarks:
            ponto = np.array([lm.x, lm.y, lm.z]) - base
            pontos.extend(ponto)
        pontos = np.array(pontos)
        norma = np.linalg.norm(pontos)
        return pontos / norma if norma != 0 else pontos

    def detect(self, frame):
        vis = frame.copy()
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.hands.process(img_rgb)
        letter = ""

        if res.multi_hand_landmarks:
            hand_landmarks = res.multi_hand_landmarks[0]
            pontos = self._extract_landmarks(hand_landmarks.landmark)

            pred = self.model.predict_proba([pontos])[0]

            top_k = min(3, len(pred))
            idxs = np.argsort(pred)[::-1][:top_k]

            debug_text = "  ".join(
                f"{self.labels[i]}:{pred[i]:.2f}" for i in idxs if i < len(self.labels)
            )
            cv2.putText(vis, debug_text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            top = idxs[0]
            conf_top = pred[top]

            if 0 <= top < len(self.labels):
                if conf_top >= self.threshold:
                    letter_raw = self.labels[top]
                    self.history.append(letter_raw)
            else:
                print(f"[AVISO] Índice fora do intervalo de labels: {top}")

            votes = [l for l in self.history if l]
            if votes:
                letter = max(set(votes), key=votes.count)

            for lm in res.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(vis, lm, self.mp_hands.HAND_CONNECTIONS)
        else:
            self.history.clear()

        return vis, letter
