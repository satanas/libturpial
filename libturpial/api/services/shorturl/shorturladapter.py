# -*- coding: utf-8 -*-

"""Adapter for shorty-python libraries"""
#
# Author: Andrea Stagi (4ndreaSt4gi)
# 2010-07-28

from libturpial.api.interfaces.service import GenericService
from libturpial.api.interfaces.service import ServiceResponse

class ShortUrlAdapter(GenericService):
    def __init__(self, obj):
        GenericService.__init__(self)
        self._obj = obj
        
    def do_service(self, longurl):
        longurl = self._quote_url(longurl)
        try:
            resp = self._obj.shrink(longurl)
            return ServiceResponse(resp)
        except Exception, error:
            self.log.debug("Error: %s\n%s" % (error, traceback.print_exc()))
            return ServiceResponse(err=True, err_msg=_('Problem shorting URL'))
