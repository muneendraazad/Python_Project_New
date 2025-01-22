# uncompyle6 version 3.9.0
# Python bytecode version base 3.7.0 (3394)
# Decompiled from: Python 3.10.8 (tags/v3.10.8:aaaf517, Oct 11 2022, 16:50:30) [MSC v.1933 64 bit (AMD64)]
# Embedded file name: build\bdist.win-amd64\egg\USCC_KGET_Post\main.py
# Compiled at: 2022-12-02 11:25:57
# Size of source mod 2**32: 12510 bytes
import json, pysftp, os, requests
from pytz import timezone
import fnmatch, time
from zipfile import ZipFile
import shutil, warnings, sys, re, pymongo, os, sys, requests
from datetime import datetime
from urllib3.exceptions import InsecureRequestWarning
from functools import partial
import http.client
import pandas as pd
import zipfile
import openpyxl


from .getDataFromPSAM import getFtpLink
from . import BotDataFlowApi
from .spUploadDownloadAPI import uploadFiles,downloadFiles
from . import BotDataFlowApi
from .keyVaultForIsfLocal import get_secret
from .handleISFactions import updateDashboard,updateOutputURL

'''
from getDataFromPSAM import getFtpLink
from keyVaultForIsfLocal import get_secret
from spUploadDownloadAPI import uploadFiles, downloadFiles
from getDataFromPSAM import getFtpLink
import BotDataFlowApi
from handleISFactions import updateDashboard,updateOutputURL

'''


def getWO_details(woID):
    url = f"https://integratedserviceflow.ericsson.net/apim/v1/externalInterface/getCompleteWorkOrderDetails?woID={woID}"
   
    payload = {}
    files={}
    headers = {
      'Apim-Subscription-Key': 'd3c4aa76496f492ca53e6d8bd5b07bbc',
      'Content-Type': 'application/json'
    }
 
    response = requests.request("GET", url, headers=headers, data=payload, files=files)
    wo_details = response.json()
    for record in wo_details['responseData'][0]:
        pid = record['projectID']
        woid = record['wOID']
        signum = record['signumID']
        sitename = record['listOfNode'][0]['nodeNames']
        WFName = record['workFlowName']
        #jNumber = (record['wOName'].split("_J-")[1].split("_")[0]).strip()
    return woid,signum,sitename,WFName,pid

def getNodeName(site_id):
   
    try:
        
        sitenum = int(site_id[-6:])
        print('-----',sitenum)
        
    except:
        sitenum = site_id[0:6]
        print("SiteNum:- ",sitenum)
       
    XAPI_KEY= get_secret('gAAAAABl-BL5e-u2IUI5vL6rGYtxwPL7EfEM3m9IqmS6WUCXn8nvwt1GGo0L_L3d95yMXzI5fdgFRQPPyikuQ_L-ylNJz4F4a80nkrJDLw-p8AjLZvSU8Nc=')    
    print(XAPI_KEY['secret'])
    url = 'https://mana-nic.internal.ericsson.com/apiserver/nic/dashboard/fetchUsccData?Site_Number=' + str(sitenum)
    payload = {}
    
    headers = XAPI_KEY['secret']
    
        #'x-api-key': 'gAAAAABl-BL5e-u2IUI5vL6rGYtxwPL7EfEM3m9IqmS6WUCXn8nvwt1GGo0L_L3d95yMXzI5fdgFRQPPyikuQ_L-ylNJz4F4a80nkrJDLw-p8AjLZvSU8Nc='}
    #print(type(eval(headers)))
    response = requests.request('GET', url, headers=eval(headers), data=payload, verify=False).json()
    
    #print(type(response))
    #print(response)
   
    nodelist = []
    for i in response:
        print(i)
        for k in i:
            if k == 'sectors':
                for j in i[k]:
                    if j['Node_Name'] not in nodelist:
                        nodelist.append(j['Node_Name'])

    print('------')
    print('Nodelist in function' + str(nodelist))
    return (nodelist,sitenum)



