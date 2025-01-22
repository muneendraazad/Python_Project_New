# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4


import datetime
import requests
import json
import pysftp
import zipfile
import re

# Mongo client
from pymongo import MongoClient


from urllib3.exceptions import InsecureRequestWarning

import time


# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

#################################
# Add to Bulk Pool and get FtpLink
#################################



def getAllTmoNodesUsingPSAM(site, UMTS=False, needAllNodes = False):
    NodeList = []
    try :
        allCombinations = ["L{}".format(site), "N{}".format(site), "M{}".format(site),#"U{}".format(site),
                               "L{}2".format(site), "N{}2".format(site), "M{}2".format(site),
                               "L{}3".format(site), "N{}3".format(site), "M{}3".format(site),
                               "L{}4".format(site), "N{}4".format(site), "M{}4".format(site),
                               "L{}5".format(site), "N{}5".format(site), "M{}5".format(site),
                               "L{}6".format(site), "N{}6".format(site), "M{}6".format(site),
                               "L{}7".format(site), "N{}7".format(site), "M{}7".format(site),
                               "L{}8".format(site), "N{}8".format(site), "M{}8".format(site)]

        if UMTS == True:
            allCombinations = allCombinations + ["U{}".format(site), "U{}2".format(site), "U{}3".format(site),"U{}4".format(site),"U{}5".format(site)]

        listOfResponses = getAllDetailsWithList(allCombinations, "T-Mobile", "eamitga")
        #print(json.dumps(listOfResponses, indent=4))

        for responseJson in listOfResponses["Nodes"]:
            node = responseJson.get("hostname","")
            status = responseJson.get("nodeStatus","")

            if (node == "" or (needAllNodes == False and status == "NotLive")):
                continue

            nodeName = responseJson["name"]
            radiotType = str(responseJson.get("ru_name", ""))
            NodeList.append(nodeName)

        return NodeList

    except Exception as e:
        print(e)
        return []


def getAllTmoUMTSNodesUsingPSAM(site):
    NodeList = []
    try :
        allCombinations = ["U{}".format(site), "U{}2".format(site), "U{}3".format(site),"U{}4".format(site),"U{}5".format(site)]

        listOfResponses = getAllDetailsWithList(allCombinations, "T-Mobile", "eamitga")
        #print(json.dumps(listOfResponses, indent=4))

        for responseJson in listOfResponses["Nodes"]:
            node = responseJson.get("hostname","")
            if (node == ""):
                continue

            nodeName = responseJson["name"]
            radiotType = str(responseJson.get("ru_name", ""))
            NodeList.append(nodeName)

        return NodeList

    except Exception as e:
        print(e)
        return []


def getGSMDetailsWithList(nodeName, customerName, signum):
    try:
        queryStr = {
            "nodelist": [],
            "customer": customerName,
            "include_mixmode" : "1"
        }

        for node in nodeName:
            queryStr["nodelist"].append(node)

        # set API passwd
        apiPasswd = "{api_password}"
        #print(json.dumps(queryStr, indent=4))

        #  is this user a registered user?
        url6="https://pes-pazmo-2.naops.exu.ericsson.se:9002/node"
        #url6="https://pes-pazmo-2.naops.exu.ericsson.se:9002/node"
        #print(url6)
        expectedResponse = requests.get(url6, auth=(signum, apiPasswd), data=json.dumps(queryStr), verify=False,timeout=10)

            #  got a success
        if (expectedResponse.status_code == 200) :
            responseJSON = json.loads(expectedResponse.content)
            #print (json.dumps(responseJSON, indent=4))
            return responseJSON

        #print (expectedResponse.content)
        return {}

    except Exception as e:
        print(e)
        return {}

def getAllDetailsWithList(nodeName, customerName, signum):
    try:
        queryStr = {
            "nodelist": [],
            "customer": customerName}

        for node in nodeName:
            queryStr["nodelist"].append(node)

        # set API passwd
        apiPasswd = "{api_password}"
        #print(queryStr)

        #  is this user a registered user?
        url6="https://pes-pazmo-2.naops.exu.ericsson.se:9002/node"
        expectedResponse = requests.post(url6, auth=(signum, apiPasswd), data=json.dumps(queryStr), verify=False,timeout=10)

            #  got a success
        if (expectedResponse.status_code == 200) :
            responseJSON = json.loads(expectedResponse.content)
            #print (json.dumps(responseJSON, indent=4))
            return responseJSON

        #print (expectedResponse.content)
        return {}

    except Exception as e:
        print(e)
        return {}

