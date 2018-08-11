# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

class Case(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    court = models.CharField(max_length=60)
    description = models.CharField(max_length=1024)
    def __unicode__(self):
        return self.description
