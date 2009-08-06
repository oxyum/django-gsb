import datetime
from urllib import urlencode
import urllib2
import re

from django.conf import settings
from django.db import models, transaction

from gsb.managers import KeyManager

BL_HEADER_RE = re.compile(ur"""\[(?P<name>[a-z-]+)\ (?P<major>\d+)\.(?P<minor>\d+)(\ (?P<update>update))?\]""")

class Key(models.Model):
    key = models.CharField(max_length=30, primary_key=True)
    length = models.PositiveIntegerField()
    value = models.CharField(max_length=50)

    objects = KeyManager()

    def __unicode__(self):
        return '%s' % (self.key,)

class List(models.Model):
    name = models.CharField(max_length=30, unique=True)
    major = models.PositiveIntegerField(default=1)
    minor = models.IntegerField(default=-1)
    update_time = models.DateTimeField()

    errors = models.PositiveSmallIntegerField(default=0)
    next_update = models.DateTimeField()


    def _is_active(self):
        return False
    _is_active.boolean = True
    _is_active.short_description = 'Is active'
    is_active = property(_is_active)

    @transaction.commit_on_success
    def _error(self):
        if self.errors < 5:
            self.errors += 1

        if self.errors in (1, 2,):
            self.next_update = datetime.datetime.now()+datetime.timedelta(minutes=1)
        elif self.errors == 3:
            self.next_update = datetime.datetime.now()+datetime.timedelta(minutes=60)
        elif self.errors == 4:
            self.next_update = datetime.datetime.now()+datetime.timedelta(minutes=180)
        else:
            self.next_update = datetime.datetime.now()+datetime.timedelta(minutes=360)
        return self.save()

    @transaction.commit_on_success
    def _update(self, header, lst):
        try:
            if header['update'] is None:
                self.records.all().delete()

            for rec in lst.readlines():
                rec = rec.strip()
                if len(rec) != 33:
                    continue
                if rec[0] == '+':
                    self.records.create(hash=rec[1:])
                elif rec[0] == '-':
                    self.records.filter(hash=rec[1:]).delete()
                else:
                    raise ValueError

            self.major = int(header['major'])
            self.minor = int(header['minor'])
            self.errors = 0
            self.update_time = datetime.datetime.now()
            self.next_update = datetime.datetime.now()+datetime.timedelta(seconds=settings.GSB_UPDATE_INTERVAL)
            return self.save()
        except:
            return self._error()

    def update(self, secure=None, keys={}):
        """Update GSB list from Google server.

        Arguments:
        - `secure`:
            * False - do not use secure list update
            * None  - check wrapped key in DB
            * True  - use keys from keys param
        - `keys`: dict with keys
        """
        """
        http://sb.google.com/safebrowsing/update?client=api&apikey=<yourkey>&version=goog-black-
        hash:1:179&wrkey=MTrILkq3LDJtWp8V8zHJaJc2
        """
        uri = """http://sb.google.com/safebrowsing/update"""
        params = urlencode((
            ('client','api'),
            ('apikey', settings.GSB_API_KEY),
            ('version', "%s:%d:%d" % (self.name, self.major, self.minor))
        ))
        lst = urllib2.urlopen("%s?%s" % (uri, params))
        if lst.code == 200:
            header = lst.readline()
            header = BL_HEADER_RE.match(header)
            if header is not None:
                header = header.groupdict()
                if header['name'] == self.name:
                    return self._update(header, lst)
        return self._error()

    def __unicode__(self):
        return '%s %d:%d' % (self.name, self.major, self.minor, )

class Record(models.Model):
    list = models.ForeignKey('gsb.List', related_name='records')
    hash = models.CharField(max_length=32, db_index=True)
