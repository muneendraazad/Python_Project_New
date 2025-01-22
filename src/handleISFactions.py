# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4
import requests
import json
import datetime
import time
from pytz import timezone
from urllib3.exceptions import InsecureRequestWarning


# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

###############################
# Close and Update Dashboard
###############################
def closeAndUploadDashboard(statusOfRequest):
    try:
        currentTime = datetime.datetime.now()
        date_time = currentTime.strftime("%Y-%m-%d %H:%M:%S")
        payload = {"WorkOrderID" : statusOfRequest["WoId"],
           "NetworkElementID" : statusOfRequest["NodeList"],
           "p2_release" : True,
           "p2_closure" : True,
           "p2_priorityTime" : date_time,
           "p2_feOnSiteTime" : date_time,
           "p2_closureTime" : date_time,
           "p2_releaseTime" : date_time,
           "p2_responseTime" : 0,
           "link" : statusOfRequest["link"],
           "market" : statusOfRequest.get("Market", ""),
            "region" : statusOfRequest["Region"],
           "p2_status" : statusOfRequest.get("StatusCode", ""),
           "p2_responseTimeTime" : date_time,
           "p2_responseTimeFlag" : True}

        if (len(statusOfRequest["NodeList"]) > 1024):
            payload["NetworkElementID"] = statusOfRequest["NodeList"][1:1000]

        if (statusOfRequest.get("p2_workFlowName", "") != ""):
            payload["p2_workFlowName"] = statusOfRequest["p2_workFlowName"]

        url = "https://mana-nic.internal.ericsson.com/apiserver/nic/dashboard"

        headers = {
          'Authorization': 'd8dead46-b476-44e4-adf9-fc81215df578',
          'Content-Type': 'text/plain'
        }
        response=requests.post(url, headers=headers, data=json.dumps(payload),verify=False,timeout=30)
        if (response.status_code != 200 and response.status_code != 201):
            print(response.text)
        else:
            print(response.text)

    except:
        pass

###############################
# Update Dashboard
###############################
def updateDashboard(statusOfRequest):
    try:
        currentTime = datetime.datetime.now()
        date_time = currentTime.strftime("%Y-%m-%d %H:%M:%S")
        payload = {"WorkOrderID" : statusOfRequest["WoId"],
            "p2_status" : statusOfRequest.get("StatusCode",""),
            "p2_responseTime" : 0,
            "p2_priorityTime" : date_time,
            "p2_feOnSiteTime" : date_time,
            #"market" : statusOfRequest["Market"],
            "market" : statusOfRequest.get("Market", ""),
            "region" : statusOfRequest.get("Region", ""),
            #"region" : statusOfRequest["Region"],
            "NetworkElementID" : statusOfRequest["NodeList"],
            "p2_engineerAssignTime" : date_time,
            "link" : statusOfRequest["link"],
            "p2_engineerStartedTime" : date_time,
            "p2_engineerAssign" : True,
            "p2_engineerStarted" : True,
            "p2_responseTimeTime" : date_time,
            "p2_responseTimeFlag" : True
        }

        if (len(statusOfRequest["NodeList"]) > 1024):
            payload["NetworkElementID"] = statusOfRequest["NodeList"][1:1000]

        if (statusOfRequest.get("p2_workFlowName", "") != ""):
            payload["p2_workFlowName"] = statusOfRequest["p2_workFlowName"]

        url = "https://mana-nic.internal.ericsson.com/apiserver/nic/dashboard"

        headers = {
          'Authorization': 'd8dead46-b476-44e4-adf9-fc81215df578',
          'Content-Type': 'text/plain'
        }
        response=requests.post(url, headers=headers, data=json.dumps(payload),verify=False,timeout=30)
        if (response.status_code != 200 and response.status_code != 201):
            print(response.text)
        else:
            print(response.text)

    except Exception as e:
        print(e)

    return


