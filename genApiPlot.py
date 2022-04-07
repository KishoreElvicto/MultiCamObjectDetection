#       --Requirments--     #
#   easy_install -U pip
#   python -m pip install --upgrade pip
#   pip install opencv-python
#   pip install requests
#   pip install matplotlib

#       About       #
#   This Project uses three API
#   1-  To Get camera details and extract it's token
#   2-  Use the Token to get the plot(x,y)
#   3-  Use the points to check if a point is with in the object frame for decting occupied parking spot
#   4-  made it generic api for working on amultiple cameras
#   5-  image is dynamic
#   6-  fixed the new device withouthout plot error
import threading

import requests
import cv2
import matplotlib.pyplot as plt
import numpy as np
import json
import os, sys, random, time
import urllib.request
from PIL import Image

cap = cv2.VideoCapture(0)
i = 0
RestUrl = "http://13.233.145.91:7702/api/"
CamUrl = "http://technopark.iospace.in/"


def thisIsIt(responseJson, imageUrl):
    #print("\n\n\n thisIsIt nresponseJson: ", responseJson)  # classes for object dectation
    config_file = './RequiredFiles/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt'
    frozen_model = './RequiredFiles/frozen_inference_graph.pb'
    model = cv2.dnn_DetectionModel(frozen_model, config_file)

    width, height = 250, 250
    halfWidth, halfHeight = round(width / 2), round(height / 2)
    res = []
    resApi = []
    n = len(responseJson)
    for idx in range(0, n):
        res.append([responseJson[idx].get('x') - halfWidth, responseJson[idx].get('y') - halfHeight])

    # print("The constructed plot position list : ", res)

    # methord to to identify vehicle parked or not
    def checkParkingSpace(imgProcessed):

        occupied = []
        for pos in res:
            cv2.circle(imgProcessed, pos, radius=10, color=(225, 0, 225), thickness=5)


            classIndex, confidence, bbox = model.detect(imgProcessed, confThreshold=0.5)

            font_scale = 2
            font = cv2.FONT_HERSHEY_PLAIN

            if np.array_equal(confidence, ()) and np.array_equal(classIndex, ()):
                #print("if np.array_equal(confidence, ()) and np.array_equal(classIndex, ()):")
                for classInd, conf, boxes in zip(bbox):
                    #print("conf: ", conf)
                    if classInd == 2 or classInd == 3 or classInd == 4 or classInd == 6:
                        #print("inside : if np.array_equal(confidence, ()) and np.array_equal(classIndex, ()): ")
                        cv2.rectangle(imgProcessed, boxes, (255, 0, 0), 2)
                        cv2.putText(imgProcessed, classLabels[classInd - 1], (boxes[0] + 10, boxes[1] + 40), font,
                                    font_scale,
                                    color=(0, 225, 0), thickness=3)


                # cv2.rectangle(imag, pos, (pos[0] + width, pos[1] + height), (0, 225, 0), 2)
            else:
                for iK in classIndex:
                    if iK == 2 or iK == 3 or iK == 4 or iK == 6:
                        # occupied.append(spot)
                        # print(occupied)
                        #print("ik: ", iK)
                        for classInd, conf, boxes in zip(classIndex.flatten(), confidence.flatten(), bbox):
                            #print("box: ",boxes)
                            #print("conf: ", conf)
                            if classInd == 2 or classInd == 3 or classInd == 4 or classInd == 6:
                                #print("box: ", boxes)
                                #print("conf: ", conf)
                                lx,ly,cw,ch = boxes

                                hw,hh= round(cw / 2), round(ch / 2)
                                cx,cy=lx + hw, ly + hh
                                rx, ry = cx + hw, cy + hh

                                #print("left x, left y, center x, center y, rignt x, right y: ",lx, ly, cx, cy, rx, ry)
                                cv2.rectangle(imgProcessed, boxes, (255, 0, 0), 2)
                                #print("pos: ", pos)
                                bindingBoxCenter=cv2.circle(imgProcessed,(cx,cy),radius=10,color=(225,225,0),thickness=5)
                                #   1758 > 940 and 1758 < 2140 and 894 > 584 and 894 < 1248 = 175, 894
                                #          942            2118           587           1265

                                #   1204 > 940 and 1204 < 2140 and 888 > 584 and 888 < 1248 = 1204, 888
                                #   786 > 940 and 786 < 2140 and 847 > 584 and 847 < 1248 = 786,584

                                if(pos[0] > lx and pos[0] < rx and pos[1] > ly and pos[1] < ry):
                                    #print(pos[0], " > ", lx, " and ", pos[0], " < ", rx, " and ", pos[1], " > ", ly,
                                     #     " and ", pos[1], " < ", ry)
                                    occupied.append(pos)
                                    print("####################################################################################")
                                    #print("left x, rignt x, left y, right y: ", lx, rx, ly, ry)
                                    #print("spots: ", res)
                                    print("occupied: ",occupied)
                                    #print("car occupied at : ", pos)
                                    print("####################################################################################")

                                cv2.putText(imgProcessed, classLabels[classInd - 1], (boxes[0] + 10, boxes[1] + 40), font,
                                            font_scale,
                                            color=(0, 225, 0), thickness=3)
                                # plt.imshow(bindingBoxCenter)
                                # plt.waitforbuttonpress()


                    else:
                        #print(iK)
                        print("it's not a vehicle")

        for indx in enumerate(responseJson):
            # print("indx: ", indx[0])
            print("res[indx]: ", indx)
            if occupied.__contains__(res[indx[0]]):
                resApi.append([responseJson[indx[0]].get('lotname'), True, 123])
                print(True)
            else:
                resApi.append([responseJson[indx[0]].get('lotname'), False, 456])
                print(False)
        # print("result api: ", resApi)

        keyList = ["spot", "occupied", "since"]
        jsonRes = []

        for idx in range(0, n):
            jsonRes.append({keyList[0]: resApi[idx][0], keyList[1]: resApi[idx][1], keyList[2]: resApi[idx][2]})

        # print("The result API list : ", str(jsonRes))
        print("The JSON result API  : " + json.dumps(jsonRes))
        jsonFullRes = {"area": "A", "spots": jsonRes}
        response = requests.post(RestUrl + "elw_camparkingstatuschange", json=jsonFullRes)
        print("Status code: ", response.status_code)

    # empty list of python
    detect = []
    classLabels = []

    # loading object dectation names
    file_name = './RequiredFiles/label.txt'
    with open(file_name, 'rt') as fpt:
        classLabels = fpt.read().rstrip('\n').split('\n')
        # print(classLabels)
        # print(len(classLabels))

        ## model
        model.setInputSize(320, 320)
        model.setInputScale(1.0 / 127.5)  ## 255/2 = 127.5
        model.setInputMean((127.5, 127.5, 127.5))
        model.setInputSwapRB(True)

        # cv2.waitKey(4000)
        urllib.request.urlretrieve(imageUrl, "spot2.jpg")
        #imag = cv2.imread('./Images/spot2.jpg')
        imag = cv2.imread('spot2.jpg')
        # cv2.imwrite('C:/Users/A N O N Y M O U S/PycharmProjects/ImageProcessingTest/LiveCam/Frame' + format(
        #    time.time()) + '.jpg', imag)
        # cv2.imshow('image', imag)
        # cv2.destroyAllWindows()
        # plt.imshow(imag)
        # imgBlur = cv2.GaussianBlur(imag, (5, 5), 5)
        # plt.waitforbuttonpress();
        checkParkingSpace(imag)
        # time.sleep(4)
        plt.imshow(cv2.cvtColor(imag, cv2.COLOR_BGR2RGB))
        plt.waitforbuttonpress()


