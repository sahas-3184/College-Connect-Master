from django.shortcuts import render
from django.http import HttpResponse,JsonResponse,FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from colcon.models import Profile,UserDetail,ProfileSerializer,Post,Channel,PostSerializer,Comments,ChannelRequests,Report
from django.core.exceptions import ObjectDoesNotExist
import math, random
from django.core.mail import send_mail
from django.conf import settings
import datetime



#utilities
keys_dict = {}
logins = {}
import pusher
pusher_client = pusher.Pusher(
  app_id='933316',
  key='f259e37a3a90ae0ee98e',
  secret='74b90e129d3ab0cafec1',
  cluster='ap2',
  ssl=True
)


# pusher_client.trigger('my-channel', 'my-event', {'message': 'hello rishab'})

def get_token(user):
    from uuid import uuid4
    auth = uuid4().__str__()
    keys_dict.update({auth:user})
    logins.update({user.username:auth})
    return auth


def generateOTP():
    digits = "0123456789"
    OTP = ""
    for i in range(4):
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

def forgot_email(receiver,msg = ''):
    subject = 'Otp to change password'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [receiver,]
    send_mail( subject, msg, email_from, recipient_list )

def activate_email(receiver,msg = ''):
    subject = 'Link to Activate Account'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [receiver,]
    send_mail( subject, msg, email_from, recipient_list )

def email(receiver,msg = '',sub = ''):
    email_from = settings.EMAIL_HOST_USER
    send_mail( sub, msg, email_from, receiver )


def encrypt(msg):
    msg = str(msg)
    temp = ''
    for x in msg:
        temp += chr(ord(x)+3)
    return temp[::-1]


def decrypt(msg):
    msg = msg[::-1]
    temp = ''
    for x in msg:
        temp += chr(ord(x)-3)
    return temp




####################################################################################################################################################################################################################################################################################################################################



#Views
@csrf_exempt
def login(req):
    try:
        if req.method != 'POST':
            return  HttpResponse(status = 405)
        id = req.POST.get("id")
        pwd = req.POST.get("pwd")
        if not (id and pwd):
            return HttpResponse(status= 400)
        user = authenticate(username=req.POST.get("id"), password=req.POST.get("pwd"))
        if user:
            temp = Profile.objects.get(user = user)
            if not temp.activated:
                import socket
                hostname = socket.gethostname()
                IPAddr = socket.gethostbyname(hostname)
                print("Your Computer Name is:" + hostname)
                print("Your Computer IP Address is:" + IPAddr)
                token = encrypt(user.username)
                print(temp.email)
                activate_email(str(temp.email),'http://'+IPAddr+':8000/colcon/activate/'+token)
                return HttpResponse(status = 403)
            if user.username in logins:
                del keys_dict[logins[user.username]]
            auth = get_token(user)
            userdetails = UserDetail.objects.get(idno = user.username)
            profile = ProfileSerializer(temp)
            data = {'id':userdetails.idno,'name':userdetails.name,'accounttype':userdetails.type,'email':userdetails.email,'image':profile.data['profilePicture']}
            return JsonResponse({"msg":"login successful","auth":auth,"data":data},status=200)
        else:
            return HttpResponse(status = 401)
    except Exception as e:
        print(e)
        return HttpResponse(status=500)


@csrf_exempt
def activate(req,id):
    id1 = decrypt(id)
    user = User.objects.get(username = id1)
    temp = Profile.objects.get(user = user)
    temp.activated = True
    user.set_password(id)
    temp.save()
    return HttpResponse("<div><h1>Account Activated</h1><p>Your new password is : <b>"+id+"</b></p></div>")


@csrf_exempt
def forgot_password(req,id):
    try:
        if req.method != 'GET':
            return  HttpResponse(status = 405)
        if not id :
            return HttpResponse(status= 400)
        user = User.objects.get(username=id)
        email = Profile.objects.get(user = user).email
        otp = generateOTP()
        forgot_email(email,'OTP:'+otp)
        return JsonResponse({'otp':otp},status=200)
    except ObjectDoesNotExist :
        return HttpResponse(status=204)
    except Exception as e:
        print(e)
        return HttpResponse(status=500)


@csrf_exempt
def reset_password(req,id,pwd):
    try:
        if req.method != 'GET':
            return  HttpResponse(status = 405)
        if not (id and pwd):
            return HttpResponse(status= 400)
        user=User.objects.get(username=id)
        user.set_password(pwd)
        user.save()
        return HttpResponse(status=200)
    except ObjectDoesNotExist :
        return HttpResponse(status=204)
    except Exception:
        return HttpResponse(status=500)


