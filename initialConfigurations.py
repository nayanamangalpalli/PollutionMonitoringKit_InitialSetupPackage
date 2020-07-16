import os
from geopy.geocoders import Nominatim
from google.cloud import bigquery		#GOOGLE_CLOUD
import googlemaps
from datetime import datetime

from azure.cosmos import exceptions, CosmosClient, PartitionKey
import json
import config


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

url = "https://pollprojectcosdb.documents.azure.com:443/"
key = 'OGYOFwBffdNGqH54A6iHKL1Ql75JKRsvmvxNhpwnDsUe8o3LgxSZ5eeGyzsbaJKMund0yN5tdQSe0WmzfLlrfg=='

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="IOT_Connectivity.json"		#GOOGLE_CLOUD

client = CosmosClient(url, key)
google_client = bigquery.Client()		#GOOGLE_CLOUD

database_id = "pollprojectdb"
container_id = "kitLocStatusData"

database = client.get_database_client(database_id)
container = database.get_container_client(container_id)

items = list(container.query_items(
    query = "SELECT * FROM c WHERE c.u_ID="+U_ID+" AND c.d_ID="+D_ID+" AND c.status='inactive'",
    enable_cross_partition_query=True,))
query_job = google_client.query('SELECT D_ID, U_ID, LAT, LAN, STATUS FROM  `theta-gizmo-240803.pollution_dataset.device_status` WHERE U_ID='+U_ID+' AND D_ID='+D_ID+' AND STATUS ="inactive"')		#GOOGLE_CLOUD


results = query_job.result() 	#GOOGLE_CLOUD
rows = list(results)		#GOOGLE_CLOUD

if len(items) == 0 and len(rows)== 0 :
	print("Please issue a previously unused Device ID (D_ID) first to activate the device from our website www.-----.com")
elif len(items) == 1 and len(rows)== 1 :
	config.D_ID = D_ID
	address = input("Please enter accurate address of where the kit will be placed : ")
	geocode_result = gmaps.geocode(address)

	latitude = geocode_result[0]['geometry']['location']['lat'];
	print ("LAT : "+str(latitude))
	longitude = geocode_result[0]['geometry']['location']['lng'];
	print("LAN : "+str(longitude))

	for item in items:
		print("ITEM : "+str(item))
		item['lat'] = latitude
		item['lng'] = longitude
		item['status'] = "active"
		item['add'] = address
		updated_item = container.upsert_item(item)
	query_job = google_client.query("UPDATE `theta-gizmo-240803.pollution_dataset.device_status` SET LAT=" +str(latitude) + " , LAN =" + str(longitude) + " , ADDRESS =" + address + " , STATUS = 'active' WHERE D_ID="+D_ID)

	results = query_job.result()  # Waits for job to complete.

	fd=open("/etc/rc.local","r")
	d=fd.read()
	fd.close()
	m=d.split("\n")
	s="\n".join(m[:-1])
	fd=open("/etc/rc.local","w+")
	for i in range(len(s)):
		fd.write(s[i])
	fd.close()
	file_object  = open('/etc/rc.local', 'a')
	file_object.write("\nsleep 60 && sudo python3 /final_all_cloud.py \nexit 0")

	if not os.path.exists('/Desktop/azure_data_files'):
		os.makedirs('/Desktop/azure_data_files')

	if not os.path.exists('/Desktop/gcp_data_files'):
		os.makedirs('/Desktop/gcp_data_files')
	
	print("Your kit has successfully been registered and setup to start sending data")
	print("Please shutdown the kit now, place the kit at the desired location and power it on")

