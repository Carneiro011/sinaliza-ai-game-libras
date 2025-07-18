import cv2
import time
import random
import json
import os
import pygame

class Game:
    def __init__(self, config):
        self.words = config["words"]
        random.shuffle(self.words)
        self.idx_word = 0
        self.idx_letter = 0
        self.points = 0
        self.feedback = ""
        self.feedback_time = 0
        self.letter_timer = 10
        self.last_time = time.time()
        self.session_start = time.time()
        self.completed = []
        self.finished = False
        self.confetes = []
        self.played_sound = False
        self.progress_file = "progresso.json"
        self.sound_path = "vitoria.mp3"

        # Inicializar pygame para tocar som
        pygame.mixer.init()
        if os.path.exists(self.sound_path):
            pygame.mixer.music.load(self.sound_path)

        self.load_progress()

    def load_progress(self):
        if os.path.exists(self.progress_file):
            with open(self.progress_file, "r", encoding="utf-8") as f:
                self.saved_progress = json.load(f)
        else:
            self.saved_progress = {}

    def save_progress(self):
        data = {
            "pontos": self.points,
            "palavras_completas": self.completed,
            "tempo_total": round(time.time() - self.session_start)
        }
        with open(self.progress_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def check_finished(self):
        return self.finished

    def skip_letter(self):
        self.idx_letter += 1
        if self.idx_letter >= len(self.words[self.idx_word]):
            self.skip_word()

    def skip_word(self):
        self.idx_word += 1
        self.idx_letter = 0
        if self.idx_word >= len(self.words):
            self.feedback = "FIM DO JOGO!"
            self.save_progress()
            self.finished = True

    def update(self, pred_letter):
        now = time.time()
        if now - self.last_time > self.letter_timer:
            self.feedback = "TEMPO ESGOTADO!"
            self.feedback_time = 30
            self.skip_letter()
            self.last_time = now
            return

        target = self.words[self.idx_word][self.idx_letter]
        if pred_letter == target:
            self.points += 10
            self.idx_letter += 1
            self.feedback = "ACERTOU!"
            self.feedback_time = 30
            self.last_time = now

            if self.idx_letter >= len(self.words[self.idx_word]):
                self.points += 50
                self.feedback = "PALAVRA COMPLETA!"
                self.feedback_time = 60
                self.completed.append(self.words[self.idx_word])
                self.idx_word += 1
                self.idx_letter = 0

                if self.idx_word >= len(self.words):
                    self.feedback = "FIM DO JOGO!"
                    self.save_progress()
                    self.finished = True

    def _draw_confetes(self, frame):
        h, w, _ = frame.shape
        if len(self.confetes) < 100:
            for _ in range(5):
                self.confetes.append({
                    "x": random.randint(0, w),
                    "y": random.randint(-100, 0),
                    "color": (
                        random.randint(100, 255),
                        random.randint(100, 255),
                        random.randint(100, 255)
                    ),
                    "speed": random.randint(3, 10)
                })
        for c in self.confetes:
            c["y"] += c["speed"]
            if c["y"] > h:
                c["y"] = random.randint(-100, 0)
                c["x"] = random.randint(0, w)
            cv2.circle(frame, (c["x"], c["y"]), 5, c["color"], -1)

    def render(self, frame, pred_letter, key=None):
        h, w, _ = frame.shape
        word = self.words[self.idx_word]

        if key == ord('p'):
            self.feedback = "Letra pulada!"
            self.feedback_time = 30
            self.skip_letter()
        elif key == ord('w'):
            self.feedback = "Palavra pulada!"
            self.feedback_time = 30
            self.skip_word()

        x = 50
        for i, ch in enumerate(word):
            cor = (255, 255, 255)
            if i < self.idx_letter:
                cor = (0, 255, 0)
            elif i == self.idx_letter:
                cor = (0, 255, 255)
            cv2.putText(frame, ch, (x, 100), cv2.FONT_HERSHEY_SIMPLEX, 2, cor, 3)
            x += 60

        cv2.putText(frame, f"PONTOS: {self.points}", (w - 300, 50),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

        cv2.putText(frame, f"Previsto: {pred_letter}", (50, h - 50),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255), 2)

        tempo_restante = max(0, int(self.letter_timer - (time.time() - self.last_time)))
        cv2.putText(frame, f"Tempo: {tempo_restante}s", (w - 300, h - 50),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 150, 255), 2)

        if self.feedback_time > 0:
            cv2.putText(frame, self.feedback, (w // 2 - 200, h // 2),
                        cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            self.feedback_time -= 1

        return frame

    def render_final(self, frame):
        h, w, _ = frame.shape

        if not self.played_sound:
            try:
                pygame.mixer.music.play()
                self.played_sound = True
            except Exception as e:
                print(f"[ERRO] ao tocar som de vitória: {e}")

        self._draw_confetes(frame)

        cv2.putText(frame, "🎉 PARABÉNS!", (w//2 - 250, h//2 - 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 4)
        cv2.putText(frame, f"Pontuação final: {self.points}", (w//2 - 250, h//2 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
        cv2.putText(frame, "Pressione ESC para sair", (w//2 - 200, h//2 + 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        return frame
