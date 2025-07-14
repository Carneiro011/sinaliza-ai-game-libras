import cv2

class Game:
    def __init__(self, config):
        self.words      = config["words"]
        self.idx_word   = 0
        self.idx_letter = 0
        self.points     = 0
        self.feedback   = ""
        self.timer      = 0

    def update(self, pred_letter):
        target = self.words[self.idx_word][self.idx_letter]
        if pred_letter == target:
            self.points     += 10
            self.idx_letter += 1
            self.feedback    = "ACERTOU!"
            self.timer       = 30
            if self.idx_letter >= len(self.words[self.idx_word]):
                self.points     += 50
                self.idx_word    = (self.idx_word + 1) % len(self.words)
                self.idx_letter  = 0
                self.feedback    = "PALAVRA COMPLETA!"
                self.timer       = 60

    def render(self, frame, pred_letter):
        h, w, _ = frame.shape
        word    = self.words[self.idx_word]

        display = "".join(
            f" [{ch}]" if i==self.idx_letter else
            f" {ch}"
            for i, ch in enumerate(word)
        )

        cv2.putText(frame, f"SOLETRE:{display}", (50,50),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255), 2)
        cv2.putText(frame, f"PONTOS: {self.points}", (w-250,50),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255,255,255),2)
        cv2.putText(frame, f"Previsto: {pred_letter}", (50,h-50),
                    cv2.FONT_HERSHEY_COMPLEX,1,(0,255,255),2)

        if self.timer > 0:
            cv2.putText(frame, self.feedback, (w//2-100,h//2),
                        cv2.FONT_HERSHEY_SIMPLEX,2,(0,255,0),3)
            self.timer -= 1

        return frame
