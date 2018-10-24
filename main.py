from bottle import run, get, post, request  
from datetime import datetime
import importlib 
import json
import subprocess
import re 
import os

req = {
    "api_key": "",
    "job_id": 6,
    "organization_id": 1,
    "organization_key": "demo",
    "region_key": "Johor",
    "mode": "s2",
    "analysis_key": ["flood_risk", "plant_productivity", "foilar_moisture"],
    "data_s2": [{
        "product_name": "S2A_MSIL1C_20180903T031541_N0206_R118_T48NUH_20180903T061615",
        "utm_zone": 48,
        "latitude_band": "N",
        "grid_square": "UH"
    }, {
        "product_name": "S2A_MSIL1C_20180903T031541_N0206_R118_T48NUH_20180903T061615",
        "utm_zone": 48,
        "latitude_band": "N",
        "grid_square": "UH"
    }]
}

# POST Request from Tasking_server Scripts from S3 Based on the tasking_server's analysis key 
@post('/tasking')
def postReq(): 
	req = request.json
	print (req) 
	return "task request received!"

# Command to sync S3 Bucket, using Subprocess module popen. output should download script in awscriptpy folder
p = subprocess.Popen(['aws', 's3', 'sync','s3://adatos-agri-services/scripts','awspyscript'], stdout=subprocess.PIPE)
print (p.communicate())

# Import Dynamically to main.py to import Josie's Script from S3 Bucket 
sample = importlib.import_module(".sample","awspyscript")
josie_script = importlib.import_module(".SentinelHubSingleDownload","awspyscript")

# Define tasking_server json as required variable 
date = req['data_s2'][0]['product_name'] 

def date_check(date):
    pattern = '_([0-9]{8})T'
    dtd_list = re.findall(pattern, date)
    dtd = dtd_list[0]
    f_dtd = datetime.strptime(dtd, '%Y%m%d').strftime('%Y-%m-%d')
    return f_dtd

tiledate = date_check(date)
 
utm = str(req['data_s2'][0]['utm_zone'])
lat = req['data_s2'][0]['latitude_band']
grid = req['data_s2'][0]['grid_square']

tilename = utm + lat + grid

# create a file to store josie's script 
downloadloc = r'./awsfolder'
if not os.path.exists(downloadloc):
    os.makedirs(downloadloc)

# Parse in variable as argument in josie function and Run Async Josie's Script 

# Run Output in sen2Cor 

# Run Hafiz's Script 

# *NEW REQUEST PENDING* 

# Error Handler to end script and notify josie & hafiz error** 

# USING REQUESTS Lib: 
# Seed Folder 
# Post to AWS S3 Bucket  
# Post to mapping_server
# python post to completejobrequest, parse in api keys and jobid to trigger email 

run(host='localhost', port=8000, reloader=True, debug=True)