# pyserverforAdatos checklist

## Completed 

- [x]  Establish the server requirements and understand how Sentinel Hub is imported to QGIS 
- [x]  Create a simple pyserver that takes an HTTP request and send a request on insomnia 
- [x]  Setting up python and conda environment locally 
- [x]  Sentinel Hub running locally 
- [x]  Implement to Python Server as a listening port to tasking_server and use GET method from taskingserver 
- [x]  Implemented GET & POST using Bottle Library (https://bottlepy.org/docs/dev/index.html)  
- [x]  Upon client's onclick that triggers tasking_server, write a script to
    * GET Request from tasking_server endpoint
    * Sync to aws S3 script buckets (aws cli & boto3)
    * Retrieve/download using aws s3 cli script to download/read Josie's and Hafiz's most updated script

## To be completed by 24 Oct 2018 (Wednesday) 

- [ ] Josie's 
    * request to be formatted in json and access to data_s2
    * Define Product_name (Filter out date with regex), utm_zone, lat_band, grid_sq as variables 
    * Pass the variables to downloadS2 function and run it using asyncio
    * Parse output image and run sen2cor to process files
- [ ]  Hafiz's
    * Check that it is running on data.json  

- [ ]   Include Error Handler** to stop script, and send notifications to josie and hafiz
    
## On-hold 
- [ ]   Intergration Testing: Run ONE and MORE Mock request from front-end, to check that it downloads the function from s3 bucket script and runs the correct functions, check if the output is correct and store in aws bucket  
- [ ]   Parse as response to tasking_server completejob to email client 
- [ ]   Output as Final Images should be stored in S3 bucket 
- [ ]   Output as Final Images to be 'POST' response to mapping_server to display 
- [ ]   Create a Checklist front page that updates on job status on Tasking Page 