#!/bin/bash
echo "Starting required package installations";

declare -a package_array
package_array=("oauth2client" "azure" "azure-storage-blob" "google-cloud-storage" "google-api-python-client" "geopy")

if ! dpkg -s $package>/dev/null 2>&1; 
then sudo apt-get install python3
fi

if ! dpkg -s $package0>/dev/null 2>&1; 
then sudo apt install python3-pip
fi

for i in ${package_array[@]}
	do
		echo $i
		if ! dpkg -s $i>/dev/null 2>&1; 
			then sudo pip install $i
		fi
	done


echo "Installations completed Successfully"

sudo python3 initialConfigurations.py 
