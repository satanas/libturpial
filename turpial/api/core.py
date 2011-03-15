# -*- coding: utf-8 -*-

'''Minimalistic and agnostic core for Turpial'''
#
# Author: Wil Alvarez (aka Satanas)
# Mar 06, 2011

import os
import Queue
import logging
import traceback

from turpial.api.common import ColumnType, STATUSPP
from turpial.api.models.response import Response
from turpial.api.models.accountmanager import AccountManager

#TODO: Implement basic code to identify generic proxies in ui_base

class Core:
    '''Turpial core'''
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        
        self.queue = Queue.Queue()
        self.log = logging.getLogger('Core')
        self.log.debug('Started')
        self.accman = AccountManager()
        
    def login(self):
        response = Response()
        for aid, acc in self.accman:
            self.log.debug('Authenticating with %s' % aid)
            try:
                response.add(acc.auth())
            except Exception, exc:
                print traceback.print_exc()
                self.log.debug('Authentication Error')
                return Response(666)
        return response
        
    def get_column_statuses(self, account_id, column_id, count=STATUSPP):
        try:
            account = self.accman.get(account_id)
            if column_id == ColumnType.TIMELINE:
                rtn = account.get_timeline(count)
            elif column_id == ColumnType.REPLIES:
                rtn = account.get_replies(count)
            elif column_id == ColumnType.DIRECTS:
                rtn = account.get_directs(count)
            elif column_id == ColumnType.SENT:
                rtn = account.get_sent(count)
            elif column_id == ColumnType.FAVORITES:
                rtn = account.get_favorites(count)
            
            return Response(rtn)
        except KeyError:
            return Response(666)
