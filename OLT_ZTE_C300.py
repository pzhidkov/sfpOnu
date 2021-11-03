import telnetlib
import time
import re

print('OLT MMT-C300-1')

ip_address = b'172.17.87.232'
login = b'anton_act\n'
password = b'mainstreet1\n'
glob = b'MMT-C300-1#'
conf = b'MMT-C300-1(config)#'
inter = b'interface gpon-olt_1/6/7\n'
inter_s = b'MMT-C300-1(config-if)#'
ont_conf = b'MMT-C300-1(gpon-onu-mng 1/6/7:1)#'
exit = b'exit\n'

#Login process:
telnet = telnetlib.Telnet(ip_address, 23, 5)
telnet.read_until(b'Username:')
telnet.write(login)
telnet.read_until(b'Password:')
telnet.write(password)
telnet.read_until(glob)
telnet.write(b'configure terminal\n')
telnet.read_until(conf)

#Clear Config
clear_or_config = input('Очистить конфигурацию ONT ID 1? Yes/No\n')
if clear_or_config.lower() == 'yes':
	telnet.write(inter)
	telnet.read_until(inter_s)
	telnet.write(b'no onu 1\n')
	telnet.read_until(inter_s)
	telnet.write(exit)
	telnet.read_until(conf)
	time.sleep(10)
	print('ONT ID 0 cleared')


#Autofind
telnet.write(b'show gpon onu uncfg gpon-olt_1/6/7\n')
autofind = telnet.read_until(conf).decode().splitlines()
ont_list = []

for i in autofind:
    if 'No related information to show' in i:
        print('Ont not connected to OLT')
        break
    else:
        if 'gpon-onu' in i:
            result = re.search('(\S{16})\s{9}(\w{16})', i)
            ont_list.append(result.group(2))
            continue
        else:
            continue

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
	print('Выберите тест:\n 1: 6.1/6.3_Trunk+IPTV\n 2: 6.2_Access+native vlan\n 3: Complex\n 4: DBA\n 5: Выход')
	test_number = int(input())
	
	#Add ONT:
	telnet.write(inter)
	telnet.read_until(inter_s)
	telnet.write('onu 1 type RT-SFP sn {}\n'.format(ont_sn).encode())
	telnet.read_until(inter_s)
	telnet.write(exit)
	telnet.read_until(conf)

	#ONT Configuration:
	if test_number == 1:
		telnet.write(b'interface gpon-onu_1/6/7:1\n')
		telnet.read_until(inter_s)
		
		with open('6.1_zte_1.txt', 'r') as f:
			test61_ont_1 = f.read().splitlines()		
		for i in test61_ont_1:
			ei = i.encode()
			telnet.write(ei)
			telnet.write(b'\n')
			telnet.read_until(inter_s)
		
		telnet.write(exit)
		telnet.read_until(conf)
		telnet.write(b'pon-onu-mng gpon-onu_1/6/7:1\n')
		telnet.read_until(ont_conf)
		
		with open('6.1_zte_2.txt', 'r') as f:
			test61_ont_2 = f.read().splitlines()	
		for i in test61_ont_2:
			ei = i.encode()
			telnet.write(ei)
			telnet.write(b'\n')
			telnet.read_until(ont_conf)
		
		telnet.write(exit)
		telnet.read_until(conf)
		telnet.write(b'igmp mvlan 99 receive-port gpon-onu_1/6/7:1 vport 2\n')
		telnet.read_until(conf)
	elif test_number == 2:
		telnet.write(b'interface gpon-onu_1/6/7:1\n')
		telnet.read_until(inter_s)
		
		with open('6.1_zte_1.txt', 'r') as f:
			test61_ont_1 = f.read().splitlines()		
		for i in test61_ont_1:
			ei = i.encode()
			telnet.write(ei)
			telnet.write(b'\n')
			telnet.read_until(inter_s)
		
		telnet.write(exit)
		telnet.read_until(conf)
		telnet.write(b'pon-onu-mng gpon-onu_1/6/7:1\n')
		telnet.read_until(ont_conf)
		
		with open('6.1_zte_2.txt', 'r') as f:
			test61_ont_2 = f.read().splitlines()	
		for i in test61_ont_2:
			ei = i.encode()
			telnet.write(ei)
			telnet.write(b'\n')
			telnet.read_until(ont_conf)
		
		telnet.write(exit)
		telnet.read_until(conf)
		telnet.write(b'igmp mvlan 99 receive-port gpon-onu_1/6/7:1 vport 2\n')
		
		telnet.read_until(conf)
		telnet.write(b'pon-onu-mng gpon-onu_1/6/7:1\n')
		telnet.read_until(ont_conf)
		telnet.write(b'no service VPN1\n')
		telnet.read_until(ont_conf)
		telnet.write(b'service VPN1 gemport 3 vlan 51\n')
		telnet.read_until(ont_conf)
		telnet.write(b'vlan port eth_0/1 mode hybrid def-vlan 51\n')
		telnet.read_until(ont_conf)
		telnet.write(exit)
		telnet.read_until(conf)
		telnet.write(b'interface gpon-onu_1/6/7:1\n')
		telnet.read_until(inter_s)
		telnet.write(b'no service-port 3\n')
		telnet.read_until(inter_s)
		telnet.write(b'service-port 3 vport 3 user-vlan 51 vlan 3900\n')
		telnet.read_until(inter_s)
		telnet.write(exit)
		telnet.read_until(conf)
	elif test_number == 4:
		telnet.write(b'interface gpon-onu_1/6/6:1\n')
		telnet.read_until(inter_s)
		telnet.write(b'registration-method sn {}\n'.format(ont_sn).encode())
		telnet.read_until(inter_s)
		telnet.write(exit)
		telnet.read_until(conf)
	elif test_number == 5:
		print('Bye')
	else:
		print('Такого значения в списке нет:')
except ValueError:
	print('Введенное значение не является числом')
finally:
	telnet.write(exit)
	telnet.read_until(glob)	
	telnet.write(exit)
	telnet.read_until(b'The configuration is changed,confirm to logout without saving?')
	telnet.write(b'yes\n')
	time.sleep(1)
	telnet.close()
	print('Finish')

input()