def getAllDetails(nodeName, customerName, signum):
    try:
        # FIXIT : run all nodes together but for now run one at a time
        queryStr = """
            {
            "nodelist": ["NODE_NAME"],
            "customer": "CUSTOMER_NAME"}"""

        queryStr = queryStr.replace("CUSTOMER_NAME", customerName)
        queryStr =queryStr.replace("NODE_NAME", nodeName)

        # set API passwd
        apiPasswd = "{api_password}"
        #print(queryStr)

        #  is this user a registered user?
        url6="https://pes-pazmo-2.naops.exu.ericsson.se:9002/node"
        expectedResponse = requests.post(url6, auth=(signum, apiPasswd), data=json.dumps(queryStr), verify=False,timeout=10)

        #  got a success
        if (expectedResponse.status_code == 200) :
            responseJSON = json.loads(expectedResponse.content)
            #print (json.dumps(responseJSON, indent=4))
            return responseJSON["Nodes"][0]

        return {}

    except Exception as e:
        print(e)
        return {}

def getENMname(nodeName, customerName, signum):
    allDetails = getAllDetailsWithList([nodeName], customerName, signum)
    return allDetails.get("enm", "")



def downloadZipFile(copyOfstatusOfRequest):

    statusOfRequest = copyOfstatusOfRequest
    time.sleep(3)
    statusOfRequest["NewZipFileName"] = ""
    try:
        # if the PSAM returned the link, download the file
        splitBySlash = statusOfRequest["PSAMftpLinkProvided"].split("/")
        # get the IP address of the FTP Link
        hostName = splitBySlash[2]
        fileName = splitBySlash[len(splitBySlash)-1]

        #remove what we don't need
        splitBySlash.pop(len(splitBySlash)-1)
        splitBySlash.pop(0)
        splitBySlash.pop(1)

        # this is our path
        pathName = "/".join(splitBySlash)
        pathName = pathName.replace("/pub/", "pub/")

        print ("Dowloading " + fileName + " from : " + pathName + " from SFTP " + hostName)

        url = "https://delivery-connector-mana.internal.ericsson.com/ccm_ms/api/services?path={}/{}".format(pathName,fileName)

        payload = {}
        headers = {
            'access-token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiZXN1amFnYSIsInJvbGUiOiJBZG1pbiIsImV4cCI6MTcwMzk4MDgwMH0.hAyJMixzbXvGNbactxzYhx1j3npWGWNVKrzDd4iW54o',
            'connection-key': 'gAAAAABlHmLQdhJVW5pi47CXPm6u13fnoVGDa-CDw64THPZsXDQtj_jsC_n8_cAEAxENz76IJ7tqC-_bfPraL9K__ZYAT2u6sqdOBUql3RwZJSjbKwXuiKrbPX08FKeniP-SNZoge5uS'
        }

        response = requests.request("GET", url, headers=headers, data=payload, verify = False)
        print(response)

        with open(fileName, "wb") as f:
            f.write(response.content)

        statusOfRequest["PSAMftpLinkDownloaded"] = "Yes"
        statusOfRequest["NewZipFileName"] = fileName

        #print ("Unzipping " + fileName)
        firstUnzip  = zipfile.ZipFile(fileName)
        zippedFileList = firstUnzip.namelist()
        nodeList =  statusOfRequest["PSAMnodeList"]
        statusOfRequest["PSAMnodeListFound"] = []
        statusOfRequest["PSAMnodeListNoContact"] = []

        for nodeName in nodeList:
            logFileFound = False
            failedLogFileFound = False

            for name in zippedFileList:
                if (re.search(r"^failedLog_[\d]+_" + nodeName + ".txt",name)):
                    # failed log file found for this node
                    failedLogFileFound = True
                    break
                elif (nodeName + ".log"  in name):
                    # log file found for this node
                    logFileFound = True

