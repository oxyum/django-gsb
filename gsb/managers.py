import urllib2
from django.db import models

class KeyManager(models.Manager):

    def update_keys(self):
        self._getkey()

    def _getkey(self):
        uri = """https://sb-ssl.google.com/safebrowsing/getkey?client=api"""
        keys = urllib2.urlopen(uri)
        if keys.code == 200:
            qs = self.get_query_set()
            for key in keys.readlines():
                key = key.strip().split(':')
                new_key, created = qs.get_or_create(
                    key = key[0],
                    defaults={
                        'length': key[1],
                        'value': key[2]
                        })
                if not created:
                    new_key.length=key[1]
                    new_key.value=key[2]
                    new_key.save()
            return True
        return False
