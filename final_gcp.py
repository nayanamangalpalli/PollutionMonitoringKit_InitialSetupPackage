#!/usr/bin/python3
#from allcodes import *
from datetime import datetime
import time
import json
from allcodes_kit2_cloud import *
from upload_to_gcp import *

if __name__==  "__main__":
    start=0
    counter=6
    num=1
    while(True):

        msg=all_codes()
        log = open("/home/pi/Desktop/gcp_data_files/log-gcp.txt","a+")
        #msg={"abcd":1234,"values":"hello"}
        outPutname = "/home/pi/Desktop/gcp_data_files/Data_gcp"+str(num)+".json"
        with open(outPutname,"a+") as f:
            f.write(msg)
            f.write("\n")
            f.close()
            print("sleeping")
            time.sleep(5)

        start=start+1
        print(start)
        if(start==counter):
            print("file writing")
            log.write(outPutname+'\n')
            data=log.read()
            print("file content",data)
            upload_to_gcp()
            start=0
            num=num+1
        print("===============================================")
        log.close()
