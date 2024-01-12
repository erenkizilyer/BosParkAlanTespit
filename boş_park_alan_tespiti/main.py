import cv2
import numpy as np
import pickle

# dikdörtgenin genişliği ve yüksekliği
rectW, rectH = 107, 48

# video dosyası okunuyor
cap = cv2.VideoCapture('carPark.mp4')

# dikdörtgen konumlarını içeren dosya
with open('bosparkalanlari', 'rb') as f:
    posList = pickle.load(f)

# sayac sıfırlanmasi
frame_counter = 0

# video durumu
pause = False

# Belirli bir kare üzerinde işlem yapıyor
def check(imgPro):
    spaceCount = 0
    for pos in posList:
        x, y = pos
        # dikdörtgen bölgesini kırpıyor.
        crop = imgPro[y:y + rectH, x:x + rectW]
        # kırpılan bölgedeki beyaz piksel sayısını sayıyor
        count = cv2.countNonZero(crop)
        # eğer belirli bir eşik değerinin altında beyaz piksel varsa, park yeri boştur
        if count < 900:
            spaceCount += 1
            color = (0, 255, 0)  # yeşil
            thick = 5  # kalınlık
        else:
            color = (0, 0, 255)  # kırmızı
            thick = 2

        # dikdörtgeni
        cv2.rectangle(img, pos, (x + rectW, y + rectH), color, thick)

    # ekranın sol üst köşesine toplam bos park yerleri sayısını ve toplam park yerleri sayısını yazıyor
    cv2.rectangle(img, (45, 30), (250, 75), (180, 0, 180), -1)
    cv2.putText(img, f'Bos Park Alani: {spaceCount}/{len(posList)}', (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.9,
                (255, 255, 255), 2)

while True:
    if not pause:
        # videodan bir kare alıyor
        ret, img = cap.read()

        # kare alınmazsa video bittiğinde başa sar
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # Eğer kare sayısı, toplam kare sayısına ulaştıysa, başa dön
        if frame_counter == cap.get(cv2.CAP_PROP_FRAME_COUNT):
            frame_counter = 0
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

        # gri tonlama
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # görüntüyü  bulanıklıklaştıryor
        blur = cv2.GaussianBlur(gray, (3, 3), 1)

        # görüntüyü adaptif thresholding uygulanıyor
        Thre = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 25, 16)

        # görüntüyü median bulanıklığına tabi tutuluyor
        blur = cv2.medianBlur(Thre, 5)

        # görüntüyü genişletme işlemine tabi tutuluyor
        kernel = np.ones((3, 3), np.uint8)
        dilate = cv2.dilate(blur, kernel, iterations=1)

        # check fonksiyonunu çağırarak park yerlerine işleniyor
        check(dilate)

        # görüntüyü göster
        cv2.imshow("Image", img)

     
        key = cv2.waitKey(10) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('s'):
            pause = True
        elif key == ord('a'):
            # 1 saniye geriye sar
            current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
            new_frame = max(0, int(current_frame - cap.get(cv2.CAP_PROP_FPS)))
            cap.set(cv2.CAP_PROP_POS_FRAMES, new_frame)
    else:
      
        cv2.putText(img, 'Video Durdu', (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.imshow("Image", img)

        key = cv2.waitKey(10) & 0xFF
        if key == ord('d'):
            pause = False

cap.release()

cv2.destroyAllWindows()
