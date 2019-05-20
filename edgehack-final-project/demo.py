import argparse

import cv2
import numpy as np
import torch
import math
import time
import TextToSpeech as tts

from models.with_mobilenet import PoseEstimationWithMobileNet
from modules.keypoints import extract_keypoints, group_keypoints, BODY_PARTS_KPT_IDS, BODY_PARTS_PAF_IDS
from modules.load_state import load_state
from val import normalize, pad_width
from flask_socketio import SocketIO,emit
from GlobalHelpers import accuracy_queue, botlog_queue



class ImageReader(object):
    def __init__(self, file_names):
        self.file_names = file_names
        self.max_idx = len(file_names)

    def __iter__(self):
        self.idx = 0
        return self

    def __next__(self):
        if self.idx == self.max_idx:
            raise StopIteration
        img = cv2.imread(self.file_names[self.idx], cv2.IMREAD_COLOR)
        if img.size == 0:
            raise IOError('Image {} cannot be read'.format(self.file_names[self.idx]))
        self.idx = self.idx + 1
        return img

class CameraReader(object):
    def __init__(self, source):
        self.source = source
    def __iter__(self):
        self.cap = cv2.VideoCapture(self.source)
        if not self.cap.isOpened():
            raise IOError('Video {} cannot be opened'.format("webcam"))
        return self

    def __next__(self):
        was_read, img = self.cap.read()
        if not was_read:
            raise StopIteration
        return img

class VideoReader(object):
    def __init__(self, file_name):
        self.file_name = file_name
        try:  # OpenCV needs int to read from webcam
            self.file_name = int(file_name)
        except ValueError:
            pass

    def __iter__(self):
        self.cap = cv2.VideoCapture(self.file_name)
        # self.cap = cv2.VideoCapture(1)
        if not self.cap.isOpened():
            raise IOError('Video {} cannot be opened'.format(self.file_name))
        return self

    def __next__(self):
        was_read, img = self.cap.read()
        if not was_read:
            raise StopIteration
        return img


