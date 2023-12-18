import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime, date
from pyzbar import pyzbar
import re

from flask import Flask
from flask_mysqldb import MySQL

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'tododb'
mysql = MySQL(app)

# Get today's date in the format YYYY_MM_DD
today_date = date.today().strftime("%Y_%m_%d")
now = datetime.now()
time = now.strftime('%H:%M:%S')

with app.app_context():
    # Connect to your MySQL database
    cur = mysql.connection.cursor()

    # Check if the column already exists
    check_query = f"SHOW COLUMNS FROM ATTENDANCE LIKE '{today_date}'"
    cur.execute(check_query)
    existing_column = cur.fetchone()

    if not existing_column:
        # SQL query to add a new column with today's date
        alter_query = f"ALTER TABLE ATTENDANCE ADD COLUMN {today_date} varchar(50) DEFAULT 'absent'"
        cur.execute(alter_query)
        print(f"Column {today_date} added successfully.")
    else:
        print(f"Already Column {today_date} is present.")
    mysql.connection.commit()
    cur.close()


path = 'ImageAttendence'
images = []
imageNames = []

imageList = os.listdir(path)

for cl in imageList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    imageNames.append(os.path.splitext(cl)[0])


def findEncoding(imgs):
    encodeList = []
    for img in imgs:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        curImgEncode = face_recognition.face_encodings(img)[0]
        encodeList.append(curImgEncode)
    return encodeList


def markAttendance(name):
    with app.app_context():
        cur = mysql.connection.cursor()

        check = f"SELECT * FROM ATTENDANCE WHERE NAME='{name}'"
        cur.execute(check)

        # Fetch the result
        result = cur.fetchone()
        if result is None:
            student_insert = f"INSERT INTO ATTENDANCE(NAME, {today_date}) VALUES('{name}', '{time}')"
            cur.execute(student_insert)
            mysql.connection.commit()
            print(
                f"Successfully added record for {name} and marked attendance")
        elif result[-1] == 'absent':
            mark_present_query = f"UPDATE ATTENDANCE SET {today_date}='{time}' WHERE NAME='{name}'"
            cur.execute(mark_present_query)
            mysql.connection.commit()
            print(f"Added attendance for {name} at {time}")


EncodeKnownList = findEncoding(images)

cam = cv2.VideoCapture(0)

# Initialize detection states for each iteration
face_detected = False
face_name = ""
barcode_data = ""

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
        barcode_data = barcode.data.decode('utf-8')
        cv2.putText(frame, barcode_data, (x-50, y-10),
                    cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

    for encodeFace, faceLoc in zip(encodeFrame, frameFaceLocations):
        matches = face_recognition.compare_faces(EncodeKnownList, encodeFace)
        faceDis = face_recognition.face_distance(EncodeKnownList, encodeFace)

        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            face_name = imageNames[matchIndex].upper()
            face_detected = True

            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(frame, (x1, y2-35), (x2, y2),
                          (0, 255, 0), cv2.FILLED)
            cv2.putText(frame, face_name, (x1+6, y2-6),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

    # Use regular expression to extract digits
    digits_match = re.search(r'\d+', barcode_data)
    extracted_digits = ""

    if digits_match:
        extracted_digits = digits_match.group()

    if extracted_digits == "":
        pass
    elif face_detected and extracted_digits in face_name:
        markAttendance(face_name)

    cv2.imshow('Camera', frame)
    k = cv2.waitKey(1)

    if k % 256 == 27:
        # ESC pressed
        print("Exiting..")
        break

cam.release()
cv2.destroyAllWindows()
