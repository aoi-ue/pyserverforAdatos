# pyserverforAdatos checklist

## Completed 
- [x]  Establish the server requirements and understand how Sentinel Hub is imported to QGIS 
- [x]  Create a simple pyserver that takes an HTTP request and send a request on insomnia 
- [x]  Setting up python and conda environment locally 
- [x]  Sentinel Hub running locally 
- [x]  Implement to Python Server as a listening port to tasking_server and use GET method from taskingserver 
- [x]  Implemented GET & POST using Bottle Library (https://bottlepy.org/docs/dev/index.html)  

## To be completed by 19 Oct 2018 (Friday) 
- [ ]  Based on client's specific analysis key, retrieve, using asyncio, Josie's and Hafiz's most updated script from S3 and run def function(s)
    *   Set up aws S3 to download/sync by accessing to scripts buckets (aws cli || boto3)
    *   Scripts should only run the specific request (for yuhan: need to gather specifications)
    *   Importing a custom python script which is not installed in a directory
  
## On-hold 
- [ ]   Testing: Script with Mock request, to check that it is downloads the script and run the functions, check if the output is correct and store in aws bucket   
- [ ]   Create a checklist that updates on job status on Tasking Page 
- [ ]   Include Error Handler** to stop script, and send notification to josie and hafiz
- [ ]   Create a function to email with SMTPlib to client once successful stored in database 
- [ ]   Output as Final Images should be stored in S3 bucket 
- [ ]   Output as Final Images to be 'POST' response to mapping_server to display 