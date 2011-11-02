from django.db import models
from django.utils import simplejson as json
import exceptions
import random

#from errors import *
class Error(Exception):
	"""Error Exception Class"""
	_errors ={ }
	def __init__(self,err,**kwargs):
		"""test"""
		self.debug = True
		
		self.vars = kwargs
		if self._errors.has_key(err):
			self.value = err+": "+self._errors[err]
		else:
			self.value = err
			
		if self.debug:
			print "-----Exception: "+self.__doc__+"-------"
			ret = self.value
			if self.vars:
				ret+="\nVarDump: "+str(self.vars.items())
			print ret
			print "-----------"
	def __repr__(self):
		ret = self.value
		if self.vars:
			ret+="\nVarDump: "+str(self.vars.items())
		return ret
		
class GameBoardError(Error):
	"""Exception: GameBoardError"""
	_errors = {
		'ToManyPlayers':'You Have To Many Players',
		'NotEnoughPlayers':"You need at least 2 players to start the game!",
		'OffBoard':"You need to choose a location on the game board!",
		'NotYourTurn':"It is not your turn",
		'InvalidBoardJSON':"Invalid JSON board data",
	}
	
class APIError(Error):
	"""Exception: API Error"""
	_errors = {
		'GameBoardNotFound':'Not A Valid Game Board',
	}


class Player(models.Model):
	"""Player class-- Even though a Player is more of an 'actor'
	in a given game (being that the same physical player would actually
	play more then one player) seperated out since I'm not quite 
	comfortable with making children django models right now"""
	id = models.AutoField(primary_key=True)
	name = models.CharField(max_length=40)
	game_piece = models.CharField(max_length=40)
	last_poll = models.DateTimeField(auto_now_add=True)
	is_computer = models.BooleanField()
	is_computer.default = False
	def __unicode__(self):
		return str(self.id)
	def play(self,gb=None):
		#Totally an AEye function--- decide where to play...
		if not gb:
			bb = ToadBoard(self.board.all()[0])
		else:
			bb = gb
		empty_spots = bb.get_empty()
		print "Emtpy: " +str(empty_spots)
		print "Okay-- how about spot #4 for the other player: "+str(gb.move_points([i for i in gb.gb.players.all() if str(i) != str(self)][0],4))
		
		for loc in empty_spots:
			if int(gb.move_points([i for i in gb.gb.players.all() if str(i) == str(self)][0],loc)) >= int(gb.gb.size)-1:
				print "Offensive move: " + str(loc)
				return loc
		for loc in empty_spots:
			if int(gb.move_points([i for i in gb.gb.players.all() if str(i) != str(self)][0],loc)) >= int(gb.gb.size)-1:
				print "Defensive move: " + str(loc)
				return loc
		if 5 in empty_spots:
			print "Grab the middle: 5"
			return 5
		else:
			for loc in [1,3,7,9]:
				if loc in empty_spots:
					print "Get corners to be save: "+str(loc)
					return loc
			for loc in empty_spots:
				print "For lack of a better idea: "+str(loc)
				return loc
		print "The game must be over..."
		return False
		return empty_spots[0]
	def __str__(self):
		return str(self.id)
class GameBoard(models.Model):
	"""GameBoard Class-- perhapse to be overloaded later
	This class holds the global variables of any game"""
	
	id = models.AutoField(primary_key=True)
	creation_datetime = models.DateTimeField(auto_now_add=True)
	players = models.ManyToManyField(Player,related_name="board")
	turn = models.IntegerField(default=0)
	
	#Is the game running?
	flag_running = models.BooleanField()
	flag_running.default = False
	
	#Completed is either False or set to the player who won.
	flag_completed =  models.ForeignKey(Player,null=True,blank=True)
	
	#JSON string-- to access the object call GameBoard.board
	#It's a simple array of self.size... with indexes equal to 
	#player IDs
	board_data = models.CharField(max_length=200, blank=True)
	
	
	#The following functions are hard coded to defaults--- but are
	#left to variables for future abstraction of the this class
	size = models.IntegerField(default=3)
	max_players = models.IntegerField(default=2)
	debug = True
	def __unicode__(self):
		return str(self.id)
		
	"""Overloaded __functions__ functions"""
	"""
	def save(self, *args, **kwargs):
		if not super(GameBoard,board) is None:
			self.board_data = str(json.dumps(super(GameBoard,self).board))
			#except:
			#	raise GameBoardError("InvalidBoardJSON")
		super(GameBoard, self).save(*args, **kwargs) # Call the "real" save() method.
		
	def __getattr__(self,name):
		print "FETCHING SOMETHING: "+str(name)
		if name == "board":
			try:
				return self.__getattribute__(name)
			except:
				try:
					super(GameBoard,self).__setattr__(name, json.loads(str(self.board_data)))
				except:
					raise GameBoardError("InvalidBoardJSON")
			return self.__getattribute__(name)
		else:
			return self.__getattribute__(name)
	"""
	
	
