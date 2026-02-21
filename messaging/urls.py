from django.urls import path
from . import views
from django.contrib.auth.views import LoginView

app_name = "messaging"

urlpatterns = [
    # create/get a conversation then redirect into it
    path("start/<int:tradesman_id>/", views.start_conversation, name="start"),

    # conversation page
    path("c/<uuid:conversation_id>/", views.conversation_detail, name="detail"),

    # APIs (AJAX)
    path("api/c/<uuid:conversation_id>/send/", views.api_send_message, name="api_send"),
    path("api/c/<uuid:conversation_id>/poll/", views.api_poll_messages, name="api_poll"),
    path("inbox/", views.inbox, name="inbox"),


]