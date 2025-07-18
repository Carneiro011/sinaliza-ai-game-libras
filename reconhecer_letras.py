import cv2
import mediapipe as mp
import numpy as np
import pickle

# Carregar o modelo treinado
with open("modelo_libras.pkl", "rb") as f:
    model = pickle.load(f)

# Inicializar o Mediapipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.7)
drawing_utils = mp.solutions.drawing_utils

# Função para normalizar os landmarks (igual à usada no treinamento)
def extrair_landmarks_normalizados(landmarks):
    base = np.array([landmarks[0].x, landmarks[0].y, landmarks[0].z])
    pontos = []
    for lm in landmarks:
        ponto = np.array([lm.x, lm.y, lm.z]) - base
        pontos.extend(ponto)
    pontos = np.array(pontos)
    norma = np.linalg.norm(pontos)
    return pontos / norma if norma != 0 else pontos

# Abrir webcam
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    img = cv2.flip(frame, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]

        # Normalizar os pontos antes da predição
        pontos_normalizados = extrair_landmarks_normalizados(hand_landmarks.landmark)

        # Fazer predição
        pred = model.predict([pontos_normalizados])[0]

        # Desenhar landmarks e resultado
        drawing_utils.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        cv2.putText(img, f"Letra: {pred}", (10, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Reconhecimento de Libras", img)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC para sair
        break

cap.release()
cv2.destroyAllWindows()
