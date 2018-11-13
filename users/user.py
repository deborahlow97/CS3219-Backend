from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from users.models import Session, SessionManager
from users import *
from django.core import serializers

class MyUser:

    def __init__( self, email, password ):
        self.email = email
        self.password = password

    def registerUser(self):
        registerUsername = self.email
        registerPassword = self.password
        isExist = self.authenticateUser(registerUsername, registerPassword)
        if isExist:
            return {"isSuccessful": False, "errorMessage": "There already exist a username under that email"}
        else:
            self.createUser(registerUsername, registerPassword)
        return {"isSuccessful": True}

    def loginUser(self):
        loginUsername = self.email
        loginPassword = self.password
        isExist = self.authenticateUser(loginUsername, loginPassword)
        if isExist:
            return {"isSuccessful": True}
        else:
            return {"isSuccessful": False, "errorMessage": "Wrong username/password"}

    def createUser(self, username, password):
        user = User.objects.create_user(username, username, password)
        return user.get_username()

    def authenticateUser(self, _username, _password):
        user = authenticate(username=_username, password=_password)
        if user is not None:
            return True
        else:
            return False