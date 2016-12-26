import subprocess
import sys
import time
import os
import signal
import hashlib
from operator import itemgetter
import math

keygen=True
getoui=True
compact=False
logging=True
colors=True
updatedelay=5
berlin=30


if len(sys.argv) == 1:
	print "Usage: python " + sys.argv[0] + " [interface]"
	sys.exit(0)
interface = sys.argv[1]
ouifile = open("oui.txt","r").readlines()
table = []
stations = []
tnum = 0
if colors:
	white = '\033[1;37;48m'
	neutral = '\033[0;37;48m'
	red = '\033[1;31;48m'
	green = '\033[1;32;48m' 
	yellow = '\033[1;33;48m'
	blue = '\033[1;34;48m'
	purple = '\033[1;35;48m'
	cyan = '\033[1;36;48m'
else:
	white = ''
	neutral = ''
	red = ''
	green = '' 
	yellow = ''
	blue = ''
	purple = ''
	cyan = ''

def get_dist(rssi):
	result = (27 - (20 * math.log10(2460)) + math.fabs(-rssi)) / 20
	meters = str(int(math.pow(10,result))) + "m"
	return meters

def get_oui(mac):
	macidlist = mac.split(':')
	macid = macidlist[0] + macidlist[1] + macidlist[2]
	macmanu = ""
	for ln in ouifile:
		if macid.upper() in ln:
			try:
				macmanu = ln.split('\t')[2].rstrip()
			except IndexError:
				macmanu = "Unknown"
	if macmanu == "":
		macmanu = "Unknown"
	return macmanu



def signal_handler(signal,frame):
	print('Exiting...')
	sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

print "LOADING DATABASE..."
try:
	infile = open("airodump-nomon.csv","r").readlines()
	for line in infile:
		e = line.split(';')
		table.append([e[0],int(e[1]),int(e[2]),e[3],e[4],e[5],e[6],e[7],e[8],e[9],e[10]])
except:
	print "NO FILE"

#DEBUG
for line in table:
	print line

while True:
	print "SCANNING..."
	try:
		output = subprocess.check_output('iw ' + interface + ' scan',shell=True)
	except subprocess.CalledProcessError as e:
		print e.output
		output = "error"
		if len(table) == 0:
			sys.exit(0)
	print "PROCESSING..."
	outlist = output.split('\n')
	timestamp = int(time.time())
	cont = True
	stations = []
	for line in outlist:
		if interface in line:
			bss = line.split()[1].split('(')[0].upper()
			#DEBUG
			print "PROCESSING " + bss
			cont = True
			for i, entry in enumerate(table):
				if entry[0] == bss:
					cont = False
					tnum = i + 1
					table[tnum-1][1] = timestamp
			if cont == True:
				if getoui:
					oui = get_oui(bss)
				else:
					oui = ""
				table.append([bss,timestamp,"","","","",oui,"","","",""])
				tnum = tnum + 1
		elif 'signal' in line:
			sigsplit = line.split()
			if len(sigsplit) == 3:
				signal = int(-float(sigsplit[1]))
			table[tnum-1][2] = signal
		elif 'TSF' in line:
			uptime = line.split('(')[1]
			uptime = uptime.split(')')[0]
			table[tnum-1][3] = uptime
		elif 'ESS' in line:
			if 'Privacy' in line:
				encmode = "ENC"
			else:
				encmode = "OPEN"

			table[tnum-1][4] = encmode
		elif 'SSID' in line:
			ssidsplit = line.split()
			if len(ssidsplit) == 2:
				ssid = ssidsplit[1]
			elif len(ssidsplit) == 3:
				ssid = ssidsplit[1] + " " + ssidsplit[2]
			elif len(ssidsplit) == 4:
				ssid = ssidsplit[1] + " " + ssidsplit[2] + " " + ssidsplit[3]
			else:
				ssid = ""
			table[tnum-1][5] = ssid
		elif 'WPS' in line:
			wps = "WPS Open"
			table[tnum-1][7] = wps
		elif 'AP setup locked: 0x01' in line:
			wps = "WPS Locked"
			table[tnum-1][7] = wps
		elif 'Model:' in line:
			modelsplit = line.split()
			if len(modelsplit) == 3:
				model = modelsplit[2]
			elif len(modelsplit) == 4:
				model = modelsplit[2] + " " + modelsplit[3]
			elif len(modelsplit) == 5:
				model = modelsplit[2] + " " + modelsplit[3] + " " + modelsplit[4]
			table[tnum-1][9] = model
		elif 'Serial' in line:
			try:
				serial = line.split()[3]
			except:
				serial = "?"
			table[tnum-1][10] = serial	
		elif 'Device name' in line:
			devsplit = line.split()
			if len(devsplit) == 4:
				dev = devsplit[3]
			elif len(devsplit) == 5:
				dev = devsplit[3] + " " + devsplit[4]
			elif len(devsplit) == 6:
				dev = devsplit[3] + " " + devsplit[4] + " " + devsplit[5]
			table[tnum-1][8] = dev
		elif 'station count:' in line:
			stasplit = line.split()
			sta = int(stasplit[3])
			stations.append([table[tnum-1][5], sta])

	print "OUTPUTTING..."
	tableprint = []
	for line in table:
		if timestamp <= (line[1] + berlin): 
			if line[2] != '':
				distance = get_dist(int(line[2]))
			else:
				distance = "?m"
			colenc = ""
			if line[4] == "ENC":
				colenc = red
			elif line[4] == "OPEN":
				colenc = green
			if compact:
				newline = white + "[" + distance + "]" + colenc + " [" + line[4] + "]" + yellow + " [" + line[5] + "]" + purple + " [" + line[6] + "]" + green + " [" + line[9] + "]"  + white + " [" + line[7] + "]" + neutral
			else:
				newline = white + "[" + line[0] + "]" + " [" + distance + "]" + purple + " [" + line[3] + "]" +  colenc + " [" + line[4] + "]" +  yellow + " [" + line[5] + "]" +  purple + " [" + line[6] + "]" + white + " [" + line[7] +  "]" + green + " [" + line[8] + "]" + " [" + line[9] + "]" + neutral
			tableprint.append(newline)
	os.system('clear')
	for line in tableprint:
		print line 
	print "Showing:" + str(len(tableprint)) + " Hidden:" + str((len(table) - len(tableprint))) + " Total:" + str(len(table)) + "\n"
	for con in stations:
		print white + str(con[1]) + " clients connected to " + con[0] + neutral
	if logging:
		print "LOGGING..."
		logfile = open("airodump-nomon.csv", "wb")
		for line in table:
			logfile.write(line[0] + ";" + str(line[1]) + ";" + str(line[2]) + ";" + line[3] + ";" + line[4] + ";" + line[5] + ";" + line[6] + ";" + line[7] + ";" + line[8] + ";" + line[9] + ";" + line[10] + ";\n")
		logfile.close()
	if keygen:
		os.system('python aircrack-nomon.py')

	time.sleep(updatedelay)

