from PIL import Image, ImageDraw, ImageFont

img = Image.new("RGB", (400, 200), (30, 30, 30))
draw = ImageDraw.Draw(img)

font = ImageFont.truetype("seguiemj.ttf", 32)
draw.text((50, 50), "🎉 PARABÉNS!", font=font, fill=(0, 255, 0))
draw.text((50, 100), "Pontuação final: 160", font=font, fill=(255, 255, 255))

img.show()
