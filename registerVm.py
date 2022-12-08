###########################################################                                           
#                     _      __           _    ____  ___
#    ________  ____ _(_)____/ /____  ____| |  / /  |/  /
#   / ___/ _ \/ __ `/ / ___/ __/ _ \/ ___/ | / / /|_/ / 
#  / /  /  __/ /_/ / (__  ) /_/  __/ /   | |/ / /  / /  
# /_/   \___/\__, /_/____/\__/\___/_/    |___/_/  /_/   
#           /____/                                      
###########################################################

import base64
import requests
import json


# disable  urllib3 warnings
requests.packages.urllib3.disable_warnings(
    requests.packages.urllib3.exceptions.InsecureRequestWarning)


vCenterSrc              = {}
vCenterDst              = {}
vCenterSrc["vmInfo"]    = {}


def getCredentials(connInfo):

    print("[Please enter SOURCE credentials]")
    connInfo["src"]               = {}
    connInfo["src"]["vcenter"]    = input("Source vCenter FQDN/IP: ")
    connInfo["src"]["username"]   = input("Source vCenter username (ex: administrator): ")
    connInfo["src"]["domain"]     = input("Source vCenter SSO domain (ex: vsphere.local): ")
    connInfo["src"]["password"]   = input("Source vCenter password: ")

    print("")
    print("[Please enter DESTINATION credentials]")
    connInfo["dst"]               = {}
    connInfo["dst"]["vcenter"]    = input("Destination vCenter FQDN/IP: ")
    connInfo["dst"]["username"]   = input("Source vCenter username: ")
    connInfo["dst"]["domain"]     = input("Source vCenter SSO domain: ")
    connInfo["dst"]["password"]   = input("Source vCenter password: ")

    return connInfo


def createSession(connInfo, location):
    creds = connInfo[location]["username"] + "@" + connInfo[location]["domain"] + ":" + connInfo[location]["password"]
    credsBytes = creds.encode('ascii')
    credsBase64 = base64.b64encode(credsBytes)
    credentials = credsBase64.decode('ascii')

    url = "https://%s/api/session" % connInfo[location]["vcenter"]
    payload={}
    headers = {
        'Authorization': 'Basic %s' % credentials
    }
    response = requests.request("POST", url, headers=headers, data=payload, verify=False)
    sessionId = response.text.strip('"')

    return sessionId


    
def getVcenterInfo(sessionId, connInfo, url, location):
    url = "https://%s/api/%s" % (connInfo[location]["vcenter"], url)
    headers = {
        'vmware-api-session-id': sessionId
    }
    response = requests.request("GET", url, headers=headers, verify=False)
    # print(response.text)
    return response.text


def registerVms(sessionId, connInfo, location, datastore, cluster, folder, vmList):

    url = "https://%s/api/vcenter/vm?action=register" % connInfo[location]["vcenter"]
    headers = {
        'content-type': 'application/json',
        'vmware-api-session-id': sessionId
    }

    for vm in vmList:

        path = vm + "/" + vm + ".vmx"
        payload = {
            "datastore": datastore,
            "path": path,
            "name": vm,
            "placement": {
                "cluster": cluster,
                "folder": folder
            }
        }


        response = requests.request("POST", url, headers=headers, data=json.dumps(payload), verify=False)
        print("Response code: %s with response detail: %s" % (response, response.text))

    return False

def getDestInfo(item):
    print("Please enter the %s to use as destination:" % item) 
    for ds in vCenterDst[item]:
        print(" * %s" % ds["name"])
    destDs = input("> ")
    for ds in vCenterDst[item]:
        if ds["name"] == destDs:
            selection = ds[item]

    print("")

    return selection


def main():
    connInfo = {}
    connInfo = getCredentials(connInfo)

    sessionIdSrc = createSession(connInfo, "src")
    sessionIdDst = createSession(connInfo, "dst")
    vmList = []

    for i in ["datastore", "cluster", "vm", "folder"]:
        url = "vcenter/" + i
        vCenterSrc[i] = json.loads(getVcenterInfo(sessionIdSrc, connInfo, url, "src"))
        vCenterDst[i] = json.loads(getVcenterInfo(sessionIdDst, connInfo, url, "dst"))
        

    print("Please enter the datastore to use as source:")

    for ds in vCenterSrc["datastore"]:
        print(" * %s" % ds["name"])
    sourceDs = input("> ")
    print("")

    print("The following VMs will be registered with the target vCenter appliance:")
    for vm in vCenterSrc["vm"]:
        vmName = vm["vm"]
        aaa = vm["name"]
        url = "vcenter/vm/" + vmName
        vCenterSrc["vmInfo"][vmName] = json.loads(getVcenterInfo(sessionIdSrc, connInfo, url, "src"))
        # print("VM info for: %s (%s) is: %s" % (vmName, aaa, vCenterSrc["vmInfo"][vmName]))
        if sourceDs in str(vCenterSrc["vmInfo"][vmName]["disks"]):
            print("* %s" % vm["name"])
            vmList.append(vm["name"])
    print("")

    datastore   = getDestInfo("datastore")
    cluster     = getDestInfo("cluster")
    folder      = getDestInfo("folder")

    registerVms(sessionIdDst, connInfo, "dst", datastore, cluster, folder, vmList)


if __name__ == "__main__":
    main()


