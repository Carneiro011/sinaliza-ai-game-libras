# game.py
import json
import os
import random
import time
import pygame
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image

click_coords = [None]

def mouse_click(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        click_coords[0] = (x, y)

class Game:
    def __init__(self, config):
        self.config = config
        self.words = config["words"]
        self.ranking_file = "data/ranking.json"
        self.sound_path = "src/assets/vitoria.mp3"
        self.font_path = "src/assets/seguiemj.ttf"
        self.letter_timer = config.get("letter_timer", 10)
        self.num_players = config.get("jogadores", 1)
        self.nomes = config.get("nomes", ["Jogador 1", "Jogador 2"])
        self.current_player = 0
        self.scores = [0, 0]
        self.reset()

        pygame.mixer.init()
        if os.path.exists(self.sound_path):
            pygame.mixer.music.load(self.sound_path)

    def reset(self):
        random.shuffle(self.words)
        self.idx_word = 0
        self.idx_letter = 0
        self.feedback = ""
        self.feedback_time = 0
        self.last_time = time.time()
        self.session_start = time.time()
        self.completed = []
        self.finished = False
        self.confetes = []
        self.played_sound = False
        self.current_player = 0
        self.scores = [0, 0]
        click_coords[0] = None

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
            self.feedback = "🏁 FIM DO JOGO!"
            self.save_ranking()
            self.finished = True
        elif self.num_players == 2:
            self.current_player = (self.current_player + 1) % 2

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
            self.scores[self.current_player] += 10
            self.idx_letter += 1
            self.feedback = "✅ ACERTOU!"
            self.feedback_time = 30
            self.last_time = now

            if self.idx_letter >= len(self.words[self.idx_word]):
                self.scores[self.current_player] += 50
                self.feedback = "🎉 PALAVRA COMPLETA!"
                self.feedback_time = 60
                self.completed.append(self.words[self.idx_word])
                self.idx_word += 1
                self.idx_letter = 0
                if self.num_players == 2:
                    self.current_player = (self.current_player + 1) % 2
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

        vencedor_idx = 0 if self.scores[0] >= self.scores[1] else 1
        ranking.append({
            "nome": self.nomes[vencedor_idx],
            "pontos": self.scores[vencedor_idx],
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

    def draw_time_bar(self, frame):
        h, w, _ = frame.shape
        elapsed = time.time() - self.last_time
        total = self.letter_timer
        remaining_ratio = max(0, (total - elapsed) / total)
        bar_total_width = int(w * 0.6)
        bar_width = int(bar_total_width * remaining_ratio)
        bar_height = 30
        x_start = int((w - bar_total_width) // 2)
        y_start = h - 100
        if remaining_ratio > 0.5:
            color = (0, 255, 0)
        elif remaining_ratio > 0.2:
            color = (0, 255, 255)
        else:
            color = (0, 0, 255)
        cv2.rectangle(frame, (x_start, y_start), (x_start + bar_width, y_start + bar_height), color, -1)
        cv2.rectangle(frame, (x_start, y_start), (x_start + bar_total_width, y_start + bar_height), (255, 255, 255), 2)
        return frame

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

        if self.num_players == 1:
            frame = self.draw_unicode_text(frame, f"{self.nomes[0]}: {self.scores[0]} pts", (w - 300, 40), 28)
        else:
            frame = self.draw_unicode_text(frame, f"{self.nomes[0]}: {self.scores[0]} pts", (w - 300, 40), 28)
            frame = self.draw_unicode_text(frame, f"{self.nomes[1]}: {self.scores[1]} pts", (w - 300, 80), 28)

        frame = self.draw_unicode_text(frame, f"🎯 Vez de: {self.nomes[self.current_player]}", (w // 2, 40), 28, (0, 255, 255), center=True)
        frame = self.draw_unicode_text(frame, f"Previsto: {pred_letter}", (50, h - 50), 28)
        tempo_restante = max(0, int(self.letter_timer - (time.time() - self.last_time)))
        frame = self.draw_unicode_text(frame, f"{tempo_restante}s", (w - 100, h - 50), 28)

        if self.feedback_time > 0:
            frame = self.draw_unicode_text(frame, self.feedback, (w // 2, h // 2), 40, (0, 255, 0), center=True)
            self.feedback_time -= 1

        frame = self.draw_time_bar(frame)

        # Botão voltar ao menu
        cv2.rectangle(frame, (10, 10), (50, 50), (255, 255, 255), -1)
        pts = np.array([[18, 30], [40, 18], [40, 42]], np.int32)
        cv2.fillPoly(frame, [pts], (0, 0, 0))
        if click_coords[0]:
            cx, cy = click_coords[0]
            if 10 <= cx <= 50 and 10 <= cy <= 50:
                click_coords[0] = None
                pygame.mixer.music.stop()
                self.finished = True
                return self.render_final(frame, key=ord('m'))

        return frame

    def render_final(self, frame, key=None):
        h, w, _ = frame.shape
        if not self.played_sound and os.path.exists(self.sound_path):
            pygame.mixer.music.play(loops=0)
            self.played_sound = True

        self._draw_confetes(frame)
        frame = self.draw_unicode_text(frame, "🎉 PARABÉNS!", (w // 2, h // 2 - 100), 48, (0, 255, 0), center=True)
        frame = self.draw_unicode_text(frame, f"{self.nomes[0]}: {self.scores[0]} pts", (w // 2, h // 2 - 30), 36, (255, 255, 255), center=True)

        if self.num_players == 2:
            frame = self.draw_unicode_text(frame, f"{self.nomes[1]}: {self.scores[1]} pts", (w // 2, h // 2 + 10), 36, (255, 255, 255), center=True)

        if self.scores[0] > self.scores[1]:
            result = f"🏆 {self.nomes[0]} venceu!"
        elif self.scores[1] > self.scores[0]:
            result = f"🏆 {self.nomes[1]} venceu!"
        else:
            result = "🤝 Empate!"

        frame = self.draw_unicode_text(frame, result, (w // 2, h // 2 + 50), 30, (0, 255, 255), center=True)
        frame = self.draw_unicode_text(frame, "Pressione R para jogar novamente", (w // 2, h // 2 + 90), 28, (255, 255, 0), center=True)
        frame = self.draw_unicode_text(frame, "Pressione ESC para sair ❌", (w // 2, h // 2 + 130), 28, (255, 255, 255), center=True)

        # Botão de voltar
        cv2.rectangle(frame, (10, 10), (50, 50), (255, 255, 255), -1)
        pts = np.array([[18, 30], [40, 18], [40, 42]], np.int32)
        cv2.fillPoly(frame, [pts], (0, 0, 0))
        if click_coords[0]:
            cx, cy = click_coords[0]
            if 10 <= cx <= 50 and 10 <= cy <= 50:
                click_coords[0] = None
                pygame.mixer.music.stop()
                return "menu"

        ranking = self.load_ranking()
        y = h // 2 + 180
        frame = self.draw_unicode_text(frame, "🏆 Ranking:", (w // 2, y), 28, (255, 215, 0), center=True)
        for i, r in enumerate(ranking):
            y += 35
            texto = f"{i + 1}º - {r.get('nome', 'Jogador')} - {r['pontos']} pts em {r['tempo']}s"
            frame = self.draw_unicode_text(frame, texto, (w // 2, y), 24, center=True)

        if key == ord('r'):
            self.reset()

        return frame
