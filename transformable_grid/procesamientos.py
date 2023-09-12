import cv2


def binaryTreshold(img, tresh):
    img = cv2.GaussianBlur(img,ksize=(5,5),sigmaX=0,sigmaY=0)
    ret, edgeImg = cv2.threshold(img, tresh.x, 255, cv2.THRESH_BINARY)
    return edgeImg


def cannyThreshold(img, thresh):
    img = cv2.GaussianBlur(img,ksize=(5,5),sigmaX=0,sigmaY=0)
    edgeImg = cv2.Canny(img, threshold1=thresh.x, threshold2=thresh.y)
    return edgeImg