try:
    # data = requests.get("https://jsonplaceholder.typicode.com/posts")
    # data.raise_for_status()

    data = [{"deviceid": "14.fsf.64161", "camurl": "http://technopark.iospace.in/cam-a.jpg"},
            {"deviceid": "12.sd.256sad", "camurl": "http://technopark.iospace.in/cam-b.jpg"},
            {"deviceid": "15.as.2345ed", "camurl": "http://technopark.iospace.in/cam-c.jpg"}]
    datas = json.dumps(data)

    dataform = datas.strip("'<>() ").replace('\'', '\"')
    struct = json.loads(dataform)

    contents = json.loads(datas)
    #print(contents)
    print(struct)
    # Data that we will send in post request.

    resJson = []
    # The POST request to our node server
    for thisDevice in struct:
        print("thisDevice: ", thisDevice)
        res = requests.post(RestUrl + 'dev_cameralogin', json=thisDevice)
        resJson.append(res.json())
    print("returned json list: ", resJson)

    token = []
    logcode = []
    for thisToken in resJson:
        print("thisToken: ", thisToken)
        # Convert response data to json
        returned_data = thisToken
        print("returned data: ", returned_data)

        logcode.append(returned_data["Response"][0][0]["_logcode"])
        if returned_data["Response"][0][0]["_logcode"] == 1000:
            token.append(returned_data["Response"][1][0]["_token"])
        else:
            token.append("token-failed")
        print("\n\n\nlogcode: ", logcode)
        print("token: ", token)

    #######################################################################################################################################################

    tcount = 0;
    plot_img = []
    logcode_img = []
    for code in logcode:
        print("log-success: ", code)
        print("token-success: ", token[tcount])
        imgData = {
            "deviceid": struct[tcount]["deviceid"],
            "token": token[tcount],
            "ipaddress": "10.10.100",
            "imageurl": struct[tcount]["camurl"]
        }
        tcount = tcount + 1

        imgDatas = json.dumps(imgData)

        imgDataForm = imgDatas.strip("'<>() ").replace('\'', '\"')
        imgStruct = json.loads(imgDataForm)

        imgContents = json.loads(imgDatas)
        # print(imgContents)
        # print("imgStruct: ",imgStruct)  # imgStruct:  {'deviceid': '14.fsf.64161', 'token': '041a4e5b-a042-11ec-9fa5-0afd0676b02c', 'ipaddress': '10.10.100', 'imageurl': ['http://technopark.iospace.in/cam-a.jpg']}
        # Data that we will send in post request.

        # The POST request to our node server
        imgRes = requests.post(RestUrl + 'dev_setcamera', json=imgStruct)
        # Convert response data to json
        img_returned_data = imgRes.json()
        print("img_returned_data: ", img_returned_data)

        if code == 1000:
            if np.array_equal(img_returned_data["Response"][1][0]["plot"],''):
                logcode_img.append(img_returned_data["Response"][0][0]["_logcode"])
                plot_img.append("plot-fail")
                print("######################")
                print("\n\n\nlogcode_img: ", logcode_img)
                print("plot_img: ", plot_img)
            else:
                logcode_img.append(img_returned_data["Response"][0][0]["_logcode"])
                plot_img.append(json.loads(img_returned_data["Response"][1][0]["plot"]))
                print("\n\n\nlogcode_img: ", logcode_img)
                print("plot_img: ", plot_img)
        elif code == 1001:
            logcode_img.append(img_returned_data["Response"][0][0]["_logcode"])
            plot_img.append("plot-fail")
            print("\n\n\nlogcode_img: ", logcode_img)
            print("plot_img: ", plot_img)

    while True:
        time.sleep(10)
        img_count = 0
        for plot in plot_img:
            print(plot)
            if np.array_equal(plot, "plot-fail"):
                print("logcode_img: ", logcode_img)
                struct[img_count]["camurl"]
                img_count = img_count + 1
            else:
                print("\n\n\nobject detection time: ", plot)
                # thisIsIt(plot, struct[img_count]["camurl"]);
                th = threading.Thread(target=thisIsIt, args=(plot, struct[img_count]["camurl"]))
                th.start()
                #th.join()
                img_count = img_count + 1
except requests.exceptions.HTTPError as errh:
    print(errh)
except requests.exceptions.ConnectionError as errc:
    print(errc)
except requests.exceptions.Timeout as errt:
    print(errt)
except requests.exceptions.RequestException as err:
    print(err)