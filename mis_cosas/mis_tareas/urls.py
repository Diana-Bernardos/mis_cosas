from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views

urlpatterns = [
    path('', views.mis_tareas_v, name='mis_tareas'),
    path('mis_cosas/', views.mis_tareas_v, name='lista_tareas_legacy'),
    path('registro/', views.registro, name='registro'),
    path('tarea/nueva/', views.crear_tarea, name='crear_tarea'),
    path(
        'accounts/login/',
        LoginView.as_view(
            template_name='login.html',
            redirect_authenticated_user=True,
            next_page='mis_tareas',
        ),
        name='login',
    ),
    path('accounts/logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('tarea/<int:tarea_id>/editar/', views.editar_tarea, name='editar_tarea'),
    path(
        'tarea/<int:tarea_id>/eliminar/',
        views.eliminar_tarea,
        name='eliminar_tarea',
    ),
]
