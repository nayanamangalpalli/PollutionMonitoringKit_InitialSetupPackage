# ----------------------------------------------------------------------------------
# MIT License
#
# Copyright(c) Microsoft Corporation. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# ----------------------------------------------------------------------------------
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.



import os
import ntpath
import time
import datetime
from azure.storage.blob import BlockBlobService, PublicAccess

# ---------------------------------------------------------------------------------------------------------
# Method that creates a test file in the 'Documents' folder.
# This sample application creates a test file, uploads the test file to the Blob storage,
# lists the blobs in the container, and downloads the file with a new name.
# ---------------------------------------------------------------------------------------------------------
# Documentation References:
# Associated Article - https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python
# What is a Storage Account - http://azure.microsoft.com/en-us/documentation/articles/storage-whatis-account/
# Getting Started with Blobs-https://docs.microsoft.com/en-us/azure/storage/blobs/storage-python-how-to-use-blob-storage
# Blob Service Concepts - http://msdn.microsoft.com/en-us/library/dd179376.aspx
# Blob Service REST API - http://msdn.microsoft.com/en-us/library/dd135733.aspx
# ----------------------------------------------------------------------------------------------------------


def run_sample():
    try:
        print ("------------------------AZURE-----------------------")
        print ( "IoT Hub file upload sample, press Ctrl-C to exit" )
        while(os.path.getsize("/home/pi/Desktop/azure_data_files/log-azure.txt")>0):
            val=None
            full_path_to_file =" "
            val1=block_blob_service = BlockBlobService(account_name='pollprojectstrgacc', account_key='1gk5tAS8bc3zCQeibeOzDttkSkzXxuEkqbJBu0TCHxlM6aW5B1HpIDGFYlHPx8Y7sERQ+kCQzrI3TcGnpXRnSw==')
            print(val1)
       
            container_name ='pollprojectstrgscccont'

            print("abc")
        
            with open("/home/pi/Desktop/azure_data_files/log-azure.txt","r") as fin:
                print("Inside while-with")
                full_path_to_file = fin.readline().rstrip()
                    #firstline = firstline
                print(full_path_to_file)
          
    
            blob_name=ntpath.basename(full_path_to_file)
            print("Temp file = " + full_path_to_file)
            print("\nUploading to Blob storage as" + blob_name)

            val=block_blob_service.create_blob_from_path(container_name, blob_name, full_path_to_file)
            print(val)
            if(val!=None):
                print ( "...file uploaded successfully." )
                print("uploaded")
                os.remove(full_path_to_file)
                print("Deleted")
                with open("/home/pi/Desktop/azure_data_files/log-azure.txt","r") as fin:
                    data = fin.read().splitlines(True)
                #os.remove(data[0])
                with open("/home/pi/Desktop/azure_data_files/log-azure.txt","w") as fout:
                    fout.writelines(data[1:])
                print("File updated")
                print ("-----------------------------AZURE END--------------------------------")
            

    except Exception as e:
        print("error")
        return






