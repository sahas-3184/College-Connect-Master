from django.contrib import admin
from .models import Channel,UserDetail,Post,Profile,Comments,ChannelRequests,Report

admin.site.register(Channel)
admin.site.register(Profile)
admin.site.register(Post)
admin.site.register(Comments)
admin.site.register(UserDetail)
admin.site.register(ChannelRequests)
admin.site.register(Report)
