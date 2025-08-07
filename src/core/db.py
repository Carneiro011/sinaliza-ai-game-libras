import sqlite3
import os

# Caminho para o banco de dados
DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "ranking.db"))

def init_db():
    """Inicializa o banco e a tabela de ranking se não existirem."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ranking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            pontos REAL NOT NULL,
            tempo INTEGER NOT NULL,
            data DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def salvar_partida(nome, pontos, tempo):
    """Salva uma nova entrada de partida no ranking."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ranking (nome, pontos, tempo)
        VALUES (?, ?, ?)
    """, (nome, round(pontos, 2), tempo))
    conn.commit()
    conn.close()

def obter_top5():
    """Retorna os 5 melhores jogadores por pontuação (e menor tempo em empate)."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nome, pontos, tempo, strftime('%d/%m/%Y %H:%M', data)
        FROM ranking
        ORDER BY pontos DESC, tempo ASC
        LIMIT 5
    """)
    resultados = cursor.fetchall()
    conn.close()
    return resultados