#taskid to be provided if known only during STOP TASKNAME
def isfActionStaus(woId, taskName, whatToDo, failure=False, signum ="", taskid=""):

    # get Customer Name
    #customerName = customerMapper[project]

    # URLs for ISF
    isfAPI = {
        "start" : {
            "url" :  "https://integratedserviceflow.ericsson.net/apim/v2/rpaController/startAutomatedTask?date=DATE&taskName=TASKNAME&woID=WOID",
            "Subscription_key": fetchSubscriptionKey("v2")
        },
        "stop" : {
            "url" :  "https://integratedserviceflow.ericsson.net/apim/v2/rpaController/completeAutomatedTask?date=DATE&taskName=TASKNAME&woID=WOID&reason=Success",
            "Subscription_key": fetchSubscriptionKey("v2")
        },
        "close" : {
            "url" :  "https://integratedserviceflow.ericsson.net/apim/v1/externalInterface/closeWO",
            "token" :  "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJlYW1pdGdhIiwib3duZXJTaWdudW0iOiJlYW1pdGdhIiwiZXh0ZXJuYWxSZWZJRCI6MTY0LCJleHBpcmF0aW9uSW5ZZWFyIjozLCJleHAiOjE2NzExNjAxMTUsImlhdCI6MTU3NjQ2NTcxNX0.jAStNN5yt_ECRjJ_LbP313C7KY7Klc0CJtpSv6P3moA",
            "Subscription_key": fetchSubscriptionKey()
        },
    }

    # lets connect to ISF and make changes
    try:
        urlToUse = isfAPI[whatToDo]["url"]

        headers = {
                          'Content-Type':'application/json'
                  }

        params =  {}

        #curDate = datetime.datetime.now()+datetime.timedelta(hours=11, minutes=31)
        curDate = datetime.datetime.now(timezone('Asia/Kolkata'))+datetime.timedelta(minutes=30)
        headers["Apim-Subscription-Key"] = isfAPI[whatToDo]["Subscription_key"]


        if("close" in whatToDo):
            params['wOID'] =  woId
            if (failure == True):
                params['deliveryStatus'] =  "Failure"
                params['reason'] =  "Tool Issue"
            else:
                params['deliveryStatus'] =  "Success"
            params['externalSourceName'] =  "EMS"
            if signum == "":
                #params['lastModifiedBy'] =  "ERIRSIH"
                #params['lastModifiedBy'] = "eamitga"
                params['lastModifiedBy'] = "eprhald"
            else:
                params['lastModifiedBy'] = signum
        else:
            try:
                urlToUse = urlToUse.replace("TASKNAME",taskName)
                urlToUse = urlToUse.replace("WOID",woId)
                urlToUse = urlToUse.replace("DATE",curDate.strftime("%Y-%m-%d %H:%M:%S"))
                urlToUse = urlToUse.replace(" ","%20")
                print(urlToUse)
                print(headers)
                params = {}

            except Exception as e:
                print(e)
                print("Attempt to {} the task ID failed for {}".format(taskName,woId))
                return False


        payload = json.dumps(params)
        #print("URL : " + urlToUse)
        #print("Params  : " + str(params))
        #print("Headers : " + str(headers))

        if ("close" not in whatToDo):
            try:
                tempData = []
                tempData.append(woId)
                tempData.append(taskName)
                tempData.append(curDate.strftime("%Y-%m-%d %H:%M:%S"))
                with open(f"/home/isfuser1/autoBots/commonFunctions/{whatToDo}_Task_Entries.csv", "a") as filename:
                    filename.write(",".join(tempData)+"\n")
            except Exception as e:
                print("Exception while writing to the task entry files",e)
                pass

        attempt_cnt = 1
        while (True):
            if(attempt_cnt > 5):
                return False
            expectedResponse = requests.post(urlToUse, data=payload, headers=headers, verify=False,timeout=45)
            print(expectedResponse.text)
            responseJSON = json.loads(expectedResponse.text)
            print (json.dumps(responseJSON, indent=4))
            #  got a success
            if (expectedResponse.status_code == 200) :
                if ("close" in whatToDo):
                    if (responseJSON.get("isValidationFailed", False) == True): # Failed
                        if "Work Order is not assigned to signum" in expectedResponse.text:
                            try:
                                url = "https://integratedserviceflow.ericsson.net/apim/v1/externalInterface/getCompleteWorkOrderDetails?woID={}".format(woId)
                                res = requests.get(url,headers=headers, verify=False, timeout=45)
                                signum = res.json()["responseData"][0][0]["signumID"]
                                params['lastModifiedBy'] = signum
                                payload = json.dumps(params)
                                expectedResponse = requests.post(urlToUse, data=payload, headers=headers, verify=False,timeout=45)
                                responseJSON = json.loads(expectedResponse.text)
                                if (expectedResponse.status_code == 200) :
                                    if (responseJSON.get("isValidationFailed", False) == False):
                                        return True
                            except Exception as e:
                                print(e)
                                pass

                        try:
                            with open("/home/isfuser1/autoBots/commonFunctions/ISFFailLogs/close_errlogs.log", "a") as filename:
                                filename.write(payload)
                                filename.write(json.dumps(responseJSON, indent=4))
                        except Exception as e1:
                            print(e1)
                            pass

                        params['deliveryStatus'] =  "Failure"
                        params['reason'] =  "DeliveryFailure_Partial completed"
                        payload = json.dumps(params)
                        expectedResponse = requests.post(urlToUse, data=payload, headers=headers, verify=False,timeout=45)
                        responseJSON = json.loads(expectedResponse.text)
                        print ("Reattempt to Close with Failure as status")
                        if (responseJSON.get("isValidationFailed", False) == True):
                            return False
                elif("start" in whatToDo):
                    with open("/home/isfuser1/autoBots/commonFunctions/ISFFailLogs/start_errlogs.log", "a") as filename:
                        filename.write(payload)
                        filename.write(json.dumps(responseJSON, indent=4))
                else:
                    with open("/home/isfuser1/autoBots/commonFunctions/ISFFailLogs/stop_errlogs.log", "a") as filename:
                        filename.write(payload)
                        filename.write(json.dumps(responseJSON, indent=4))
                #print(woId + " : " + whatToDo + " OK")
                return True
            elif (expectedResponse.status_code == 408 or expectedResponse.status_code == 429 or expectedResponse.status_code == 423 or expectedResponse.status_code == 504):
                attempt_cnt = attempt_cnt + 1
                print("Recevied 429 response, attempting again after 30 seconds. Attempt Count: "+str(attempt_cnt))
                time.sleep(30)

                pass
            else : # for all other failures
                print (str(expectedResponse.status_code) + "  " +  expectedResponse.text)
                print(woId + " : " + whatToDo + " Failed ")
                return False

    except Exception as e:
        print (e)
        return False