@csrf_exempt
def logout(req):
    try:
        del logins[keys_dict[req.headers['Authorization']].username]
        del keys_dict[req.headers['Authorization']]
        return HttpResponse(status=200)
    except KeyError:
        return HttpResponse(status=404)

@csrf_exempt
def profile_picture_upload(req):
    try:
        user = keys_dict[req.headers['Authorization']]
        profile = Profile.objects.get(user=user)
        profile.profilePicture.delete()
        profile.profilePicture.save(user.username+'_'+str(datetime.datetime.now())+'_'+req.FILES['my_photo'].name,req.FILES['my_photo'])
        return JsonResponse({'image':ProfileSerializer(profile).data['profilePicture']},status=200)
    except KeyError:
        return HttpResponse(status=404)
    except Exception as e:
        print(type(e),e)
        return HttpResponse(status=500)

@csrf_exempt
def channel_list(req):
    try:
        if req.method != 'GET':
            return HttpResponse(status=405)
        user = keys_dict[req.headers['Authorization']]
        profile = Profile.objects.get(user=user)
        channels = profile.channels.all()
        data = []
        for x in channels:
            temp = {'title':x.channel_name}
            data.append(temp)
        return JsonResponse({'data':data},status=200)
    except KeyError:
        return HttpResponse(status=404)
    except Exception as e:
        print(type(e),e)
        return HttpResponse(status=500)



@csrf_exempt
def invitation_list(req):
    try:
        if req.method != 'GET':
            return HttpResponse(status=405)
        user = keys_dict[req.headers['Authorization']]
        profile = Profile.objects.get(user=user)
        channels = profile.invitations.all()
        data = []
        for x in channels:
            temp = {'title':x.channel_name,'description':x.description}
            data.append(temp)
        return JsonResponse({'data':data},status=200)
    except KeyError:
        return HttpResponse(status=404)
    except Exception as e:
        print(type(e),e)
        return HttpResponse(status=500)
@csrf_exempt
def process_invitation(req):
    try:
        if req.method != 'POST':
            return HttpResponse(status=405)
        user = keys_dict[req.headers['Authorization']]
        profile = Profile.objects.get(user = user)
        channel = Channel.objects.get(channel_name=req.POST.get('channel'))
        profile.invitations.remove(channel)
        if req.POST.get('accepted') == 'y':
            profile.channels.add(channel)
        return HttpResponse(status=200)
    except KeyError:
        return HttpResponse(status=404)
    except Exception as e:
        print(type(e),e)
        return HttpResponse(status=500)



@csrf_exempt
def add_post(req):
    try:
        if req.method != 'POST':
            return HttpResponse(status=405)
        user = keys_dict[req.headers['Authorization']]
        profile = Profile.objects.get(user=user)
        channel = profile.channels.get(channel_name = req.POST.get('channelName'))
        post = Post()
        post.posted_in = channel
        post.posted_by = user
        post.title = req.POST.get('title')
        post.description = req.POST.get('description')
        post.save()
        if 'my_photo' in req.FILES:
            post.image.save(user.username+'_'+str(datetime.datetime.now())+'_'+req.FILES['my_photo'].name,req.FILES['my_photo'])
        if 'my_file' in req.FILES:
            post.files.save(user.username + '_' + str(datetime.datetime.now()) + '_' + req.FILES['my_file'].name,req.FILES['my_file'])
        return HttpResponse(status=200)
    except KeyError:
        return HttpResponse(status=404)
    except Exception as e:
        print(type(e),e)
        return HttpResponse(status=500)


@csrf_exempt
def get_posts(req,channel_name):
    try:
        if req.method != 'GET':
            return HttpResponse(status=405)
        user = keys_dict[req.headers['Authorization']]
        channel = Channel.objects.get(channel_name = channel_name)
        posts = Post.objects.filter( posted_in= channel)
        data = []
        for x in posts:
            temp = PostSerializer(x).data
            temp.update({'by':UserDetail.objects.get(idno = x.posted_by.username).name})
            data.append(temp)
        return JsonResponse({'data':data},status=200)
    except KeyError:
        return HttpResponse(status=404)
    except Exception as e:
        print(type(e),e)
        return HttpResponse(status=500)


