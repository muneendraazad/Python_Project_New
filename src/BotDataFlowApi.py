import requests
from datetime import datetime
import sys,os
import json
import warnings
warnings.filterwarnings("ignore")

def fetchSubscriptionKey(keyVersion="v1"):

    defaultKey = "6a471f4480054b539c73172dcffa247c"
    try:
        api_url = "https://mana-nic.internal.ericsson.com/apiserver/nic/dashboard/projectinfo?projectid=ISF_SUBKEY"
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", api_url, headers=headers, data={},timeout=5,verify=False)
        #print(response.text)
        subkey = ""
        if(response.status_code == 200): # succesful case
            subkey = str(response.json()["field1"])
            if(subkey == ""):
                subkey = str(response.json()["field2"])
            if(subkey == ""):
                return defaultKey
            else:
                return subkey
        else:
            return defaultKey
    except Exception as e:
        return defaultKey


# For Updating Bot Data flow
def data_flow_details(dataflowdpayload, woId):
    try:
        if (woId == ""):
            return None
        headers = {
            "Content-Type": "application/json",
            "Apim-Subscription-Key": fetchSubscriptionKey()
        }
        url = "https://integratedserviceflow.ericsson.net/apim/v1/externalInterface/getCompleteWorkOrderDetails?woID={}".format(
            woId)
        response = requests.get(url, headers=headers, verify=False, timeout=30)
        woDetails = json.loads(response.content)
        print(woDetails)
        dataflowdpayload["NodeCount"] = len(woDetails["responseData"][0][0]["listOfNode"])
        dataflowdpayload["ProjectID"] = str(woDetails["responseData"][0][0]["projectID"])
        dataflowdpayload["WorkFlowName"] = woDetails["responseData"][0][0]["workFlowName"]
        dataflowdpayload["TimeStamp"] = str(datetime.now())
        dataflowdpayload["Signum"] = woDetails["responseData"][0][0]["signumID"]
        dataflowdpayload["Team"] = "NDO Team"
        dataflowdpayload["WOID"] = str(woId)

        url = "https://delivery-connector-mana.internal.ericsson.com/user_ms/api/auth/token"
        payload = {}
        headers = {'Authorization': 'Basic ZGF0YWZsb3djb2x1c2VyOmxsJEJPOFE3NjA='}
        response = requests.request("GET", url, headers=headers, data=payload, verify=False)
        print("----Token response----", response.status_code)
        respObj = response.json()
        accesstoken = respObj.get("token", "")

        url = "https://delivery-connector-mana.internal.ericsson.com/utils_ms/api/dm_mana_data_flow"
        headers = {
            'x-access-token': accesstoken,
            'Content-Type': 'application/json'
        }
        payload = json.dumps(dataflowdpayload)

        print(payload)
        response = requests.request("POST", url, headers=headers, data=payload, verify=False)
        print("----API response----", response.text)

    except Exception as e:
        print(datetime.now(), " *** Caught exception: %s: %s" % (e.__class__, e))
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)


# For Testing -------------------
# dataflowdpayload = {
#     "CustomerUnit": "Regional Carriers",
#     "DataNature": "Report",
#     "Source": "EPP",
#     "DataSource": "EPP",
#     "DataDownload": "Yes",
#     "DataType": "PM",
#     "DataDownloadedTo": "Share Point",
#     "BotName": "BOT28689",
#     "Tool": "",
#     "SourceCountry": "USA",
#     "StoredLocation": "SharePoint",
#     "UpdateFrequency": "Daily",
#     "DailyVolume": 1,
#     "StoredCountry": "India",
#     "Remarks": ""
# }
# data_flow_details(dataflowdpayload, "220278481")
# For Testing -------------------






