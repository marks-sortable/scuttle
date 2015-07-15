#!/usr/bin/env python
import sys
import string
from string import *

class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            try:
	        self.impl = _GetchUnix()
            except ImportError:
                self.impl = _GetchMacCarbon()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys, termios # import termios now or else you'll get the Unix version on the Mac

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


class _GetchMacCarbon:
	"""
	A function which returns the current ASCII key that is down;
	if no ASCII key is down, the null string is returned.  The
	page http://www.mactech.com/macintosh-c/chap02-1.html was
	very helpful in figuring out how to do this.  
	"""
	def __init__(self):
		import Carbon
		
	def __call__(self):
		import Carbon
		if Carbon.Evt.EventAvail(0x0008)[0]==0: # 0x0008 is the keyDownMask
			return ''
		else:
			#
			# The event contains the following info:
			# (what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
			# 
			# The message (msg) contains the ASCII char which is
			# extracted with the 0x000000FF charCodeMask; this
			# number is converted to an ASCII character with chr() and 
			# returned
			#
			(what,msg,when,where,mod)=Carbon.Evt.GetNextEvent(0x0008)[1]
			return chr(msg & 0x000000FF)

getch = _Getch()

class Raft:
	def __init__(self,point):
		#print "Starting with point", point
		self.cur_dir = 'x'
		self.points = []
		self.points.append(point)
		unchecked = []
		try:
			if point[0] > 0 and program[point[1]][point[0]-1] not in (0,32, ord('o')):
				unchecked.append([point[0]-1,point[1]])
		except:
			pass
		try:
			if program[point[1]][point[0]+1] not in (0,32, ord('o')):
				unchecked.append([point[0]+1,point[1]])
		except:
			pass
		try:
			if program[point[1]+1][point[0]] not in (0,32, ord('o')):
				unchecked.append([point[0],point[1]+1])
		except:
			pass
		try:
			if point[1] > 0 and program[point[1]-1][point[0]] not in (0,32, ord('o')):
				unchecked.append([point[0],point[1]-1])
		except:
			pass
		while unchecked:
			point = unchecked.pop()
			if point in self.points:
				continue
			self.points.append(point)
			try:
				if point[0] > 0 and  program[point[1]][point[0]-1] not in (0,32, ord('o')) and [point[0]-1, point[1]] not in self.points:
					unchecked.append([point[0]-1,point[1]])
			except:
				pass
			try:
				if program[point[1]][point[0]+1] not in (0,32, ord('o')) and [point[0]+1, point[1]] not in self.points:
					unchecked.append([point[0]+1,point[1]])
			except:
				pass
			try:
				if program[point[1]+1][point[0]] not in (0,32, ord('o')) and [point[0], point[1]+1] not in self.points:
					unchecked.append([point[0],point[1]+1])
			except:
				pass
			try:
				if point[1] > 0 and program[point[1]-1][point[0]] not in (0,32, ord('o')) and [point[0], point[1]-1] not in self.points:
					unchecked.append([point[0],point[1]-1])
			except:
				pass
	
	def move(self):
#		print "Moves:", str(self.points)
		if self.cur_dir == 'n':
			# Ugly
			blocked = [point for point in self.points if point[1] == 0 or not (program[point[1]-1][point[0]] in (0, 32) or [point[0], point[1]-1] in self.points)]
			if not blocked:
				if cur_pos in self.points:
					cur_pos[1] -= 1
				# Very ugly
				values = [([point[0], point[1]-1], program[point[1]][point[0]]) for point in self.points]
				#print values
				for point in self.points:
					program[point[1]][point[0]] = 32
				for (point, value) in values:
					program[point[1]][point[0]] = value
				for point in self.points:
					point[1] -= 1
			else:
				self.cur_dir = 'x'
		if self.cur_dir == 's':
			# Ugly
			blocked = [point for point in self.points if point[1] + 1 == len(program) or not (program[point[1]+1][point[0]] in (0, 32) or [point[0], point[1]+1] in self.points)]
			if not blocked:
				if cur_pos in self.points:
					cur_pos[1] += 1
				# Very ugly
				values = [([point[0], point[1]+1], program[point[1]][point[0]]) for point in self.points]
				for point in self.points:
					program[point[1]][point[0]] = 32
				for (point, value) in values:
					program[point[1]][point[0]] = value
				for point in self.points:
					point[1] += 1
			else:
				self.cur_dir = 'x'
		if self.cur_dir == 'e':
			# Ugly
			blocked = [point for point in self.points if point[0] + 1 == len(program[point[1]]) or not (program[point[1]][point[0]+1] in (0, 32) or [point[0] + 1, point[1]] in self.points)]
			if not blocked:
				if cur_pos in self.points:
					cur_pos[0] += 1
				# Very ugly
				values = [([point[0]+1, point[1]], program[point[1]][point[0]]) for point in self.points]
				for point in self.points:
					program[point[1]][point[0]] = 32
				for (point, value) in values:
					program[point[1]][point[0]] = value
				for point in self.points:
					point[0] += 1
			else:
				self.cur_dir = 'x'
		if self.cur_dir == 'w':
			# Ugly
			blocked = [point for point in self.points if point[0] == 0 or not (program[point[1]][point[0]-1] in (0, 32) or [point[0] - 1, point[1]] in self.points)]
			if not blocked:
				if cur_pos in self.points:
					cur_pos[0] -= 1
				# Very ugly
				values = [([point[0]-1, point[1]], program[point[1]][point[0]]) for point in self.points]
				for point in self.points:
					program[point[1]][point[0]] = 32
				for (point, value) in values:
					program[point[1]][point[0]] = value
				for point in self.points:
					point[0] -= 1
			else:
				self.cur_dir = 'x'
		