class ToadBoard(object):
	def __init__(self,gb = None):
		if not gb:
			raise GameBoardError("No Gameboard Loaded")
		self.gb = gb
		self.board = None
		try:
			self.board = json.loads(self.gb.board_data)
		except:
			pass
	
	"""Sort of Win condition detections-- All take in a tile location
	and return how many points that location has before it's played"""
	def _vertical_points(self,p,loc):
		"""Point test for verictal plays"""
		points = 0
		for i in range((int(loc-1)%3)+1,(self.gb.size*self.gb.size)+1,int(self.gb.size )):
			if loc == i: continue
			if str(p) == str(self.board[i-1]):
				points+=1
			else:
				print str(self.board[i-1])
		return points
		
	def _horizontal_points(self,p,loc):
		"""Point test for verictal plays"""
		points = 0
		for i in range(int(int((loc-1)/3)*self.gb.size)+1,int(int((loc-1)/3)*self.gb.size)+int(self.gb.size)+1):
			if loc == i: continue
			if str(p) == str(self.board[i-1]):
				points+=1
			else:
				print str(self.board[i-1])
		return points
	
	def _diag_points(self,player,loc):
		"""Do a point test for both diagnals Gross but I thought I would
		waste to much time thinking to hard about it-- just made 2 modes"""
		#for i in range(1,(self.gb.size*self.gb.size)+1,int(self.gb.size+1)):
		#	#1,5,9
		#for i in range(int(self.gb.size),(self.gb.size*self.gb.size)-1,int(self.gb.size)-1):
		#	#3,5,7
		
		if not loc in [1,3,5,7,9]:
			return 0
		points = 0
		if loc in [1,5,9]:
			for loc2 in [1,5,9]:
				if loc == loc2: continue
				if str(player) == str(self.board[loc2-1]):
					points+=1
			print "DIAG POINTs0:"+str(points)
		
		points2=0
		if loc in [3,5,7]:
			for loc2 in [3,5,7]:
				if loc == loc2: continue
				if str(player) == str(self.board[loc2-1]):
					points2+=1
			print "DIAG POINTs2:"+str(points2)
		
		if points2>=points:
			return points2
		return points
		
	"""Utility Functions"""
	def i_from_c(self,y,x):
		""" Come up with tile number
		takes in: y,x cord (1,1 is top left)
		returns: tile location on the board"""
		if x < 1 or y < 1 or x > self.gb.size or y > self.gb.size:
			raise GameBoardError("OffBoard",x=x,y=y)
		index = (self.gb.size * y)-self.gb.size
		index+=x
		return index
		
	def c_from_i(self,index):
		""" Come up with y,x cords from the tile number
		takes in: tile space (self.board index +1)
		returns: y,x location on the board"""
		if index>len(self.board) or index < 1:
			raise GameBoardError("OffBoard")
		
		y,x = 1,index
		while x > self.gb.size:
			y+=1
			x = x - self.gb.size
		return int(y),int(x)
	def get_empty(self):
		"""Return a list of empty tiles"""
		return [i+1 for i,v in enumerate(self.board) if not v]
	
	"""Specific Utility for a 2 player game board"""
	def current_player(self):
		"""Return the player of whom is currently up"""
		return self.gb.players.all()[(self.gb.turn+1)%self.gb.players.count()]
		
	"""Specific to a 3*3 game board win detection"""
	def detect_win(self,player,loc=False):
		"""This function is for the gameboard to self-check the board
		to see if anyone has won yet..."""
		if self.move_points(str(player),loc) == int(self.gb.size)-1:
			self.gb.flag_completed = player
			self.gb.flag_running = False
			self.save()
		elif len(self.get_empty())==0:
			self.gb.flag_running=False
			self.save()
		return self.gb.flag_completed
	
	"""Abstract GameBoad Functions"""		
	def start_game(self):
		"""Start a game that has not been started yet"""
		if self.gb.flag_running:
			raise GameBoardError("CanNotStartGame")
		elif self.gb.players.count()>self.gb.max_players:
			raise GameBoardError("ToManyPlayers",playercount=self.gb.players.count())
		elif self.gb.players.count()<2:
			raise GameBoardError("NotEnoughPlayers")
			
		self.board = [False for i in range(0,self.gb.size*self.gb.size)]
		
		self.gb.flag_running = True
		self.gb.turn = 0
		self.save()
		
	def move_points(self,player,loc):
		player=str(player)
		"""Return the highest number of points that any move generated"""
		points = 0
		debug = False
		print "testing location: "+ str(loc)
		p = self._diag_points(str(player),loc)
		if debug: print "Diag1 points: "+str(p)
		if p > points: points = p
		
		p = self._horizontal_points(str(player),loc)
		if debug: print "whore points: "+str(p)
		if p > points: points = p
		
		p = self._vertical_points(str(player),loc)
		if debug: print "vert points: "+str(p)
		if p > points: points = p
		
		print "going with: "+str(points) + "At location: "+str(loc)
		return points
	
	"""Kind of specific to TickTacToe-- since it calls wincondition
	but otherwise just do error handling and set an attempted play"""
	def set_square(self,player,loc):
		"""Attempts to set square located at loc to the player"""
		print self.gb.flag_running
		if loc < 1 or loc > len(self.board):
			raise GameBoardError("OffBoard",loc=loc)
		elif not self.gb.flag_running:
			raise GameBoardError("NotRunning")
		elif self.board[loc-1]:
			raise GameBoardError('Illegal Play: Space Taken By: '+str(self.board[loc-1]), loc=loc)
		elif not str(player) == str(self.current_player()):
			raise GameBoardError("NotYourTurn",player=str(player))
		else:
			self.board[loc-1] = str(player)
		
		#self.detect_win(player,loc)
		self.gb.turn+=1
			
	def save(self):
		self.gb.board_data = str(json.dumps(self.board))
		self.gb.save()
		self.board = json.loads(self.gb.board_data)
	def __unicode__(self):
		return str(self.gb)
	def __repr__(self):
		return str(self.gb)
