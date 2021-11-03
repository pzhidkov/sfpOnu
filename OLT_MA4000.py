import telnetlib
import time
import re

try:
	print('Выберите OLT MA4000:\n 1. MMT-MA4000-1\n 2. MMT-MA4000-2\n')
	olt_number = int(input())
	if olt_number == 1:
		ip_address = b'172.17.87.230'
	elif olt_number == 2:
		ip_address = b'172.17.87.245'
	else:
		print('Такого значения в списке нет')
		input()
except ValueError:
	print('Введенное значение не является числом')

login = b'anton_act\n'
password = b'mainstreet1\n'
glob = 'MMT-MA4000-{}#'.format(olt_number).encode()
conf = 'MMT-MA4000-{}(config)#'.format(olt_number).encode()
exit = b'exit\n'

if olt_number == 1:
	inter = b'MMT-MA4000-1(config)(if-ont-5/4/0)#'
else:
	inter = b'MMT-MA4000-2(config)(if-ont-7/5/0)#'

#Login process:
telnet = telnetlib.Telnet(ip_address, 23, 5)
telnet.read_until(b'login:')
telnet.write(login)
telnet.read_until(b'Password:')
telnet.write(password)
telnet.read_until(glob)
telnet.write(b'configure terminal\n')
telnet.read_until(conf)

def save():
	telnet.write(b'do commit\n')
	telnet.read_until(conf)
	telnet.write(b'do confirm\n')
	telnet.read_until(conf)

#Clear Config
clear_or_config = input('Очистить конфигурацию ONT ID 0? Yes/No\n')
if clear_or_config.lower() == 'yes':
	if olt_number == 1:
		telnet.write(b'no interface ont 5/4/0\n')
	else:
		telnet.write(b'no interface ont 7/5/0\n')
	telnet.read_until(conf)
	save()
	time.sleep(5)
	print('ONT ID 0 cleared')

#Autofind
if olt_number == 1:
	telnet.write(b'do show interface ont 5/4 unactivated\n')
else:
	telnet.write(b'do show interface ont 7/5 unactivated\n')

autofind = telnet.read_until(conf).decode().splitlines()
ont_list = []

for i in autofind:
	if 'has no unactivated ONTs' in i:
		print('Ont not connected to OLT')
		break
	else:
		if 'UNACTIVATED' in i:
			result = re.search('(\d)\s\s\s\s(\w{16})', i)
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
	print('Выберите тест:\n 1: 6.1_Trunk+IPTV\n 2: 6.2_Access+native vlan\n 3: DBA\n 4: Complex\n 5: Выход')
	test_number = int(input())
	
	if test_number == 1:
		if olt_number == 1:
			telnet.write(b'interface ont 5/4/0\n')
		else:
			telnet.write(b'interface ont 7/5/0\n')
		telnet.read_until(inter)	
		telnet.write('serial {}\n'.format(ont_sn).encode())
		fail = telnet.read_until(inter).decode().splitlines()
		for i in fail:
			if 'Can\'t set serial' in i:
				print(i)
				break
			else:
				with open('6.1_eltex.txt', 'r') as f:
					test61_ont = f.read().splitlines()		
					for i in test61_ont:
						ei = i.encode()
						telnet.write(ei)
						telnet.write(b'\n')
						telnet.read_until(inter)
		telnet.write(exit)
		telnet.read_until(conf)
		save()
	elif test_number == 2:
		if olt_number == 1:
			telnet.write(b'interface ont 5/4/0\n')
		else:
			telnet.write(b'interface ont 7/5/0\n')
		telnet.read_until(inter)	
		telnet.write('serial {}\n'.format(ont_sn).encode())
		fail = telnet.read_until(inter).decode().splitlines()
		for i in fail:
			if 'Can\'t set serial' in i:
				print(i)
				break
			else:
				with open('6.1_eltex.txt', 'r') as f:
					test61_ont = f.read().splitlines()		
				for i in test61_ont:
					ei = i.encode()
					telnet.write(ei)
					telnet.write(b'\n')
					telnet.read_until(inter)
				telnet.write(b'service 7 profile cross-connect VPN_1\n')
				telnet.read_until(inter)
		telnet.write(exit)
		telnet.read_until(conf)
		save()
	elif test_number == 3:
		if olt_number == 1:
			telnet.write(b'interface ont 5/3/1\n')
			telnet.read_until(b'MMT-MA4000-1(config)(if-ont-5/3/1)#')
			telnet.write('serial {}\n'.format(ont_sn).encode())
			telnet.read_until(b'MMT-MA4000-1(config)(if-ont-5/3/1)#')
		else:
			telnet.write(b'interface ont 7/5/0\n')
			telnet.read_until(b'MMT-MA4000-2(config)(if-ont-7/5/0)#')
			telnet.write('serial {}\n'.format(ont_sn).encode())
			telnet.read_until(b'MMT-MA4000-2(config)(if-ont-7/5/0)#')
		telnet.write(exit)
		telnet.read_until(conf)
		save()
	elif test_number == 4:
		if olt_number == 1:
			telnet.write(b'interface ont 5/4/0\n')
		else:
			telnet.write(b'interface ont 7/5/0\n')
		telnet.read_until(inter)	
		telnet.write('serial {}\n'.format(ont_sn).encode())
		fail = telnet.read_until(inter).decode().splitlines()
		for i in fail:
			if 'Can\'t set serial' in i:
				print(i)
				break
			else:
				with open('6.1_eltex.txt', 'r') as f:
					test61_ont = f.read().splitlines()		
				for i in test61_ont:
					ei = i.encode()
					telnet.write(ei)
					telnet.write(b'\n')
					telnet.read_until(inter)
				telnet.write(b'service 2 profile cross-connect SFP_TG dba unlim\n')
				telnet.read_until(inter)
				telnet.write(b'service 2 custom cvid 111\n')
				telnet.read_until(inter)
				telnet.write(b'service 2 custom svid 4000\n')
				telnet.read_until(inter)
		telnet.write(exit)
		telnet.read_until(conf)
		save()
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
	time.sleep(1)
	telnet.close()
	print('Finish')

input()