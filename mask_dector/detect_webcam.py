import os
import imghdr
import argparse
import time
import datetime
import subprocess
import smtplib
import socket
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import datetime
from email.message import EmailMessage
from PIL import Image

import cv2
import imutils
import mtcnn
import numpy as np
from imutils.video import WebcamVideoStream
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from smbus2 import SMBus
from mlx90614 import MLX90614
import mysql.connector
from mysql.connector import Error


# 初始化臉部偵測模型
detector = mtcnn.MTCNN()


# 辨識人臉與偵測是否有戴口罩
def detect_and_predict_mask(frame, mask_net):
    faces = []
    locs = []
    preds = []

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_h, img_w = rgb.shape[:2]
    bboxes = detector.detect_faces(rgb)
    for bbox in bboxes:
        (x, y, w, h) = bbox['box']
        padding = 35
        (crop_x0, crop_x1) = (x - padding if x > padding else 0, x + w + padding if x + w + padding < img_w else img_w)
        (crop_y0, crop_y1) = (y - padding if y > padding else 0, y + h + padding if y + h + padding < img_h else img_h)
        face = rgb[crop_y0:crop_y1, crop_x0:crop_x1]
        face = cv2.resize(face, (224, 224))

        face = img_to_array(face)
        face = preprocess_input(face)

        faces.append(face)
        locs.append((x, y, x + w, y + h))

    if len(faces) > 0:
        faces = np.array(faces, dtype="float32")
        preds = mask_net.predict(faces, batch_size=32)

    return (locs, preds)

def main():

    bus = SMBus(1)
    time.sleep(1)
    sensor = MLX90614(bus, address=0x5A)
    img_save = "./save_img/"

    # 初始化Arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-m", "--model", default="mask_detector.model", help="path to the trained mask model")
    args = vars(ap.parse_args())

    maskNet = load_model(args["model"])

    # 啟動WebCam
    vs = WebcamVideoStream().start()
    time.sleep(2.0)

    while True:
        frame = vs.read()
        frame = imutils.resize(frame, width=400)

        (locs, preds) = detect_and_predict_mask(frame, maskNet)

        for (box, pred) in zip(locs, preds):
            (startX, startY, endX, endY) = box
            (mask, withoutMask) = pred

            (label, color) = ("Mask", (0, 255, 0)) if mask > withoutMask else ("No Mask", (0, 0, 255))
            label = "{}: {:.2f}%".format(label, max(mask, withoutMask) * 100)

            cv2.putText(frame, label, (startX, startY - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)
            cv2.rectangle(frame, (startX, startY), (endX, endY), color, 2)

        cv2.imshow("Frame", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("p"):
            temp = sensor.get_object_1()
            print ("Temperature : ", temp)
            t = time.localtime(time.time())
            img_file = "./save_img/"
            img_name = time.strftime("%Y-%m-%d_%H-%M-%S",t)+".jpg"
            cv2.imwrite(img_file+img_name, frame)

            try:
                connection = mysql.connector.connect(
                        host='localhost',
                        database='covid19',
                        user='lsa',
                        password='lsa')
                ifmask = 0
                if label == "Mask":
                    ifmask = 1

                sql = "INSERT INTO wearmask(time, temperature, ifmask, image, image_name) VALUES (%s, %s, %s, %s, %s)"
                new_data = (time.strftime("%Y-%m-%d %H:%M:%S"), temp, ifmask, "image.jpg", img_name)
                cursor = connection.cursor()
                cursor.execute(sql, new_data)

                connection.commit()

            except Error as e:
                print("connect SQL fail", e)

            finally:
                if (connection.is_connected()):
                    cursor.close()
                    connection.close()


            #send mail to let you know the information
            to = 's110321515@mail1.ncnu.edu.tw'
            gmail_user = 'rox873626@gmail.com'
            gmail_password = 'Axlaxl123'
            smtpserver = smtplib.SMTP('smtp.gmail.com', 587)
            smtpserver.ehlo()
            smtpserver.starttls()
            smtpserver.login(gmail_user, gmail_password)
            today = datetime.datetime.now()
            my_temp = 'Temperature is %s' % temp
            msg = EmailMessage()
            msg['Subject'] = 'Epidemic privention breach detcted on %s' %today.strftime('%b %d %Y')
            msg['From'] = gmail_user
            msg['TO'] = to
            msg.set_content(my_temp)

            with open(img_file+img_name, 'rb') as f:
                file_data = f.read()
                file_type = imghdr.what(f.name)
                file_name = img_name

            msg.add_attachment(file_data, maintype='image', subtype=file_type, filename=file_name)

            smtpserver.sendmail(gmail_user, [to], msg.as_string())
            smtpserver.quit()

        if key == ord("q"):
            break

    cv2.destroyAllWindows()
    vs.stop()
    bus.close()


if __name__ == '__main__':
    main()

