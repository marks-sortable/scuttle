#!/usr/bin/env python
import sys
import string
from string import *
from getch import getch

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
	def __sub__(self, other):
		return Point( self.x - other.x, self.y - other.y )
	def __add__(self, other):
		return Point( self.x + other.x, self.y + other.y )
	def out_of_bounds(self):
		return self.x < 0 or self.y < 0

class Program(object):
	def __init__(self, raw):
		self.raw = raw
		# breaking program into rafts
		self.rafts = None
		rafts = []
		seen_space = True
		for y in range(len(raw)):
			for x in range(len(raw[y])):
				if raw[y][x] in (0, 10, 13, 32):
					seen_space = True
				else:
					seen_point = False
					for raft in rafts:
						if raft.contains( Point(x,y) ):
							seen_point = True
					if not seen_point:
						rafts.append(Raft(self, Point(x,y)))
					
					seen_space = False
		self.rafts = rafts
		
	def get(self, point):
		if self.rafts:
			for raft in self.rafts:
				if raft.contains( point ):
					return raft.get( point )
			return 0
		if point.x < 0 or point.y < 0 or point.y >= len(self.raw) or point.x >= len( self.raw[point.y] ):
			return 0
		return self.raw[point.y][point.x]
	def set(self, point, value):
		for raft in self.rafts:
			if raft.contains( point ):
				raft.set(point, value)
				return
		# self.rafts.append( Raft(self, None))

	def remove( self, point ):
		for raft in self.rafts:
			if raft.contains( point ):
				raft.remove( point )
				break

	def inbounds( self, point ):
		min_x = min( raft.ul.x for raft in self.rafts )
		min_y = min( raft.ul.y for raft in self.rafts )
		max_x = max( raft.lr.x for raft in self.rafts )
		max_y = max( raft.lr.y for raft in self.rafts )
		return min_x <= point.x <= max_x and min_y <= point.y <= max_y

	def dump_program(self, formatted=False):
		max_x = max( cur_pos.x, max( raft.lr.x for raft in self.rafts ) )
		max_y = max( cur_pos.y, max( raft.lr.y for raft in self.rafts ) )

		for y in xrange(max_y + 1):
			linestring = "" 
			for x in xrange(max_x + 1):
				
				if x == cur_pos.x and y == cur_pos.y:
					linestring += '@'
				elif formatted:
					xy_instr = chr(self.get( Point(x,y) ) or 32 )
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
					ch = chr( self.get( Point(x,y) ) or 32 )
					linestring += ch if ch != '\n' else ' '
				
			print linestring.rstrip('\n')
		print "*" * 20



		
class Raft(object):
	def __init__(self,program,point):
		self.cur_dir = 'x'
		self.points = [point]
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

		# Compute bounding box
		max_x = min_x = self.points[0].x
		max_y = min_y = self.points[0].y
		
		for point in self.points:
			if point.x > max_x:
				max_x = point.x
			elif point.x < min_x:
				min_x = point.x

			if point.y > max_y:
				max_y = point.y
			elif point.y < min_y:
				min_y = point.y
		self.ul = Point( min_x, min_y )
		self.lr = Point( max_x, max_y )
		self.points = dict((point - self.ul, program.get(point)) for point in self.points )

	def __repr__(self):
		return "Raft[({},{})-({},{})]".format( self.ul.x, self.ul.y, self.lr.x, self.lr.y )

	def get(self, point):
		return self.points.get( point - self.ul )
	def set( self, point, value ):
		self.points[point - self.ul] = value

	def remove( self, point ):
		point -= self.ul
		del self.points[point]

	@staticmethod
	def _validLocation( value ):
		return not value in (0, 32, ord('o'))

	def contains(self, point):
		point = point - self.ul
		return point in self.points


	def blockedmoving(self, offset):
		newul = self.ul + offset
		newlr = self.lr + offset
		for raft in program.rafts:
			if raft == self:
				continue
			if raft.ul.x > newlr.x or raft.lr.x < newul.x or raft.ul.y > newlr.y or raft.lr.y < newul.y:
				continue
			hit = any( raft.contains( point + newul ) for point in self.points )
			if hit:
				return hit
		return False
	
	def render(self):
		size = self.lr - self.ul
		
		for y in xrange(size.y+1):
			sys.stdout.write("\n|")
			for x in xrange(size.x+1):
				p = Point(x,y)
				if p in self.points:
					sys.stdout.write(chr(self.points[p]))
				else:
					sys.stdout.write(" ")
		sys.stdout.write("\n")

	def move(self):
		global cur_pos

		offset, new_pos_func = { 
			'n': ( Point(0,-1), lambda x: x.n() ),
			's': ( Point(0,1), lambda x: x.s() ),
			'e': ( Point(1,0), lambda x: x.e() ),
			'w': ( Point(-1,0), lambda x: x.w() ),
			'x': ( Point(0,0), lambda x: x)
			 }[self.cur_dir]
		if self.cur_dir != 'x':
			blocked = self.blockedmoving( offset )
			if not blocked:
				if self.contains( cur_pos ):
					cur_pos += offset
				self.ul += offset
				self.lr += offset

			else:
				self.cur_dir = 'x'