def dump_program(formatted=False):
	for y in range(len(program)):
		linestring = "" 
		for x in range(len(program[y])):
			if x == cur_pos[0] and y == cur_pos[1]:
				linestring += '@'
			elif formatted:
				xy_instr = chr(program[y][x])
				if xy_instr in ('(', ')'):
					linestring += '<font color="green">%s</font>' % xy_instr
				elif xy_instr in ('[',']','~','_'):
					linestring += '<font color="purple">%s</font>' % xy_instr
				elif xy_instr in ('"','#','?'):
					linestring += '<font color="blue">%s</font>' % xy_instr
				elif xy_instr in ('^','v','<','>'):
					if xy_instr == '<':
						xy_instr = '&lt;'
					elif xy_instr == '>':
						xy_instr = '&gt;'
					linestring += '<font color="orange">%s</font>' % xy_instr
				elif xy_instr in ('a','s','d','f','h','j','k','l'):
					linestring += '<font color="red">%s</font>' % xy_instr
				elif xy_instr == '@':
					linestring += '='
				else:
					linestring += xy_instr
			else:
				linestring += chr(program[y][x])
			
		print rstrip(linestring)
	print "*" * 20
	
def ns(x):
	sys.stdout.softspace = 0
	return x

def hextoint(c):
	if 48 <= ord(c) < 58:
		return ord(c) - 48
	if 65 <= ord(c) <= 70:
		return ord(c) - 55
	if 97 <= ord(c) <= 102:
		return ord(c) - 87
	return 0

fname = sys.argv[1]
fp = open(fname, 'r')
program = []
cur_dir = 'e'
cur_pos = [0,0]
for line in fp:
	if line.find('@') >= 0:
		cur_pos = [line.find('@'), len(program)]
	l_line = [ord(c) for c in line if not c in (10, 13)]
	if len(l_line) < 80:
		l_line += [32] * (80 - len(l_line))
	program.append(l_line)

memory = [0]
mem_pos = 0
# breaking program into rafts
rafts = []
seen_space = True
for y in range(len(program)):
	for x in range(len(program[y])):
		if program[y][x] in (0, 32, ord('o')):
			seen_space = True
		else:
			seen_point = False
			for raft in rafts:
				if [x,y] in raft.points:
					seen_point = True
			if not seen_point:
				rafts.append(Raft([x,y]))
			seen_space = False

