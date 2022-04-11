import urllib3
from requests import Session
from zeep import Client
from zeep.transports import Transport
import ssl


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
    print(i['Name'] + " - " + i['DriverId'])

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
### Send Command
factory = client.type_factory('ns45')
### Choose command
operation=factory.DeviceCallMethodOperation(MethodName="Open", Id=DoorID)
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
        for y in client.service.GetAcsEmployeesByGroup(id):
            if y["FirstName"] is not None:
                if y["LastName"] is not None:
                    if y['Keys'] is not None:
                        if y['Keys']['AcsKeyInfo'][0]['KeyNumber'] is not None:
                            print(y["FirstName"] + " " + y["LastName"] + ":" + str(
                                y['Keys']['AcsKeyInfo'][0]['KeyNumber']))
                else:
                    if y['Keys'] is not None:
                        if y['Keys']['AcsKeyInfo'][0]['KeyNumber'] is not None:
                            print(y["FirstName"] + ":" + str(y['Keys']['AcsKeyInfo'][0]['KeyNumber']))
            else:
                if y["LastName"] is not None:
                    if y['Keys'] is not None:
                        if y['Keys']['AcsKeyInfo'][0]['KeyNumber'] is not None:
                            print(y["LastName"] + ":" + str(y['Keys']['AcsKeyInfo'][0]['KeyNumber']))
                else:
                    if y['Keys'] is not None:
                        if y['Keys']['AcsKeyInfo'][0]['KeyNumber'] is not None:
                            print("No Name" + ":" + str(y['Keys']['AcsKeyInfo'][0]['KeyNumber']))
for i in client.service.GetAcsEmployeeGroupsFull():
    if i["IsRemoved"] == False:
        print(i)
        if i['EmployeeGroups'] is not None:
            get_employ_key(i["ID"])
            for t in i['EmployeeGroups']["AcsEmployeeGroup"]:
                get_employ_key(t["ID"])
        else:
            get_employ_key(i["ID"])