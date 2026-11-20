"""Premultiplied projective shutter, soft mattes and contact shadows."""
import cv2
import numpy as np

def projected_exposure(packed,src,corners,size):
    w,h=size
    acc=np.zeros((h,w,4),np.float32)
    for quad in corners:
        T=cv2.getPerspectiveTransform(np.float32(src),np.float32(quad))
        acc+=cv2.warpPerspective(packed,T,(w,h),flags=cv2.INTER_LINEAR)
    return np.uint8(np.clip(acc/len(corners),0,255))

def shadow_pass(roi,alpha,dx,dy,sigma,opacity,color=(0,0,0)):
    h,w=roi.shape[:2]; a=alpha.reshape(h,w)
    if sigma>.15:a=cv2.GaussianBlur(a,(0,0),sigma)
    a=cv2.warpAffine(a,np.float32([[1,0,dx],[0,1,dy]]),(w,h),flags=cv2.INTER_LINEAR)
    a=np.clip(a*opacity,0,1)[...,None]
    return roi*(1-a)+np.asarray(color,dtype=np.float32)*a

def feather_mask(alpha,distance,progress,feather):
    feather=max(.0001,min(1.,float(feather)))
    return np.uint8(alpha*np.clip((progress-distance)/feather+.5,0,1))
