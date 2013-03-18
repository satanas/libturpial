'''
List of twitter method names that require the use of POST
'''

POST_ACTIONS = (

    # Status Methods
    'update',

    # Direct Message Methods
    'new',

    # Account Methods
    'update_profile_image', 'update_delivery_device', 'update_profile',
    'update_profile_background_image', 'update_profile_colors',
    'update_location', 'end_session',

    # Notification Methods
    'leave', 'follow',

    # Status Methods, Block Methods, Direct Message Methods,
    # Friendship Methods, Favorite Methods
    'destroy',

    # Block Methods, Friendship Methods, Favorite Methods, Report Spam
    'create',
    'retweet',
    'report_spam',

)

CK = 'W2wNN0zVTOTCZuvCx87fpg'
CS = 'S3JnWnhlNkxtU2JZRjBUZFN4UnZHR2xvUjdXSnlpZz'
SALT = 'hyNmF5OW1uT2hZ'
