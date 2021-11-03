import telnetlib
import time

print('EX3300-Complex')

ip_address = b'172.17.252.19'
login = b'admin\n'
password = b'znanie8\n'
glob = b'admin@LABS-SSW12>'
conf = b'admin@LABS-SSW12#'
exit = b'exit\n'

#Login process:
telnet = telnetlib.Telnet(ip_address, 23, 5)
telnet.read_until(b'login:')
telnet.write(login)
telnet.read_until(b'Password:')
telnet.write(password)
telnet.read_until(glob)

def save():
	telnet.write(b'commit\n')
	telnet.read_until(conf)

try:
	print('Выберите конфигурацию портов EX:\n 1. Порты 20-39: Trunk\n 2. Порты 20-39: Access\n')
	vibor = int(input())
	telnet.write(b'edit\n')
	telnet.read_until(conf)
	if vibor == 1:
		telnet.write(b'wildcard range set interfaces ge-0/0/[20-39] unit 0 family ethernet-switching port-mode trunk\n')
		telnet.read_until(conf)
		save()
	elif vibor == 2:
		telnet.write(b'wildcard range set interfaces ge-0/0/[20-39] unit 0 family ethernet-switching port-mode access\n')
		telnet.read_until(conf)
		save()
	else:
		print('Такого значения в списке нет')
		input()
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