import telnetlib
import time
import re

print('OLT MMT-MA5603T-1')

ip_address = b'172.17.87.229'
login = b'anton_act\n'
password = b'mainstreet1\n'
glob = b'MMT-MA5603T-1>'
enab = b'MMT-MA5603T-1#'
conf = b'MMT-MA5603T-1(config)#'
int_4 = b'MMT-MA5603T-1(config-if-gpon-0/4)#'
btv = b'MMT-MA5603T-1(config-btv)#'
mcast = b'MMT-MA5603T-1(config-mvlan99)#'
quit = b'quit\n'

#Login process:
telnet = telnetlib.Telnet(ip_address, 23, 5)
telnet.read_until(b'User name:')
telnet.write(login)
telnet.read_until(b'User password:')
telnet.write(password)
telnet.read_until(glob)
telnet.write(b'enable\n')
telnet.read_until(enab)
telnet.write(b'config\n')
telnet.read_until(conf)
telnet.write(b'undo smart\n')
telnet.read_until(conf)
telnet.write(b'undo interactive\n')
telnet.read_until(conf)

#Clear Config
clear_or_config = input('Очистить конфигурацию ONT ID 0? Yes/No\n')
if clear_or_config.lower() == 'yes':
	telnet.write(b'undo service-port port 0/4/10 ont 0\n')
	telnet.read_until(conf)
	telnet.write(b'interface gpon 0/4\n')
	telnet.read_until(int_4)
	telnet.write(b'ont delete 10 0\n')
	telnet.read_until(int_4)
	telnet.write(quit)
	telnet.read_until(conf)
	time.sleep(5)
	print('ONT ID 0 cleared')


#Autofind
telnet.write(b'interface gpon 0/4\n')
telnet.read_until(int_4)
telnet.write(b'display ont autofind 10\n')
telnet.write(b' ')
autofind = telnet.read_until(int_4).decode().splitlines()
ont_list = []
for i in autofind:
	if 'Failure: The automatically found ONTs do not exist' in i:
		print('Ont not connected to OLT')
		break
	else:
		if 'SN' in i:
			result = re.search('(SN\s{14}):(\s\w{16})', i)
			ont_list.append(result.group(2))
			continue
		else:
			continue

telnet.write(quit)
telnet.read_until(conf)

#Copy ONT SN	
try:
	print('Список серийных номер в autofind:', ont_list)
	ont_pos = int(input('Выберите нужный от 0 до {} или любой символ для выхода: '.format(len(ont_list) - 1)))
	while ont_pos >= len(ont_list):
		print('Некорректный выбор')
		ont_pos = int(input('Выберите нужный от 0 до {} или любой символ для выхода:'.format(len(ont_list) - 1)))
	else:
		ont_sn = ont_list[ont_pos]
		print('Выбран серийный номер: ', ont_sn)
except ValueError:
	telnet.close()
	print('Введенное значение не является числом. Выход.')
	
