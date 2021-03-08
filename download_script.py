import datetime
import json
from datetime  import date, timedelta
import tempfile
import requests
import os.path
from csv import reader



HW_BASE_URL = 'https://connect-api.cloud.huawei.com'
HW_APP_ID = ""
HW_CLIENT_ID = ""
HW_CLIENT_SECRET = ""


'''
Use this function to generate an authentication token for huawey app gallery API. 
get_hw_token take in input:
    - clientID and clientSecret generated inside app gallery developer portal
'''
def get_hw_token(clientID, clientSecret):

    print("getting HW token...")
    headers = {
        'Content-Encoding': 'UTF-8',
        'Content-Type': 'application/json'
    }
    data = [
        {
            "client_id": clientID,
            "client_secret": clientSecret,
            "grant_type": 'client_credentials',
        }
    ]

    tokenResponse = requests.post(url=HW_BASE_URL+"/api/oauth2/v1/token", json =data, headers=headers)
    res = tokenResponse.json()
    return res['access_token']

'''
downloadHVCsv take in input: 
    - token generated with get_hw_token()
    - appID that is the application id in huawey app gallery
    - startDate and endDate datetime for report (the range cannot exceed 30 days)
    - outputFilename path for final CSV (optional)

    The result is the CSV file path with download data inside. Header of CSV:
    Date,Impressions,Details screen views,Total downloads,Update downloads,New downloads,Uninstalls,CTR,Details screen CVR,Installation success rate
'''
def downloadHVCsv(token, appId, startDate, endDate, outputFilename=None):
    startDate = startDate.strftime("%Y%m%d")
    endDate = endDate.strftime("%Y%m%d")
    
    urlDownload=HW_BASE_URL+"/api/report/distribution-operation-quality/v1/appDownloadExport/"+appId+"?language=en-US&startTime="+startDate+"&endTime="+endDate
    headersDownload = {
            'Authorization': 'Bearer '+token,
            'client_id': HW_CLIENT_ID,
            
        }
    downloadHWResponse = requests.get(url=urlDownload,headers=headersDownload)
    fileURL = downloadHWResponse.json()['fileURL'] #this is the CSV url with download data

    if outputFilename is None:
        temp_folder = tempfile.gettempdir()
        outputFilename = os.path.join(temp_folder, 'downloadHW.csv')
    
    #write to file
    req = requests.get(fileURL)
    csv_file = open(outputFilename, 'wb')
    csv_file.write(req.content)
    csv_file.close()

    return outputFilename


def main():
    #generate auth token
    token = get_hw_token(HW_CLIENT_ID, HW_CLIENT_SECRET)

    today = datetime.date.today()
    endDate = today - datetime.timedelta(days=1)
    startDate = today - datetime.timedelta(days=30)
    
    #get download for last 30 day of HW_APP_ID
    downloadCsv = downloadHVCsv(token, HW_APP_ID, startDate, endDate)

    #convert to JSON
    downloadJson = dict()

    with open(downloadCsv, 'r') as read_obj:
        csv_reader = reader(read_obj)
        rowCount = 1
        for row in csv_reader:
            if rowCount == 1: #this is the header
                pass
            else:
                date = row[0]
                date = datetime.datetime.strptime(date, '%Y%m%d') #Conver date to datetime
                new_download = int(row[5])
                uninstall = int(row[6])
                downloadJson[date]={'download':new_download, 'uninstall':uninstall}
            rowCount+=1

    print(downloadJson)

if __name__ == "__main__":
    main()