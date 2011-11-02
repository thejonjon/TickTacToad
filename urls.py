from django.conf.urls.defaults import patterns, include, url

urlpatterns = patterns('',
	(r'^$', 'website.ticktactoad.views.index'),
	(r'^api/$','website.ticktactoad.views.api'),
	
	#Pass throughs for some static files just for ease
	(r'^js/(?P<filename>.+).js$','website.ticktactoad.views.link_file',{'type':'js'}),
	(r'^img/(?P<filename>.+).jpg$','website.ticktactoad.views.link_file',{'type':'jpeg'}),
	(r'^img/(?P<filename>.+).png$','website.ticktactoad.views.link_file',{'type':'png'}),
	(r'^img/(?P<filename>.+).gif$','website.ticktactoad.views.link_file',{'type':'gif'}),
	(r'^css/(?P<filename>.+).css$','website.ticktactoad.views.link_file',{'type':'css'}),
	(r'^game/(?P<gameboard_id>.+)/$','website.ticktactoad.views.game_on'),
)