#ONT Add and Configuration
try:
	print('Выберите тест:\n 1: 6.1/6.3_Trunk+IPTV\n 2: 6.2_Access+native vlan\n 3: 6.3.1_QinQ+native\n 4: Complex\n 5: DBA\n 6: Выход')
	test_number = int(input())
	
	#Add ONT:
	telnet.write(b'interface gpon 0/4\n')
	telnet.read_until(int_4)
	telnet.write('ont add 10 0 sn-auth {} omci ont-lineprofile-id 97 ont-srvprofile-id 97 desc "Anton_SFP"\n'.format(ont_sn).encode())
	add_error = telnet.read_until(int_4).decode().splitlines()
	for i in add_error:
		if 'Failure: SN already exists' in i:
			print('SN already exists')
			break
		else:
			continue
			
	telnet.write(quit)
	telnet.read_until(conf)
	
	#ONT Configuration:
	if test_number == 1:
		with open('6.1_ont.txt', 'r') as f:
			test61_ont = f.read().splitlines()		
		for i in test61_ont:
			ei = i.encode()
			telnet.write(ei)
			telnet.write(b'\n')
			telnet.read_until(conf)
		#BTV Configuration:
		telnet.write(b'display current-configuration section bbs | include 0/4/10 ont 0 gemport 0 multi-service user-vlan 99\n')
		sp_for_igmp = telnet.read_until(conf).decode().splitlines()
		
		for i in sp_for_igmp:
			if 'service-port' in i:
				btv_sp = re.search('service-port\s\d{1,5}', i)
		
		telnet.write(b'btv\n')
		telnet.read_until(btv)
		telnet.write('igmp user add {} max-program no-limit\n'.format(btv_sp.group(0)).encode())
		telnet.read_until(btv)
		telnet.write(b'multicast-vlan 99\n')
		telnet.read_until(mcast)
		telnet.write('igmp multicast-vlan member {}\n'.format(btv_sp.group(0)).encode())
		telnet.read_until(mcast)
		telnet.write(quit)
		telnet.read_until(conf)		
	elif test_number == 2:
		with open('6.1_ont.txt', 'r') as f:
			test61_ont = f.read().splitlines()		
		for i in test61_ont:
			ei = i.encode()
			telnet.write(ei)
			telnet.write(b'\n')
			telnet.read_until(conf)
		#BTV Configuration:
		telnet.write(b'display current-configuration section bbs | include 0/4/10 ont 0 gemport 0 multi-service user-vlan 99\n')
		sp_for_igmp = telnet.read_until(conf).decode().splitlines()
		
		for i in sp_for_igmp:
			if 'service-port' in i:
				btv_sp = re.search('service-port\s\d{1,5}', i)
		
		telnet.write(b'btv\n')
		telnet.read_until(btv)
		telnet.write('igmp user add {} max-program no-limit\n'.format(btv_sp.group(0)).encode())
		telnet.read_until(btv)
		telnet.write(b'multicast-vlan 99\n')
		telnet.read_until(mcast)
		telnet.write('igmp multicast-vlan member {}\n'.format(btv_sp.group(0)).encode())
		telnet.read_until(mcast)
		telnet.write(quit)
		telnet.read_until(conf)	
		telnet.write(b'interface gpon 0/4\n')
		telnet.read_until(int_4)
		telnet.write(b'ont port native-vlan 10 0 eth 1 vlan 51 priority 0\n')
		telnet.read_until(int_4)
		telnet.write(quit)
		telnet.read_until(conf)	
		telnet.write(b'service-port vlan 3900 gpon 0/4/10 ont 0 gemport 0 multi-service user-vlan 51 tag-transform translate inbound traffic-table index 10 outbound traffic-table index 10\n')
		telnet.read_until(conf)
	elif test_number == 3:
		telnet.write(b'interface gpon 0/4\n')
		telnet.read_until(int_4)
		telnet.write(b'ont port native-vlan 10 0 eth 1 vlan 51 priority 0\n')
		telnet.read_until(int_4)
		telnet.write(quit)
		telnet.read_until(conf)	
		telnet.write(b'service-port vlan 3800 gpon 0/4/10 ont 0 gemport 0 inbound traffic-table index 13 outbound traffic-table index 13\n')
		telnet.read_until(conf)
	elif test_number == 4:
		telnet.write(b'service-port vlan 3952 gpon 0/4/10 ont 0 gemport 0 multi-service user-vlan 9 tag-transform translate-and-add inner-vlan 9 inbound traffic-table index 13 outbound traffic-table index 13\n')
		telnet.read_until(conf)
		telnet.write(b'service-port vlan 3952 gpon 0/4/10 ont 0 gemport 0 multi-service user-vlan 1026 tag-transform translate-and-add inner-vlan 960 inbound traffic-table index 13 outbound traffic-table index 13\n')
		telnet.read_until(conf)
		telnet.write(b'service-port vlan 3952 gpon 0/4/10 ont 0 gemport 0 multi-service user-vlan 99 tag-transform translate-and-add inner-vlan 960 inbound traffic-table index 13 outbound traffic-table index 13\n')
		telnet.read_until(conf)
		telnet.write(b'service-port vlan 4000 gpon 0/4/10 ont 0 gemport 0 multi-service user-vlan 14 tag-transform translate-and-add inner-vlan 100 inbound traffic-table index 13 outbound traffic-table index 13\n')
		telnet.read_until(conf)
	elif test_number == 5:
		telnet.write(b'interface gpon 0/4\n')
		telnet.read_until(int_4)
		telnet.write(b'ont modify 10 0 ont-lineprofile-id 94\n')
		telnet.read_until(int_4)
		telnet.write(quit)
		telnet.read_until(conf)	
		telnet.write(b'service-port vlan 4000 gpon 0/4/10 ont 0 gemport 0 multi-service user-vlan 212 tag-transform translate-and-add inner-vlan 173 inbound traffic-table index 13 outbound traffic-table index 13\n')
		telnet.read_until(conf)
	elif test_number == 6:
		print('Bye')
	else:
		print('Такого значения в списке нет:')
except ValueError:
	print('Введенное значение не является числом')
finally:
	telnet.write(quit)
	telnet.read_until(enab)	
	telnet.write(quit)
	telnet.read_until(b'Configuration console exit, please retry to log on')
	time.sleep(1)
	telnet.close()
	print('Finish')

input()