def infer_fast(net, img, net_input_height_size, stride, upsample_ratio, cpu,
               pad_value=(0, 0, 0), img_mean=(128, 128, 128), img_scale=1/256):
    height, width, _ = img.shape
    scale = net_input_height_size / height

    scaled_img = cv2.resize(img, (0, 0), fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    scaled_img = normalize(scaled_img, img_mean, img_scale)
    min_dims = [net_input_height_size, max(scaled_img.shape[1], net_input_height_size)]
    padded_img, pad = pad_width(scaled_img, stride, pad_value, min_dims)

    tensor_img = torch.from_numpy(padded_img).permute(2, 0, 1).unsqueeze(0).float()
    if not cpu:
        tensor_img = tensor_img.cuda()

    stages_output = net(tensor_img)

    stage2_heatmaps = stages_output[-2]
    heatmaps = np.transpose(stage2_heatmaps.squeeze().cpu().data.numpy(), (1, 2, 0))
    heatmaps = cv2.resize(heatmaps, (0, 0), fx=upsample_ratio, fy=upsample_ratio, interpolation=cv2.INTER_CUBIC)

    stage2_pafs = stages_output[-1]
    pafs = np.transpose(stage2_pafs.squeeze().cpu().data.numpy(), (1, 2, 0))
    pafs = cv2.resize(pafs, (0, 0), fx=upsample_ratio, fy=upsample_ratio, interpolation=cv2.INTER_CUBIC)

    return heatmaps, pafs, scale, pad

class keyPointLocations(object):
    def __init__(self):
        self.i = 0

class Checker(object):
    def __init__(self, message_time_gap, reset_time_gap, checker, message):
        self.check_pass = True
        self.message = message
        self.time = 0
        self.display_message = False
        self.checker = checker
        self.reset_time = 0
        self.message_time_gap = message_time_gap
        self.reset_time_gap = reset_time_gap
    def check(self, wes, esh, shk, seh, sek):
        if self.checker(wes, esh, shk, seh, sek):
            self.check_pass = False
            print("{0} check failed".format(self.message))
            self.reset_time = 0
            print(self.message)
            print(self.time)
            if self.time == 0:
                self.time = time.time()
            else:
                d = time.time() - self.time
                if d > self.message_time_gap:
                    self.display_message = True
                    self.time = 0
                else:
                    self.display_message = False                
        else:
            print("{0} check passed".format(self.message))
            self.reset()
        return self.check_pass
    def reset(self):
        if self.reset_time == 0:
            self.reset_time = time.time()
        else:
            if time.time() - self.reset_time > self.reset_time_gap:

                print("Resetting")
                self.check_pass = True
                self.display_message = False
                self.time = 0
                self.reset_time = 0
def bodyDownCheck(wes, esh, shk, seh, sek):
    if esh > 112 and wes > 108 and seh < 100:
        return True
    else:
        return False
def kneeDownCheck(wes, esh, shk, seh, sek):
    if seh < 110 and sek < 95:
        return True
    else:
        return False
def backHighCheck(wes, esh, shk, seh, sek):
    print ("shk {0} seh {1}".format(shk, seh))
    print("shk < 145 {0} seh > 110 {1}".format(shk<145, seh>110))
    if shk < 145 and seh > 110:
        return True
    else:
        return False
class AverageAccuracy(object):
    def __init__(self):
        self.accuracy = 0
        self.count = 0
    def put(self, accuracy):
        self.accuracy += accuracy
        self.count += 1
    def get(self):
        return self.accuracy/self.count
def getAccuracy(wes, esh, shk, seh, sek):
    wesA = np.abs(90.-np.abs(wes))/90.
    eshA = np.abs(90.-np.abs(esh))/90.
    shkA = np.abs(180.-np.abs(shk))/180.
    sekA = np.abs(100. - np.abs(sek))/100.
    sehA = np.abs(110. - np.abs(seh))/110.
    ratio = 1/5
    return 100-(wesA + eshA + shkA + sekA + sehA)*ratio*100

font                   = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (10,500)
fontScale              = 1
fontColor              = (255,255,255)
lineType               = 2

def run_demo(net, image_provider, height_size, cpu):
    net = net.eval()
    if not cpu:
        net = net.cuda()

    stride = 8
    upsample_ratio = 4
    color = [0, 224, 255]


    # buf = []
    finish = False
    begun = False
    count = 0
    avgwes, avgesh, avgshk, avgseh, avghorizontal, avgsek = 0., 0., 0., 0., 0., 0.
    badpose_startt = 0
    pose_startt = 0
    total_bad_duration = 0
    lower_hip_time = 0
    averaging_duration = 3
    message_time_gap = 7
    reset_time_gap = 5
    all_checks = (
        Checker(message_time_gap, reset_time_gap, bodyDownCheck, "Raise your body up"), 
        Checker(message_time_gap, reset_time_gap, kneeDownCheck, "Raise your knees"),
        Checker(message_time_gap, reset_time_gap, backHighCheck, "Lower your back"))
    avg_accuracy = AverageAccuracy()

    #Stop the workout if the an incorrect posture lasts for more than 15 seconds
    max_bad_pose_duration = 20
    last_time_time = time.time()
    knee_touching_ground = False
    for img in image_provider:
        orig_img = img.copy()
        heatmaps, pafs, scale, pad = infer_fast(net, img, height_size, stride, upsample_ratio, cpu)

        total_keypoints_num = 0
        all_keypoints_by_type = []
        for kpt_idx in range(18):  # 19th for bg
            total_keypoints_num += extract_keypoints(heatmaps[:, :, kpt_idx], all_keypoints_by_type, total_keypoints_num)

        pose_entries, all_keypoints = group_keypoints(all_keypoints_by_type, pafs, demo=True)
        for kpt_id in range(all_keypoints.shape[0]):
            all_keypoints[kpt_id, 0] = (all_keypoints[kpt_id, 0] * stride / upsample_ratio - pad[1]) / scale
            all_keypoints[kpt_id, 1] = (all_keypoints[kpt_id, 1] * stride / upsample_ratio - pad[0]) / scale
        # print(len(pose_entries))
        # print("parts__")
        
        kpLocations = dict()
        
        # print("Pose entries: ", len(pose_entries))
        for n in range(len(pose_entries)):
            # print("pose entries length ", len(pose_entries[n]))
            if len(pose_entries[n]) <10:
                continue
            if not checkDistance(pose_entries[n], all_keypoints, "left", "Shoulder", "Ankle"):
                continue
            if not checkDistance(pose_entries[n], all_keypoints, "left", "Elbow", "Hip"):
                continue
            if not checkDistance(pose_entries[n], all_keypoints, "left", "Shoulder", "Hip"):
                continue
            if not checkDistance(pose_entries[n], all_keypoints, "left", "Shoulder", "Knee"):
                continue
            if not checkDistance(pose_entries[n], all_keypoints, "left", "Shoulder", "Ankle"):
                continue
            if not checkDistance(pose_entries[n], all_keypoints, "left", "Elbow", "Hip"):
                continue
            if not checkDistance(pose_entries[n], all_keypoints, "left", "Elbow", "Knee"):
                continue
            # print("Is horizontal : " , horizontal)
            
            left = isFacingLeft(pose_entries[n], all_keypoints)
            print("Is facing left ", left)
            anglehorizontal = horizontalAngle(pose_entries[n], all_keypoints)
            displayText("Hor: " + str(anglehorizontal), 50, 20, img)
            anglewes, angleesh, angleshk, angleseh, anglesek = getPlankAngles(pose_entries[n], all_keypoints, img)
            cont = False
            for angl in (anglewes, angleesh, angleshk, angleseh, anglesek):
                if math.isnan(angl):
                    cont = True
                    print("nan found")
                    break
            if cont:
                continue
            avghorizontal += anglehorizontal
            
            avgwes += anglewes
            avgesh += angleesh
            avgshk += angleshk
            avgseh += angleseh
            avgsek += anglesek
            count += 1
            if count == averaging_duration:
                count = 0
                avgwes /= averaging_duration
                avgesh /= averaging_duration
                avgshk /= averaging_duration
                avgseh /= averaging_duration
                avghorizontal /= averaging_duration
                avgsek /= averaging_duration
                horizontal = checkHorizontal(avghorizontal)
                # print("Is horizontal ", horizontal)
                if horizontal:
                    # print("Avg Angles: wrist elbow shoulder: {0} elbow shoulder hips: {1} shoulder hips knee: {2} shoulder elbow hip {3}".format(avgwes, avgesh, avgshk, avgseh))
                    correct_pose, wes, esh, shk, seh = checkCorrectPlank(avgwes, avgesh, avgshk, avgseh)
                    if not begun and correct_pose:
                        begun = True
                        pose_startt = time.time()
                        last_time_time = time.time()
                        tts.BotSpeak("Now that you are in position, I'll start the timer.")
                        botlog_queue.put("Now that you are in position, I'll start the timer.")
                    if begun: 
                        accuracy = getAccuracy(avgwes, avgesh, avgshk, avgseh, avgsek)
                        accuracy_queue.put(accuracy)
                        avg_accuracy.put(accuracy)
                        displayText(accuracy, 10, 120, img)
                        correct_pose = True                        
                        for check in all_checks:
                            if not check.check(avgwes, avgesh, avgshk, avgseh, avgsek):
                                # if check.display_message:
                                    # tts.BotSpeak(check.message)
                                if check.display_message:
                                    tts.BotSpeak(check.message)
                                    botlog_queue.put(check.message)
                                    displayText(check.message, 20, 100, img, (0, 255, 0))
                                correct_pose = False
                                break
                        d = time.time()-last_time_time
                        if d > 10:
                            seconds_over = int(time.time()-pose_startt)
                            tts.BotSpeak("{0} seconds over".format(seconds_over))
                            botlog_queue.put("{0} seconds over".format(seconds_over))
                            last_time_time = time.time()
                        if not correct_pose:                            
                            # if not shk:
                            #     if lower_hip_time > 0:
                            #         d = time.time() - lower_hip_time
                            #         if d > 5:
                            #             tts.BotSpeak("Lower your hips")
                            #             lower_hip_time = 0
                            #     else:
                            #         lower_hip_time = time.time()
                            # else:
                            #     lower_hip_time = 0
                            if badpose_startt != 0:
                                duration = time.time()-badpose_startt
                                displayText("badpose duration: "+str(duration), 0, 50, img)
                                if duration > max_bad_pose_duration:
                                    finish = True
                                # if duration > 20:
                                #     displayText("Pose broken for 20", 0, 40, img)
                            else:
                                badpose_startt = time.time()
                        else:
                            lower_hip_time = 0
                            
                            if badpose_startt != 0:
                                total_bad_duration += time.time()-badpose_startt
                                badpose_startt = 0
                            displayText("Correct Pose", 0, 30, img)
                    
                    print("Correct Pose: ", correct_pose)
                elif begun:
                    finish = True
                avgwes, avgesh, avgshk, avgseh, avghorizontal, avgsek = 0., 0., 0., 0., 0., 0.
            if finish:
                if badpose_startt > 0:
                    total_bad_duration += time.time()-badpose_startt
                duration = time.time() - pose_startt
                good_duration = duration-total_bad_duration
                tts.BotSpeak("You held an incorrect position for too long.")
                botlog_queue.put("You held an incorrect position for too long.")
                tts.BotSpeak("Your workout is now complete")
                botlog_queue.put("Your workout is now complete")
                tts.BotSpeak("Your average accuracy was {0}".format( int(avg_accuracy.get())))
                botlog_queue.put("Your average accuracy was {0}".format( int(avg_accuracy.get())))
                tts.BotSpeak("You held the correct plank position for {0} seconds and your workout lasted for {1} seconds.".format(int(good_duration), int(duration)))
                botlog_queue.put("You held the correct plank position for {0} seconds and your workout lasted for {1} seconds.".format(int(good_duration), int(duration)))
                # tts.BotSpeak("end")



                print("-"*20)
                print("Total duration: ", good_duration)
                return
            # print("true_count {0} count {1} finish {2} begun {3} ".format(true_count, count, finish, begun))
            # triplet = ("left", "Shoulder", "Hip", "Ankle")
            # # triplet = ("left", "Wrist", "Elbow", "Shoulder")
            # print(getAngle(pose_entries[n], all_keypoints, *triplet))

            # print("wes", getAngle(pose_entries[n], all_keypoints, "left", "Wrist", "Elbow", "Shoulder"))
            # print("esh", getAngle(pose_entries[n], all_keypoints, "left", "Elbow", "Shoulder", "Hip"))
            # drawLinesTriplets(pose_entries[n], all_keypoints, img, color, *triplet)
            # print("trip2", getAngle(pose_entries[n], all_keypoints, "", "leftShoulder", "chestCenter", "rightShoulder")/180)
            for part_id in range(len(BODY_PARTS_PAF_IDS) - 2):
                kpt_a_id = BODY_PARTS_KPT_IDS[part_id][0]
                global_kpt_a_id = pose_entries[n][kpt_a_id]
                if global_kpt_a_id != -1:
                    x_a, y_a = all_keypoints[int(global_kpt_a_id), 0:2]

                    cv2.circle(img, (int(x_a), int(y_a)), 3, color, -1)
                    # cv2.putText(img, str(kpt_a_id), 
                    #             (int(x_a), int(y_a)), 
                    #             font, 
                    #             fontScale,
                    #             fontColor,
                    #             lineType)
                kpt_b_id = BODY_PARTS_KPT_IDS[part_id][1]
                global_kpt_b_id = pose_entries[n][kpt_b_id]
                if global_kpt_b_id != -1:
                    x_b, y_b = all_keypoints[int(global_kpt_b_id), 0:2]
                    cv2.circle(img, (int(x_b), int(y_b)), 3, color, -1)
                if global_kpt_a_id != -1 and global_kpt_b_id != -1:
                    cv2.line(img, (int(x_a), int(y_a)), (int(x_b), int(y_b)), color, 2)
                # print(part_id, (x_a, y_a), (x_b, y_b))

        img = cv2.addWeighted(orig_img, 0.6, img, 0.4, 0)
        cv2.imshow('Lightweight Human Pose Estimation Python Demo', img)
        # cv2.imwrite("output.jpeg", img)
        key = cv2.waitKey(33)
        if key == 27:  # esc
            # tts.BotSpeak("end")
            return

class Struct:
    def __init__(self, **entries): self.__dict__.update(entries)
def getPlankAngles(pose_entries, all_keypoints, img):
    angleWES = wesAngle(pose_entries, all_keypoints, img)
    angleESH = eshAngle(pose_entries, all_keypoints, img)
    angleSHK = shkAngle(pose_entries, all_keypoints, img)
    angleSEH = sehAngle(pose_entries, all_keypoints, img)
    angleSEK = sekAngle(pose_entries, all_keypoints, img)

    # print("Angles: wrist elbow shoulder: {0} elbow shoulder hips: {1} shoulder hips knee: {2}".format(angleWES, angleESH, angleSHK))
    return angleWES, angleESH, angleSHK, angleSEH, angleSEK
def checkCorrectPlank(wesAngle, eshAngle, shkAngle, sehAngle):
    wes = wesCorrect(wesAngle)
    esh = eshCorrect(eshAngle)
    shk = shkCorrect(shkAngle)
    seh = sehCorrect(sehAngle)

    # print("Correctness: wrist elbow shoulder: {0} elbow shoulder hips: {1} shoulder hips knee: {2}".format(wes, esh, shk))
    return wes and esh and shk and seh, wes, esh, shk, seh
def horizontalAngle(pose_entries, all_keypoints):
    side = "left"
    part1 = "Shoulder"
    part2 = "Hip"
    part1_global = pose_entries[partIntMap[side+part1]]
    part1 = all_keypoints[int(part1_global), 0:2]
    part2_global = pose_entries[partIntMap[side+part2]]
    part2 = all_keypoints[int(part2_global), 0:2]
    if (part2[0] - part1[0] == 0):
        return 90
    
    m = np.arctan(-(part2[1]-part1[1])/(part2[0]-part1[0]))*180/np.pi
    # print(part1, part2)
    # print("Horizontal angle ", m)
    return m
def checkHorizontal(angle):
    if np.abs(90-np.abs(angle) ) < 20:
        return False
    return True
def wesAngle(pose_entries, all_keypoints, img):
    angle, m1, m2, xe, ye = getAngle(pose_entries, all_keypoints, "left", "Wrist", "Elbow", "Shoulder")
    # print("is angle nan " , angle)
    if np.abs(m2) == np.inf or np.abs(m2) == math.inf:
        # print("i")
        if m1 == 0:
            # print("j")
            angle = 90
        else:
            # print("k")
            angle = np.arctan(1/m1)*180/np.pi
    printAngle(angle, xe, ye, img)
    return angle
def wesCorrect(angle):    
    if np.abs(90-np.abs(angle)) < 30:
        return True
    else:
        return False
def eshAngle(pose_entries, all_keypoints, img):
    angle, m1, m2, xs, ys = getAngle(pose_entries, all_keypoints, "left", "Elbow", "Shoulder", "Hip")
    # print("is nan angle ? ", angle)
    if np.abs(m1) == np.inf:
        # print("j")
        if m2 == 0:
            # print("k")
            angle = 90
        else:
            # print("l", 1./m2, math.atan(np.abs(1./m2)))
            angle = np.arctan(np.abs(1./m2))*180/np.pi
    # if angle == np.nan or angle == math.nan:
    #     print("yes nan angle")
    #     if m1 == 0:
    #         angle = 90
    #     else:
    #         angle = np.arctan(1/m1)*180/np.pi
    # print("esh angle: ", angle)
    printAngle(angle, xs, ys, img)
    return angle
def eshCorrect(angle):
    if np.abs(90-np.abs(angle)) < 30:
        return True
    else:
        return False
def shkAngle(pose_entries, all_keypoints, img):
    angle, m1, m2, xh, yh = getAngle(pose_entries, all_keypoints, "left", "Shoulder", "Hip", "Knee")
    # print("shk angle : ", angle)
    printAngle(angle, xh, yh, img)
    return angle
def shkCorrect(angle):
    if np.abs(180-np.abs(angle)) < 30:
        return True
    else:
        return False

def sehAngle(pose_entries, all_keypoints, img):
    angle, m1, m2, xh, yh = getAngle(pose_entries, all_keypoints, "left", "Shoulder", "Elbow", "Hip")
    if math.isnan(angle):
        if m2 == 0:
            angle = 90
        else:
            angle = np.arctan(np.abs(1./m2))*180/np.pi
    # print("seh angle : ", angle)
    printAngle(angle, xh+50, yh+20, img, (0, 255, 0))
    return angle

def sehCorrect(angle):
    if np.abs(120-np.abs(angle))< 20:
        return True
    return False

def sekAngle(pose_entries, all_keypoints, img):
    angle, m1, m2, xh, yh = getAngle(pose_entries, all_keypoints, "left", "Shoulder", "Elbow", "Knee")
    if math.isnan(angle):
        if m2 == 0:
            angle = 90
        else:
            angle = np.arctan(np.abs(1./m2))*180/np.pi
    # print("sek angle : ", angle)
    printAngle(angle, xh+150, yh+40, img)
    return angle

def sekCorrect(angle):
    if np.abs(120-np.abs(angle))< 20:
        return True
    return False


def printAngle(angle, x, y, img, font_color=(255, 255, 255)):
    if not math.isnan(angle):
        angle = int(angle)
    displayText(angle, x, y, img, font_color)
def displayText(text, x, y, img, font_color=(255, 255, 255)):
    cv2.putText(img, str(text), 
                (int(x), int(y)), 
                font, 
                fontScale,
                font_color,
                lineType)
def getAngle(pose_entries, all_keypoints, side, part1, part2, part3):
    part1_global = pose_entries[partIntMap[side+part1]]
    part1 = all_keypoints[int(part1_global), 0:2]
    part2_global = pose_entries[partIntMap[side+part2]]
    part2 = all_keypoints[int(part2_global), 0:2]
    part3_global = pose_entries[partIntMap[side+part3]]
    part3 = all_keypoints[int(part3_global), 0:2]
    # print(part1, part2, part3)
    m1 = (part2[1]-part1[1])/(part2[0]-part1[0])
    m2 = (part2[1]-part3[1])/(part2[0]-part3[0])
    # print("m1 {0} m2 {1}".format(m1, m2))

    if (part2[0] - part3[0] == 0):
        if m1 != 0:
            m = np.arctan(1/m1)
        else:
            m = 90
    else: 

        m = 180 - np.arctan(np.abs((m2-m1)/(1+m2*m1)))*180/np.pi
    return m, m1, m2, part2[0], part2[1]


def isFacingLeft(pose_entries, all_keypoints):
    side = "left"
    part1 = "Hip"
    part2 = "Shoulder"
    part3 = "Elbow"
    part1_global = pose_entries[partIntMap[side+part1]]
    if part1_global == -1:
        side = "right"
        part1_global = pose_entries[partIntMap[side+part1]]
    part1 = all_keypoints[int(part1_global), 0:2]
    part2_global = pose_entries[partIntMap[side+part2]]
    part2 = all_keypoints[int(part2_global), 0:2]
    part3_global = pose_entries[partIntMap[side+part3]]
    part3 = all_keypoints[int(part3_global), 0:2]

    td = part2-part3
    esDistance = np.sqrt(np.inner(td, td))
    if part2[0] < part1[0]:
        return True
    return False

def drawLinesTriplets(pose_entries, all_keypoints, img, color, side, part1L, part2L, part3L):
    part1_global = pose_entries[partIntMap[side+part1L]]
    part1 = all_keypoints[int(part1_global), 0:2]
    cv2.circle(img, (int(part1[0]), int(part1[1])), 3, color, -1)
    font                   = cv2.FONT_HERSHEY_SIMPLEX
    bottomLeftCornerOfText = (10,500)
    fontScale              = 1
    fontColor              = (255,255,255)
    lineType               = 2
    cv2.putText(img, part1L, 
                    (int(part1[0]), int(part1[1])), 
                    font, 
                    fontScale,
                    fontColor,
                    lineType)
    part2_global = pose_entries[partIntMap[side+part2L]]
    part2 = all_keypoints[int(part2_global), 0:2]
    cv2.circle(img, (int(part2[0]), int(part2[1])), 3, color, -1)
    cv2.putText(img, part2L, 
                    (int(part2[0]), int(part2[1])), 
                    font, 
                    fontScale,
                    fontColor,
                    lineType)
    part3_global = pose_entries[partIntMap[side+part3L]]
    part3 = all_keypoints[int(part3_global), 0:2]
    cv2.circle(img, (int(part3[0]), int(part3[1])), 3, color, -1)
    cv2.putText(img, part3L, 
                    (int(part3[0]), int(part3[1])), 
                    font, 
                    fontScale,
                    fontColor,
                    lineType)
    cv2.line(img, (int(part1[0]), int(part1[1])), (int(part2[0]), int(part2[1])), color, 2)
    cv2.line(img, (int(part2[0]), int(part2[1])), (int(part3[0]), int(part3[1])), color, 2)




def checkDistance(pose_entries, all_keypoints, side, part1, part2):
    part1_global = pose_entries[partIntMap[side+part1]]
    part1 = all_keypoints[int(part1_global), 0:2]
    part2_global = pose_entries[partIntMap[side+part2]]
    part2 = all_keypoints[int(part2_global), 0:2]
    distance = np.square((part1[0]-part2[0])) + np.square((part1[1]-part2[0]))
    if distance < 20:
        return False
    return True
partIntMap = {
        'leftHip': 11,
        'rightHip': 8,
        'leftKnee': 12,
        'rightKnee': 9,
        'nose': 0,
        'leftElbow': 6,
        'rightElbow': 3,
        'rightShoulder': 2,
        'leftShoulder': 5,
        'chestCenter': 1,
        'leftEye': 15,
        'rightEye': 14,
        'rightWrist': 4,
        'leftWrist': 7,
        'rightAnkle': 10,
        'leftAnkle': 13,
        'leftEar': 16,
        'rightEar': 17
    }
intPartMap = dict((v, k) for k, v in partIntMap.items())
net = PoseEstimationWithMobileNet()
checkpoint = torch.load('.\checkpoints\checkpoint_iter_370000.pth', map_location='cpu')
load_state(net, checkpoint)


def start_planks(source=0, vid=None):
    # accuracy_queue.put("from demo fun")
    print(source, vid)
    frame_provider = CameraReader(source=source)
    if vid is not None:
        frame_provider = VideoReader(vid)
    height_size = 256
    cpu = False
    # tts.init()
    run_demo(net, frame_provider, height_size, cpu)
if __name__ == '__main__':
    tts.init()
    # vid = 'shivam plank_Trim.mp4'
    # vid = 'mayank quick start.mp4'
    vid = None
    source = 1
    frame_provider = CameraReader(source)
    if vid is not None:
        frame_provider = VideoReader(vid)
    height_size = 256
    cpu = False
    # vid = 'mayank back raise.mp4'
    start_planks(0, vid)
    
