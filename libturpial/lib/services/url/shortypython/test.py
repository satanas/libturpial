# Shorty
# Copyright 2009 Joshua Roesslein
# See LICENSE

import sys

from . import shorty

print('Running shorty tests...')

passes = 0
fails = 0

# get services to test
if len(sys.argv) > 1:
    try:
        services = dict((name, shorty.services[name]) for name in sys.argv[1:])
    except KeyError as k:
        print('ERROR: %s not valid service' % k)
        exit(1)
else:
    services = shorty.services

# run tests
for name, service in list(services.items()):
    try:
        if service.tested:
            # skip services with aliases
            continue
        service._test()
        passes += 1
        print('PASS: <%s>' % name)
    except shorty.ShortyError as e:
        fails += 1
        print('FAIL: <%s> %s' % (name, e))

print('PASSES: %i  FAILS: %i' % (passes, fails))
