from django.urls import path
from . import views

urlpatterns = [
    path('', views.profiles_View , name= 'profiles'),
    path('settings', views.settings_View , name= 'settings'),
    path('profile_edit', views.edit_profile_View , name= 'profile_edit'),
    path('add_project/', views.add_project, name='add_project'), 
    path('privacy-policy/', views.privacy_policy_view, name='privacy_policy'),
    path('add-social-link/', views.add_social_link, name='add_social_link'),
    path('update_social_link/<str:platform>/', views.update_social_link, name='update_social_link'),
    path('delete_project_experience/<int:project_experience_id>/', views.delete_project_experience, name='delete_project_experience'),
    path('project_experience/edit/<int:experience_id>/', views.update_project, name='update_project'),
    
    path('how_it_work/',views.how_it_work, name='skill_level_page'),
    path('project/<int:project_id>/<str:action>/', views.update_project_status, name='update_project_status'),

    path('projects/<int:project_id>/add-stage/', views.add_progress_stage_view, name='add_progress_stage_view'),

    path('projects/<int:project_id>/progress/', views.view_project_progress_view, name='view_project_progress_view'),

    path('stage/<int:stage_id>/complete/', views.mark_stage_completed_view, name='mark_stage_completed'),
   
    path('stage/<int:stage_id>/confirm/', views.confirm_stage_completion_view, name='confirm_stage_completion_view'),




]


