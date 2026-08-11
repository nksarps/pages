from . import views
from django.urls import path

urlpatterns = [
    path('signup', views.sign_up, name='sign_up'),
    path('login', views.login, name='login'),
    path('refresh', views.refresh, name='token_refresh'),
    path('<uuid:user_id>/status', views.update_user_status, name='update_user_status'),
]