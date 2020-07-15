#!/usr/bin/python3
#from allcodes import *
from datetime import datetime
import time
import json
#from FileUpload_azure import *
from allcodes_kit2_cloud import *
from upload_to_azure  import *
from upload_to_gcp import *

if __name__==  "__main__":
    start=0
    counter=3
    timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
    while(True):
        msg=all_codes()
        
        log_azure = open("/home/pi/Desktop/azure_data_files/log-azure.txt","a+")
        log_gcp = open("/home/pi/Desktop/gcp_data_files/log-gcp.txt","a+")
        
        outPutname_gcp = "/home/pi/Desktop/gcp_data_files/Data_gcp"+timestamp+".json"
        outPutname_azure = "/home/pi/Desktop/azure_data_files/Data_azure"+timestamp+".json"
        if(start==0):
            with open(outPutname_azure,"a+") as f:
                f.write("[")
        
        with open(outPutname_azure,"a+") as f:
            f.write(msg)
            if(start!=2):
                f.write(",")
            f.write("\n")
            f.close()
        with open(outPutname_gcp,"a+") as f:
            f.write(msg)
            f.write("\n")
            f.close()
             
        print("sleeping")
        time.sleep(3)
        
        start=start+1
        print(start)
        if(start==counter):
            
            with open(outPutname_azure,"a+") as f:
                f.write("]")
            log_azure.write(outPutname_azure+'\n')
            log_gcp.write(outPutname_gcp+'\n')
            
            data=log_azure.read()
            print("log-azure:=========",data)
            
            
            data1=log_gcp.read()
            print("log-gcp:=========",data1)
            upload_to_gcp()
            run_sample()
            start=0
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        print("===============================================")
        log_azure.close()
        log_gcp.close()
        print("Done")
