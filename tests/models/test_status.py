from libturpial.api.models.status import Status

def test_structure():
    status = Status()
    status.id_ = "123"
    status.original_status_id = "123"
    status.created_at = ""
    status.username = "foo"
    status.avatar = "my_avatar.png"
    status.text = "Tweet text"
    status.in_reply_to_id = "123"
    status.in_reply_to_user = "bar"
    status.is_favorite = False
    status.is_protected = False
    status.is_verified = True
    status.repeated_by = "baz"
    status.datetime = "01-01-1900 00:00"
    status.timestamp = 123456789
    status.entities =  {
        'urls': [],
        'hashtags': [],
        'mentions': [],
        'groups': [],
    }
    status.type_ = Status.NORMAL
    status.account_id = "foo-twitter"
    status.is_own = True
    status.repeated = False
    status.repeated_count = None
    status.local_timestamp = 123456789
    status.source = None
