from datetime import datetime, timedelta
import logging

from django.core.management.base import NoArgsCommand
from django.db import transaction

from gsb.models import List

class Command(NoArgsCommand):
    help = 'Update Google Safe Browsing lists'

    def handle_noargs(self, **options):

        for lst in List.objects.all():
            if lst.next_update <= datetime.now():

                transaction.commit_unless_managed()
                transaction.enter_transaction_management()
                transaction.managed(True)

                try:
                    lst.update()
                    transaction.commit()
                    transaction.leave_transaction_management()
                except:
                    transaction.rollback()
                    transaction.leave_transaction_management()
