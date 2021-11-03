import telnetlib
import time
import subprocess


print('MES2428P-SFP-ONU')

ip_address = b'172.17.255.105'
login = b'admin\n'
password = b'admin\n'
sw_glob = b'MES2428P-SFP-ONU#'

with open('6.1.txt', 'r') as f:
	test61 = f.read().splitlines()

#Login process:
telnet = telnetlib.Telnet(ip_address, 23, 5)
telnet.read_until(b'MES2428P-SFP-ONU login:')
telnet.write(login)
telnet.read_until(b'Password:')
telnet.write(password)
telnet.read_until(sw_glob)

clear_or_config = input('Очистить конфигурацию? Yes/No\n')
if clear_or_config.lower() == 'yes':
	telnet.write(b'configure t\n')
	telnet.read_until(b'(config)#')
	telnet.write(b'default interface range gig0/1-24\n')
	telnet.read_until(b'proceed?')
	telnet.write(b'Y\n')
	telnet.read_until(b'(config)#')
	telnet.write(b'exit\n')
	telnet.read_until(b'#')
	print('Ports config cleared')

try:
	print('Выберите тест:\n 1: 6.1_Trunk+IPTV\n 2: 6.2_Access+native vlan\n 3: 6.4_IPTV\n 4: ServiceCheck\n 5: Выход')
	test_number = int(input())
	if test_number == 1:
		for i in test61:
			ei = i.encode()
			telnet.write(ei)
			telnet.write(b'\n')
			telnet.read_until(b'ONU')
	elif test_number == 2:
		for i in test61:
			ei = i.encode()
			telnet.write(ei)
			telnet.write(b'\n')
			telnet.read_until(b'ONU')
		telnet.write(b'conf t\n')
		telnet.read_until(b'(config)#')
		telnet.write(b'default interface gig 0/5\n')	
		telnet.read_until(b'proceed?')
		telnet.write(b'Y\n')
		telnet.read_until(b'(config)#')
		telnet.write(b'exit\n')
		telnet.read_until(b'ONU')
	elif test_number == 3:
		telnet.write(b'conf t\n')
		telnet.read_until(b'(config)#')
		telnet.write(b'interface range gig0/1-24\n')
		telnet.read_until(b'#')
		telnet.write(b'loopback-detection enable\n')
		telnet.read_until(b'#')
		telnet.write(b'switchport mode access\n')
		telnet.read_until(b'#')
		telnet.write(b'switchport access vlan 99\n')
		telnet.read_until(b'#')
		telnet.write(b'exit\n')
		telnet.read_until(b'#')
		telnet.write(b'exit\n')
		telnet.read_until(b'#')
	elif test_number == 4:
		for i in test61:
			ei = i.encode()
			telnet.write(ei)
			telnet.write(b'\n')
			telnet.read_until(b'ONU')
		telnet.write(b'conf t\n')
		telnet.read_until(b'(config)#')
		telnet.write(b'default interface gig 0/5\n')	
		telnet.read_until(b'proceed?')
		telnet.write(b'Y\n')
		telnet.read_until(b'(config)#')
		telnet.write(b'default interface gig 0/6\n')	
		telnet.read_until(b'proceed?')
		telnet.write(b'Y\n')
		telnet.write(b'interface gig 0/6\n')
		telnet.read_until(b'#')
		telnet.write(b'switchport mode access\n')
		telnet.read_until(b'#')
		telnet.write(b'switchport access vlan 194\n')
		telnet.read_until(b'#')
		telnet.write(b'exit\n')
		telnet.read_until(b'ONU')
	elif test_number == 5:
		print('Bye')
	else:
		print('Такого значения в списке нет:')
except ValueError:
	print('Введенное значение не является числом')
finally:
	#telnet.write(b'clear line vty all\n')
	time.sleep(1)
	telnet.write(b'exit\n')
	time.sleep(1)
	telnet.close()
	print('Finish')

try:
	print('Выберите OLT для дальнейшей конфигурации:\n 1: Huawei MA5603T\n 2: Huawei MA5800X2\n 3: Eltex MA4000\n 4: ZTE C300\n 5: Выход\n')
	olt = int(input())
	if olt == 1:
		subprocess.call('python3 /home/pavel/Documents/Scripts/sfp_onu/OLT_Huawei_5603.py', executable='/bin/bash', shell=True)
	elif olt == 2:
		subprocess.call('python3 /home/pavel/Documents/Scripts/sfp_onu/OLT_Huawei_5800.py', executable='/bin/bash', shell=True)
	elif olt == 3:
		subprocess.call('python3 /home/pavel/Documents/Scripts/sfp_onu/OLT_MA4000.py', executable='/bin/bash', shell=True)
	elif olt == 4:
		subprocess.call('python3 /home/pavel/Documents/Scripts/sfp_onu/OLT_ZTE_C300.py', executable='/bin/bash', shell=True)
	elif olt == 5:
		print('Bye')
	else:
		print('Такого значения в списке нет:')
except ValueError:
	print('Введенное значение не является числом')