def downloadJsonZipFile(INPATH,copyOfstatusOfRequest):
    statusOfRequest = copyOfstatusOfRequest
    statusOfRequest["NewZipFileName"] = ""
    try:
        # if the PSAM returned the link, download the file
        print("Json Link :", statusOfRequest["PSAMjsonLinkProvided"])
        INPATH_JSON=statusOfRequest["INPATH"]
        print("INPATH_JSON",INPATH_JSON)
        url = statusOfRequest["PSAMjsonLinkProvided"]
        #url = "ftp://138.85.123.205/pub/" + url.split("9090/")[1]
        base_url = "https://138.85.123.205/pub/"
        url_suffix = url.split("9090/")[1]
        url_components = [base_url, url_suffix]
        url = os.path.join(*url_components)
        splitBySlash = url.split("/")
        # print(splitBySlash)
        hostName = splitBySlash[2]
        pathName = splitBySlash[3] + "/" + splitBySlash[4] + "/PR3_" + statusOfRequest["UseCase"] + "/json"
        fileName = splitBySlash[-1]
        local_file_path = os.path.join(INPATH_JSON, fileName)

        print("Dowloading " + fileName + " from : " + pathName + " from SFTP " + hostName +"to::"+local_file_path)
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        SFTPkeys = get_secret("gAAAAABl8-v_Klblk2SonXrgHBTX9EwMhNIahJ1v8S8SPsxq8SJBQvLc1Z8dLDRAUDfMoLV18BhchEJHsFMQFmjMrK_kT_k-fJw-CmMLTfO8zV8TjYhzUHE=")
        #SFTPkeys = dcKeyVault.get_secret("gAAAAABl8-v_Klblk2SonXrgHBTX9EwMhNIahJ1v8S8SPsxq8SJBQvLc1Z8dLDRAUDfMoLV18BhchEJHsFMQFmjMrK_kT_k-fJw-CmMLTfO8zV8TjYhzUHE=")
        #print("SFTPkeys",SFTPkeys)
        dict= json.loads(list(SFTPkeys.values())[0])

        user=list(dict.values())[0]
        pass1=list(dict.values())[1]
        with pysftp.Connection(hostName, username=str(user), password=str(pass1), cnopts=cnopts) as sftp:
            with sftp.cd(pathName):  # temporarily chdir to public
                sftp.get(fileName,local_file_path)  # get a remote file

        print("File Downloaded: " + fileName)
        statusOfRequest["PSAMJsonLinkDownloaded"] = "Yes"
        statusOfRequest["NewZipFileName"] = fileName
        return statusOfRequest

    except Exception as e:
        print(e)
        print("PSAM provided incorrect FTP file")
        return statusOfRequest
        NewZipFileName = os.path.join(INPATH, fileName)


'''
def downloadJsonZipFile(INPATH,copyOfstatusOfRequest):
    statusOfRequest = copyOfstatusOfRequest
    statusOfRequest["NewZipFileName"] = ""
    try:
        # if the PSAM returned the link, download the file
        print("Json Link :", statusOfRequest["PSAMjsonLinkProvided"])
        INPATH_JSON=statusOfRequest["INPATH"]
        print("INPATH_JSON",INPATH_JSON)
        url = statusOfRequest["PSAMjsonLinkProvided"]
        #url = "ftp://138.85.123.205/pub/" + url.split("9090/")[1]
        base_url = "https://138.85.123.205/pub/"
        url_suffix = url.split("9090/")[1]
        url_components = [base_url, url_suffix]
        url = os.path.join(*url_components)
        splitBySlash = url.split("/")
        # print(splitBySlash)
        hostName = splitBySlash[2]
        pathName = splitBySlash[3] + "/" + splitBySlash[4] + "/PR3_" + statusOfRequest["UseCase"] + "/json"
        fileName = splitBySlash[-1]
        local_file_path = os.path.join(INPATH_JSON, fileName)

        print("Dowloading " + fileName + " from : " + pathName + " from SFTP " + hostName +"to::"+local_file_path)
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None

        with pysftp.Connection(hostName, username='isfuser1', password='HappyGreen2019', cnopts=cnopts) as sftp:
            with sftp.cd(pathName):  # temporarily chdir to public
                sftp.get(fileName,local_file_path)  # get a remote file

        print("File Downloaded: " + fileName)
        statusOfRequest["PSAMJsonLinkDownloaded"] = "Yes"
        statusOfRequest["NewZipFileName"] = fileName
        return statusOfRequest

    except Exception as e:
        print(e)
        print("PSAM provided incorrect FTP file")
        return statusOfRequest
        NewZipFileName = os.path.join(INPATH, fileName)
'''

