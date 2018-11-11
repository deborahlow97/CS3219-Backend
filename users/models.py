# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Session(models.Model):
    email = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    name = models.CharField(verbose_name="Session Name", max_length=50)
    files = models.TextField(verbose_name="File Names", max_length=50)
    data = models.TextField(verbose_name="File Data")

