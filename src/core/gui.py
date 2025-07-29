import tkinter as tk
from tkinter import ttk, messagebox
import main
import os
import json

class ConfigScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Configurações do Soletrador")
        self.geometry("400x400")

        self.tempo_var = tk.IntVar(value=10)
        self.jogadores_var = tk.IntVar(value=2)
        self.nome1 = tk.StringVar(value="Jogador 1")
        self.nome2 = tk.StringVar(value="Jogador 2")

        tk.Label(self, text="⏳ Tempo por letra (s):").pack(pady=5)
        tk.Spinbox(self, from_=5, to=30, textvariable=self.tempo_var).pack()

        tk.Label(self, text="🎮 Número de jogadores:").pack(pady=5)
        ttk.Combobox(self, values=[1, 2], textvariable=self.jogadores_var).pack()

        tk.Label(self, text="🧑 Nome do Jogador 1:").pack(pady=5)
        tk.Entry(self, textvariable=self.nome1).pack()

        tk.Label(self, text="🧑 Nome do Jogador 2:").pack(pady=5)
        tk.Entry(self, textvariable=self.nome2).pack()

        tk.Button(self, text="Iniciar Jogo", command=self.start_game).pack(pady=15)
        tk.Button(self, text="Modo de Teste", command=self.start_test_mode).pack(pady=5)
        tk.Button(self, text="Ver Ranking 🏆", command=self.show_ranking).pack(pady=5)

    def start_game(self):
        tempo = self.tempo_var.get()
        jogadores = self.jogadores_var.get()
        nomes = [self.nome1.get(), self.nome2.get()]
        self.destroy()
        main.run_game(tempo, jogadores, nomes)

    def start_test_mode(self):
        self.destroy()
        import test_mode
        test_mode.run_test()

    def show_ranking(self):
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "ranking.json"))
        if not os.path.exists(path):
            messagebox.showinfo("Ranking", "Nenhum ranking salvo ainda.")
            return

        with open(path, "r", encoding="utf-8") as f:
            ranking = json.load(f)

        texto = "\n".join([f"{i+1}º - {r['pontos']} pts em {r['tempo']}s" for i, r in enumerate(ranking)])
        messagebox.showinfo("🏆 Ranking", texto or "Nenhum dado disponível.")

if __name__ == "__main__":
    app = ConfigScreen()
    app.mainloop()