def isfActionStaus_Old(woId, taskName, whatToDo, failure=False, signum =""):

    # get Customer Name
    #customerName = customerMapper[project]

    # URLs for ISF
    isfAPI = {
        "start" : {
            "url" :  "https://10.174.134.83:443/startNewTask",
            "token" :  "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJlYW1pdGdhIiwib3duZXJTaWdudW0iOiJlYW1pdGdhIiwiZXh0ZXJuYWxSZWZJRCI6MTY0LCJleHBpcmF0aW9uSW5ZZWFyIjozLCJleHAiOjE2NzExNjAxMTUsImlhdCI6MTU3NjQ2NTcxNX0.jAStNN5yt_ECRjJ_LbP313C7KY7Klc0CJtpSv6P3moA"
        },
        "stop" : {
            "url" :  "https://10.174.134.83:443/endTask",
            "token" :  "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJlYW1pdGdhIiwib3duZXJTaWdudW0iOiJlYW1pdGdhIiwiZXh0ZXJuYWxSZWZJRCI6MTY0LCJleHBpcmF0aW9uSW5ZZWFyIjozLCJleHAiOjE2NzExNjAxMTUsImlhdCI6MTU3NjQ2NTcxNX0.jAStNN5yt_ECRjJ_LbP313C7KY7Klc0CJtpSv6P3moA"
        },
        "close" : {
            "url" :  "https://integratedserviceflow.ericsson.net/apim/v1/externalInterface/closeWO",
            "token" :  "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJlYW1pdGdhIiwib3duZXJTaWdudW0iOiJlYW1pdGdhIiwiZXh0ZXJuYWxSZWZJRCI6MTY0LCJleHBpcmF0aW9uSW5ZZWFyIjozLCJleHAiOjE2NzExNjAxMTUsImlhdCI6MTU3NjQ2NTcxNX0.jAStNN5yt_ECRjJ_LbP313C7KY7Klc0CJtpSv6P3moA",
            "Subscription_key": fetchSubscriptionKey()
        },
    }

    # lets connect to ISF and make changes
    try:
        urlToUse = isfAPI[whatToDo]["url"]
        access_token = isfAPI[whatToDo]["token"]

        headers = {
                          'Content-Type':'application/json'
                  }

        params =  {}

        #curDate = datetime.datetime.now()+datetime.timedelta(hours=11, minutes=31)
        curDate = datetime.datetime.now(timezone('Asia/Kolkata'))+datetime.timedelta(minutes=30)

        if("close" in whatToDo):
            params['wOID'] =  woId
            headers["Apim-Subscription-Key"] = isfAPI[whatToDo]["Subscription_key"]
            if (failure == True):
                params['deliveryStatus'] =  "Failure"
                params['reason'] =  "DeliveryFailure_Partial completed"
            else:
                params['deliveryStatus'] =  "Success"
            params['externalSourceName'] =  "EMS"
            if signum == "":
                #params['lastModifiedBy'] =  "ERIRSIH"
                params['lastModifiedBy'] = "eprhald"
            else:
                params['lastModifiedBy'] = signum
        else:
            params['woID'] =  woId
            headers["X-Auth-Token"] = "Bearer {}".format(access_token)
            params['date'] =  curDate.strftime("%Y-%m-%d %H:%M:%S")
            params['taskName'] =  taskName

        payload = json.dumps(params)
        #print("URL : " + urlToUse)
        #print("Params  : " + str(params))
        #print("Headers : " + str(headers))

        attempt_cnt = 1
        while (True):
            if(attempt_cnt > 5):
                return False
            expectedResponse = requests.post(urlToUse, data=payload, headers=headers, verify=False,timeout=45)
            responseJSON = json.loads(expectedResponse.text)
            #print (json.dumps(responseJSON, indent=4))
            #  got a success
            if (expectedResponse.status_code == 200) :
                if (responseJSON.get("isValidationFailed", False) == True): # Failed
                    if ("close" in whatToDo):
                        if "Work Order is not assigned to signum" in expectedResponse.text:
                            try:
                                url = "https://integratedserviceflow.ericsson.net/apim/v1/externalInterface/getCompleteWorkOrderDetails?woID={}".format(woId)
                                res = requests.get(url,headers=headers, verify=False, timeout=45)
                                signum = res.json()["responseData"][0][0]["signumID"]
                                params['lastModifiedBy'] = signum
                                payload = json.dumps(params)
                                expectedResponse = requests.post(urlToUse, data=payload, headers=headers, verify=False,timeout=45)
                                responseJSON = json.loads(expectedResponse.text)
                                if (expectedResponse.status_code == 200) :
                                    if (responseJSON.get("isValidationFailed", False) == False):
                                        return True
                            except Exception as e1:
                                pass

                        params['deliveryStatus'] =  "Failure"
                        params['reason'] =  "DeliveryFailure_Partial completed"
                        payload = json.dumps(params)
                        expectedResponse = requests.post(urlToUse, data=payload, headers=headers, verify=False,timeout=45)
                        responseJSON = json.loads(expectedResponse.text)
                        print ("Reattempt to Close with Failure as status")
                        if (responseJSON.get("isValidationFailed", False) == True):
                            return False

                #print(woId + " : " + whatToDo + " OK")
                return True
            elif (expectedResponse.status_code == 408 or expectedResponse.status_code == 429 or expectedResponse.status_code == 423 or expectedResponse.status_code == 504):
                attempt_cnt = attempt_cnt + 1
                print("Recevied 429 response, attempting again after 30 seconds. Attempt Count: "+str(attempt_cnt))
                time.sleep(30)
                pass
            else : # for all other failures
                print (str(expectedResponse.status_code) + "  " +  expectedResponse.text)
                print(woId + " : " + whatToDo + " Failed ")
                return False

    except Exception as e:
        print (e)
        return False


