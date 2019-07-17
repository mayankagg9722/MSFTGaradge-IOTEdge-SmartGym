import sys    
import numpy as np

'''
Usage:
from PostureUtils import Point
pose_entry = pose_entries[0]
#Making the point objects
p1 = Point(pose_entry, all_keypoints, "left", "Shoulder")
p2 = Point(pose_entry, all_keypoints, "chestCenter")
p3 = Point(pose_entry, all_keypoints,"nose")

#Get angle formed at p2 by the lines joining p2 with p1 and p3
print("angle : " + str(p2.getJointAngle(p1,p3)))
'''
class Point:
    def __init__(self,pose_entries, all_keypoints, side, part=None):
        if part is None:
            pos = pose_entries[partIntMap[side]]
        else:
            pos = pose_entries[partIntMap[side+part]]
        self.coord = all_keypoints[int(pos), 0:2]
        self.side = side
        self.part = part
    
    def distance(self, otherPoint):
        return np.square((self.coord[0]-otherPoint.coord[0])) + np.square((self.coord[1]-otherPoint[1]))
    
    def getJointAngle(self,point1,point2):
        line1 = point1.coord - self.coord
        line2 = point2.coord - self.coord

        cosine_angle = np.dot(line1, line2) / (np.linalg.norm(line1) * np.linalg.norm(line2))
        angle = np.arccos(cosine_angle)

        return np.degrees(angle)


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
