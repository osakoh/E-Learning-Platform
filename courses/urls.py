from django.urls import path
from . import views

urlpatterns = [
    # course urls
    path('list/', views.ManageCourseListView.as_view(), name='manage_course_list'),  # view course list

    path('create/', views.CourseCreateView.as_view(), name='course_create'),  # create new course

    path('<pk>/edit/', views.CourseUpdateView.as_view(), name='course_edit'),  # update an existing course

    path('<pk>/delete/', views.CourseDeleteView.as_view(), name='course_delete'),  # delete an existing course
    # course urls

    # update modules belonging to a course
    path('<pk>/module/', views.CourseModuleUpdateView.as_view(), name='course_module_update'),
    # module url

    # content urls#
    # creates new objects(text/video/image/file); includes the module_id and model_name
    path('module/<int:module_id>/content/<model_name>/create/', views.ContentCreateUpdateView.as_view(),
         name='module_content_create'),

    # updates an existing object(text/video/image/file); includes the module_id and model_name
    path('module/<int:module_id>/content/<model_name>/<id>/', views.ContentCreateUpdateView.as_view(),
         name='module_content_update'),

    path('content/<int:id>/delete/', views.ContentDeleteView.as_view(), name='module_content_delete'),

    path('module/<int:module_id>/', views.ModuleContentListView.as_view(), name='module_content_list'),

    # path('content/order/', views.ContentOrderView.as_view(), name='content_order'),
    # content urls
]