#            if (nodeName + ".log"  in zippedFileList):
            if (logFileFound == True and failedLogFileFound == False):
                # log file found for this node and no Failure files
                statusOfRequest["PSAMnodeListFound"].append(nodeName)
            else:
                statusOfRequest["PSAMnodeListNoContact"].append(nodeName)

        # close the zip file
        firstUnzip.close()
        #os.remove(fileName)

        statusOfRequest["DownloadedZipFileValid"] = "Yes"
        #statusOfRequest["Success"] = "Yes"

        return statusOfRequest

    except Exception as e:
        print(e)
        print("PSAM provided incorrect FTP file")
        return statusOfRequest


# To Download Json file
def downloadJsonZipFile(copyOfstatusOfRequest):
    statusOfRequest = copyOfstatusOfRequest
    time.sleep(3)
    statusOfRequest["NewZipFileName"] = ""
    try:
        # if the PSAM returned the link, download the file
        splitBySlash = statusOfRequest["PSAMftpLinkProvided"].split("/")
        # get the IP address of the FTP Link
        hostName = splitBySlash[2]
        fileName = splitBySlash[len(splitBySlash)-1]

        #remove what we don't need
        splitBySlash.pop(len(splitBySlash)-1)
        splitBySlash.pop(0)
        splitBySlash.pop(1)

        # this is our path
        pathName = "/".join(splitBySlash)
        pathName = pathName.replace("/pub/", "pub/")

        print ("Dowloading " + fileName + " from : " + pathName + " from SFTP " + hostName)

        url = "https://delivery-connector-mana.internal.ericsson.com/ccm_ms/api/services?path={}/{}".format(pathName,fileName)

        payload = {}
        headers = {
            'access-token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiZXN1amFnYSIsInJvbGUiOiJBZG1pbiIsImV4cCI6MTcwMzk4MDgwMH0.hAyJMixzbXvGNbactxzYhx1j3npWGWNVKrzDd4iW54o',
            'connection-key': 'gAAAAABlHmLQdhJVW5pi47CXPm6u13fnoVGDa-CDw64THPZsXDQtj_jsC_n8_cAEAxENz76IJ7tqC-_bfPraL9K__ZYAT2u6sqdOBUql3RwZJSjbKwXuiKrbPX08FKeniP-SNZoge5uS'
        }

        response = requests.request("GET", url, headers=headers, data=payload, verify = False)
        print(response)

        with open(fileName, "wb") as f:
            f.write(response.content)

        statusOfRequest["PSAMftpLinkDownloaded"] = "Yes"
        statusOfRequest["NewZipFileName"] = fileName

        #print ("Unzipping " + fileName)
        firstUnzip  = zipfile.ZipFile(fileName)
        zippedFileList = firstUnzip.namelist()
        nodeList =  statusOfRequest["PSAMnodeList"]
        statusOfRequest["PSAMnodeListFound"] = []
        statusOfRequest["PSAMnodeListNoContact"] = []

        for nodeName in nodeList:
            logFileFound = False
            failedLogFileFound = False

            for name in zippedFileList:
                if (re.search(r"^failedLog_[\d]+_" + nodeName + ".txt",name)):
                    # failed log file found for this node
                    failedLogFileFound = True
                    break
                elif (nodeName + ".log"  in name):
                    # log file found for this node
                    logFileFound = True

#            if (nodeName + ".log"  in zippedFileList):
            if (logFileFound == True and failedLogFileFound == False):
                # log file found for this node and no Failure files
                statusOfRequest["PSAMnodeListFound"].append(nodeName)
            else:
                statusOfRequest["PSAMnodeListNoContact"].append(nodeName)

        # close the zip file
        firstUnzip.close()
        #os.remove(fileName)

        statusOfRequest["DownloadedZipFileValid"] = "Yes"
        #statusOfRequest["Success"] = "Yes"

        return statusOfRequest

    except Exception as e:
        print(e)
        print("PSAM provided incorrect FTP file")
        return statusOfRequest