def PSAM_JSON_Data(node_names,woid,Site_id,path):
    try:
        statusOfRequest={}
        statusOfRequest["PSAMaccountValid"]= "No"
        statusOfRequest["PSAMrequestStartTime"]= ""
        statusOfRequest["PSAMapiFailed"]= "No"
        statusOfRequest["PSAMrequestAccepted"]= "No"
        statusOfRequest["PSAMrequestInQueueTime"]= ""
        statusOfRequest["PSAMrequestInCollectionTime"]= ""
        statusOfRequest["PSAMrequestCompletionTime"]= ""
        statusOfRequest["PSAMftpLinkProvided"]= ""
        statusOfRequest["PSAMftpLinkDownloaded"]= "No"
        statusOfRequest["DownloadedZipFileValid"]= "No"
        statusOfRequest["PSAMjsonLinkProvided"]= ""
        statusOfRequest["SignumForPSAM"]="ehapanc"
        statusOfRequest["CustomerName"]="US Cellular"
        statusOfRequest["PSAMnodeList"]=node_names
        statusOfRequest["EmailForPSAM"]="hardikkumar.babulal.panchal@ericsson.com>"
        statusOfRequest["Priority"]="4"
        statusOfRequest["UseCase"] ="NetEng_Light_kget"
        statusOfRequest["NewZipFileName"] = ""
        statusOfRequest["INPATH"] = path
        print('###########',node_names)

        # Download the second file from the FTP link provided by PSAM
        statusOfRequest=downloadJsonZipFile(path,getFtpLink(statusOfRequest))
        
        jsonfile=statusOfRequest["NewZipFileName"]
        print("jsonfilejsonfile",jsonfile)
        
        
        
        directory_path = path
        os.chdir(directory_path)
        # print("Current working directory:", os.getcwd())

        zip_file_name = jsonfile

        #print("unzip_directory",unzip_directory)

        # Combine the directory and the original zip file name to get the full path to the zip file
        zip_file_path = os.path.join(directory_path, zip_file_name)
        print("zip_file_path:zip_file_path:",zip_file_path)

        # Extract the contents of the zip file to the specified directory
        try:
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(directory_path)
            print(f"Unzipped {zip_file_name} to {directory_path}")
            # After unzipping, rename the file to "jsonfile.json"
            original_file_name = os.path.splitext(zip_file_name)[0]  # Remove the .zip extension
            new_file_name =str(woid) + '_' + str(Site_id).strip() +'_Post.json'
            original_file_path = os.path.join(directory_path, original_file_name)
            new_file_path = os.path.join(directory_path, new_file_name)
            print('#######',new_file_name,new_file_path)
            print(new_file_name)

            os.rename(original_file_path, new_file_path)
            
            print(f"Renamed {original_file_name} to {new_file_name}")
            
            
            return new_file_name  
        
        except Exception as e:
            print(f"Error: {e}")  
    
    except Exception as e:
        print(f"An exception occurred: {e}")
        # Raise the exception again to propagate it to the calling function
        raise e

