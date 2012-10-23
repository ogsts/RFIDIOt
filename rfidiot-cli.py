#!/usr/bin/python


#  rfidiot-cli.py - CLI for rfidiot
# 
#  Adam Laurie <adam@algroup.co.uk>
#  http://rfidiot.org/
# 
#  This code is copyright (c) Adam Laurie, 2012, All rights reserved.
#  For non-commercial use only, the following terms apply - for all other
#  uses, please contact the author:
#
#    This code is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This code is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#


#
# This program is intended to illustrate RFIDIOt's capabilities. It is deliberately
# written in a style that is easy to understand rather then one that is elegant
# or efficient. Everything is done in longhand so that individual functions can 
# be easily understood and extracted.
#
# On the other hand, due to it's completely open structure, it can be a powerful 
# tool when commands are combined, and it's easy to create shell scripts that 
# perform one-off tasks that are not worth writing an entire program for.


import rfidiot
import sys

args= rfidiot.args
help= rfidiot.help

if help or len(sys.argv) == 1:
	print
	print 'Usage: %s [OPTIONS] <COMMAND> [ARG(s)] ... [<COMMAND> [ARG(s)] ... ]' % sys.argv[0]
	print
	print '  Commands:'
	print
	print '     AID <AID|"ALL"|"ANY">                            Select ISO 7816 AID'
	print '     AIDS                                             List well known AIDs'
	print '     APDU <CLA> <INS> <P1> <P2> <LC> <DATA> <LE>      Send raw ISO 7816 APDU (use "" for empty elements)'
	print '     FILE <"A|H"> <ASCII|HEX>                         Select ISO 7816 FILE'
	print '     HSS <SPEED>                                      High Speed Select TAG. SPEED values are:'
	print '                                                        1 == 106 kBaud'
	print '                                                        2 == 212 kBaud'
	print '                                                        4 == 424 kBaud'
	print '                                                        8 == 848 kBaud'
	print '     MF <COMMAND> [<ARGS> ... ]                       Mifare commands:'
	print '        AUTH <"A|B"> <BLOCK>                            Authenticate with KEY A or B (future authentications'
	print '                                                        are automated)'
	print '        KEY <"A|B"> <HEX KEY>                           Set Mifare KEY A or B'
	print '        DUMP <START> <END>                              Show data blocks'
	print '        READ <START> <END> <FILE>                       Read data blocks and save as FILE'
	print '        WRITE <START> <FILE>                            Write data blocks from FILE (note that KEY A will'
	print '                                                        be reconstructed from previously set value)'
	print '     SELECT                                           Select TAG'
	print
	print '  Commands will be executed sequentially and must be combined as appropriate.'
	print '  Block numbers must be specified in HEX.'
	print
	print '  Examples:'
	print
	print '     Select TAG, set Mifare KEY to "FFFFFFFFFFFF" and authenticate against sector 0:'
	print
	print '       rfidiot-cli.py select mf key a FFFFFFFFFFFF mf auth a 0'
	exit(True)

try:
        card= rfidiot.card
except:
	print "Couldn't open reader!"
        exit(True)

print
card.info('rfidiot-cli v0.1')

# globals
Mifare_Key= None
Mifare_KeyType= None
Mifare_KeyA= None
Mifare_KeyB= None

