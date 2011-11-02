from django.conf.urls.defaults import *

urlpatterns = patterns('website.ticktactoad.views',
	(r'^api/$','api'),
	#Pass throughs for some static files just for ease
	(r'^js/(?P<filename>.+).js$','link_file',{'type':'js'}),
	(r'^img/(?P<filename>.+).jpg$','link_file',{'type':'jpeg'}),
	(r'^img/(?P<filename>.+).png$','link_file',{'type':'png'}),
	(r'^img/(?P<filename>.+).gif$','link_file',{'type':'gif'}),
	(r'^css/(?P<filename>.+).css$','link_file',{'type':'css'}),
	(r'^game/(?P<gameboard_id>.+)/$','game_on'),
)