def checkStatus(work_order_id):
    credentials = {
        "WO_Details_API_URL": "https://integratedserviceflow.ericsson.net/apim/v1/externalInterface/getCompleteWorkOrderDetails?woID={}",
        "Subscription_key": fetchSubscriptionKey()

    }
    # Call to WO_Details_API
    headers = {
        'Content-Type':'application/json',
        'Apim-Subscription-Key': credentials["Subscription_key"]
    }

    if (work_order_id == ""):
        return True

    try:
        res = requests.get(credentials["WO_Details_API_URL"].format(
                work_order_id), headers=headers, verify=False, timeout=45)
    except Exception as e:
        print(e)
        print(credentials["WO_Details_API_URL"].format(work_order_id),": URL Not Reachable")
        return False

    try:
        status = res.json()["responseData"][0][0]["status"]
        if (status == "CLOSED"):
            return True
        else:
            return False

    except Exception as e:
        print(e)
        print("Did not get status for WO " + work_order_id)
        return True

def updatePriorityAndComments(work_order_id, Signum, comment, priority=""):
    credentials = {
        "WO_Details_API_URL": "https://integratedserviceflow.ericsson.net/apim/v1/externalInterface/getCompleteWorkOrderDetails?woID={}",
        "Update_Priority_URL": "https://integratedserviceflow.ericsson.net/apim/v1/externalInterface/addCommentAndUpdatePriority",
    }
    credentials["Subscription_key"] = fetchSubscriptionKey()
    headers = {
        'Content-Type':'application/json',
        'Cache-Control': 'no-cache',
        'Apim-Subscription-Key': credentials["Subscription_key"]
    }

    payload = [{
        "comment": comment,
        "signumID": Signum,
        "wOID": work_order_id
    }]
    if priority != "":
        payload[0]["priority"] = priority
    try:
        #print (json.dumps(payload))
        res = requests.post(credentials["Update_Priority_URL"], data=json.dumps(payload), headers=headers, verify=False, timeout=45)
        if res.status_code == 200:
            return True
        else:
            print (res.text)
            print("response failed")
            return False
    except Exception as e:
        print(e)
        print("{} URL Not Reachable".format(credentials["Update_Priority_URL"]))
        return False