def parse_Pre_json_to_excel(INPATH,pre_json_file):
    
    # input_file_path = os.path.join(INPATH, "jsonfile.json")
    print(pre_json_file)
    input_file_path = os.path.join(INPATH, str(pre_json_file))
    output_file_path = os.path.join(INPATH, "JSON_PRE_PARSED.xlsx")
    data = pd.read_json(input_file_path).reset_index()

    ElementLevelStatus = data[data["index"].str.contains("ElementLevelStatus")].reset_index()["DATA"][0]
    AllNodes = list(data[data["index"].str.contains("AllNodes")].reset_index()["METADATA"][0].keys())
    DateTime = str(
        list(data[data["index"].str.contains("TimestampPerFieldGroup")].reset_index()["METADATA"][0]["NodeLevelStatus"]
             .keys())[0])
    
    final_list = []
    for node in AllNodes:
        
        MO_List = list(ElementLevelStatus["eNodeB"][node].keys())
        
        for MO in MO_List:
            param_List = list(ElementLevelStatus["eNodeB"][node][MO][DateTime].keys())
            for param in param_List:
                value = ElementLevelStatus["eNodeB"][node][MO][DateTime][param]["val"]
    
                # Remove "[1] = " from the beginning of the value
                value = value.replace("[1] = ", "")  #optional
                
                # Remove "[1] = " from the beginning of the value
                value = value.replace("i[1] = ", "")  #optional
    
                # Remove "i" from the "EAI" parameter value
                if param == 'emergencyAreaId' or param == 'bandListManual':
                    value = value.replace("i", "")
    
                # Replace column names as required
                if param == 'transmissionMode':
                    param = 'Transmission Mode'
                elif param == 'freqBand':
                    param = 'eUTRA operating band'
    
                # Change 'earfcndl' to 'earfcnDl'
                if param == 'earfcndl':
                    param = 'earfcnDl'
    
                # Change 'emergencyAreaId' to 'EAI'
                if param == 'emergencyAreaId':
                    param = 'EAI'
    
                # Change 'nRTAC' to 'tac'
                if param == 'nRTAC':
                    param = 'tac'
    
                # Change 'arfcnDL' to 'Arfcndl'
                if param == 'arfcnDL':
                    param = 'Arfcndl'
    
                # Change 'bandListManual' to 'NR_freqband'
                if param == 'bandListManual':
                    param = 'NR_freqband'
    
                # Change 'cellRange' to 'Cellrange'
                if param == 'cellRange':
                    param = 'Cellrange'
    
                # Change 'configuredMaxTxPower' to 'configureMaxTxPower'
                if param == 'configuredMaxTxPower':
                    param = 'configureMaxTxPower'
    
                # Change 'nRPCI' to 'PCI'
                if param == 'nRPCI':
                    param = 'PCI'
                    
                    
                # Remove unwanted substrings from the 'Parameter Value' column
                value = value.replace('[1] = ', '').replace('i[4] = ', '').replace(' -1 -1 -1', '').replace('[4] = ', '')
    
                final_list.append(node + "|" + DateTime + "|" + MO + "|" + param + "|" + value)
                
    df = pd.DataFrame({'Final': final_list})
    df[['Node ID', 'Date & Time', "MO Name", "Parameter Name", "Parameter Value"]] = df['Final'].str.split('|',
                                                                                                              expand=True)
    
    # Remove "EUtranCellFDD=" and "NRCellDU=" from MO Name
    df['MO Name'] = df['MO Name'].str.replace('EUtranCellFDD=', '').str.replace('EUtranCellTDD=', '').str.replace('NRCellDU=', '')
    
    # Remove rows where MO Name contains the specified substring
    df = df[~df['MO Name'].str.contains('ENodeBFunction=1,EUtraNetwork=1,ExternalENodeBFunction=')]
    
    df = df.filter(items=['Node ID', 'MO Name', "Parameter Name", "Parameter Value"])  # Remove 'Date & Time' column
    
    # Create a list of parameters to be removed
    parameters_to_remove = [
        # 'pZeroNominalPusch',
        'additionalFreqBandList',
        'mfbiFreqBandIndPrio',
        'prioAdditionalFreqBandList',
        'crsGain',
        # 'cellId',
        # 'pZeroNominalPucch',
        'maximumTransmissionPower',
        # 'operationalState',
        # 'administrativeState',
        'sectorEquipmentFunctionRef',
        # 'bandList',
        'configuredEpsTAC'
    ]
    
    # Remove rows with the specified parameters
    df_filtered = df[~df['Parameter Name'].isin(parameters_to_remove)]
    df_filtered.drop_duplicates().to_excel(output_file_path, sheet_name='parsed_json', index=False,engine='openpyxl')
    return output_file_path

