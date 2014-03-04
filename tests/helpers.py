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
    def __init__(self, arg1=None, arg2=None):
        self.id_ = arg1
        self.config = DummyConfig()
        self.protocol = None
    def setup_user_credentials(self, arg1, arg2, arg3):
        pass
    def fetch(self):
        pass
    def get_profile_image(self, arg):
        return "http://dummy.url"
    def verify_credentials_provider(self):
        return 'http://provider.com'
    @staticmethod
    def new(arg1, arg2):
        return DummyAccount(arg1, arg2)

class DummyHttp:
    def sign_request(self, req):
        req.headers['Authorization'] = 'Dummy OAuth'
        return req

class DummyProtocol:
    def __init__(self):
        self.profile = Profile()
        self.friends = []
        self.http = DummyHttp()
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
        self.imgdir = "/path/to/ble"
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

class DummyResponse:
    def __init__(self, content):
        self.content = content
        self.text = content

class DummyService:
    def __init__(self, default=None):
        self.default = default or 'dummy-service'
    def do_service(self, arg1, arg2=None, arg3=None):
        return self.default
