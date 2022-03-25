import numpy as np
import cv2
import mediapipe as mp
import os
import csv
import alignment as alignment


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands


# video recognition

# load five_template keypoints
confident_col = np.ones((21,1))
five_temp = np.hstack((np.loadtxt('template_data/five_temp.csv', dtype = float, delimiter=','), confident_col))
arrow_temp = np.hstack((np.loadtxt('template_data/arrow_temp.csv', dtype = float, delimiter=','), confident_col))
templates = [five_temp, arrow_temp]
templates_category = ['five', 'arrow']


# initialize mp hand module
hands = mp_hands.Hands(
    min_detection_confidence=0.7)
cap = cv2.VideoCapture(0)

draw_cnt = 0
while cap.isOpened():
    success, image = cap.read()
    image = cv2.flip(image, 1)
    if not success:
      print("Ignoring empty camera frame.")
      # If loading a video, use 'break' instead of 'continue'.
      continue

    # To improve performance, optionally mark the image as not writeable to
    # pass by reference.
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image)

    # Draw the hand annotations on the image.
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)



    if results.multi_hand_landmarks:
        right_hand = None
        left_hand = None
        for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
            handedness = results.multi_handedness[i].classification[0].label
            print(handedness)
            mp_drawing.draw_landmarks(
                image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

            landmark_data = []
            for point in hand_landmarks.landmark:
                landmark_data.append([point.x, point.y])
            landmark_data = np.array(landmark_data)
            landmark_data = np.hstack((landmark_data, confident_col))
            # if handedness == 'Left':
            #     _, score = alignment.pose_affinematrix(landmark_data, temp, dst_area=1.0, hard=True)
            #     print(score)
            # if handedness == 'Right':
            #     _, score = alignment.pose_affinematrix(landmark_data, temp, dst_area=1.0, hard=True)
            #     print(score)
            best_score = 0.
            for pose, pose_category in zip(templates, templates_category):
                matrix, score = alignment.pose_affinematrix(landmark_data, pose, dst_area=1.0, hard=True)
                if score > 0:
                    # valid `matrix`. default (dstH, dstW) is (1.0, 1.0)
                    # matrix = get_resize_matrix(1.0, 1.0, dstW, dstH).dot(matrix)
                    # scale = math.sqrt(matrix[0,0] ** 2 + matrix[0,1] ** 2)
                    print(score)
                    if score > best_score:
                        category = pose_category
                        best_score = score
                # else:
                #     # matrix = basic_matrix
                #     category = -1
            cv2.putText(image, 'pose: ' + category, (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (209, 80, 0, 255), 3)
    cv2.imshow('MediaPipe Hands', image)
    if cv2.waitKey(5) & 0xFF == 27:
      break

cap.release()