def parse_Post_json_to_excel(INPATH,post_json_file):
    
    # input_file_path = os.path.join(INPATH, "jsonfile.json")
    print(post_json_file)
    input_file_path = os.path.join(INPATH, str(post_json_file))
    output_file_path = os.path.join(INPATH, "JSON_POST_PARSED.xlsx")
    data = pd.read_json(input_file_path).reset_index()

    ElementLevelStatus = data[data["index"].str.contains("ElementLevelStatus")].reset_index()["DATA"][0]
    AllNodes = list(data[data["index"].str.contains("AllNodes")].reset_index()["METADATA"][0].keys())
    DateTime = str(
        list(data[data["index"].str.contains("TimestampPerFieldGroup")].reset_index()["METADATA"][0]["NodeLevelStatus"]
             .keys())[0])
    
    final_list = []
    for node in AllNodes:
        MO_List = list(ElementLevelStatus["eNodeB"][node].keys())
        for MO in MO_List:
            param_List = list(ElementLevelStatus["eNodeB"][node][MO][DateTime].keys())
            for param in param_List:
                value = ElementLevelStatus["eNodeB"][node][MO][DateTime][param]["val"]
    
                # Remove "[1] = " from the beginning of the value
                value = value.replace("[1] = ", "")
                
                # Remove "[1] = " from the beginning of the value
                value = value.replace("i[1] = ", "")
    
                # Remove "i" from the "EAI" parameter value
                if param == 'emergencyAreaId' or param == 'bandListManual':
                    value = value.replace("i", "")
    
                # Replace column names as required
                if param == 'transmissionMode':
                    param = 'Transmission Mode'
                elif param == 'freqBand':
                    param = 'eUTRA operating band'
    
                # Change 'earfcndl' to 'earfcnDl'
                if param == 'earfcndl':
                    param = 'earfcnDl'
    
                # Change 'emergencyAreaId' to 'EAI'
                if param == 'emergencyAreaId':
                    param = 'EAI'
    
                # Change 'nRTAC' to 'tac'
                if param == 'nRTAC':
                    param = 'tac'
    
                # Change 'arfcnDL' to 'Arfcndl'
                if param == 'arfcnDL':
                    param = 'Arfcndl'
    
                # Change 'bandListManual' to 'NR_freqband'
                if param == 'bandListManual':
                    param = 'NR_freqband'
    
                # Change 'cellRange' to 'Cellrange'
                if param == 'cellRange':
                    param = 'Cellrange'
    
                # Change 'configuredMaxTxPower' to 'configureMaxTxPower'
                if param == 'configuredMaxTxPower':
                    param = 'configureMaxTxPower'
    
                # Change 'nRPCI' to 'PCI'
                if param == 'nRPCI':
                    param = 'PCI'
                    
                    
                # Remove unwanted substrings from the 'Parameter Value' column
                value = value.replace('[1] = ', '').replace('i[4] = ', '').replace(' -1 -1 -1', '').replace('[4] = ', '')
    
                final_list.append(node + "|" + DateTime + "|" + MO + "|" + param + "|" + value)
                
    df = pd.DataFrame({'Final': final_list})
    df[['Node ID', 'Date & Time', "MO Name", "Parameter Name", "Parameter Value"]] = df['Final'].str.split('|',
                                                                                                              expand=True)
    
    # Remove "EUtranCellFDD=" and "NRCellDU=" from MO Name
    df['MO Name'] = df['MO Name'].str.replace('EUtranCellFDD=', '').str.replace('EUtranCellTDD=', '').str.replace('NRCellDU=', '')
    
    # Remove rows where MO Name contains the specified substring
    df = df[~df['MO Name'].str.contains('ENodeBFunction=1,EUtraNetwork=1,ExternalENodeBFunction=')]
    
    df = df.filter(items=['Node ID', 'MO Name', "Parameter Name", "Parameter Value"])  # Remove 'Date & Time' column
    
    # Create a list of parameters to be removed
    parameters_to_remove = [
        # 'pZeroNominalPusch',
        'additionalFreqBandList',
        'mfbiFreqBandIndPrio',
        'prioAdditionalFreqBandList',
        'crsGain',
        # 'cellId',
        # 'pZeroNominalPucch',
        'maximumTransmissionPower',
        # 'operationalState',
        # 'administrativeState',
        'sectorEquipmentFunctionRef',
        # 'bandList',
        'configuredEpsTAC'
    ]
    
    # Remove rows with the specified parameters
    df_filtered = df[~df['Parameter Name'].isin(parameters_to_remove)]
    df_filtered.drop_duplicates().to_excel(output_file_path, sheet_name='parsed_json', index=False,engine='openpyxl')
    print("POST JSON FILE PARSING COMPLETED")
    return output_file_path

