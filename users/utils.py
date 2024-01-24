import cv2
import face_recognition
import threading
from keras.models import model_from_json
import numpy as np

class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        self.lock = threading.Lock()
        self.frame_counter = 0

    def __del__(self):
        self.video.release()

    def get_frame(self):
        with self.lock:
            success, frame = self.video.read()
            self.frame_counter += 1
        return success, frame

# face recognition
def f_recognition(camera, known_face_encodings, known_face_names, frame_skip = 5):
    while True:
        success, frame = camera.get_frame()
        if not success: continue

        if camera.frame_counter % (frame_skip + 1) == 0:
            face_locations = face_recognition.face_locations(frame)
            face_encodings = face_recognition.face_encodings(frame, face_locations)

            with camera.lock:
                for face_encoding in face_encodings:
                    # Compare the current face encoding with known face encodings
                    matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                    name = "Unknown"

                    if True in matches:
                        first_match_index = matches.index(True)
                        name = known_face_names[first_match_index]

                    # Draw rectangle around the face and display the name
                    top, right, bottom, left = face_recognition.face_locations(frame)[0]
                    cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 1)
                    cv2.putText(frame, name, (left, bottom + 25), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 255), 2)

                ret, jpeg = cv2.imencode('.jpg', frame)
                frame = jpeg.tobytes()
                yield (b'--frame\r\n'
                        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# emotion recognition

def extract_features(image):
    feature = np.array(image)
    feature = feature.reshape(1,48,48,1)
    return feature/255.0

def e_recognition(camera, face_cascade, model, labels):
    while True:
        success, frame = camera.get_frame()

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(frame, 1.3, 5)

        for (p, q, r, s) in faces:
            image = gray[q:q+s, p:p+r]
            cv2.rectangle(frame, (p, q), (p+r, q+s), (255, 0, 0), 2)
            image = cv2.resize(image, (48, 48))
            img = extract_features(image)
            pred = model.predict(img)
            prediction_label = labels[pred.argmax()]
            cv2.putText(frame, '%s' % (prediction_label), (p-10, q-10), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 255))

        ret, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')