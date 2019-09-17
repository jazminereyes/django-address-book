# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv, logging, io

from django.utils.encoding import smart_str
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
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

@method_decorator(login_required, name='dispatch')
class ContactCreate(CreateView):
    model = Contact
    fields = ['first_name', 'last_name', 'contact_number', 'address']
    success_url = '/home/'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(ContactCreate, self).form_valid(form)

@method_decorator(login_required, name='dispatch')
class ContactUpdate(UpdateView):
    model = Contact
    fields = ['first_name', 'last_name', 'contact_number', 'address']
    pk_url_kwarg = 'contact_id'
    success_url = '/home/'

@method_decorator(login_required, name='dispatch')
class ContactDelete(DeleteView):
    model = Contact
    pk_url_kwarg = 'contact_id'
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


# Function-based Views
# def register(request):
#     if request.method == "POST":
#         form = UserCreationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get('username')
#             raw_password = form.cleaned_data.get('password1')
#             user = authenticate(username=username, password=raw_password)
#             login(request, user)
#             return redirect('index')
#     else: 
#         form = UserCreationForm()
#     return render(request, 'registration/register.html', {'form': form})

# @login_required(login_url='/')
# def index(request):
#     contact_list = Contact.objects.filter(user=request.user)

#     paginator = Paginator(contact_list, 10)

#     page = request.GET.get('page')

#     try:
#         contact = paginator.page(page)
#     except PageNotAnInteger:
#         contact = paginator.page(1)
#     except EmptyPage:
#         contact = paginator.page(paginator.num_pages)

#     return render(request, 'addressbook/home.html', {'contact': contact})

# @login_required(login_url='/')
# def add_contact(request):
#     if request.method == "POST":
#         form = ContactForm(request.POST)
#         if form.is_valid():
#             contact = form.save(commit=False)
#             contact.user = request.user
#             contact.save()
#             return redirect('index')
#     else:
#         form = ContactForm()
#     return render(request, 'addressbook/contact_detail.html', {'form': form})

# @login_required(login_url='/')
# def edit_contact(request, contact_id):
#     contact = Contact.objects.get(pk=contact_id)
#     if request.method == "POST":
#         form = ContactForm(request.POST, instance=contact)
#         if form.is_valid():
#             contact = form.save(commit=False)
#             contact.user = request.user
#             contact.save()
#             return redirect('index')
#     else:
#         form = ContactForm(instance=contact)
#     return render(request, 'addressbook/contact_detail.html', {'form': form})

# @login_required(login_url='/')
# def delete_contact(request, contact_id):
#     contact = Contact.objects.get(pk=contact_id)
#     if request.method == "POST":
#         contact.delete()
#         return redirect('index')
#     else:
#         return render(request, 'addressbook/contact_confirm.html', {'contact': contact})

# @login_required(login_url='/')
# def import_contact(request):
#     if request.method == "POST":
#         form = DataForm(request.POST, request.FILES)

#         csv_file = request.FILES['file_contacts']

#         if not csv_file.name.endswith('.csv'):
# 			messages.error(request,'File is not CSV type')
# 			return HttpResponseRedirect(reverse('import_contact'))
        
#         if csv_file.multiple_chunks():
# 			messages.error(request,"Uploaded file is too big (%.2f MB)." % (csv_file.size/(1000*1000),))
# 			return HttpResponseRedirect(reverse('import_contact'))

#         if form.is_valid():
#             f = io.TextIOWrapper(form.cleaned_data['file_contacts'].file)
#             reader = csv.DictReader(f)
               
#             for contact in reader:
#                 obj_value = Contact.objects.filter(user=request.user, first_name=contact['FirstName'], last_name=contact['LastName'], contact_number=contact['ContactNo'], address=contact['Address'])

#                 if not obj_value:
#                     if len(contact['ContactNo']) > 13:
#                         messages.error(request,"Invalid contact number for %s %s" % (contact['FirstName'], contact['LastName']))
#                         return HttpResponseRedirect(reverse('import_contact'))
#                     else:
#                         Contact.objects.create(user=request.user, first_name=contact['FirstName'], last_name=contact['LastName'], contact_number=contact['ContactNo'], address=contact['Address'])
            
#             return redirect('index')
        
#     else:
#         form = DataForm()
#         return render(request, 'addressbook/contact_import.html', {'form': form})

# @login_required(login_url='/')
# def export_contact(request):
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename=address-book.csv'
#     writer = csv.writer(response, csv.excel)
#     writer.writerow([
#         smart_str(u"FirstName"),
#         smart_str(u"LastName"),
#         smart_str(u"ContactNo"),
#         smart_str(u"Address"),
#     ])
#     contacts = Contact.objects.filter(user=request.user)
#     for data in contacts:
#         writer.writerow([
#             smart_str(data.first_name),
#             smart_str(data.last_name),
#             smart_str(data.contact_number),
#             smart_str(data.address),
#         ])
#     return response