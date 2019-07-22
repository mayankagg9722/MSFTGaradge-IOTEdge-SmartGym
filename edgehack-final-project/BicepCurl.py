import sys    
import numpy as np
from demo import partIntMap,isFacingLeft
from PostureUtils import Point,partIntMap
from demo import infer_fast, extract_keypoints, group_keypoints
class BicepCurl:
    def __init__(self,pose_entries, all_keypoints):
        self.side = "left" if isFacingLeft(pose_entries, all_keypoints) else "right"
        self.shoulder = Point(pose_entries, all_keypoints, self.side, "Shoulder")
        self.elbow = Point(pose_entries, all_keypoints, self.side, "Elbow")
        self.wrist = Point(pose_entries, all_keypoints, self.side, "Wrist")
        self.hip = Point(pose_entries, all_keypoints, self.side, "Hip")
        self.knee = Point(pose_entries, all_keypoints, self.side, "Knee")

    def isCorrectElbow(self):
        elbowAngle = self.shoulder.getJointAngle(self.hip, self.elbow)
        #print (elbowAngle)
        if elbowAngle > 60:
            return False
        else:
            return True
    
    def isCorrectBack(self):
        backAngle = self.hip.getJointAngle(self.shoulder,self.knee)
        #print(backAngle)
        if(backAngle < 160):
            return False
        else:
            return True

    def getCurlAngle(self):
        curlAngle = self.elbow.getJointAngle(self.shoulder, self.wrist)
        return curlAngle

def run_bicepcurl(net, image_provider, height_size, cpu):
    net = net.eval()
    if not cpu:
        net = net.cpu()

    stride = 8
    upsample_ratio = 4
    
    reps = 0
    prev_curl_angle = 180
    incomplete_dir_count = 0
    concentric = True

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

        for n in range(len(pose_entries)):
            pose_entry = pose_entries[n]
            if len(pose_entries[n]) <10:
                continue
            #print(pose_entry)
            #print(all_keypoints)
            bicepCurl = BicepCurl(pose_entry, all_keypoints)
            cur_curl_angle = bicepCurl.getCurlAngle()

            print (bicepCurl.isCorrectElbow())
            print (bicepCurl.isCorrectBack())

            if concentric and cur_curl_angle < 30:
                reps +=1
                print (str(reps) + "done")
                concentric = not concentric
                incomplete_dir_count = 0
                continue
            elif concentric and cur_curl_angle > prev_curl_angle:
                incomplete_dir_count += 1
            elif concentric:
                print ("carry on")
            elif not concentric and cur_curl_angle > 160:
                print ("come on next rep")
                if cur_curl_angle < prev_curl_angle:
                    concentric = not concentric
                    continue
            
            prev_curl_angle = cur_curl_angle
            if incomplete_dir_count > 10:
                print ("incomplete rep. Try again")
                incomplete_dir_count = 0
