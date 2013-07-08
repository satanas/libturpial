#!/usr/bin/python
# -*- coding: utf-8 -*-

# Libturpial usage example
#
# Author: Carlos Guerrero <guerrerocarlos@gmail.com>
# 24 June 2013

import os
import sys
import argparse

try:
    from libturpial.api.models.account import Account
    from libturpial.api.core import Core
except ImportError:
    path = \
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
    sys.path.append(path)

    from libturpial.api.models.account import Account
    from libturpial.api.core import Core

core = Core()

# Parsing the command line
description = "Send a message from libturpial"
parser = argparse.ArgumentParser(description=description)
parser.add_argument("-u", "--username", dest="username",
                    help="Username", required=True)
parser.add_argument("-p", "--protocol", dest="protocol",
                    choices=core.list_protocols(), help="Protocol",
                    required=True)
parser.add_argument("-m", "--message", dest="message", help="Message",
                    required=True)
args = parser.parse_args()


username = args.username
protocol = args.protocol
account_pattern = "-".join([username, protocol])
message = args.message

print "Trying to send message '%s'\nas user: %s, protocol: %s" % (message,
                                                                  username,
                                                                  protocol)

if account_pattern in core.list_accounts():
    core.update_status(account_pattern, message)
else:
    # If account is not already registered in libturpial,
    # access must be granted:
    account = Account.new(protocol)
    url = account.request_oauth_access()
    instructions = "Please go to the following URL, log-in and allow access" \
                   " for libturpial. Then write the PIN in here."
    print "%s\n%s" % (instructions, url)
    cod = raw_input("PIN: ")
    account.authorize_oauth_access(cod)
    account_id = core.register_account(account)
    core.update_status(account_id, message)
