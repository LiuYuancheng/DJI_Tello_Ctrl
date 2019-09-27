import cv2
import time

LOCAL_IP = '192.168.10.2'
LOCAL_PORT_VIDEO = '11111'

if __name__ == '__main__':

    addr = 'udp://' + LOCAL_IP + ':' + str(LOCAL_PORT_VIDEO)
    cap = cv2.VideoCapture(addr)

    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == True:
            cv2.imshow("Flame", frame)
            k = cv2.waitKey(1)
    cap.release()
    cv2.destroyAllWindows()