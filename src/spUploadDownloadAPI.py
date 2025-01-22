import base64
import requests
import os
import traceback

#apiUrl = "https://mana-nic.internal.ericsson.com/apiserver/nic/dashboard/spUploadDownload"
apiUrl = "https://delivery-connector-mana.internal.ericsson.com/cdh_ms/api/sp_upload_download"

def getAutoBotToken():
    try:
        url = "https://delivery-connector-mana.internal.ericsson.com/user_ms/api/auth/token"

        headers = {
        'Authorization': 'Basic c3BfYXV0b3VzZXI6dXYxQDhRalpBTw=='
        }

        response = requests.request("GET", url, headers=headers, data={}, verify=False)
        if(response.status_code == 200):
            respobj = response.json()
            if(respobj["status"] == True):
                return respobj["token"]
    except Exception as e:
        print("Exception while getting the token",e)
    return ""

'''
def uploadFiles(woid, pid, wfname, sitename, filepath):
    try:
        print(woid, pid,wfname,sitename,filepath)
        url = "{}?WoId={}&ProjectId={}&WorkFlowName={}&SiteName={}".format(apiUrl,woid,pid,wfname,sitename)
        print(url)
        url = url.replace(" ","%20")
        with open(filepath, 'rb') as ip_file:
            encoded_string = base64.b64encode(ip_file.read()).decode('UTF-8')
        payload = {
            "Filename": os.path.basename(filepath),
            "File": encoded_string
        }
        response = requests.request("POST",url,json=payload,verify=False)
        print(response,response.text)
        return response.text
    except Exception as e:
        print("Exception while uploading files through API",e)
        traceback.print_exc()
    return "Error"


def downloadFiles(woid, pid, wfname, sitename, latest=False, timeSpan=0, specificFileName=""):
    try:
        print(woid, pid,wfname,sitename,latest,timeSpan,specificFileName)
        url = "{}?WoId={}&ProjectId={}&WorkFlowName={}&SiteName={}&latest={}&timeSpan={}".format(apiUrl,woid,pid,wfname,sitename,latest,timeSpan)
        if(specificFileName != ""):
            url = url + "&specificFileName=" + specificFileName
        print(url)
        url = url.replace(" ","%20")
        response = requests.request("GET",url,data={},verify=False)
        print(response)
        if(response.status_code == 200):
            respobj = response.json()
            if(respobj["status"] == "Success" and len(respobj["Content"]) >= 0):
                for entries in respobj["Content"]:
                    filename = entries["Filename"]
                    base64_file_str = entries["File"]
                    with open(filename, 'wb') as file_to_save:
                        decoded_data = base64.b64decode(base64_file_str)
                        file_to_save.write(decoded_data)
                return filename
    except Exception as e:
        print("Exception while downloading files through API",e)
        traceback.print_exc()
    return ""
'''

fetchApiUrl = "https://delivery-connector-mana.internal.ericsson.com/cdh_ms/api/sp_files_list"
def fetchFilesList(splink,timeZone="US/Central"):
    try:
        splink = splink.replace(" ", "%20")
        splink = splink.replace("&", "%26")
        timeZone = timeZone.replace("/","%2F")
        url = "{}?SPLink={}&timeZone={}".format(fetchApiUrl,splink,timeZone)
        headers = {
            "access-token": getAutoBotToken()
        }
        response = requests.request("GET",url,headers=headers,json={},verify=False)
        print(response,response.text)
        if(response.status_code == 200):
            respobj = response.json()
            if(respobj["status"] == "Success"):
                return respobj["Content"]
    except Exception as e:
        print("Exception while fetching file list through API",e)
    return []


def uploadFiles(woid, pid, wfname, sitename, filepath):
    try:
        print(woid, pid,wfname,sitename,filepath)
        url = "{}?WoId={}&ProjectId={}&WorkFlowName={}&SiteName={}".format(apiUrl,woid,pid,wfname,sitename)
        print(url)
        url = url.replace(" ","%20")
        with open(filepath, 'rb') as ip_file:
            encoded_string = base64.b64encode(ip_file.read()).decode('UTF-8')
        payload = {
            "Filename": os.path.basename(filepath),
            "File": encoded_string
        }
        headers = {
            "access-token": getAutoBotToken()
        }
        response = requests.request("POST",url,headers=headers,json=payload,verify=False)
        print(response,response.text)
        if(response.status_code == 200):
            respobj = response.json()
            if(respobj["status"] == "Success" and "https" in respobj["Content"]):
                return respobj["Content"]
    except Exception as e:
        print("Exception while uploading files through API",e)
        traceback.print_exc()
    return "Error"

