import sys
import os

# Adiciona a pasta src ao sys.path (necessário para importar 'core.main')
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tkinter as tk
import customtkinter as ctk
import json
from core import main



ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

def load_config():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.abspath(os.path.join(base_dir, "..", "..", "config.json"))
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERRO] ao ler config: {e}")
        return {}

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GAME-LIBRAS")
        self.geometry("700x500")
        self.resizable(False, False)

        self.config_data = load_config()
        self.temporizador = tk.IntVar(value=self.config_data.get("letter_timer", 10))
        self.num_jogadores = tk.IntVar(value=1)
        self.nome1 = tk.StringVar(value="Jogador 1")
        self.nome2 = tk.StringVar(value="Jogador 2")

        self.label_valor_tempo = None  # referência ao valor do tempo mostrado
        self.criar_abas()

    def criar_abas(self):
        self.frame_abas = ctk.CTkFrame(self)
        self.frame_abas.pack(fill="x", pady=(10, 0))

        self.btn_inicio = ctk.CTkButton(self.frame_abas, text="🏠 Início", command=self.mostrar_inicio)
        self.btn_inicio.pack(side="left", padx=10)

        self.btn_config = ctk.CTkButton(self.frame_abas, text="⚙️ Configurar Jogo", command=self.mostrar_config)
        self.btn_config.pack(side="left", padx=10)

        self.frame_conteudo = ctk.CTkFrame(self)
        self.frame_conteudo.pack(fill="both", expand=True, padx=20, pady=20)

        self.mostrar_inicio()

    def limpar_conteudo(self):
        for widget in self.frame_conteudo.winfo_children():
            widget.destroy()

    def mostrar_inicio(self):
        self.limpar_conteudo()

        ctk.CTkLabel(self.frame_conteudo, text="🏆 Ranking", font=("Arial", 20)).pack(pady=10)

        ranking = self.carregar_ranking()
        if not ranking:
            ctk.CTkLabel(self.frame_conteudo, text="Nenhum ranking disponível.").pack()
        else:
            for i, r in enumerate(ranking):
                texto = f"{i+1}º - {r.get('nome', 'Jogador')} - {r['pontos']} pts em {r['tempo']}s"
                ctk.CTkLabel(self.frame_conteudo, text=texto).pack()

        ctk.CTkButton(self.frame_conteudo, text="▶️ Iniciar Jogo", command=self.iniciar_jogo).pack(pady=20)

    def mostrar_config(self):
        self.limpar_conteudo()

        ctk.CTkLabel(self.frame_conteudo, text="⚙️ Configurações", font=("Arial", 20)).pack(pady=10)

        ctk.CTkLabel(self.frame_conteudo, text="⏱️ Tempo por letra (segundos):").pack()

        tempo_frame = ctk.CTkFrame(self.frame_conteudo, fg_color="transparent")
        tempo_frame.pack()

        ctk.CTkSlider(
            tempo_frame,
            from_=3, to=20,
            variable=self.temporizador,
            number_of_steps=17,
            command=self.atualizar_tempo_valor
        ).pack(side="left", padx=5)

        self.label_valor_tempo = ctk.CTkLabel(tempo_frame, text=f"{self.temporizador.get()}s")
        self.label_valor_tempo.pack(side="left")

        ctk.CTkLabel(self.frame_conteudo, text="👥 Número de jogadores:").pack(pady=(10, 0))
        ctk.CTkOptionMenu(self.frame_conteudo, variable=self.num_jogadores, values=["1", "2"]).pack(pady=5)

        ctk.CTkLabel(self.frame_conteudo, text="👤 Nome do Jogador 1:").pack(pady=(10, 0))
        ctk.CTkEntry(self.frame_conteudo, textvariable=self.nome1).pack()

        ctk.CTkLabel(self.frame_conteudo, text="👤 Nome do Jogador 2:").pack(pady=(10, 0))
        ctk.CTkEntry(self.frame_conteudo, textvariable=self.nome2).pack()

    def atualizar_tempo_valor(self, value):
        if self.label_valor_tempo:
            self.label_valor_tempo.configure(text=f"{int(float(value))}s")

    def iniciar_jogo(self):
        tempo = int(self.temporizador.get())
        jogadores = int(self.num_jogadores.get())
        nomes = [self.nome1.get(), self.nome2.get()]
        main.run_game(tempo, jogadores, nomes)

    def carregar_ranking(self):
        caminho = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "ranking.json"))
        if os.path.exists(caminho):
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

if __name__ == "__main__":
    app = App()
    app.mainloop()