# Start program execution
while not program[cur_pos[1]][cur_pos[0]] in (32, 0):
	instr = program[cur_pos[1]][cur_pos[0]]
	if instr == ord('+'):
		memory[mem_pos] += 1
	elif instr == ord('-'):
		memory[mem_pos] -= 1
	elif instr == ord('!'):
		memory[mem_pos] = 0
	elif instr == ord('('):
		if mem_pos == 0:
			memory[0:0] = [0]
		else:
			mem_pos -= 1
	elif instr == ord(')'):
		if mem_pos == len(memory) - 1:
			memory.append(0)
		mem_pos += 1
	elif instr == ord("?"):
		memory[mem_pos] = ord(getch())
	elif instr == ord('"'):
		print ns(chr(memory[mem_pos])),
	elif instr == ord('#'):
		print ns(memory[mem_pos]),
	elif instr == ord('.'):
		for raft in rafts:
			raft.move()
	elif instr == ord('h'):
		cur_dir = 'w'
	elif instr == ord('j'):
		cur_dir = 'n'
	elif instr == ord('k'):
		cur_dir = 's'
	elif instr == ord('l'):
		cur_dir = 'e'
	elif instr == ord('^'):
		scan_pos = cur_pos[:]
		scan_pos[1] += 1
		total = 0
		while program[scan_pos[1]][scan_pos[0]] != ord('v'):
			num = chr(program[scan_pos[1]][scan_pos[0]])
			if num == '0':
				total = total << 4
			elif hextoint(num):
				total = total << 4
				total += hextoint(num)
			scan_pos[1] += 1
		memory[mem_pos] = total
	elif instr == ord('v'):
		scan_pos = cur_pos[:]
		scan_pos[1] -= 1
		total = 0
		while program[scan_pos[1]][scan_pos[0]] != ord('^'):
			num = chr(program[scan_pos[1]][scan_pos[0]])
			if num == '0':
				total = total << 4
			elif hextoint(num):
				total = total << 4
				total += hextoint(num)
			scan_pos[1] -= 1
		memory[mem_pos] = total
	elif instr == ord('>'):
		scan_pos = cur_pos[:]
		scan_pos[0] -= 1
		total = 0
		while program[scan_pos[1]][scan_pos[0]] != ord('<'):
			num = chr(program[scan_pos[1]][scan_pos[0]])
			if num == '0':
				total = total << 4
			elif hextoint(num):
				total = total << 4
				total += hextoint(num)
			scan_pos[0] -= 1
		memory[mem_pos] = total
	elif instr == ord('<'):
		scan_pos = cur_pos[:]
		scan_pos[0] += 1
		total = 0
		while program[scan_pos[1]][scan_pos[0]] != ord('>'):
			num = chr(program[scan_pos[1]][scan_pos[0]])
			if num == '0':
				total = total << 4
			elif hextoint(num):
				total = total << 4
				total += hextoint(num)
			scan_pos[0] += 1
		memory[mem_pos] = total
	elif instr == ord('['):
		if memory[mem_pos] == 0:
			heading = -1
		else:
			heading = 1
		cur_pos[0] += heading
		try:
			while program[cur_pos[1]][cur_pos[0]] != ord(']'):
				cur_pos[0] += heading
		except:
			dump_program()
			print cur_pos
			sys.exit()
	elif instr == ord(']'):
		if memory[mem_pos] == 0:
			heading = -1
		else:
			heading = 1
		cur_pos[0] -= heading
		while program[cur_pos[1]][cur_pos[0]] != ord('['):
			cur_pos[0] -= heading
	elif instr == ord('~'):
		if memory[mem_pos] == 0:
			heading = -1
		else:
			heading = 1
		cur_pos[1] += heading
		while program[cur_pos[1]][cur_pos[0]] != ord('_'):
			cur_pos[1] += heading
	elif instr == ord('_'):
		if memory[mem_pos] == 0:
			heading = -1
		else:
			heading = 1
		cur_pos[1] -= heading
		while program[cur_pos[1]][cur_pos[0]] != ord('~'):
			cur_pos[1] -= heading
	elif instr == ord('$'):
		try:
			if program[cur_pos[1]-1][cur_pos[0]] in (ord('s'), ord('j')):
				scan_pos = [cur_pos[0],cur_pos[1]-2]
				while program[scan_pos[1]][scan_pos[0]] in (0, 32):
					scan_pos = [scan_pos[0], scan_pos[1]-1]
				program[scan_pos[1]][scan_pos[0]] = 32
				for raft in rafts:
					if [scan_pos[0], scan_pos[1]] in raft.points:
						raft.points.remove(scan_pos)
		except:
			pass
		try:
			if program[cur_pos[1]+1][cur_pos[0]] in (ord('d'), ord('k')):
				scan_pos = [cur_pos[0],cur_pos[1]+2]
				while program[scan_pos[1]][scan_pos[0]] in (0, 32):
					scan_pos = [scan_pos[0], scan_pos[1]+1]
				program[scan_pos[1]][scan_pos[0]] = 32
		except:
			pass
		try:
			if program[cur_pos[1]][cur_pos[0]-1] in (ord('a'), ord('h')):
				scan_pos = [cur_pos[0],cur_pos[1]-2]
				while program[scan_pos[1]][scan_pos[0]] in (0, 32):
					scan_pos = [scan_pos[0]-1, scan_pos[1]]
				program[scan_pos[1]][scan_pos[0]] = 32
				for raft in rafts:
					if [scan_pos[0], scan_pos[1]] in raft.points:
						raft.points.remove(scan_pos)
		except:
			pass
		try:
			if program[cur_pos[1]][cur_pos[0]+1] in (ord('f'), ord('l')):
				scan_pos = [cur_pos[0]+2,cur_pos[1]]
				while program[scan_pos[1]][scan_pos[0]] in (0, 32):
					scan_pos = [scan_pos[0]+1, scan_pos[1]]
				program[scan_pos[1]][scan_pos[0]] = 32
				for raft in rafts:
					if [scan_pos[0], scan_pos[1]] in raft.points:
						raft.points.remove(scan_pos)
		except:
			pass
	elif instr == ord('a'):
		for raft in rafts:
			if cur_pos in raft.points:
				raft.cur_dir = 'w'
				break
	elif instr == ord('f'):
		for raft in rafts:
			if cur_pos in raft.points:
				raft.cur_dir = 'e'
				break
	elif instr == ord('s'):
		for raft in rafts:
			if cur_pos in raft.points:
				raft.cur_dir = 'n'
				break
	elif instr == ord('d'):
		for raft in rafts:
			if cur_pos in raft.points:
				raft.cur_dir = 's'
				break
	elif instr == ord('x'):
		for raft in rafts:
			if cur_pos in raft.points:
				raft.cur_dir = 'x'
				break
			
	if cur_dir == 'e':
		cur_pos[0] += 1
	elif cur_dir == 'n':
		cur_pos[1] -= 1
	elif cur_dir == 's':
		cur_pos[1] += 1
	elif cur_dir == 'w':
		cur_pos[0] -= 1
	for raft in rafts:
		raft.move()
#	continue
#	dump_program(True)
#dump_program(True)
