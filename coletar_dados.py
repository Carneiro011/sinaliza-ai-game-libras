import cv2
import mediapipe as mp
import numpy as np
import pickle

mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
cap = cv2.VideoCapture(0)

data = []
labels = []

print("📸 Coletor de dados - Libras com landmarks")
print("👉 Mostre a mão para a câmera e pressione uma letra (A-Z) para registrar.")
print("✅ Pressione 'Q' para salvar e sair.")
print("❌ Pressione 'ESC' para sair (com confirmação).")

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

    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        pontos = []
        for lm in hand_landmarks.landmark:
            pontos.extend([lm.x, lm.y, lm.z])
        pontos = np.array(pontos)

        mp.solutions.drawing_utils.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
        cv2.putText(img, "Pressione uma letra (A-Z), Q para salvar, ESC para sair", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        cv2.imshow("Coletor de Dados - Libras", img)

        key = cv2.waitKey(1) & 0xFF
        if key != 255:
            char = chr(key).upper()
            if char.isalpha():
                print(f"🔡 Letra '{char}' registrada.")
                data.append(pontos)
                labels.append(char)
            elif char == 'Q':
                print("💾 Salvando e saindo...")
                salvar_dados()
                break
            elif key == 27:  # ESC
                resposta = input("❓ Deseja salvar os dados antes de sair? (s/n): ").strip().lower()
                if resposta == 's':
                    salvar_dados()
                else:
                    print("⚠️ Saída sem salvar.")
                break
    else:
        cv2.imshow("Coletor de Dados - Libras", img)
        if cv2.waitKey(1) & 0xFF == 27:
            resposta = input("❓ Deseja salvar os dados antes de sair? (s/n): ").strip().lower()
            if resposta == 's':
                salvar_dados()
            else:
                print("⚠️ Saída sem salvar.")
            break

cap.release()
cv2.destroyAllWindows()