def ns(x):
	sys.stdout.softspace = 0
	return x

def hextoint(c):
	try:
		return int(c,16)
	except ValueError:
		return 0

fname = sys.argv[1]
fp = open(fname, 'r')
program = []
cur_dir = 'e'
cur_pos = Point(0,0)
for line in fp:
	if line.find('@') >= 0:
		cur_pos = Point(line.find('@'), len(program))
	l_line = [ord(c) for c in line if not c in "\r\n"]
	if len(l_line) < 80:
		l_line += [32] * (80 - len(l_line))
	program.append(l_line)

memory = [0]
mem_pos = 0

program = Program(program)
program.set( cur_pos, ord('=') )
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
		for raft in program.rafts:
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
		while program.get( cur_pos ) != ord(']') and program.inbounds(cur_pos):
			cur_pos.x += heading
	elif instr == ord(']'):
		if memory[mem_pos] == 0:
			heading = -1
		else:
			heading = 1
		cur_pos.x -= heading
		while program.get(cur_pos) != ord('[') and program.inbounds(scan_pos):
			cur_pos.x -= heading
	elif instr == ord('~'):
		if memory[mem_pos] == 0:
			heading = -1
		else:
			heading = 1
		cur_pos.y += heading
		while program.get(cur_pos) != ord('_') and program.inbounds(scan_pos):
			cur_pos.y += heading
	elif instr == ord('_'):
		if memory[mem_pos] == 0:
			heading = -1
		else:
			heading = 1
		cur_pos.y -= heading
		while program.get(cur_pos) != ord('~') and program.inbounds(scan_pos):
			cur_pos.y -= heading
	elif instr == ord('$'):
		
		if program.get(cur_pos.n()) in (ord('s'), ord('j')):
			scan_pos = Point( cur_pos.x, cur_pos.y-2)
			while program.get(scan_pos) in (0, 32) and program.inbounds(scan_pos):
				scan_pos = scan_pos.n()
			program.remove(scan_pos)
			
		if program.get(cur_pos.s()) in (ord('d'), ord('k')):
			scan_pos = Point(cur_pos.x,cur_pos.y+2)
			while program.get(scan_pos) in (0, 32) and program.inbounds(scan_pos):
				scan_pos = scan_pos.s()
			program.remove(scan_pos)
			
		if program.get(cur_pos.w()) in (ord('a'), ord('h')):
			scan_pos = Point(cur_pos.x-2,cur_pos.y)
			while program.get(scan_pos) in (0, 32) and program.inbounds(scan_pos):
				scan_pos = scan_pos.w()
			program.remove(scan_pos)
			
		if program.get(cur_pos.e()) in (ord('f'), ord('l')):
			scan_pos = Point(cur_pos.x+2,cur_pos.y)
			while program.get(scan_pos) in (0, 32) and program.inbounds(scan_pos):
				scan_pos = scan_pos.e()
			program.remove(scan_pos)
		
	elif instr == ord('a'):
		for raft in program.rafts:
			if raft.contains( cur_pos ):
				raft.cur_dir = 'w'
				break
	elif instr == ord('f'):
		for raft in program.rafts:
			if raft.contains( cur_pos ):
				raft.cur_dir = 'e'
				break
	elif instr == ord('s'):
		for raft in program.rafts:
			if raft.contains( cur_pos ):
				raft.cur_dir = 'n'
				break
	elif instr == ord('d'):
		for raft in program.rafts:
			if raft.contains( cur_pos ):
				raft.cur_dir = 's'
				break
	elif instr == ord('x'):
		for raft in program.rafts:
			if raft.contains( cur_pos ):
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
	for raft in program.rafts:
		raft.move()

program.dump_program()
print cur_pos