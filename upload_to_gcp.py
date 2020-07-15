import socket
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import os
import functools
import json
import ntpath
import datetime
import time
from google.cloud import storage
import socket
#check if connected to internet
def is_connected():
    try:
    # connect to the host -- tells us if the host is actually
    # reachable
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        pass
        return False


    
def upload_to_gcp():
    
    print ("-----------------------------GCP BEGIN-------------------------------")
    while(os.path.getsize("/home/pi/Desktop/gcp_data_files/log-gcp.txt") > 0):
        with open("/home/pi/Desktop/gcp_data_files/log-gcp.txt","r") as fin:
            firstline = fin.readline().rstrip()
            print("file name :",firstline)
            storage_client = storage.Client.from_service_account_json('IOT Connectivity-6e262958d322.json')
            bucket_name = 'uploaded_files'
            blob_name=ntpath.basename(firstline) 
            #print(buckets = list(storage_client.list_buckets())

            try :

                bucket = storage_client.get_bucket(bucket_name)
                blob = bucket.blob(str(blob_name))
                flag=blob.upload_from_filename(firstline)
                print(flag)
                if(flag==None):
                    print("uploaded")
                    os.remove(firstline)
                    print("Deleted")
                    data = fin.read().splitlines(True)
                    with open("/home/pi/Desktop/gcp_data_files/log-gcp.txt","w") as fout:
                        fout.writelines(data[0:])
                        data=fin.read()
                        print("file content1:",data)
                    print ("-----------------------------GCP END--------------------------------")

            except :
                print("error")
                return
    
    







