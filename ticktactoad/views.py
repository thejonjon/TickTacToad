# Create your views here
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson as json
from django.conf import settings

from website.ticktactoad.models import *
from datetime import datetime

class APIResponse(object):
	"""
	this class is a wrapper for my standard API response formats
	more comments soon
	"""
	def __init__(self,status=None,message=None,**kwargs):
		self.return_data = { }
		for k,v in kwargs.items():
			self.return_data[k] = v
		if status:
			self.result = "success"
		else:
			self.result = "error"
			if not self.return_data.has_key('suggestion'):
				self.return_data['suggestion'] = "home"
		if message:
			self.message = message
	def __repr__(self):
		try:
			return json.dumps(dict({"result":self.result,"message":self.message}.items()+self.return_data.items()))
		except:
			raise
	
#Shortcut functions		
def _u(data):
	#Shortcut for calling unicode()
	return unicode(data)
	
def link_file(request,filename=None,**kwargs):
	"""
		This function is basically a little pass through for required
		static files... It could be taken out when run on a real server that can host static files
	"""
	print filename
	
	if kwargs['type'] == "css":
		mimetype = "text/css"
	elif kwargs['type'] == "png":
		mimetype="image/png"
		fbin = open(settings.TEMPLATE_DIRS[0]+'/resources/img/'+filename+".png",'r');
		return HttpResponse(fbin.read(), mimetype=mimetype)
	elif kwargs['type'] == "jpeg":
		mimetype="image/jpeg"
		fbin = open(settings.TEMPLATE_DIRS[0]+'/resources/img/'+filename+".jpg",'r');
		return HttpResponse(fbin.read(), mimetype=mimetype)
	elif kwargs['type'] == "gif":
		mimetype="image/gif"
		fbin = open(settings.TEMPLATE_DIRS[0]+'/resources/img/'+filename+".gif",'r');
		return HttpResponse(fbin.read(), mimetype=mimetype)
	else:
		mimetype = "text/html"
	return render_to_response("resources/"+kwargs['type']+"/"+filename+"."+kwargs['type'],mimetype=mimetype)
	
def index(request,message=None):
	if request.GET.has_key("message"):
		message = request.GET['message']
	return render_to_response('index.html',{'message':message})

def game_on(request,gameboard_id=False):
	try:
		gb = ToadBoard(get_object_or_404(GameBoard,pk=gameboard_id))
	except:
		return HttpResponseRedirect("/?message=Invalid+Game")
		
	return render_to_response('game_on.html',{'gameboard':gb,"my_id":int(request.session['player_id'])})

@csrf_exempt
def api(request):
	"""
	api call hub. Distributes api calls to their isolated functions
	always returns an APIResponse object. All valid requests should
	include a POST (or GET) action and a JSON encoded data field
	"""
	
	
	#rd stands for requestdata
	if request.method=="POST": rd = request.POST
	else: rd = request.GET
	
	for a in ['action','data']:
		if not a in rd:
			return HttpResponse(_u(APIResponse(False,"Invalid API Request. data is a required field.")))
	
	#Decode the data field
	try:
		data = json.loads(rd['data'])
	except:
		return HttpResponse(_u(APIResponse(False,"Invalid JSON",data=_u(rd['data']))))
	
	#General validation-----
	if rd['action'].lower() in ['find_players','short_poll','play']:
		try:
			gb = ToadBoard(get_object_or_404(GameBoard,pk=data['game_id']))
		except:
			return HttpResponse(APIResponse(False,"GameBoard Not Found: "+str(data['game_id'])))
		
		#Disabled for dev
		"""
		try:
			player = get_object_or_404(Player,pk=request.session['player_id'])
		except:
			return HttpResponse(APIResponse(False,"Invalid Player",suggestion="home"))
		"""
	#stuff simply used to make lines shorter for the actual api routing
	stuff = [request,rd['action'],data]
	
	#Acceptable action routing "We will start with the non-game ones"
	if rd['action'] == "vs_computer":
		return HttpResponse(_u(api_new_game("computer",*stuff)))
	elif rd['action'] == "play":
		return HttpResponse(_u(api_play(*stuff)))
	
	#Catch all-- action was not valid
	return HttpResponse(_u(APIResponse(False,"Invalid API Request"+str(stuff))))
def api_new_game(vs,request,action,data):
	if not request.session:
		request.session = { }
	if not data.has_key("name"):
		return APIResponse(False,"Required Field Missing")
	
	p = Player()
	p.game_piece = "X"
	p.save()
	
	if vs == "computer":
		pp = Player()
		pp.is_computer = True
		pp.game_piece = "O"
		pp.save()
		request.session['player_id'] = pp.id
		request.session.save()
	else:
		pp = get_object_or_404(Player,pk=vs)
	gb = GameBoard()
	gb.save()
	gb.players.add(p)
	gb.players.add(pp)
	gb = ToadBoard(gb)
	gb.save()
	
	try:
		gb.start_game()
	except Error as e:
		return APIResponse(False,str(e.value),game_id=str(gb))
	gb.save()
	return APIResponse(True,"Loading Game",game_id=str(gb))

def api_play(request,action,data):
	"""
	A user is trying to make a move....
	We are going to validate all the info-- then make sure it's their
	turn and they're aloud on the board....
	Then attempt to play what they want to play--- and make sure it works
	
	But since the user is going to get the updates through the short
	poll request, we won't force an update to the gameboard just yet
	plus that way it'll look like a computer player is thinking....
	"""
	
	#Validation----------------
	for a in ['tile','game_id',]:
		if not a in data:
			return APIResponse(False,"Required Field Missing: "+_u(a))
	player = get_object_or_404(Player,pk=request.session['player_id'])
	gb = ToadBoard(get_object_or_404(GameBoard,pk=data['game_id']))
	
	#Attempt to play the piece
	try:
		tile = int(data['tile'].replace("tile_",""))
	except:
		return APIResponse(False,"Invalid Tile Selection")
	try:
		print "Current Player now: "+ str(gb.current_player())
		gb.set_square(player,tile)
		is_it_completed = gb.detect_win(player,tile)
	except Error as e:
		return APIResponse(False,"Error: "+str(e.value))	
	if is_it_completed:
		toplay=-1
	else:
		try:
			player = gb.current_player()
			toplay = player.play(gb)
			print "-------------"
			print "-------------"
			print "-------------"
			print "I WILL PLAY: "+str(toplay)
			if toplay:
				gb.set_square(player,toplay)
				is_it_completed = gb.detect_win(player,toplay)
			else:
				is_it_completed = "yes: TIE GAME!"
		except Error as e:
			return APIResponse(False,"Error: "+str(e.value))
		
	if is_it_completed: is_it_completed = str(is_it_completed)
	gb.save()
	return APIResponse(True,"Well Played", board = gb.board,last_move=toplay, won=is_it_completed) #Snarky message
	
