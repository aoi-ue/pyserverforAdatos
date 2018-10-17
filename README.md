# pyserverforAdatos checklist

## Completed 
- [x]  Establish the server requirements and understand how Sentinel Hub is imported to QGIS 
- [x]  Create a simple pyserver that takes an HTTP request and send a request on insomnia 
- [x]  Implemented GET & POST using Requests Library (http://docs.python-requests.org/en/master/) to fetch HTTP Request from 
- [x]  Setting up python and conda environment locally 
- [x]  sentinel hub running locally 

## To be completed by 18 Oct 2018 (Thursday) 
- [ ]  Implement a Python Server with websocket lib(tornado) as a listening port (GET from taskingserver and POST to S3 Aws) 
- [ ]  Retrieve Josie's and Hafiz's script from S3 and Run functions based on client's requirements from tasking_server with insomnia
    *   Set up aws S3 to download/sync by accessing to scripts buckets (aws cli || boto3)
    *   Importing a custom python script which is not installed in a directory
    *   Mock data, to run defined functions which downloads most updated scripts, check if the output is correct and store in aws bucket   
  
## On-hold 
- [ ]   A Tasking checklist that updates on job status on Tasking Page 
- [ ]   Create a function to email with SMTPlib to client once successful stored in database 
- [ ]   Output should include middleware for error handling, if valid output should be stored in S3 images as Database
- [ ]   Integrate GET request from AWS bucket to display on mapping_server