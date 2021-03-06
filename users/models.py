# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User, UserManager

# Create your models here.
class SessionManager(models.Manager):
    def create_session(self, user, name, date, time, files, data):
        session = self.model(user=user, name=name, date=date, time=time, files=files, data=data)
        session.save()
        return session
        
class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null = True)
    date = models.DateField()
    time = models.TimeField()
    name = models.CharField(verbose_name="Session Name", max_length=50)
    files = models.TextField(verbose_name="File Names", max_length=50)
    data = models.TextField(verbose_name="File Data")
    objects = SessionManager()

