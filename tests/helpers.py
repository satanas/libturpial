from libturpial.api.models.profile import Profile

class DummyFileHandler:
    def __init__(self, array=None):
        if array:
            self.array = array
        else:
            self.array = []
    def __iter__(self):
        return iter(self.array)
    def close(self):
        pass
    def write(self, argument):
        pass

class DummyAccount:
    def __init__(self, arg1, arg2):
        self.id_ = arg1
        self.config = None
    def setup_user_credentials(self, arg1, arg2, arg3):
        pass
    def fetch(self):
        pass
    @staticmethod
    def new(arg1, arg2):
        return DummyAccount(arg1, arg2)

class DummyProtocol:
    def __init__(self):
        self.profile = Profile()
        self.friends = []
    def request_token(self):
        return 'token'
    def authorize_token(self, pin):
        return self.profile
    def verify_credentials(self):
        return self.profile
    def get_lists(self, arg):
        return []
    def get_following(self, only_id):
        return self.friends
    def update_profile(self, fullname, url, bio, location):
        self.profile.fullname = fullname
        self.profile.url = url
        self.profile.bio = bio
        self.profile.location = location
        return self.profile

class DummyConfig:
    def __init__(self, arg=None):
        self.cache_size = 0
    @staticmethod
    def exists(value):
        return False
    def save_oauth_credentials(self, arg1, arg2):
        pass
    def load_oauth_credentials(self):
        pass
    def dismiss(self):
        pass
    def delete_cache(self):
        pass
    def calculate_cache_size(self):
        return self.cache_size

class DummyToken:
    def __init__(self):
        self.key = '123'
        self.secret = '456'

class DummyProfile:
    def is_me(self):
        return True