def updateOutputURL(woid, outputurl, outputName=""):
    url = "https://integratedserviceflow.ericsson.net/apim/v1/externalInterface/updateOutputFileLinkWO"
    headers = {
        'Content-Type':'application/json',
        "Apim-Subscription-Key": fetchSubscriptionKey()
    }
    if outputName == "":
        outputName = "output"
    req_body = [{
        "outputName" : outputName,
        "outputUrl" : outputurl
    }]
    payload = [{
        "woid": woid,
        "file": req_body,
        "lastModifiedBy": ""
    }]
    try:
        #print (json.dumps(payload))
        res = requests.post(url, data=json.dumps(payload), headers=headers, verify=False, timeout=45)
        #print("response: ",res.status_code)
        if res.status_code == 200:
            return True
        else:
            print("Failed to update the output url: ",woid)
            return False
    except Exception as e:
        print(e)
        print("Failed to update the output url: ",woid)
        return False

def createInstantWO(copyOfstatusOfRequest, assignedTo = True, assignSignum = ""):
    statusOfRequest = copyOfstatusOfRequest

    url = "https://integratedserviceflow.ericsson.net/apim/v1/externalInterface/createWorkOrderPlan"
    headers = {
        'Content-Type':'application/json',
        'Apim-Subscription-Key': fetchSubscriptionKey()
    }

    statusOfRequest["WoId"] = ""
    #currdatetime = datetime.datetime.now() + datetime.timedelta(hours=13)
    currdatetime = datetime.datetime.now(timezone('Asia/Kolkata'))+datetime.timedelta(minutes=30)


    req_body = {
        "projectID" : statusOfRequest["ProjectID"],
        "priority" : statusOfRequest["WoPriority"],
        "startDate" : currdatetime.strftime("%Y-%m-%d"),
        "startTime" : currdatetime.strftime("%H:%M:%S"),
        "wOName": statusOfRequest["WoName"],
        "lastModifiedBy" : statusOfRequest["DrSignum"],
        "listOfNode" : [{
            "nodeNames" : statusOfRequest["sitelist"],
            "nodeType" : "SITE"
            }],
        "comment" : statusOfRequest["comments"],
        "executionPlanName" : statusOfRequest["deliverablePlanName"],
        "externalSourceName" : "EMS"
    }

    try:
        if "inputUrl" in statusOfRequest and statusOfRequest["inputUrl"] != "":
            req_body["inputName"] = statusOfRequest.get("inputName", "Input")
            req_body["inputUrl"] = statusOfRequest["inputUrl"]
    except Exception as e:
        pass
    if(assignedTo == True):
        if(assignSignum == ""):
            req_body["assignedTo"] = statusOfRequest["DrSignum"]
        else:
            req_body["assignedTo"] = assignSignum

    print(json.dumps(req_body))
    attempt_cnt = 1
    while(True):
        try:
            if(attempt_cnt > 5):
                break
            response = requests.post(url, headers=headers, data=json.dumps(req_body),verify=False, timeout=60)
            print(response.text)
            if(response.status_code == 200): # succesful case
                if(len(response.json()["responseData"]["WorkOrderID"]) == 0):
                    #Error message received
                    err_msg = response.json()["responseData"]["msg"]
                    statusOfRequest["err_msg"] = err_msg
                    print("Wo creation failed: Response Code: {}, Error: {}".format(response.status_code,err_msg))
                    print(response.text)
                    break
                else:
                    woid = str(response.json()["responseData"]["WorkOrderID"][0]["woId"])
                    print("WO Created Successfully. WOID: "+woid)
                    statusOfRequest["WoId"] = woid
                    return statusOfRequest
            elif(response.status_code == 429):
                attempt_cnt = attempt_cnt + 1
                print("Recevied 429 response, attempting again after 5 seconds. Attempt Count: "+str(attempt_cnt))
                time.sleep(20)
            else:
                print(response.text)
                err_msg = response.json()["responseData"]["msg"]
                statusOfRequest["err_msg"] = err_msg
                print("Wo creation failed: Response Code: {}, Error: {}".format(response.status_code,err_msg))
                break
        except Exception as e:
            print("Exception while creating WO: ",e)
            statusOfRequest["err_msg"] = "Exception while creating WO"
            break
    return statusOfRequest

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