# main loop
args.reverse()
while args:
	command= args.pop().upper()
	if command == 'AID':
		arg= args.pop().upper()
		if arg == 'ANY' or arg == 'ALL':
			aids= card.AIDS.keys()
		else:
			aids= [arg]
		while aids:
			aid= aids.pop()
			print
			print '  Selecting AID: %s' % aid,
			try:
				print '(%s)' % card.AIDS[aid],
			except:
				pass
			print
			print
			if card.iso_7816_select_file(aid,card.ISO_7816_SELECT_BY_NAME,'0C'):
				print '    OK'
				if arg == 'ANY':
					break
			else:
				print '    '+card.ISO7816ErrorCodes[card.errorcode]
		continue
	if command == 'AIDS':
		print
		print '  AIDs:'
		print
		for aid in card.AIDS.iteritems():
			print '    % 24s: %s' % (aid[0], aid[1])
		print
		continue
	if command == 'APDU':
		cla= args.pop().upper()
		ins= args.pop().upper()
		p1= args.pop().upper()
		p2= args.pop().upper()
		lc= args.pop().upper()
		data= args.pop().upper()
		le= args.pop().upper()
		print
		print '  Sending APDU:', cla+ins+p1+p2+lc+data+le
		print
		if card.send_apdu('','','','',cla,ins,p1,p2,lc,data,le):
			print '    OK'
			print '    Data:', card.data
		else:
			print '    '+card.ISO7816ErrorCodes[card.errorcode]
		continue
	if command == 'FILE':
		mode= args.pop().upper()
		if mode == 'A':
			isofile= args.pop().encode('hex')
		elif mode == 'H':
			isofile= args.pop().upper()
		else:
			print 'Invalid FILE mode:', args.pop().upper()
			exit(True)
		print
		print '  Selecting ISO File:', isofile
		print
		if card.iso_7816_select_file(isofile,card.ISO_7816_SELECT_BY_NAME,'00'):
			print '    OK'
		else:
			print '    '+card.ISO7816ErrorCodes[card.errorcode]
		continue
	if command == 'HSS':
		speed= '%02X' % int(args.pop())
		print
		print '  High Speed Selecting (%s)' % card.ISO_SPEED[speed]
		print
		if card.hsselect(speed):
			print '    Card ID: ' + card.uid
		else:
			if card.errorcode:
				print '    '+card.ISO7816ErrorCodes[card.errorcode]
			else:
				print '    No card present'
		continue
	if command == 'MF':
		print
		mfcommand= args.pop().upper()
		if mfcommand == 'AUTH':
			keytype= args.pop().upper()
			sector= int(args.pop(),16)
			print '  Authenticating to sector %02X with Mifare Key' % sector,
			Mifare_KeyType= keytype
			if keytype == 'A':
				Mifare_Key= Mifare_KeyA
				print 'A (%s)' % Mifare_Key
			elif keytype == 'B':
				Mifare_Key= Mifare_KeyB
				print 'B (%s)' % Mifare_Key
			else:
				print 'failed! Invalid keytype:', keytype
				exit(True)
			print
			if card.login(sector, Mifare_KeyType, Mifare_Key):
				print '    OK'
			else:
				print '    '+card.ISO7816ErrorCodes[card.errorcode]
			continue
		if mfcommand == 'DUMP':
			start= int(args.pop(),16)
			end= int(args.pop(),16)
			print '  Dumping data blocks %02X to %02X:' % (start, end)
			print
			sector= start
			while sector <= end:
				if card.login(sector, Mifare_KeyType, Mifare_Key) and card.readMIFAREblock(sector):
					print '    %02X: %s %s' % (sector, card.MIFAREdata, card.ReadablePrint(card.MIFAREdata.decode('hex')))
				else:
					print '    '+card.ISO7816ErrorCodes[card.errorcode]
				sector += 1
			continue
		if mfcommand == 'KEY':
			print '  Setting Mifare Key',
			keytype= args.pop().upper()
			Mifare_KeyType= keytype
			if keytype == 'A':
				Mifare_KeyA= args.pop().upper()
				print 'A:', Mifare_KeyA
			elif keytype == 'B':
				Mifare_KeyB= args.pop().upper()
				print 'B:', Mifare_KeyB
			else:
				print 'failed! Invalid keytype:', keytype
				exit(True)
			continue
		if mfcommand == 'READ':
			start= int(args.pop(),16)
			end= int(args.pop(),16)
			filename= args.pop()
			print '  Reading data blocks %02X to %02X and saving as %s:' % (start, end, filename)
			print
			outfile= open(filename, "wb")
			if not outfile:
				print "Failed! Couldn't open output file!"
				exit(True)
			sector= start
			while sector <= end:
				if card.login(sector, Mifare_KeyType, Mifare_Key) and card.readMIFAREblock(sector):
					outfile.write(card.MIFAREdata.decode('hex'))
				else:
					print '    '+card.ISO7816ErrorCodes[card.errorcode]
				sector += 1
			outfile.close()
			print '    OK'
			continue
		if mfcommand == 'WRITE':
			start= int(args.pop(),16)
			filename= args.pop()
			infile= open(filename,"rb")
			data= infile.read()
			infile.close()
			print '  Writing data from file', filename,
			if len(data) % 16:
				print 'failed! File length is not divisible by Mifare block length (16)!'
				exit(True)
			if not Mifare_KeyA:
				print 'failed! KEY A not set!'
				exit(True)
			end= start + len(data) / 16 - 1
			print 'to blocks %02X to %02X' % (start, end)
			print
			sector= start
			p= 0
			while sector <= end:
				block= data[p:p + 16].encode('hex')
				if not (sector + 1) % 4:
					# trailing block must contain key A, so reconstruct
					block= Mifare_KeyA + block[12:]
				if not (card.login(sector, Mifare_KeyType, Mifare_Key) and card.writeblock(sector, block)):
					if sector == 0:
						print '    Sector 0 write failed'
					else:
						print '    '+card.ISO7816ErrorCodes[card.errorcode]
						exit(True)
				sector += 1
				p += 16
			print '    OK'
			continue
		print '  Invalid MF command:', mfcommand
		exit(True)
	if command == 'SELECT':
		print
		print '  Selecting TAG'
		print
		if card.select():
			print '    Card ID: ' + card.uid
			if card.readertype == card.READER_PCSC:
				print '    ATR: ' + card.pcsc_atr
		else:
			if card.errorcode:
				print '    '+card.ISO7816ErrorCodes[card.errorcode]
			else:
				print '    No card present'
		continue
	print
	print 'Unrecognised command:', command
	exit(True)
print
exit(False)