def Comparison_Report(pre,post):
    PRE_file_path = pre
    POST_file_Path = post
    output_file_path = os.path.join("Pre_Post_Kget_Comparsion_Report.csv")

    # Load the two Excel sheets into DataFrames
    df_pre= pd.read_excel(PRE_file_path, dtype={'Node ID': str})
    df_post = pd.read_excel(POST_file_Path, dtype={'Node ID': str})
   
    post=df_post.drop_duplicates()
    pre=df_pre.drop_duplicates()
    # Merge the two DataFrames based on multiple columns: "Node ID," "MO Name," and "Parameter Name"
    merged_df = pd.merge(pre, post, on=["Node ID", "MO Name", "Parameter Name"], suffixes=('_PRE', '_POST'))
   

    # Create a new column "Result" and mark rows as "Matched" where "Parameter Name" are matched
    # and "Parameter Value" matches (while ignoring case); mark other rows as "Not matched"
    merged_df['Result'] = 'Not matched'
   

    # Specify the names of the two columns you want to compare
    pre_param = "Parameter Value_PRE"
    post_param = "Parameter Value_POST"
  
    # Create a new column with the comparison results
    mask = merged_df[pre_param] == merged_df[post_param]

    # Print the DataFrame to see the comparison results

    merged_df.loc[mask,'Result'] = 'Matched'
    merged_df.to_excel('merge.xlsx')
   
    
    # # Create a Pandas Excel writer using XlsxWriter as the engine for Code 2
    merged_df.to_csv(output_file_path, index=False)
    return output_file_path

