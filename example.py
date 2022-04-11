import urllib3
from requests import Session
from zeep import Client
from zeep.transports import Transport
import ssl
import datetime

#####  disable ssl warning
urllib3.disable_warnings()
ssl._create_default_https_context = ssl._create_unverified_context

##### connect to rusguard server
from zeep.wsse.username import UsernameToken
session = Session()
session.verify =False
transport=Transport(session=session)

client = Client('https://YOUR_IP/LNetworkServer/LNetworkService.svc?wsdl',
                wsse=UsernameToken("LOGIN", "PASSWORD"), transport=transport)

##### Show All method and what they need
for service in client.wsdl.services.values():
    print("service:", service.name)
    for port in service.ports.values():
        operations =(port.binding._operations.values())
        # print(operations)

        for operation in operations:
            print("method :", operation.name)
            print("  input :", operation.input.signature())
            print("  output:", operation.output.signature())

##### Print Door name and door ID
for i in client.service.GetAcsAccessPointDrivers():
    print(f"{i['Name'] }:{i['DriverId']}")

##### Send command to door
### Door command: 
# Block
# Unblock
# ArmGuard
# DisarmGuard
# TurnOnSiren
# TurnOffSiren
# LongOpen
# Open
# Close
### Before send command you need generate Connection ID
conid= client.service.Connect()
### Choose command
factory = client.type_factory('ns45')
operation=factory.DeviceCallMethodOperation(MethodName="Open", Id=DoorID)
### Send Command
client.service.Process(operation=operation, connectionId=conid)
### After all you need Disconnect from service
client.service.Disconnect(connectionId=conid)

##### Logging
import logging.config
logging.config.dictConfig({
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(name)s: %(message)s'
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'zeep.transports': {
            'level': 'DEBUG',
            'propagate': True,
            'handlers': ['console'],
        },
    }
})

##### Get All key, First name, Last Name
def get_employ_key(id):
    if client.service.GetAcsEmployeesByGroup(id) != None:
        for employer in client.service.GetAcsEmployeesByGroup(id):
            firstname = employer["FirstName"]
            lastname = employer["LastName"]
            if employer['Keys'] is not None:
                for card_key in employer['Keys']['AcsKeyInfo']:
                    userkey = card_key['KeyNumber']
                    print(f"{firstname} {lastname}:{userkey}")
            else:
                print(f"{firstname} {lastname}")

for group in client.service.GetAcsEmployeeGroupsFull():
    if group["IsRemoved"] == False:
        if group['EmployeeGroups'] is not None:
            get_employ_key(group["ID"])
            for acsgroup in group['EmployeeGroups']["AcsEmployeeGroup"]:
                get_employ_key(acsgroup["ID"])
        else:
            get_employ_key(group["ID"])


### Get Event by date
#### Summary
#param name="fromMessageId" -  Return only those events whose ID is greater than the given value.
#param name="fromDateTime" - Starting from what date/time the events occurred. 
#param name="toDateTime" - Until what date/time the events occurred. 
#param name="msgTypes" - Message types. If null or an empty array, then the selection will be made for all types of events
#param name="msgSubTypes" - Message subtypes. If null or an empty array, then the selection will be made for all types of events
#param name="deviceIDs" - IDs of device drivers
#param name="subjectIDs"
#param name="subjectType"
#param name="pageNumber"
#param name="pageSize"
#param name="sortedColumn"
#param name="sortOrder"
###Example
door_ID="23303bb2-062e-477f-b15f-9d475cd33f8c"
events=client.service.GetEventsByDeviceIDs(0, datetime.datetime(2022, 6, 6, 00, 1), datetime.datetime(2022, 6, 6, 23, 59), msgTypes="Information", msgSubTypes="AccessPointEntryByKey", deviceIDs=door_ID)
