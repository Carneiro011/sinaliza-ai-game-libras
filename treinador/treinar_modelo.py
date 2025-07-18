import pickle
import os
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Definir caminhos corretos
BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "models", "dados_libras.pkl"))
MODEL_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "models", "modelo_libras.pkl"))
LABELS_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "src", "labels.txt"))

# Carregar dados
with open(DATA_PATH, "rb") as f:
    X, y = pickle.load(f)

# Dividir em treino/teste
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Treinar o modelo
clf = MLPClassifier(hidden_layer_sizes=(128, 64), max_iter=1000)
clf.fit(X_train, y_train)

# Avaliar
print("✅ Avaliação do modelo:")
print(classification_report(y_test, clf.predict(X_test)))

# Salvar modelo
with open(MODEL_PATH, "wb") as f:
    pickle.dump(clf, f)
print(f"💾 Modelo salvo em: {MODEL_PATH}")

# Salvar labels únicos ordenados (para o reconhecimento visual)
labels_unicos = sorted(set(y))
with open(LABELS_PATH, "w", encoding="utf-8") as f:
    for label in labels_unicos:
        f.write(label + "\n")
print(f"📄 Labels salvos em: {LABELS_PATH}")