@csrf_exempt
def add_comment(req):
    try:
        if req.method != 'POST':
            return HttpResponse(status=405)
        user = keys_dict[req.headers['Authorization']]
        post = Post.objects.get(id = req.POST.get('id'))
        comment = Comments()
        comment.comment = req.POST.get('comment')
        comment.commented_by = user
        comment.commented_post = post
        comment.save()
        return HttpResponse(status=200)
    except KeyError:
        return HttpResponse(status=404)
    except Exception as e:
        print(type(e),e)
        return HttpResponse(status=500)


@csrf_exempt
def get_comments(req,postid):
    try:
        if req.method != 'GET':
            return HttpResponse(status=405)
        user = keys_dict[req.headers['Authorization']]
        post = Post.objects.get( id = postid)
        comments = Comments.objects.filter(commented_post = post)
        data = []
        for x in comments:
            profile = Profile.objects.get(user=x.commented_by)
            temp = {'title':UserDetail.objects.get(idno = x.commented_by.username).name,'description':x.comment,'image':ProfileSerializer(profile).data['profilePicture']}
            data.append(temp)
        return JsonResponse({'data':data},status=200)
    except KeyError:
        return HttpResponse(status=404)
    except Exception as e:
        print(type(e),e)
        return HttpResponse(status=500)


@csrf_exempt
def add_channel_request(req):
    try:
        if req.method != 'POST':
            return HttpResponse(status=405)
        user = keys_dict[req.headers['Authorization']]
        cr = ChannelRequests()
        cr.by = user
        cr.name = req.POST.get('name')
        cr.description = req.POST.get('description')
        cr.type = req.POST.get('type')
        cr.save()
        return HttpResponse(status=200)
    except KeyError:
        return HttpResponse(status=404)
    except Exception as e:
        print(type(e),e)
        return HttpResponse(status=500)


@csrf_exempt
def add_complaint(req):
    try:
        if req.method != 'POST':
            return HttpResponse(status=405)
        user = keys_dict[req.headers['Authorization']]
        cr = Report()
        cr.reported_by = user
        cr.channel = req.POST.get('name')
        cr.person = req.POST.get('idp')
        cr.complaint = req.POST.get('issue')
        cr.save()
        return HttpResponse(status=200)
    except KeyError:
        return HttpResponse(status=404)
    except Exception as e:
        print(type(e),e)
        return HttpResponse(status=500)

@csrf_exempt
def add_people(req):
    try:
        if req.method != 'POST':
            return HttpResponse(status=405)
        user = keys_dict[req.headers['Authorization']]
        users_list = req.POST.getlist('users')
        channel = Channel.objects.get(channel_name = req.POST.get('channel'))
        email_set = set()
        for x in users_list:
            temp_user = User.objects.get(username = x)
            temp_profile = Profile.objects.get(user = temp_user)
            temp_profile.invitations.add(channel)
            email_set.add(temp_profile.email)
        email(list(email_set), 'you are invited to join ' + channel.channel_name, 'Invitation')
        return HttpResponse(status=200)
    except KeyError:
        return HttpResponse(status=404)
    except Exception as e:
        print(type(e),e)
        return HttpResponse(status=500)

@csrf_exempt
def get_people(req,type,dept,year,sec):
    try:
        if req.method != 'GET':
            return HttpResponse(status=405)
        user = keys_dict[req.headers['Authorization']]
        if type == 0:
            temp = UserDetail.objects.filter(type = 'F',dept = dept)
        else:
            temp = UserDetail.objects.filter(type = 'S',dept = dept,year = year,sec = sec)
        data = []
        for x in temp:
            obj = {
                'name' : x.name,
                'id':x.idno,
                'checked':False,
            }
            data.append(obj)
        return JsonResponse({'data':data},status=200)
    except KeyError:
        return HttpResponse(status=404)
    except Exception as e:
        print(type(e),e)
        return HttpResponse(status=500)

@csrf_exempt
def delete_channel(req,channel):
    try:
        if req.method != 'GET':
            return HttpResponse(status=405)
        if channel in {'College','Library','Placement'}:
            raise Exception
        temp = Channel.objects.get(channel_name= channel)
        temp.delete()
        return HttpResponse(status=200)
    except KeyError:
        return HttpResponse(status=404)
    except Exception as e:
        print(type(e),e)
        return HttpResponse(status=500)


@csrf_exempt
def change_pwd(req):
    try:
        if req.method != 'POST':
            return HttpResponse(status=405)
        user = keys_dict[req.headers['Authorization']]
        pwd = req.POST.get('pwd')
        user.set_password(pwd)
        user.save()
        return HttpResponse(status=200)
    except KeyError:
        return HttpResponse(status=404)
    except Exception as e:
        print(type(e),e)
        return HttpResponse(status=500)