def uploadFilesWithURL(splink, filepath):
    try:
        apiUrl="https://delivery-connector-mana.internal.ericsson.com/cdh_ms/api/sp_url_upload"
        url = "{}?SPLink={}".format(apiUrl,splink)
        print(url)
        url = url.replace(" ","%20")
        with open(filepath, 'rb') as ip_file:
            encoded_string = base64.b64encode(ip_file.read()).decode('UTF-8')
        payload = {
            "Filename": os.path.basename(filepath),
            "File": encoded_string
        }
        headers = {
            "access-token": getAutoBotToken()
        }
        response = requests.request("POST",url,headers=headers,json=payload,verify=False)
        print(response,response.text)
        if(response.status_code == 200):
            respobj = response.json()
            if(respobj["status"] == "Success" and "https" in respobj["Content"]):
                return respobj["Content"]
    except Exception as e:
        print("Exception while uploading files through API",e)
        traceback.print_exc()
    return "Error"


def downloadFilesWithURL(url =""):
    try:
        apiUrl="https://delivery-connector-mana.internal.ericsson.com/cdh_ms/api/sp_url_download"
        url = "{}?SPLink={}".format(apiUrl,url)
        url = url.replace(" ","%20")
        url = url.replace("&","%2F")
        headers = {
            "access-token": getAutoBotToken()
        }
        response = requests.request("POST",url,headers=headers, data={},verify=False)
        #print(response,response.text)
        if(response.status_code == 200):
            respobj = response.json()
            if(respobj["status"] == "Success" and len(respobj["Content"]) >= 0):
                for entries in respobj["Content"]:
                    filename = entries["Filename"]
                    base64_file_str = entries["File"]
                    with open(filename, 'wb') as file_to_save:
                        decoded_data = base64.b64decode(base64_file_str)
                        file_to_save.write(decoded_data)
                return filename
    except Exception as e:
        print("Exception while downloading files through API",e)
        traceback.print_exc()
    return ""

def downloadFiles(woid, pid, wfname, sitename, latest=False, timeSpan=0, specificFileName=""):
    try:
        print(woid, pid,wfname,sitename,latest,timeSpan,specificFileName)
        url = "{}?WoId={}&ProjectId={}&WorkFlowName={}&SiteName={}&latest={}&timeSpan={}".format(apiUrl,woid,pid,wfname,sitename,latest,timeSpan)
        if(specificFileName != ""):
            url = url + "&specificFileName=" + specificFileName
        headers = {
            "access-token": getAutoBotToken()
        }
        url = url.replace(" ","%20")
        response = requests.request("GET",url,headers=headers, data={},verify=False)
        if(response.status_code == 200):
            respobj = response.json()
            if(respobj["status"] == "Success" and len(respobj["Content"]) >= 0):
                for entries in respobj["Content"]:
                    filename = entries["Filename"]
                    base64_file_str = entries["File"]
                    with open(filename, 'wb') as file_to_save:
                        decoded_data = base64.b64decode(base64_file_str)
                        file_to_save.write(decoded_data)
                return filename
    except Exception as e:
        print("Exception while downloading files through API",e)
        traceback.print_exc()
    return ""

if __name__ == '__main__':
    #print(fetchFilesList("https://ericssonnam.sharepoint.com/MANA_DELIVERY_ATT/Shared%20Documents/ECI%20Scripts/1148/FASE%20Program/ARL01359"))
    #print(fetchFilesList("https://ericssonnam.sharepoint.com/sites/MANA_DELIVERY_ATT/sites/MANA_DELIVERY_TMO/Shared%20Documents/ECI%20Scripts/1140/FASE%20Program/4DE4398A", "Asia/Calcutta"))
    #print(downloadFilesWithURL("https://ericssonnam.sharepoint.com/MANA_DELIVERY_ATT/Shared%20Documents/ECI%20Scripts/1148/FASE%20Program/ARL01359"))
    #print(uploadFilesWithURL("https://ericssonnam.sharepoint.com/sites/MANA_DELIVERY_TMO/Shared%20Documents/ECI Scripts/1140/FASE Program/4DE4398A","temp.txt"))
    #print(os.getcwd())
    uploadFiles("testWOid", "638", "testWF", "testsite", "WO_Details.txt")
    #uploadFiles(woid,pid,WFName,sitename,'WO_' + str(woid),pre_json_file)


