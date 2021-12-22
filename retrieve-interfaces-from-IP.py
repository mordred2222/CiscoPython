import paramiko
import time
import pandas as pa
import re
import os 

model_pattern = re.compile(r'Model Number (.+) : (.*)')
serial_no_pattern = re.compile(r'Processor board ID (\S+)')
uptime_pattern = re.compile(r'(.+) uptime is (.*)')
#interface_pattern=re.compile(r'Gi\s?(\d+)(/\d+)(/\d+)* (.+) (.+) (.+)(.*)')
Gi_interface_pattern=re.compile(r'Gi\s?(\d+)(/\d+)(/\d+)* (.+) (.+) (.+)(.*)')
Fa_interface_pattern=re.compile(r'Fa\s?(\d+)(/\d+)(/\d+)* (.+) (.+) (.+)(.*)')

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
        print('Device Uptime '.ljust(18)+': '+uptime)

        DEVICE_ACCESS.send(b'en\n')
        # if you need password to use enable mode, uncomment this line
        # DEVICE_ACCESS.send(b''+password+\n')   
        DEVICE_ACCESS.send(b'show int status\n')  
        
        time.sleep(1)
        shinterfaces = (DEVICE_ACCESS.recv(9500).decode('ascii'))
              
        
        file1= open('output-'+hostname+' sh interfaces.txt', 'w')
        file1.write(shinterfaces)
        file1.close()
        
        isExist = os.path.exists("./"+hostname)   
        if (isExist):
            pass
        else:
            os.makedirs("./"+hostname)
        
        file1= open('output-'+hostname+' sh interfaces.txt','r')
        file2= open("./"+hostname+'/interfaces.txt', 'w')
        
        
        Lines=file1.readlines()
        count=0
        for line in Lines:
            count +=1
            interface=line.strip()
            if interface!='': 
                if (Fa_interface_pattern.search(interface)):
                    newtxt=Fa_interface_pattern.search(interface)
                    file2.writelines('Fa'+newtxt.group(1)+newtxt.group(2)+'\n')
                if (Gi_interface_pattern.search(interface)):
                    newtxt=Gi_interface_pattern.search(interface)
                    file2.writelines('Gi'+newtxt.group(1)+newtxt.group(2)+'\n')
        file2.close()
        file1.close()
       
               
        SESSION.close()

        
        return hostname
    
    except paramiko.ssh_exception.AuthenticationException:
        print("Authentication Failed")
    except AttributeError:
        print("Parsing Error, Please check the command")
    except:
        print("Can not connect to Device - stop")

def cisco_get_interfaces_detail (host,username,password,hostname):
    print(f"\n{'#' * 55}\nConnecting to the Device {host}\n{'#' * 55} ")
    SESSION = paramiko.SSHClient()
    SESSION.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    SESSION.connect(host, port=22,
                    username=username,
                    password=password,
                    look_for_keys=False,
                    allow_agent=False)

    DEVICE_ACCESS = SESSION.invoke_shell()
    file1= open("./"+hostname+'/interfaces.txt', 'r')
    Lines=file1.readlines()
     
    count=0
    for line in Lines:
        count +=1
        interface=line.strip()
        sendcommand='sh ru int '+interface+'\n'
        print(sendcommand)
        
        DEVICE_ACCESS.send(b'en \n')
        DEVICE_ACCESS.send(sendcommand)
        time.sleep(1)
        output = (DEVICE_ACCESS.recv(1000).decode('ascii'))
        interfacetxt=interface.replace('/', '-')
        file2= open("./"+hostname+'/'+interfacetxt+'.txt', 'w')
        file2.write(output)
        file2.close()
        
    file1.close()
    
    SESSION.close()

    
count = 0
file2=open('resultats.csv','w')
for eachHost in readHosts:
    count +=1
    #print (eachHost.strip())
    resultat=cisco_parse_version(eachHost.strip(),askedUsername,askedPassword)
    print (resultat.strip())
    cisco_get_interfaces_detail(eachHost.strip(),askedUsername,askedPassword,resultat.strip())
    #if (resultat.count()>0):
    #file2.writelines(";".join(resultat))
file2.close()
