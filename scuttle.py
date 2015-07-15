#!/usr/bin/env python
import sys
import string
from string import *

# We need getch to properly implement "?"
class _Getch(object):
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


class _GetchUnix(object):
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

class _GetchWindows(object):
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


class _GetchMacCarbon(object):
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

class Point(object):
	__slots__ = ('x','y')
	def __init__(self,x,y):
		self.x = x
		self.y = y

	def __hash__(self):
		return hash((self.x, self.y))

	def __eq__(self, other):
		return self.x == other.x and self.y == other.y

	def __repr__(self):
		return "Point({},{})".format(self.x, self.y)

	def n(self):
		return Point( self.x, self.y - 1 )
	def s(self):
		return Point( self.x, self.y + 1 )
	def e(self):
		return Point( self.x + 1, self.y )
	def w(self):
		return Point( self.x - 1, self.y )

	def out_of_bounds(self):
		return self.x < 0 or self.y < 0

class Program(object):
	def __init__(self, raw):
		self.raw = raw

	def get(self, point):
		if point.x < 0 or point.y < 0 or point.y >= len(self.raw) or point.x >= len( self.raw[point.y] ):
			return 0
		return self.raw[point.y][point.x]
	def set(self, point, value):
		if point.x < 0 or point.y < 0:
			return
		while point.y >= len( self.raw ):
			self.raw.append([])
		while point.x >= len( self.raw[point.y] ):
			self.raw[point.y].append(0)
		self.raw[point.y][point.x] = value
		
class Raft(object):
	def __init__(self,program,point):
		#print "Starting with point", point
		self.cur_dir = 'x'
		self.points = []
		visited = set()
		unchecked = [point]
			
		while unchecked:
			point = unchecked.pop()
			
			if point in visited:
				continue
			
			visited.add(point)
			if not self._validLocation( program.get(point) ):
				continue
			
			self.points.append(point)
			unchecked.append( point.n() )
			unchecked.append( point.s() )
			unchecked.append( point.e() )
			unchecked.append( point.w() )

	@staticmethod
	def _validLocation( value ):
		return not value in (0, 32, ord('o'))

	def move(self):
#		print "Moves:", str(self.points)
		offset, new_pos_func = { 
			'n': ( Point(0,-1), lambda x: x.n() ),
			's': ( Point(0,1), lambda x: x.s() ),
			'e': ( Point(1,0), lambda x: x.e() ),
			'w': ( Point(-1,0), lambda x: x.w() ),
			'x': ( Point(0,0), lambda x: x)
			 }[self.cur_dir]
		if self.cur_dir != 'x':
			blocked = any( True for point in self.points 
				if new_pos_func(point).out_of_bounds() or not 
				(program.get(new_pos_func(point)) in (0,32) or new_pos_func(point) in self.points))
			if not blocked:
				if cur_pos in self.points:
					cur_pos.x += offset.x
					cur_pos.y += offset.y
				values = [ (new_pos_func(point), program.get(point)) for point in self.points ]
				for point in self.points:
					program.set( point, 32 )
				for (point, value) in values:
					program.set( point, value )
				for point in self.points:
					point.x += offset.x
					point.y += offset.y
			else:
				self.cur_dir = 'x'

def dump_program(formatted=False):
	for y in range(len(program.raw)):
		linestring = "" 
		for x in range(len(program.raw[y])):
			if x == cur_pos.x and y == cur_pos.y:
				linestring += '@'
			elif formatted:
				xy_instr = chr(program.raw[y][x])
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
				linestring += chr(program.raw[y][x])
			
		print rstrip(linestring)
	print "*" * 20
	
def ns(x):
	sys.stdout.softspace = 0
	return x

def hextoint(c):
	return int(c,16)

fname = sys.argv[1]
fp = open(fname, 'r')
program = []
cur_dir = 'e'
cur_pos = Point(0,0)
for line in fp:
	if line.find('@') >= 0:
		cur_pos = Point(line.find('@'), len(program))
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
				if Point(x,y) in raft.points:
					seen_point = True
			if not seen_point:
				
				rafts.append(Raft(Program( program ), Point(x,y)))
			seen_space = False

