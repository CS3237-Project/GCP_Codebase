import subprocess
import json
import numpy as np
import glob
import os.path
import struct
import math

def getAngle():
  inputFileName = os.path.basename(glob.glob('/home/pratyushghosh14/inputImages/*.jpg')[0])
  inputDateTime = inputFileName[0:len(inputFileName)-4]

  args = "/home/pratyushghosh14/openpose/openpose.bin --image_dir /home/pratyushghosh14/inputImages --display 0 --write_images /home/pratyushghosh14/outputImages --write_images_format jpg --write_json /home/pratyushghosh14/outputJSONs"

  program = subprocess.Popen(args, stdout=subprocess.PIPE, shell=True, cwd='/home/pratyushghosh14/openpose/')

  program.wait()
  
  keypoints = json.load(open('/home/pratyushghosh14/outputJSONs/' + inputDateTime + '_keypoints.json'))['people'][0]['pose_keypoints_2d']
  
  a = np.array(keypoints[0:2])
  b = np.array(keypoints[3:5])
  c = np.array(b[0] + 0.5, b[1])
  
  angleCVA = -angleBetween(a,b,c)
  return angleCVA

def angleBetween(a, b, c):
  
  ba = a - b
  bc = c - b
  
  cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
  
  angle = np.arccos(cosine_angle)
  
  return(np.degrees(angle) - 90)

def getCurrentImage():
  return (glob.glob('/home/pratyushghosh14/outputImages/*.jpg')[0])

