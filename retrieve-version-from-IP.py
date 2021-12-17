import paramiko
import time
from getpass import getpass
import pandas as pa

import re

model_pattern = re.compile(r'Model Number (.+) : (.*)')
serial_no_pattern = re.compile(r'Processor board ID (\S+)')
uptime_pattern = re.compile(r'(.+) uptime is (.*)')

askedUsername=input("Enter your username : \n")
askedPassword=input("Enter your password : \n")

listOfIP="IP.txt"
readHostsFile=open(listOfIP,'r')
readHosts=readHostsFile.readlines()
readHostsFile.close()

def cisco_parse_version(host,username,password):
    try:
        print(f"\n{'#' * 55}\nConnecting to the Device {host}\n{'#' * 55} ")
        SESSION = paramiko.SSHClient()
        SESSION.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        SESSION.connect(host, port=22,
                        username=username,
                        password=password,
                        look_for_keys=False,
                        allow_agent=False)

        DEVICE_ACCESS = SESSION.invoke_shell()
        DEVICE_ACCESS.send(b'term length 0\n')
        DEVICE_ACCESS.send(b'show ver\n')
        time.sleep(1)
        output = (DEVICE_ACCESS.recv(95000).decode('ascii'))
        
        uptime_match = uptime_pattern.search(output)
        hostname=uptime_match.group(1)
        uptime=uptime_match.group(2)

        file1= open('output-shver'+hostname+'.txt', 'w')
        file1.write(output)
        file1.close()
        
        print('Host Name '.ljust(18)+': '+uptime_match.group(1))
        print('Device Uptime '.ljust(18)+': '+uptime_match.group(2))

        
        SESSION.close()

        return [hostname,uptime]
    
    except paramiko.ssh_exception.AuthenticationException:
        print("Authentication Failed")
    except AttributeError:
        print("Parsing Error, Please check the command")
    except:
        print("Can not connect to Device")
count = 0

file2=open('resultats.csv','w')
for eachHost in readHosts:
    count +=1
    #print (eachHost.strip())
    resultat=cisco_parse_version(eachHost.strip(),askedUsername,askedPassword)
    file2.writelines(";".join(resultat))
file2.close()
