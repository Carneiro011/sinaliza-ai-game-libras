# 🧠 Sinaliza Aí! - GAME-LIBRAS

**Sinaliza Aí!** é um jogo educativo interativo para auxiliar o aprendizado da Língua Brasileira de Sinais (LIBRAS), utilizando visão computacional para reconhecer gestos capturados por uma webcam.

## 📦 Requisitos

- Python 3.10 ou superior
- Windows (versão com executável `.exe` gerado via PyInstaller)
- Webcam funcional

## 🧪 Funcionalidades

- Reconhecimento em tempo real de letras em LIBRAS com MediaPipe + modelo MLP
- Modo de teste de gestos
- Jogo competitivo com até 2 jogadores
- Ranking com pontuações salvas em SQLite
- Interface com abas (Início, Configurações)
- Sons e feedback visual para acertos e erros
- Sistema de pontuação com tempo e bonificações

## 🎮 Como Jogar

1. Execute o programa (`Sinaliza Ai!.exe` ou `main.py`).
2. Vá até "Configurar Jogo" e defina:
   - Tempo por letra
   - Número de jogadores
   - Nomes dos jogadores
3. Clique em **Iniciar Jogo**.
4. Sinalize as letras conforme aparecem na tela.
5. Ao final, veja sua pontuação e o ranking!

## 📁 Estrutura do Projeto

├── data/
│ └── ranking.db
├── models/
│ └── modelo_libras.pkl
├── src/
│ ├── assets/
│ │ ├── vitoria.mp3
│ │ └── seguiemj.ttf
│ ├── core/
│ │ ├── gui.py
│ │ ├── game.py
│ │ ├── main.py
│ │ └── test_mode.py
│ ├── config.json
│ └── labels.txt


## 🔨 Como Compilar (.exe)

```bash
pyinstaller src/core/gui.py ^
  --name "Sinaliza Ai!" ^
  --noconfirm ^
  --clean ^
  --onefile ^
  --windowed ^
  --icon=favicon.ico ^
  --paths=src ^
  --add-data "models/modelo_libras.pkl;models" ^
  --add-data "data/ranking.db;data" ^
  --add-data "src/config.json;src" ^
  --add-data "src/labels.txt;src" ^
  --add-data "src/assets/vitoria.mp3;src/assets" ^
  --add-data "src/assets/seguiemj.ttf;src/assets"


Créditos
Desenvolvido por Guilherme Carneiro
Projeto acadêmico com fins educacionais.
Inspirado no ensino e inclusão através da LIBRAS.