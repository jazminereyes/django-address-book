from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', auth_views.LoginView.as_view(), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    url(r'^register/$', views.register, name='register'),
    url(r'^home/$', views.index, name='index'),
    url(r'^contact/', include([
        url(r'^add/$', views.add_contact, name='add_contact'),
        url(r'^import/$', views.import_contact, name='import_contact'),
        url(r'^export/$', views.export_contact, name='export_contact'),
    ])),
    url(r'^contact/(?P<contact_id>[0-9]+)/', include([
        url(r'^edit/$', views.edit_contact, name='edit_contact'),
        url(r'^delete/$', views.delete_contact, name='delete_contact')
    ]))
]