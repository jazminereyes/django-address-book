from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from . import views
from .views import RegisterView, ContactListView, ContactCreate, ContactImport, ContactExport, ContactUpdate, ContactDelete

urlpatterns = [
    url(r'^$', auth_views.LoginView.as_view(), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^home/$', ContactListView.as_view(), name='index'),
    url(r'^contact/', include([
        url(r'^add/$', ContactCreate.as_view(), name='add_contact'),
        url(r'^import/$', ContactImport.as_view(), name='import_contact'),
        url(r'^export/$', ContactExport.as_view(), name='export_contact'),
    ])),
    url(r'^contact/(?P<pk>[0-9]+)/', include([
        url(r'^$', ContactUpdate.as_view(), name='edit_contact'),
        url(r'^delete/$', ContactDelete.as_view(), name='delete_contact')
    ]))
]