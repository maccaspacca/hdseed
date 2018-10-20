"""
 HD Seed Address Generator for Testing
 Version 0.1 Test Version
 Date 20/10/2018
 Copyright Maccaspacca and Jimhsu 2018
 Copyright The Bismuth Foundation 2016 to 2018
 Author Maccaspacca
 
 Test deterministic address generation
 Addresses are generated deterministically
 
 Usage
 
 To create addresses use"python hd_test.py write"
  
 You will be prompted for a number of addresses to generate
 If you don't enter a number it will default to 100
 The output will store a list of seeds with the correponding address.
 The output is stored in a file called "testfile.txt".
 This part also tests for duplicates.
 
 To test the created addresses use "python hd_test.py read"
 
 This uses the seed in "testfile.txt" so recreate the addresses
 It compares the re-created addresses to the original address.
 If the re-created address is the same as the original then all is good.
 
 The standard test would be to create the testfile.txt on one OS and then
 do the re-creation test on a different OS platform and then vice-versa
 
 The test should result on 100% success 
"""

import os, logging, pathlib, string, hashlib, time, sys, random
from logging.handlers import RotatingFileHandler
from Crypto.Protocol.KDF import PBKDF2
from Crypto.PublicKey import RSA
from libs.mnemonic import Mnemonic
from libs.rsa_py import rsa_functions

# setup logging

log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s')
logFile = 'hdtest.log'
my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5 * 1024 * 1024, backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)
app_log = logging.getLogger('root')
app_log.setLevel(logging.INFO)
app_log.addHandler(my_handler)

# some predefined variables to keep parity with jimhsu code

mnemo = Mnemonic('english')
iterations = 20000
length = 48
n = 4096
cointype = 209 # Provisionally, 209 (atomic weight of bismuth) (see https://github.com/satoshilabs/slips/blob/master/slip-0044.md )
aid = 1
addrs = 1

test_type = sys.argv[1]


# we don't want ":" in the random passphrase do we :)
test_chars = ""

for c in string.punctuation:
	if c != ":":
		test_chars = test_chars + c

# Alatay Test
def getpwd(length = 72, char = string.ascii_uppercase + string.digits + string.ascii_lowercase + test_chars):

# string.punctuation

	return ''.join(random.choice(char) for x in range(length))
# Alatay Test

if test_type == "write":

	try:
		test_in = int(input("Enter number of seeds to generate and hit return: "))
		if test_in < 10:
			test_in = 10
	except:
		print("No entry made or invalid entry the default of 10 will be used")
		test_in = 10

# key generation

	k_count = 1
	
	if os.path.isfile('testfile.txt'):
		os.rename('testfile.txt','testfile.txt.old')

	test_file = open('testfile.txt', 'a')

	while k_count < (test_in + 1):
	
		m_ken = False
		
		while not m_ken: # catch a bad seed
		
			try:

				address = ""
				pwd_a = mnemo.generate(strength=256)
				
				app_log.info("Mnemonic (seed) = {}".format(pwd_a))
				passphrase = getpwd() # Alatay Test
				passP = "mnemonic" + passphrase
				
				master_key = PBKDF2(pwd_a.encode('utf-8'), passP.encode('utf-8'), dkLen=length, count=iterations)
				
				deriv_path = "m/44'/"+ str(cointype) +"'/" + str(aid) + "'/0/" + str(addrs) #HD path

				account_key = PBKDF2(master_key, deriv_path.encode('utf-8'), dkLen=length, count=1)
				
				rsa = rsa_functions.RSAPy(n,account_key)
				key = RSA.construct(rsa.keypair)
				
				private_key_readable = key.exportKey().decode("utf-8")
				public_key_readable = key.publickey().exportKey().decode("utf-8")
				address = hashlib.sha224(public_key_readable.encode("utf-8")).hexdigest()  # hashed public key
				
				if (len(public_key_readable)) != 271 and (len(public_key_readable)) != 799:
					app_log.info('Generation fail pubkey {} : {}'.format(str(len(public_key_readable)),address))
				else:
					app_log.info('Address {} generated successfully: {}'.format(str(k_count),address))
					app_log.info('Password used: {}'.format(passphrase))
					test_file.write("{}:{}:{}\n".format(address,pwd_a,passphrase))
					k_count +=1
				m_ken = True
			
			except Exception as e: 
				app_log.warning('Key Generation error: {}'.format(e))
				app_log.warning('Seed used: {}'.format(pwd_a))
				app_log.warning('Password used: {}'.format(passphrase))
				
				m_ken = False

	test_file.close()
	
	app_log.info('Looking for duplicates.....')
	
	with open('testfile.txt') as f:
		seen = set()
		for line in f:
			if line in seen:
				app_log.info('Duplicate found: {}'.format(line))
			else:
				seen.add(line)
	app_log.info('Check for duplicates complete')

# key testing

if test_type == "read":

	address = ""

	with open('testfile.txt') as file:
		for line in file:
			line = line.strip() #preprocess line
			testline = line.split(":")
			test_address = testline[0]
			pwd_a = testline[1]
			
			passphrase = testline[2]
			passP = "mnemonic" + passphrase
			
			master_key = PBKDF2(pwd_a.encode('utf-8'), passP.encode('utf-8'), dkLen=length, count=iterations)
			
			deriv_path = "m/44'/"+ str(cointype) +"'/" + str(aid) + "'/0/" + str(addrs) #HD path

			account_key = PBKDF2(master_key, deriv_path.encode('utf-8'), dkLen=length, count=1)
			
			rsa = rsa_functions.RSAPy(n,account_key)
			key = RSA.construct(rsa.keypair)

			#private_key_readable = key.exportKey().decode("utf-8")
			public_key_readable = key.publickey().exportKey().decode("utf-8")
			address = hashlib.sha224(public_key_readable.encode("utf-8")).hexdigest()  # hashed public key
			
			if address == test_address:
				app_log.info('Test re-key success: {}'.format(test_address))
			else:
				app_log.info('Test re-key failure: {}'.format(test_address))
				app_log.info('Test passphrase: {}'.format(passphrase))
