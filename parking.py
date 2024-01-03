# import necessary packages
from imutils.video import VideoStream
import numpy as np
from imutils.video import FPS
import imutils
import time
import cv2
from keras.models import load_model
from src.DB import Db
from src.yolo_video import helmet_detect_frame
from src.classify_triple import predict_triple

# initialize the list of class labels MobileNet SSD was trained to detect
# generate a set of bounding box colors for each class
CLASSES = ['background', 'aeroplane', 'bicycle', 'bird', 'boat', 'bottle', 'bus', 'car', 'cat', 'chair', 'cow',
           'diningtable', 'dog', 'horse', 'motorbike', 'person', 'pottedplant', 'sheep', 'sofa', 'train', 'tvmonitor']
# CLASSES = ['motorbike', 'person']
COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))

# load our serialized model from disk
# print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe('MobileNetSSD_deploy.prototxt.txt', 'MobileNetSSD_deploy.caffemodel')

# print('Loading helmet model...')
loaded_model = load_model('new_helmet_model.h5')
loaded_model.compile(loss='binary_crossentropy', optimizer='rmsprop', metrics=['accuracy'])

# initialize the video stream,
# print("[INFO] starting video stream...")

# Loading the video file
# cap = cv2.VideoCapture('vid1.mp4')
# cap = cv2.VideoCapture('static/v.mp4')
cap = cv2.VideoCapture('static/v.mp4')

# time.sleep(2.0)

# Starting the FPS calculation
fps = FPS().start()


def solve(R1, R2):
    if (R1[0] >= R2[2]) or (R1[2] <= R2[0]) or (R1[3] <= R2[1]) or (R1[1] >= R2[3]):
        return False
    else:
        return True

vehcount=0
# loop over the frames from the video stream
# i = True
while True:
    # i = not i
    # if i==True:

    try:
        # grab the frame from the threaded video stream and resize it
        # to have a maxm width and height of 600 pixels
        ret, frame = cap.read()
        frame = cv2.imread(r"D:\pending\helmetviolation\src\rc.jpeg")

        # resizing the images
        frame = imutils.resize(frame, width=600, height=600)

        # grab the frame dimensions and convert it to a blob
        (h, w) = frame.shape[:2]

        # Resizing to a fixed 300x300 pixels and normalizing it.
        # Creating the blob from image to give input to the Caffe Model
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)

        # pass the blob through the network and obtain the detections and predictions
        net.setInput(blob)

        detections = net.forward()  # getting the detections from the network

        persons = []
        person_roi = []
        motorbi = []

        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            # extract the confidence associated with the prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the confidence
            # is greater than minimum confidence
            if confidence > 0.5:

                # extract index of class label from the detections
                idx = int(detections[0, 0, i, 1])

                if idx == 15:
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")
                    # roi = box[startX:endX, startY:endY/4]
                    # person_roi.append(roi)
                    persons.append((startX, startY, endX, endY))

                if idx == 14:
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")
                    motorbi.append((startX, startY, endX, endY))

        xsdiff = 0
        xediff = 0
        ysdiff = 0
        yediff = 0
        p = ()
        flag=False
        if vehcount!=len(motorbi):
            if vehcount<len(motorbi):
                vehcount=len(motorbi)
                flag=True
            else:
                vehcount = len(motorbi)

        print(flag, "//////////////////////////////////////////////////////////////////////////////////////////")

        for i in motorbi:
            mi = float("Inf")
            roix = []
            for j in range(len(persons)):
                res = solve(i, persons[j])
                if res:

                    if i[0] < persons[j][0]:
                        roix.append(i[0])
                    else:
                        roix.append(persons[j][0])

                    if i[1] < persons[j][1]:
                        roix.append(i[1])
                    else:
                        roix.append(persons[j][1])

                    if i[2] > persons[j][2]:
                        roix.append(i[2])
                    else:
                        roix.append(persons[j][2])

                    if i[3] < persons[j][3]:
                        roix.append(i[3])
                    else:
                        roix.append(persons[j][3])

                    break






            if len(roix) == 0:



                        timestr = time.strftime("%Y%m%d-%H%M%S")

                        try:

                            if flag:
                                filename = timestr + "frame.jpg"
                                cv2.imwrite(r"D:\pending\helmetviolation\src\static\helmet_images\\" + filename, frame)
                                db = Db()
                                db.insert("INSERT INTO `helmet_violation` VALUES(NULL,3,'" + filename + "',CURDATE(),CURTIME(),'no parking')")
                                print("123")
                        # cv2.imwrite(timestr+"frame.jpg", frame)  # save frame as JPEG file
                        except Exception as e:
                            pass

    except Exception as e:
        print(e)
        pass

    cv2.imshow('Frame', frame)  # Displaying the frame
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):  # if 'q' key is pressed, break from the loop
        break

    # update the FPS counter
    fps.update()

# stop the timer and display FPS information
fps.stop()

# print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
# print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

cv2.destroyAllWindows()
cap.release()  # Closing the video stream
