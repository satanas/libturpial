# -*- coding: utf-8 -*-

from libturpial.api.core import Core
from libturpial.api.models.account import Account
from libturpial.api.models.column import Column
from libturpial.api.models.status import Status
from libturpial.api.models.profile import Profile

# TODO:
# * Mock tests to avoid the internet connection
# * Test failure cases
# * Test service methods
# * Test config methods
# * Test register and unregister account
# * Test register and unregister columns

# To run this test make sure you have an account_id file inside tests folder
# with the id of the account you want to use to test. This test is not
# optimized, so it will connect to Twitter and it will perform some actions
# with the specified account

try:
    fd = open('tests/account_id', 'r')
    account_id = fd.read().strip()
    fd.close()
except Exception:
    print "Error opening the tests/account_id file"
    exit(-1)

core = Core()

def assert_column_as_content(rtn):
    if len(rtn) > 0:
        acc = rtn.keys()[0]
        assert type(rtn[acc]) == list
        assert rtn[acc][0].__class__ == Column

def test_list_accounts():
    rtn = core.list_accounts()
    assert type(rtn) == list

def test_all_columns():
    rtn = core.all_columns()
    assert type(rtn) == dict
    assert_column_as_content(rtn)

def test_list_protocols():
    rtn = core.list_protocols()
    assert 'twitter' in rtn
    assert len(rtn) == 2
    assert type(rtn) == list

def test_available_columns():
    rtn = core.available_columns()
    assert type(rtn) == dict
    assert_column_as_content(rtn)

def test_registered_columns():
    rtn = core.registered_columns()
    assert type(rtn) == dict
    assert_column_as_content(rtn)

def test_registered_accounts():
    rtn = core.registered_accounts()
    assert type(rtn) == list
    if len(rtn) > 0:
        assert type(rtn[0]) == Account

def test_column_statuses():
    rtn = core.get_column_statuses(account_id, 'timeline')
    assert len(rtn) > 0
    assert type(rtn) == list
    assert rtn[0].__class__ == Status

def test_followers():
    rtn = core.get_followers(account_id)
    assert type(rtn) == list
    if len(rtn) > 0:
        assert rtn[0].__class__ == Profile

    rtn = core.get_followers(account_id, only_id=True)
    assert type(rtn) == list
    if len(rtn) > 0:
        assert type(rtn[0]) == str

def test_following():
    rtn = core.get_following(account_id)
    assert type(rtn) == list
    if len(rtn) > 0:
        assert rtn[0].__class__ == Profile

    rtn = core.get_following(account_id, only_id=True)
    assert type(rtn) == list
    if len(rtn) > 0:
        assert type(rtn[0]) == str

def test_get_all_friends_list():
    rtn = core.get_all_friends_list()
    assert type(rtn) == list
    if len(rtn) > 0:
        assert type(rtn[0]) == unicode

def test_load_all_friends_list():
    rtn = core.load_all_friends_list()
    assert type(rtn) == list
    if len(rtn) > 0:
        assert type(rtn[0]) == str

def test_get_user_profile():
    rtn = core.get_user_profile(account_id, 'turpialve')
    assert rtn.__class__ == Profile

def test_get_conversation():
    rtn = core.get_conversation(account_id, '353903608762339331')
    assert type(rtn) == list
    assert rtn[0].__class__ == Status

def test_update_status():
    rtn = core.update_status(account_id, '#1 Test from libturpial')
    assert rtn.__class__ == Status

def test_broadcast_status():
    rtn = core.broadcast_status(None, '#2 Broadcast test from libturpial')
    assert type(rtn) == dict

def test_deleting_status():
    rtn = core.update_status(account_id, '#3 Deletion test')
    assert rtn.__class__ == Status

    rtn2 = core.destroy_status(account_id, rtn.id_)
    assert rtn2.__class__ == Status

def test_get_sinle_status():
    rtn = core.get_single_status(account_id, '353903608762339331')
    assert rtn.__class__ == Status

def test_repeat_status():
    rtn = core.repeat_status(account_id, '353221797858123776')
    assert rtn.__class__ == Status

def test_mark_status_as_favorite():
    rtn = core.mark_status_as_favorite(account_id, '353221797858123776')
    assert rtn.__class__ == Status

def test_unmark_status_as_favorite():
    rtn = core.unmark_status_as_favorite(account_id, '353221797858123776')
    assert rtn.__class__ == Status

def test_send_direct_message():
    rtn = core.send_direct_message(account_id, account_id.split('-')[0], 'Hello world from libturpial!')
    assert rtn.__class__ == Status

#@raises(libturpial.exceptions.ResourceNotFound)
#def test_destroy_direct_message():
#    rtn = core.send_direct_message(account_id, account_id.split('-')[0], 'Bye world from libturpial!')
#    assert rtn.__class__ == Status
#    rtn2 = core.destroy_direct_message(account_id, rtn.id_)

def test_update_profile():
    current_profile = core.get_user_profile(account_id)
    rtn = core.update_profile(account_id, location='Hell')
    assert rtn.__class__ == Profile
    rtn = core.update_profile(account_id, location=current_profile.location)
    assert rtn.__class__ == Profile

def test_follow():
    rtn = core.follow(account_id, 'BBCNews')
    assert rtn.__class__ == Profile

def test_unfollow():
    rtn = core.unfollow(account_id, 'BBCNews')
    assert rtn.__class__ == Profile

def test_block():
    rtn = core.block(account_id, 'BBCNews')
    assert rtn.__class__ == Profile

def test_unblock():
    rtn = core.unblock(account_id, 'BBCNews')
    assert rtn.__class__ == Profile

def test_report_as_spam():
    rtn = core.report_as_spam(account_id, 'Horse_ebooks')
    assert rtn.__class__ == Profile

def test_mute():
    rtn = core.mute('foo')
    assert rtn == 'foo'

def test_unmute():
    rtn = core.unmute('foo')
    assert rtn == 'foo'

def test_verify_friendship():
    rtn = core.verify_friendship(account_id, 'Microsoft')
    assert rtn == False

def test_search():
    rtn = core.search(account_id, 'turpial')
    assert type(rtn) == list
    if len(rtn) > 0:
        assert rtn[0].__class__ == Status

def test_get_profile_image():
    rtn = core.get_profile_image(account_id, 'turpialve')
    assert type(rtn) == str

#def test_get_status_avatar():
#    rtn = core.get_status_avatar(account_id, '353221797858123776')
#    assert type(rtn) == str
