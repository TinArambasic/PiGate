import cv2
from picamera2 import Picamera2
from fast_alpr import ALPR

alpr = ALPR(
    detector_model="yolo-v9-t-384-license-plate-end2end",
    ocr_model="cct-xs-v1-global-model",
)

picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"size": (2304, 1296)}))
picam2.start()

while True:
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    
    results = alpr.predict(frame)
    
    if results:
        for plate in results:
            text = plate.ocr.text
            confidence = sum(plate.ocr.confidence) / len(plate.ocr.confidence)
            if confidence > 0.9:
                print(f"Tablica: {text} | Confidence: {confidence:.2f}")
