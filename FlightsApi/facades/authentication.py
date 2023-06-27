from hashlib import md5

class LoginToken():
    def __init__(self, user) -> None:
        if 'admin' in user and user['admin']:
            group = 'admin'
        elif 'airline' in user and user['airline']:
            group = 'airline'
        elif 'customer' in user and user['customer']:
            group = 'customer'
        else:
            group = 'anonymous'
        self.__group = group
        self.__generate_token(user)

    
    @property
    def group(self):
        return self.__group
    
    @property
    def login_token(self):
        return self.__token
    
    def __generate_token(self, user):
        hash = md5(user['id'] + user['username']).hexdigest()
        self.__token = self.group + hash
        
class AuthenticationError(Exception):
    pass