# def fetchSubscriptionKey(keyVersion="v1"):
#     APIS = {
#     "api_url1" : "http://138.85.32.228/api/v1/projectinfo?projectid=ISF_SUBKEY",
#     "api_url2" : "http://138.85.32.229/api/v1/projectinfo?projectid=ISF_SUBKEY",
#     "api_url3" : "http://138.85.32.164/api/v1/projectinfo?projectid=ISF_SUBKEY"
#     }
#     api_url = "https://mana-nic.internal.ericsson.com/apiserver/nic/dashboard/projectinfo?projectid=ISF_SUBKEY"
#     defaultKey = "6a471f4480054b539c73172dcffa247c"
#     for eachkeys in APIS.keys():
#         try:
#             api_url = APIS[eachkeys]
#             if keyVersion == "v2":
#                 api_url = api_url.replace("ISF_SUBKEY","ISF_SUBKEY_v2")
#                 defaultKey = "17365c45227d4538bf58ac34a1279f0e"
#             headers = {
#                 'Content-Type': 'application/json'
#             }
#             response = requests.request("GET", api_url, headers=headers, data={},timeout=5)
#             #print(response.text)
#             subkey = ""
#             if(response.status_code == 200): # succesful case
#                 subkey = str(response.json()["field1"])
#                 if(subkey == ""):
#                     subkey = str(response.json()["field2"])
#                 if(subkey == ""):
#                     continue
#                 else:
#                     return subkey
#             else:
#                 continue
#         except Exception as e:
#             continue
#     return defaultKey

# main Body
#isfA471f4480054b539c73172dcffa247c"ctionStaus(sys.argv[1], sys.argv[2])
copyOfstatusOfRequest = {
        "ProjectID" : "21644",
        "WoPriority" : "Normal",
        "WoName" : "TEST WO",
        "DrSignum" : "eprhald",
        "sitelist" : "TESTNODE",
        "comments" : "TEST COMMENTS",
        "deliverablePlanName" : "TMO Integration Common Flow"
        }

#createInstantWO(copyOfstatusOfRequest)#,assignedTo = True, assignSignum = "esujaga")
#work_order_id = "26936718"
#updatePriorityAndComments(work_order_id, "eamitga", "TEST COMMENT1")
#updatePriorityAndComments(work_order_id, "eamitga", "TEST COMMENT2", priority="High")
#updatePriorityAndComments(work_order_id, "eamitga", "TEST COMMENT3", priority="Normal")
#print(checkStatus(work_order_id))
#updateOutputURL(work_order_id,"https://ericsson.sharepoint.com/sites/NDO_MANA/Shared%20Documents/Project%20Logs")
#isfActionStaus(work_order_id, "Reporting", "stop")
#isfActionStaus(work_order_id, "", "close", failure=False)
#print(isfActionStaus("27273463", "Pre-Check", "stop"))