def doProcess(INPATH=".", OUTPATH=".",wo_details="."):
#def doProcess(INPATH=".", OUTPATH="."):
   # run on server
    try:
        
        woid = str(wo_details['WONO'])
        sitename=str(wo_details['NODES'])

        try:
             WFName=str(wo_details['WORKFLOWNAME'])
        except KeyError:
                WFName='USCC_KGET'
        #WFName=str(wo_details['WORKFLOWNAME'])
        pid=str(wo_details['PROJECTID'])
        print("Work Order id is=",woid," sitename:", sitename, " Workflowname ", WFName)
        #woid,signum,sitename,WFName,pid=getWO_details(woid)
        
        #woid,signum,sitename,WFName,pid=getWO_details(222604134)
       
        print(woid,sitename,WFName,pid)
        WONodeName,Site_id= getNodeName(sitename)
        if len(WONodeName)==0:
            print('No Node found,exiting from the program')
            # time.sleep(50)
            sys.exit() 
            
        else:    
  
            print('===========')
            print('Nodelist->')
            print(WONodeName)
            print('===========')
            # json file of logs
            post_json_file= PSAM_JSON_Data(WONodeName,woid,sitename,INPATH)
            print(post_json_file)
         
           
             # json file upload on sharepoint
            filepath = uploadFiles(woid,pid,WFName,sitename,post_json_file)
            #filepath = uploadFiles('638', 'USCC_KGET', 'WO_' + str(woid), post_json_file )
            print('File Uploaded on Sharepoint')
           
           
            # making json file name which need to download from the sharepoint
            pre_json_file=str(woid) + '_' + str(sitename).strip() +'_Pre.json'
             # post_json_file=str(woid) + '_' + str(site_id).strip() +'_Post.json'
           
             # Download PRE and POST json file from sharepoint
            Pre_filepath= downloadFiles(woid,pid,WFName,sitename, pre_json_file)
            #Pre_filepath = downloadFiles('638', 'USCC_KGET', 'WO_' + str(woid),False,1,pre_json_file,False)
            print('pre file downloaded for comapre----------------')
             # Post_filepath = downloadFiles('638', 'USCC_KGET', 'WO_' + str(woid),False,0,post_json_file,False)
           
          
            if Pre_filepath=="" :
                 print("Fail to download")
            else:
                 print('Pre_Json and Post_json File is downloaded from Sharepoint')
            
            # Parsing PRE and POST json to excel
            parse_pre=parse_Pre_json_to_excel(INPATH, pre_json_file)
            parse_post=parse_Post_json_to_excel(INPATH, post_json_file)
            # print(parse_post,parse_pre)
            print('PARSED FILES SUCCESSFULL')
             #Creation of Comparison report of PRE and POST --> Pre_Post_Kget_Comparsion_Report.csv
            compare_file=Comparison_Report(parse_pre, parse_post)
            print('compare file',compare_file)
            #compare_file_name='WO_' + str(woid),'Pre_Post_Kget_Comparsion_Report.csv'
            filepath = uploadFiles(woid,pid,WFName,sitename, compare_file)
            uploadFiles("", "638", "TransactionalFolders", WFName,compare_file)
            #filepath = uploadFiles('638', 'USCC_KGET', 'WO_' + str(woid),os.path.join(INPATH,'Pre_Post_Kget_Comparsion_Report.csv') )
            print('File Uploaded on Sharepoint ', filepath)
            statusOfRequest= {}
            statusOfRequest["WoId"] = woid
            statusOfRequest["CustomerName"]="RC NDO"
            statusOfRequest["ISFTaskName"]=WFName
            statusOfRequest["StatusCode"] = "Kget compare"
            statusOfRequest["Market"] = "National"
            statusOfRequest["Region"] = "National"
            statusOfRequest["NodeList"] = sitename

            statusOfRequest["link"]= filepath
            
            updateDashboard(statusOfRequest)
            updateDashboard(statusOfRequest)
            print(statusOfRequest)
            print(" Dashboard updated")
            updateOutputURL(woid, filepath, outputName="kget compare")
            
            print('compare file uploaded successfully')
            #Delete '.json','.xlsx', '.zip' files from current  working directory
            files = os.listdir(INPATH)
            file_extensions_to_delete = ['.json','.xlsx', '.zip','.csv']
            for file_name in files:
                file_extension = os.path.splitext(file_name)[-1].lower()
                if file_extension in file_extensions_to_delete:
                    file_path = os.path.join(INPATH, file_name)
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}") 
   
    
            dataflowdpayload = {
                "CustomerUnit": "USCC",
                "DataNature": "Report",
                "Source": "ENM",
                "DataSource": "ENM",
                "DataDownload": "Yes",
                "DataType": "CM",
                "DataDownloadedTo": "SharePoint",
                "BotName": "213734",
                "Tool": "PSAM",
                "SourceCountry": "USA",
                "StoredLocation": "SharePoint",
                "UpdateFrequency": "Daily",
                "DailyVolume": 1,
                "StoredCountry": "USA",
                "Remarks": "Pre_PostKget_Comparison"
            }
            BotDataFlowApi.data_flow_details(dataflowdpayload, woid)
    
    
    except Exception as e:
        print(datetime.now(),"Exception occured- Error ", e)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)    
        print('Not able to read wo detail, Exiting the program')
        time.sleep(10)
        sys.exit()



#if __name__ == '__main__':
   
   #doProcess(INPATH='.',OUTPATH='.',wo_details='.')
   #INPATH=OUTPATH=os.getcwd()
   #doProcess(INPATH,OUTPATH) 
