# src/core/utils.py

import os
import sys

def get_path(relative_path: str) -> str:
    """
    Retorna o caminho absoluto de um arquivo, compatível com o PyInstaller.
    """
    base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    return os.path.join(base_path, relative_path)
