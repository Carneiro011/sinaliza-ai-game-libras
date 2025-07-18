import json
import os
import random
import time
import pygame
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

class Game:
    def __init__(self, config):
        self.config = config
        self.words = config["words"]
        self.ranking_file = "ranking.json"
        self.sound_path = "src/vitoria.mp3"
        self.font_path = "seguiemj.ttf"  # Ou "arial.ttf"
        self.reset()

        pygame.mixer.init()
        if os.path.exists(self.sound_path):
            pygame.mixer.music.load(self.sound_path)

    def reset(self):
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
            self.save_ranking()
            self.finished = True

    def update(self, pred_letter):
        now = time.time()
        if now - self.last_time > self.letter_timer:
            self.feedback = "⏳ TEMPO ESGOTADO!"
            self.feedback_time = 30
            self.skip_letter()
            self.last_time = now
            return

        target = self.words[self.idx_word][self.idx_letter]
        if pred_letter == target:
            self.points += 10
            self.idx_letter += 1
            self.feedback = "✅ ACERTOU!"
            self.feedback_time = 30
            self.last_time = now

            if self.idx_letter >= len(self.words[self.idx_word]):
                self.points += 50
                self.feedback = "🎉 PALAVRA COMPLETA!"
                self.feedback_time = 60
                self.completed.append(self.words[self.idx_word])
                self.idx_word += 1
                self.idx_letter = 0

                if self.idx_word >= len(self.words):
                    self.feedback = "🏁 FIM DO JOGO!"
                    self.save_ranking()
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

    def save_ranking(self):
        ranking = []
        if os.path.exists(self.ranking_file):
            try:
                with open(self.ranking_file, "r", encoding="utf-8") as f:
                    ranking = json.load(f)
            except:
                ranking = []
        ranking.append({
            "pontos": self.points,
            "tempo": round(time.time() - self.session_start)
        })
        ranking = sorted(ranking, key=lambda x: (-x["pontos"], x["tempo"]))[:5]
        with open(self.ranking_file, "w", encoding="utf-8") as f:
            json.dump(ranking, f, indent=2)

    def load_ranking(self):
        if os.path.exists(self.ranking_file):
            try:
                with open(self.ranking_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def draw_unicode_text(self, frame, text, position, font_size=32, color=(255, 255, 255), center=False):
        img_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(img_pil)

        try:
            font = ImageFont.truetype(self.font_path, font_size)
        except:
            font = ImageFont.load_default()

        if center:
            text_size = draw.textbbox((0, 0), text, font=font)
            text_width = text_size[2] - text_size[0]
            position = (position[0] - text_width // 2, position[1])

        draw.text(position, text, font=font, fill=color)
        return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)

    def render(self, frame, pred_letter, key=None):
        h, w, _ = frame.shape

        if self.finished:
            return self.render_final(frame, key)

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

        frame = self.draw_unicode_text(frame, f"PONTOS: {self.points}", (w - 300, 40), 28)
        frame = self.draw_unicode_text(frame, f"Previsto: {pred_letter}", (50, h - 50), 28)
        tempo_restante = max(0, int(self.letter_timer - (time.time() - self.last_time)))
        frame = self.draw_unicode_text(frame, f"Tempo: {tempo_restante}s", (w - 300, h - 50), 28)

        if self.feedback_time > 0:
            frame = self.draw_unicode_text(frame, self.feedback, (w // 2, h // 2), 40, (0, 255, 0), center=True)
            self.feedback_time -= 1

        return frame

    def render_final(self, frame, key=None):
        h, w, _ = frame.shape

        if not self.played_sound and os.path.exists(self.sound_path):
            pygame.mixer.music.play(loops=0)
            self.played_sound = True

        self._draw_confetes(frame)

        frame = self.draw_unicode_text(frame, "🎉 PARABÉNS!", (w // 2, h // 2 - 100), 48, (0, 255, 0), center=True)
        frame = self.draw_unicode_text(frame, f"Pontuação final: {self.points}", (w // 2, h // 2 - 30), 36, (255, 255, 255), center=True)
        frame = self.draw_unicode_text(frame, "Pressione R para jogar novamente", (w // 2, h // 2 + 30), 28, (255, 255, 0), center=True)
        frame = self.draw_unicode_text(frame, "Pressione ESC para sair ❌", (w // 2, h // 2 + 70), 28, (255, 255, 255), center=True)

        ranking = self.load_ranking()
        y = h // 2 + 120
        frame = self.draw_unicode_text(frame, "🏆 Ranking:", (w // 2, y), 28, (255, 215, 0), center=True)
        for i, r in enumerate(ranking):
            y += 35
            texto = f"{i + 1}º - {r['pontos']} pts em {r['tempo']}s"
            frame = self.draw_unicode_text(frame, texto, (w // 2, y), 24, center=True)

        if key == ord('r'):
            self.reset()

        return frame
