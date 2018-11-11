from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

# def createUser(data):
#     email = "abc@gmail.com"
#     pw="1234"
#     user = User.objects.create_user(email, email, password)
#     user.save()

# def authenticateUser(_username):
#     user = authenticate(username=_username, password='secret')
#     if user is not None:
#         return True
#     else:
#         return False


# def loginUser(request):
#     username = request.POST['username']
#     password = request.POST['password']
#     user = authenticate(request, username=username, password=password)
#     if user is not None:
#         login(request, user)
#         # Redirect to a success page.

#     else:
#         print("Invalid Login =(")

# def registerUser(_username):
#     if request.user.is_authenticated: