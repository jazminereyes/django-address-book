# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv, logging, io

from django.utils.encoding import smart_str
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from django.utils.decorators import method_decorator

from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.edit import FormView, CreateView, DeleteView, UpdateView
from django.views.generic.list import MultipleObjectMixin

from .models import Contact
from .forms import ContactForm, DataForm

# Create your views here.
class RegisterView(View):
    template_name = 'registration/register.html'
    form_class = UserCreationForm

    def get(self, request, *args, **kwargs):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
        else:
            return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name='dispatch')
class ContactListView(ListView):
    model = Contact
    context_object_name = 'contact_list'
    template_name = 'addressbook/home.html'
    paginate_by = 10

    def get_queryset(self):
        return Contact.objects.filter(user=self.request.user)

class AjaxableResponseMixin(object):

    def form_invalid(self, form):
        response = super(AjaxableResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return JsonResponse(form.errors, status=400)
        else:
            return response

    def form_valid(self, form):
        response = super(AjaxableResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
            }
            return JsonResponse(data)
        else:
            return response

@method_decorator(login_required, name='dispatch')
class ContactCreate(AjaxableResponseMixin, CreateView):
    model = Contact
    fields = ['first_name', 'last_name', 'contact_number', 'address']
    success_url = '/home/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ContactCreate, self).form_valid(form)

@method_decorator(login_required, name='dispatch')
class ContactUpdate(AjaxableResponseMixin, UpdateView):
    model = Contact
    fields = ['first_name', 'last_name', 'contact_number', 'address']
    template_name = 'addressbook/contact_detail.html'
    success_url = '/home/'

@method_decorator(login_required, name='dispatch')
class ContactDelete(DeleteView):
    model = Contact
    success_url = '/home/'

@method_decorator(login_required, name='dispatch')
class ContactImport(View):
    template_name = 'addressbook/contact_import.html'
    form_class = DataForm

    def get(self, request, *args, **kwargs):
        form = self.form_class
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = DataForm(request.POST, request.FILES)

        csv_file = request.FILES['file_contacts']

        if not csv_file.name.endswith('.csv'):
            messages.error(request,'File is not CSV type')
            return HttpResponseRedirect(reverse('import_contact'))
        
        if csv_file.multiple_chunks():
            messages.error(request,"Uploaded file is too big (%.2f MB)." % (csv_file.size/(1000*1000),))
            return HttpResponseRedirect(reverse('import_contact'))

        if form.is_valid():
            f = io.TextIOWrapper(form.cleaned_data['file_contacts'].file)
            reader = csv.DictReader(f)
               
            for contact in reader:
                obj_value = Contact.objects.filter(user=request.user, first_name=contact['FirstName'], last_name=contact['LastName'], contact_number=contact['ContactNo'], address=contact['Address'])

                if not obj_value:
                    if len(contact['ContactNo']) > 13:
                        messages.error(request,"Invalid contact number for %s %s" % (contact['FirstName'], contact['LastName']))
                        return HttpResponseRedirect(reverse('import_contact'))
                    else:
                        Contact.objects.create(user=request.user, first_name=contact['FirstName'], last_name=contact['LastName'], contact_number=contact['ContactNo'], address=contact['Address'])
            
            return redirect('index')
 
@method_decorator(login_required, name='dispatch')
class ContactExport(View):

    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=address-book.csv'
        writer = csv.writer(response, csv.excel)
        writer.writerow([
            smart_str(u"FirstName"),
            smart_str(u"LastName"),
            smart_str(u"ContactNo"),
            smart_str(u"Address"),
        ])
        contacts = Contact.objects.filter(user=request.user)
        for data in contacts:
            writer.writerow([
                smart_str(data.first_name),
                smart_str(data.last_name),
                smart_str(data.contact_number),
                smart_str(data.address),
            ])
        return response