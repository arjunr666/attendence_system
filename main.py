import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
from pyzbar import pyzbar

path = 'ImageAttendence'
images = []
imageNames = []

imageList = os.listdir(path)

for cl in imageList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    imageNames.append(os.path.splitext(cl)[0])

# print(imageList, imageNames)


def findEncoding(imgs):
    encodeList = []
    for img in imgs:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        curImgEncode = face_recognition.face_encodings(img)[0]
        encodeList.append(curImgEncode)
    return encodeList


def markAttendence(name):

    with open('Attendence.csv', 'r+') as f:
        myDataList = f.readlines()
        nameList = []

        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])

        if name not in nameList:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name},{dtString}')


EncodeKnownList = findEncoding(images)

# print(len(EncodeKnownList))

cam = cv2.VideoCapture(0)

while True:
    check, frame = cam.read()

    imgS = cv2.resize(frame, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    frameFaceLocations = face_recognition.face_locations(imgS)
    encodeFrame = face_recognition.face_encodings(imgS)

    barcodes = pyzbar.decode(frame)

    for barcode in barcodes:
        x, y, w, h = barcode.rect
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        bdata = barcode.data.decode('utf-8')
        cv2.putText(frame, bdata, (x-50, y-10),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

    for encodeFace, faceLoc in zip(encodeFrame, frameFaceLocations):
        matches = face_recognition.compare_faces(EncodeKnownList, encodeFace)
        faceDis = face_recognition.face_distance(EncodeKnownList, encodeFace)

        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = imageNames[matchIndex].upper()
            markAttendence(name)

            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(frame, (x1, y2-35), (x2, y2),
                          (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, name, (x1+6, y2-6),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow('Camera', frame)
    k = cv2.waitKey(1)

    if k % 256 == 27:
        # ESC pressed
        print("Exiting..")
        break
