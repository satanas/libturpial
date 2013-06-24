#!/usr/bin/python
# -*- coding: utf-8 -*-

# Libturpial usage example
# 
# Author: Carlos Guerrero <guerrerocarlos@gmail.com>
# 24 June 2013


from libturpial.api.models.account import Account
from libturpial.api.core import Core

account = "username-twitter" #Replace <username> with the user you want to send tweet with
message = "Tweet sent using Libturpial"

c = Core()
accounts = c.list_accounts()

if account in accounts:
    c.update_status(account,message)
else:
    #If account is not already registered in libturpial, acces must be granted:
    a = Account.new('twitter') #you can also create identi.ca accounts
    url = a.request_oauth_access()
    print "Please go to the following URL, log-in and allow access for Libturpial. Then write the PIN in here."
    print url
    cod = raw_input("PIN:")
    a.authorize_oauth_access(cod)
    c.register_account(a)
