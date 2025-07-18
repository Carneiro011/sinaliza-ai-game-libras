import cv2
import mediapipe as mp
import numpy as np
import pickle
from collections import defaultdict

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=2, min_detection_confidence=0.7)
cap = cv2.VideoCapture(0)

data = []
labels = []
contador_por_letra = defaultdict(int)

print("📸 Coletor de dados - Libras com melhorias")
print("👉 Mostre a mão para a câmera e pressione uma letra (A-Z) para registrar.")
print("✅ Pressione 'Q' para salvar e sair.")
print("❌ Pressione 'ESC' para sair (com confirmação).")

def extrair_landmarks_normalizados(landmarks):
    base = np.array([landmarks[0].x, landmarks[0].y, landmarks[0].z])
    pontos = []
    for lm in landmarks:
        ponto = np.array([lm.x, lm.y, lm.z]) - base
        pontos.extend(ponto)
    pontos = np.array(pontos)
    norma = np.linalg.norm(pontos)
    return pontos / norma if norma != 0 else pontos

def salvar_dados():
    with open("dados_libras.pkl", "wb") as f:
        pickle.dump((data, labels), f)
    print("✅ Dados salvos em 'dados_libras.pkl'.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    img = cv2.flip(frame, 1)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    img_mostrar = img.copy()
    key = cv2.waitKey(1) & 0xFF

    if results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            pontos_normalizados = extrair_landmarks_normalizados(hand_landmarks.landmark)

            mp.solutions.drawing_utils.draw_landmarks(
                img_mostrar, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            if key != 255:
                char = chr(key).upper()
                if char.isalpha():
                    data.append(pontos_normalizados)
                    labels.append(char)
                    contador_por_letra[char] += 1
                    print(f"🔡 Letra '{char}' registrada ({contador_por_letra[char]} amostras).")
                elif char == 'Q':
                    print("💾 Salvando e saindo...")
                    salvar_dados()
                    cap.release()
                    cv2.destroyAllWindows()
                    exit()
                elif key == 27:  # ESC
                    resposta = input("❓ Deseja salvar os dados antes de sair? (s/n): ").strip().lower()
                    if resposta == 's':
                        salvar_dados()
                    else:
                        print("⚠️ Saída sem salvar.")
                    cap.release()
                    cv2.destroyAllWindows()
                    exit()

    texto_status = "Pressione uma letra (A-Z), Q para salvar, ESC para sair"
    cv2.putText(img_mostrar, texto_status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    y = 60
    for letra in sorted(contador_por_letra):
        cv2.putText(img_mostrar, f"{letra}: {contador_por_letra[letra]} amostras", (10, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y += 20

    cv2.imshow("Coletor de Dados - Libras", img_mostrar)

    if key == 27 and not results.multi_hand_landmarks:
        resposta = input("❓ Deseja salvar os dados antes de sair? (s/n): ").strip().lower()
        if resposta == 's':
            salvar_dados()
        else:
            print("⚠️ Saída sem salvar.")
        break

cap.release()
cv2.destroyAllWindows()
