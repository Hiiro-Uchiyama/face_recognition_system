from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import BadHeaderError, send_mail
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views import generic
import cv2
import os
import numpy as np
from PIL import Image
from matplotlib import pyplot as plt

from django.shortcuts import render
from django.http.response import StreamingHttpResponse
from .camera import VideoCamera, IPWebCam, MaskDetect, LiveWebCam
from django.views import View

class IndexView(View):
    def get(self, request):
        return render(request, 'home.html', {})

def video_feed_view():
    return lambda _: StreamingHttpResponse(generate_frame(), content_type='multipart/x-mixed-replace; boundary=frame')

def generate_frame():
    capture = cv2.VideoCapture(0)
    while True:
        if not capture.isOpened():
            print("Capture is not opened.")
            break
        ret, frame = capture.read()
        if not ret:
            print("Failed to read frame.")
            break
        ret, jpeg = cv2.imencode('.jpg', frame)
        byte_frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + byte_frame + b'\r\n\r\n')
    capture.release()

def video_index(request):
	return render(request, 'home.html', {})

def gen(camera):
	while True:
		frame = camera.get_frame()
		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_feed(request):
	return StreamingHttpResponse(gen(VideoCamera()),
					content_type='multipart/x-mixed-replace; boundary=frame')

def webcam_feed(request):
	return StreamingHttpResponse(gen(IPWebCam()),
					content_type='multipart/x-mixed-replace; boundary=frame')

def mask_feed(request):
	return StreamingHttpResponse(gen(MaskDetect()),
					content_type='multipart/x-mixed-replace; boundary=frame')
					
def livecam_feed(request):
	return StreamingHttpResponse(gen(LiveWebCam()),
					content_type='multipart/x-mixed-replace; boundary=frame')

def recognition_video_feed():
	return lambda _: StreamingHttpResponse(recognition_feed(), content_type='multipart/x-mixed-replace; boundary=frame')

def recognition_feed():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    filepath = os.path.join(settings.DATA_ROOT,"trainer/trainer.yml")
    recognizer.read(filepath)
    cascadePath = os.path.join(settings.DATA_ROOT,"haarcascade_frontalface_default.xml")
    faceCascade = cv2.CascadeClassifier(cascadePath)
    font = cv2.FONT_HERSHEY_SIMPLEX
    id = 0
    names = ['None', 'USER', 'Paula', 'Ilza', 'Z', 'W']
    cam = cv2.VideoCapture(0)
    cam.set(3, 640)
    cam.set(4, 480)
    minW = 0.1*cam.get(3)
    minH = 0.1*cam.get(4)
    while True:
        if not cam.isOpened():
            print("Capture is not opened.")
            break
        ret, img = cam.read()
        if not ret:
            print("Failed to read frame.")
            break
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        faces = faceCascade.detectMultiScale( 
            gray,
            scaleFactor = 1.2,
            minNeighbors = 5,
            minSize = (int(minW), int(minH)),
        )
        for(x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
            id, confidence = recognizer.predict(gray[y:y+h,x:x+w])
            if (confidence < 100):
                if id > len(names):
                    pass
                else:
                    id = names[id]
                    confidence = "  {0}%".format(round(100 - confidence))
            else:
                id = "unknown"
                confidence = "  {0}%".format(round(100 - confidence))
            cv2.putText(img, str(id), (x+5,y-5), font, 1, (255,255,255), 2)
            cv2.putText(img, str(confidence), (x+5,y+h-5), font, 1, (255,255,0), 1)  
        ret, jpeg = cv2.imencode('.jpg', img)
        byte_frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + byte_frame + b'\r\n\r\n')
    cam.release()

def add_face_data(request):
    cam = cv2.VideoCapture(0)
    cam.set(3, 640) # set video width
    cam.set(4, 480) # set video height
    cascadePath = os.path.join(settings.DATA_ROOT,"haarcascade_frontalface_default.xml")
    face_detector = cv2.CascadeClassifier(cascadePath)
    # For each person, enter one numeric face id
    face_id = input('\n enter user id end press <return> ==>  ')
    print("\n [INFO] Initializing face capture. Look the camera and wait ...")
    # Initialize individual sampling face count
    count = 0
    while(True):
        ret, img = cam.read()
        # img = cv2.flip(img, -1) # flip video image vertically
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in faces:
            cv2.rectangle(img, (x,y), (x+w,y+h), (255,0,0), 2)     
            count += 1
            # Save the captured image into the datasets folder
            dataset = os.path.join(settings.DATA_ROOT,"dataset/")
            cv2.imwrite(dataset + str(face_id) + '.' + str(count) + ".jpg", gray[y:y+h,x:x+w])
        k = cv2.waitKey(100) & 0xff # Press 'ESC' for exiting video
        if k == 27:
            break
        elif count >= 30: # Take 30 face sample and stop video
            break
    print("\n [INFO] Exiting Program and cleanup stuff")
    cam.release()
    return render(request, 'home.html', {})

def getImagesAndLabels(path):
    imagePaths = [os.path.join(path,f) for f in os.listdir(path)]     
    faceSamples=[]
    ids = []
    cascadePath = os.path.join(settings.DATA_ROOT,"haarcascade_frontalface_default.xml")
    detector = cv2.CascadeClassifier(cascadePath)
    for imagePath in imagePaths:
        PIL_img = Image.open(imagePath).convert('L') # convert it to grayscale
        img_numpy = np.array(PIL_img,'uint8')
        id = int(os.path.split(imagePath)[-1].split(".")[1])
        faces = detector.detectMultiScale(img_numpy)
        for (x,y,w,h) in faces:
            faceSamples.append(img_numpy[y:y+h,x:x+w])
            ids.append(id)
    return faceSamples,ids

def train_face_data(request):
    # Path for face image database
    path = os.path.join(settings.DATA_ROOT,"dataset")
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    print ("\n [INFO] Training faces. It will take a few seconds. Wait ...")
    faces,ids = getImagesAndLabels(path)
    recognizer.train(faces, np.array(ids))
    # Save the model into trainer/trainer.yml
    trainer_path = os.path.join(settings.DATA_ROOT,"trainer/trainer.yml")
    print(trainer_path)
    recognizer.write(trainer_path) # recognizer.save() worked on Mac, but not on Pi
    # Print the numer of faces trained and end program
    print("\n [INFO] {0} faces trained. Exiting Program".format(len(np.unique(ids))))
    return render(request, 'home.html', {})