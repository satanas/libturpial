from libturpial.api.core import Core

#Put here your twitter account username
account = '@example'

#This example is for a twitter account
service_account = account+'-twitter'

core = Core()
core.register_account(account, 'twitter')
response = core.login(service_account)

if response.code > 0:
    raise Exception

auth_obj = response.items

# Validates if account needs authorization
if auth_obj.must_auth():
    print "Visit %s, authorize Turpial and write back the pin" % auth_obj.url
    pin = raw_input('Pin: ')
    core.authorize_oauth_token(service_account, pin)
    
data = core.auth()
core.send_direct(service_account,'@guerrerocarlos',"testing!")
#core.broadcast_status([service_account],"123 testing from libturpial')
