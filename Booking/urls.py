from django.conf.urls import url
from . import views


app_name = 'Booking'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login, name='login'),
    url(r'^logout/$', views.logout, name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^dashboard/(?P<guest_id>[0-9]+)/$', views.dashboard, name='dashboard'),
    url(r'^manageprojects/(?P<manager_id>[0-9]+)/$', views.managerOp, name='manageOp'),
    url(r'^homer/$', views.homer, name='homer'),
    url(r'^registration/$', views.registration, name='registration'),
    url(r'^manager/(?P<manager_id>[0-9]+)/$', views.manager, name='manager'),
    url(r'^lookingup/(?P<manager_id>[0-9]+)/$', views.lookingup, name='lookingup'),
    url(r'^updating/(?P<manager_id>[0-9]+)/$', views.updating, name='updating'),
    url(r'^guest/(?P<guest_id>[0-9]+)/$', views.guest, name='guest'),
    url(r'^datacenter/(?P<manager_id>[0-9]+)/$', views.data_center, name='data_center'),
    url(r'^friends/(?P<guest_id>[0-9]+)/$', views.friends, name='friends'),
    url(r'^apply/(?P<guest_id>[0-9]+)/(?P<opportunity_id>[0-9]+)/$', views.applying, name='applying'),
    url(r'^clearapplying/(?P<guest_id>[0-9]+)/(?P<opportunity_id>[0-9]+)/$', views.clear_applying, name='clear_applying'),
    url(r'^search/(?P<guest_id>[0-9]+)/$', views.search, name='search'),
    url(r'^connect/(?P<guest_id>[0-9]+)/(?P<connection_id>[0-9]+)/$', views.connect, name='connect'),
    url(r'^disconnect/(?P<guest_id>[0-9]+)/(?P<friend_id>[0-9]+)/$', views.disconnect, name='disconnect'),
    url(r'^profile/(?P<guest_id>[0-9]+)/$', views.profile, name='profile'),
    url(r'^update/(?P<guest_id>[0-9]+)/$', views.update, name='update'),
    url(r'^searching/(?P<guest_id>[0-9]+)/$', views.searching, name='searching'),
    url(r'^projectlist/(?P<guest_id>[0-9]+)/$', views.projectList, name='projectlist'),
    url(r'^addOpportunity/(?P<manager_id>[0-9]+)', views.addOpportunity, name='addOpportunity'),
    url(r'^reserveGame/(?P<guest_id>[0-9]+)', views.reserveGame, name='reserveGame'),

]