program = Program(program)
# Start program execution
while not program.get(cur_pos) in (32, 0):
	instr = program.get(cur_pos)
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
		scan_pos = cur_pos.s()
		total = 0
		while program.get(scan_pos) != ord('v'):
			num = chr(program.get(scan_pos))
			if num == '0':
				total = total << 4
			elif hextoint(num):
				total = total << 4
				total += hextoint(num)
			scan_pos.y += 1
		memory[mem_pos] = total
	elif instr == ord('v'):
		scan_pos = cur_pos.n()
		total = 0
		while program.get(scan_pos) != ord('^'):
			num = chr(program.get(scan_pos))
			if num == '0':
				total = total << 4
			elif hextoint(num):
				total = total << 4
				total += hextoint(num)
			scan_pos.y -= 1
		memory[mem_pos] = total
	elif instr == ord('>'):
		scan_pos = cur_pos.w()
		total = 0
		while program.get(scan_pos) != ord('<'):
			num = chr(program.get(scan_pos))
			if num == '0':
				total = total << 4
			elif hextoint(num):
				total = total << 4
				total += hextoint(num)
			scan_pos.x -= 1
		memory[mem_pos] = total
	elif instr == ord('<'):
		scan_pos = cur_pos.e()
		total = 0
		while program.get(scan_pos) != ord('>'):
			num = chr(program.get(scan_pos))
			if num == '0':
				total = total << 4
			elif hextoint(num):
				total = total << 4
				total += hextoint(num)
			scan_pos.x += 1
		memory[mem_pos] = total
	elif instr == ord('['):
		if memory[mem_pos] == 0:
			heading = -1
		else:
			heading = 1
		cur_pos.x += heading
		try:
			while program.get( cur_pos ) != ord(']'):
				cur_pos.x += heading
		except:
			print "Could not find matching point for ["
			dump_program()
			print cur_pos
			sys.exit()
	elif instr == ord(']'):
		if memory[mem_pos] == 0:
			heading = -1
		else:
			heading = 1
		cur_pos.x -= heading
		while program.get(cur_pos) != ord('['):
			cur_pos.x -= heading
	elif instr == ord('~'):
		if memory[mem_pos] == 0:
			heading = -1
		else:
			heading = 1
		cur_pos.y += heading
		while program.get(cur_pos) != ord('_'):
			cur_pos.y += heading
	elif instr == ord('_'):
		if memory[mem_pos] == 0:
			heading = -1
		else:
			heading = 1
		cur_pos.y -= heading
		while program.get(cur_pos) != ord('~'):
			cur_pos.y -= heading
	elif instr == ord('$'):
		
		if program.get(cur_pos.n()) in (ord('s'), ord('j')):
			scan_pos = Point( cur_pos.x, cur_pos.y-2)
			while program.get(scan_pos) in (0, 32):
				scan_pos = scan_pos.n()
			program.set(scan_pos, 32)
			for raft in rafts:
				if scan_pos in raft.points:
					raft.points.remove(scan_pos)
		
		if program.get(cur_pos.s()) in (ord('d'), ord('k')):
			scan_pos = Point(cur_pos.x,cur_pos.y+2)
			while program.get(scan_pos) in (0, 32):
				scan_pos = scan_pos.s()
			program.set(scan_pos, 32)
	
		if program.get(cur_pos.w()) in (ord('a'), ord('h')):
			scan_pos = Point(cur_pos.x-2,cur_pos.y)
			while program.get(scan_pos) in (0, 32):
				scan_pos = scan_pos.w()
			program.set(scan_pos, 32)
			for raft in rafts:
				if scan_pos in raft.points:
					raft.points.remove(scan_pos)
		
		if program.get(cur_pos.e()) in (ord('f'), ord('l')):
			scan_pos = Point(cur_pos.x+2,cur_pos.y)
			while program.get(scan_pos) in (0, 32):
				scan_pos = scan_pos.e()
			program.set(scan_pos, 32)
			for raft in rafts:
				if scan_pos in raft.points:
					raft.points.remove(scan_pos)
	
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
		cur_pos = cur_pos.e()
	elif cur_dir == 'n':
		cur_pos = cur_pos.n()
	elif cur_dir == 's':
		cur_pos = cur_pos.s()
	elif cur_dir == 'w':
		cur_pos = cur_pos.w()
	for raft in rafts:
		raft.move()
#	continue
	# dump_program()
#dump_program(True)
