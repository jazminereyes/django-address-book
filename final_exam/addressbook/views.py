# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv, logging, io

from django.utils.encoding import smart_str
from django.shortcuts import render, redirect, reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm

from .models import Contact
from .forms import ContactForm, DataForm

# Create your views here.
def index(request):
    contact = Contact.objects.filter(user=request.user)
    return render(request, 'addressbook/home.html', {'contact': contact})

def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('index')
    else: 
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required(login_url='/')
def add_contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
            return redirect('index')
    else:
        form = ContactForm()
    return render(request, 'addressbook/contact_detail.html', {'form': form})

@login_required(login_url='/')
def edit_contact(request, contact_id):
    contact = Contact.objects.get(pk=contact_id)
    if request.method == "POST":
        form = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            contact = form.save(commit=False)
            contact.user = request.user
            contact.save()
            return redirect('index')
    else:
        form = ContactForm(instance=contact)
    return render(request, 'addressbook/contact_detail.html', {'form': form})

@login_required(login_url='/')
def delete_contact(request, contact_id):
    contact = Contact.objects.get(pk=contact_id)
    if request.method == "POST":
        contact.delete()
        return redirect('index')
    else:
        return render(request, 'addressbook/contact_confirm.html', {'contact': contact})

@login_required(login_url='/')
def import_contact(request):
    if request.method == "POST":
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
                    Contact.objects.create(user=request.user, first_name=contact['FirstName'], last_name=contact['LastName'], contact_number=contact['ContactNo'], address=contact['Address'])
            
            return redirect('index')
        
    else:
        form = DataForm()
        return render(request, 'addressbook/contact_import.html', {'form': form})

@login_required(login_url='/')
def export_contact(request):
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