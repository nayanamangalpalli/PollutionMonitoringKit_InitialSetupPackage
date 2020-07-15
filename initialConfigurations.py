import os
#from azure.cosmos import exceptions, cosmos_client, partition_key
from geopy.geocoders import Nominatim
from google.cloud import bigquery		#GOOGLE_CLOUD
import googlemaps
from datetime import datetime

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.errors as errors
import azure.cosmos.http_constants as http_constants
import json
from config import D_ID


gmaps = googlemaps.Client(key='AIzaSyAhi518dsLAktyY8d1BG9gnugORBBfdEMg')

U_IDisAcceptable = "false"
D_IDisAcceptable = "false"

while U_IDisAcceptable != "true" :
	try:
		U_ID = input("Enter UserID (U_ID) : ")
		num = int(U_ID)
		U_IDisAcceptable = "true"
	except ValueError:
		print (" U_ID must be a Number !!")
	
while D_IDisAcceptable != "true" :
	try:	
		D_ID = input("Enter issued Device ID (D_ID) : ")
		num = int(D_ID)
		D_IDisAcceptable = "true"
	except:
		print (" D_ID must be a Number !!")

endpoint = "https://pollprojectcosdb.documents.azure.com:443/"
key = 'OGYOFwBffdNGqH54A6iHKL1Ql75JKRsvmvxNhpwnDsUe8o3LgxSZ5eeGyzsbaJKMund0yN5tdQSe0WmzfLlrfg=='

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="IOT_Connectivity.json"		#GOOGLE_CLOUD

client = cosmos_client.CosmosClient(endpoint, {'masterKey': key})
google_client = bigquery.Client()		#GOOGLE_CLOUD

database_id = "pollprojectdb"
container_id = "kitLocStatusData"

container = client.ReadContainer("dbs/" + database_id + "/colls/" + container_id)
*query = "SELECT * FROM c WHERE c.u_ID="+U_ID+" AND c.d_ID="+D_ID+" AND c.status='inactive'"*
query_job = google_client.query('SELECT D_ID, U_ID, LAT, LAN, STATUS FROM  `theta-gizmo-240803.pollution_dataset.device_status` WHERE U_ID='+U_ID+' AND D_ID='+D_ID+' AND STATUS ="inactive"')		#GOOGLE_CLOUD


items = list(client.QueryItems("dbs/" + database_id + "/colls/" + container_id,
    query,
    {'enableCrossPartitionQuery':True}
))

results = query_job.result() 	#GOOGLE_CLOUD
rows = list(results)		#GOOGLE_CLOUD

if len(items) == 0 and len(rows)== 0 :
	print("Please issue a previously unused Device ID (D_ID) first to activate the device from our website www.-----.com")
elif len(items) == 1 and len(rows)== 1 :
	address = input("Please enter accurate address of where the kit will be placed")
	geocode_result = gmaps.geocode(address)

	latitude = geocode_result[0]['geometry']['location']['lat'];
	longitude = geocode_result[0]['geometry']['location']['lng'];

	for item in items:
		*item['lat'] = latitude*
		*item['lng'] = longitude*
		*item['status'] = "active"*
		*item['add'] = "address"*
		client.ReplaceItem(item['_self'], item)
	query_job = google_client.query("UPDATE `theta-gizmo-240803.pollution_dataset.device_status` SET LAT=" +str(latitude) + " , LAN =" + str(longitude) + " , ADDRESS =" + address + " , STATUS = 'active' WHERE D_ID="+D_ID)

	results = query_job.result()  # Waits for job to complete.

	file_object  = open('/etc/rc.local', 'a')
	file_object.write("sleep 60 && python3 final_all_cloud.py") 

	if not os.path.exists('/Desktop/azure_data_files'):
		os.makedirs('/Desktop/azure_data_files')

	if not os.path.exists('/Desktop/gcp_data_files'):
		os.makedirs('/Desktop/gcp_data_files')
	
	print("Your kit has successfully been registered and setup to start sending data")
	print("Please shutdown the kit now, place the kit at the desired location and power it on")