def getFtpLink(copyOfstatusOfRequest, allNodesCheck=False):
    print("getFtpLink called")

    statusOfRequest = copyOfstatusOfRequest

    # set API passwd
    apiPasswd = "neteng_api_key"

    # URLs for PSAM
    url1="https://pes-pazmo-2.naops.exu.ericsson.se:9002/status"
    url2="https://pes-pazmo-2.naops.exu.ericsson.se:9002/tasks"
    url3="https://pes-pazmo-2.naops.exu.ericsson.se:9002/task/"
    url4="https://pes-pazmo-2.naops.exu.ericsson.se:9002/queue/"
    url6="https://pes-pazmo-2.naops.exu.ericsson.se:9002/node"

    statusOfRequest["PSAMrequestStartTime"] =  datetime.datetime.now()

    # lets try PSAM now
    try:
        #  is this user a registered user?
        expectedResponse = requests.get(url1, auth=(statusOfRequest["SignumForPSAM"], apiPasswd), verify=False,timeout=10)
        print("expectedResponse",expectedResponse.text)
        print("expectedResponse",expectedResponse.status_code)
        #  got a success
        if (expectedResponse.status_code == 200) :
            #print (expectedResponse.text)
            responseJSON = json.loads(expectedResponse.text)
            print ("Allowed Customers : " + str(responseJSON["Allowed customers"]))
            #print ("Allowed UseCases : " + str(responseJSON["Allowed usecases"]))
            #print ("Current Number of Nodes Run in the last 24 hours : " + str(responseJSON["Current Number of Nodes Run in the last 24 hours"]))
            #print ("Max nodes Per 24 hours : " + str(responseJSON["Max nodes Per 24 hours"]))
            if (statusOfRequest["CustomerName"] not in responseJSON["Allowed customers"]):
                print ("You are not authorized to use PSAM for " + statusOfRequest["CustomerName"])
                return statusOfRequest
            statusOfRequest["PSAMaccountValid"] = "Yes"
        else :
            #print (expectedResponse.text)
            print ("You are not authorized to use PSAM for any customer")
            # Status failed - do not proceed furtehr
            return statusOfRequest

    except Exception as e:
        print (e)
        statusOfRequest["PSAMapiFailed"] = "Yes"
        return statusOfRequest

    # lets get a list of VALID nodes
    try:
        newNodeList = []
        discardNodeList = []
        currentNodeList = statusOfRequest["PSAMnodeList"]

        currentNodeList = list(dict.fromkeys(currentNodeList))

        queryStr = { "nodelist": [],
                "customer": statusOfRequest["CustomerName"]}

        for node in currentNodeList:
            queryStr["nodelist"].append(node)

        print(queryStr)

        #  is this user a registered user?
        expectedResponse = requests.post(url6, auth=(statusOfRequest["SignumForPSAM"], apiPasswd), data=json.dumps(queryStr), verify=False,timeout=10)

        print(expectedResponse)

        #  got a success
        if (expectedResponse.status_code == 200) :
            responseJSON = json.loads(expectedResponse.content)
            #print (json.dumps(responseJSON, indent=4))
            for nodeDetail in responseJSON["Nodes"]:
                node = nodeDetail.get("hostname","")
                if (node == ""):
                    node = nodeDetail.get("node_id", "")
                if (node == ""):
                    continue

                if(nodeDetail.get("enm","") != "unknown"): # this is a valid node
                    newNodeList.append(node)
                else:
                    discardNodeList.append(node)

        # lets override the list with only the valid node ids
        statusOfRequest["PSAMnodeList"] = newNodeList
        statusOfRequest["PSAMnodeListDiscarded"] = discardNodeList
        if (len(newNodeList) == 0):
            print ("No Valid Node Found")
            return statusOfRequest

    except Exception as e:
        print (e)
        print("PSAM ENM lookup failed")
        pass

    # user is legit, lets send the post to start a new query
    queueNum = ""
    queryStr = {"nodelist":[],
                "customer": statusOfRequest["CustomerName"],
                "email": statusOfRequest["EmailForPSAM"],
                "priority": statusOfRequest["Priority"],
                "usecase": statusOfRequest["UseCase"] }

    for node in newNodeList:
        queryStr["nodelist"].append(node)

    #print ("PSAM Query : " + queryStr)
    print ("PSAM Query : {}".format(json.dumps(queryStr,indent=4)))

    # this is for posting the query
    while(True):
        try :
            expectedResponse = requests.post(url2, auth=(statusOfRequest["SignumForPSAM"], apiPasswd), data=json.dumps(queryStr), headers={"Content-Type": "application/json"}, verify=False,timeout=20)
            #print (expectedResponse.status_code)
            if (expectedResponse.status_code == 200 or expectedResponse.status_code == 202):
                print (expectedResponse.text)
                queueLocationJson = json.loads(expectedResponse.text)
                location = queueLocationJson["Location"]
                #location ="/queue/134618"
                queueNum = location.split("/")[2]
                print ("Job Number : " + queueNum)
                if (queueNum == "" ):
                    print ("Could not create a request with PSAM")
                    return statusOfRequest

                # we are in queue
                statusOfRequest["PSAMrequestAccepted"] = "Yes"
                statusOfRequest["PSAMrequestInQueueTime"] =  datetime.datetime.now()
                break
            else:
                '''
                elif (expectedResponse.status_code == 500): # likely ran out of allowed nodes per day
                    print("Ran out of Nodes Quota, Wait 15 mins and then try again")
                    time.sleep(15*60)
                    continue
                '''
                if (expectedResponse.status_code == 400):
                    if("exceeds the allowable number" in expectedResponse.text):
                        print(expectedResponse.text)
                        print("Ran out of Nodes Quota, Wait 15 mins and then try again")
                        time.sleep(15*60)
                        continue
                    else:
                        print("PSAM Query Failed with Status Code {}".format(expectedResponse.status_code))
                        return statusOfRequest

                else:
                    print("PSAM Query Failed with Status Code {}".format(expectedResponse.status_code))
                    return statusOfRequest

        except Exception as e:
            print (e)
            statusOfRequest["PSAMapiFailed"] = "Yes"
            return statusOfRequest


    FtpLocation = ""
    while (True) :
        try :
            # get task status
            expectedResponse = requests.get(url4 + queueNum, auth=(statusOfRequest["SignumForPSAM"], apiPasswd), verify=False,timeout=10)
            if (expectedResponse.status_code == 200 or expectedResponse.status_code == 202):
                statusResponseJson = json.loads(expectedResponse.text)
                if ("Status" in expectedResponse.text) and ("FtpLocation" not in expectedResponse.text):
                    Status  = statusResponseJson["Status"]
                    if (Status == "Running"):
                        if(statusOfRequest.get("PSAMrequestInCollectionTime", "") == ""):
                            statusOfRequest["PSAMrequestInCollectionTime"] = datetime.datetime.now()
                        # wait 15 seconds
                        print ("{}, In Collection : Job : {}, Customer : {}".format(datetime.datetime.now(), queueNum,statusOfRequest["CustomerName"]))
                        time.sleep (60)
                    else :
                        # wait 15 seconds
                        print ("{}, In Queue : Job {}, Queue # : {}, Customer : {}".format(datetime.datetime.now(), queueNum, statusResponseJson["PendingTasks"], statusOfRequest["CustomerName"]))
                        time.sleep (60)
                elif("FtpLocation" in expectedResponse.text):
                    FtpLocation  = statusResponseJson["FtpLocation"]

                    if "JsonResult" in expectedResponse.text :
                        JsonLocation  = statusResponseJson["JsonResult"]
                        statusOfRequest["PSAMjsonLinkProvided"] = JsonLocation

                    if (FtpLocation != ""): # if so, return from here
                        print(FtpLocation)
                        statusOfRequest["PSAMrequestCompletionTime"] = datetime.datetime.now()
                        # wait 15 seconds
                        statusOfRequest["PSAMftpLinkProvided"] = FtpLocation
                        return statusOfRequest
                    else :
                        if(statusOfRequest.get("PSAMrequestInCollectionTime", "") == ""):
                            statusOfRequest["PSAMrequestInCollectionTime"] = datetime.datetime.now()
                        # wait 15 seconds
                        print ("{}, In Collection : Job : {}, Customer : {}".format(datetime.datetime.now(), queueNum,statusOfRequest["CustomerName"]))
                        time.sleep (60)
                else : # it failed
                    print ("{}, PSAM Failed : Job : {}, Customer : {}".format(datetime.datetime.now(), queueNum,statusOfRequest["CustomerName"]))
                    return statusOfRequest
        except Exception as e:
            print("PSAM did not respond")
            print (e)
            #statusOfRequest["PSAMapiFailed"] = "Yes"
            time.sleep(60)
            pass
            #return statusOfRequest

#res = (getGSMDetailsWithList(["1111"], "T-Mobile", "eamitga"))
#print(type(res), res)
#print(res['result'])
#print (getAllTmoNodesUsingPSAM("NY10531A"))
