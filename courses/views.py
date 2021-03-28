from django.shortcuts import render
from django.urls import reverse_lazy

from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .models import Course

"""
Mixin: a type of multiple inheritance for a 'class'.
Use cases:
1) to provide multiple optional features for a class
2) to use a particular feature in several classes

Syntax for permission_required: CRUD appName.add_modelName,
C: appName.add_modelName -> add: user.has_perm('courses.add_course')
R: appName.view_modelName -> view: user.has_perm('courses.view_course')
U: appName.change_modelName -> change: user.has_perm('courses.change_course')
D: appName.delete_modelName -> delete: user.has_perm('courses.delete_course')
"""


class OwnerMixin(object):
    """
    OwnerMixin: used on views that interact with any model containing an 'owner' field/attribute
    """

    def get_queryset(self):
        """
        override the get_queryset method.
        this displays only courses created by the current logged in user
        """
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)


class OwnerEditMixin(object):
    """
    OwnerEditMixin: used on views that interact with any model containing an 'owner' field/attribute
    """

    def form_valid(self, form):
        """
        used by CreateView and UpdateView.
        saves the instance of a form to the current logged in user
        .owner: is from the owner field in Course Model
        """
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin):
    """
    OwnerCourseMixin: specifies 4 fields to be displayed;
    Also redirects the user to 'manage_course_list' view after creating/updating/deleting a Course
      - OwnerMixin: ensures that the user only see his created Courses
      - LoginRequiredMixin: ensures a user is logged in before viewing a page
      - PermissionRequiredMixin: checks if the user accessing a view has all given permissions.
        Superusers automatically have all permissions.
    """
    model = Course
    fields = ['subject', 'title', 'slug', 'overview']
    success_url = reverse_lazy('manage_course_list')  # used by CreateView, UpdateView, and DeleteView


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    """
    OwnerCourseMixin: composed of OwnerMixin, LoginRequiredMixin and PermissionRequiredMixin:
      - OwnerMixin: ensures that the user only see his created Courses
      - LoginRequiredMixin: ensures a user is logged in before viewing a page
      - PermissionRequiredMixin: checks if the user accessing a view has all given permissions.
        Superusers automatically have all permissions.

    OwnerEditMixin: this saves the instance of a form to the current logged in user
    """
    # template to be used for the CreateView and UpdateView views
    template_name = 'courses/manage/course/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
    """
    OwnerCourseMixin: composed of OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin & OwnerEditMixin
      - OwnerMixin: ensures that the user only see his created Courses
      - LoginRequiredMixin: ensures a user is logged in before viewing a page
      - PermissionRequiredMixin: checks if the user accessing a view has all given permissions.
        Superusers automatically have all permissions.

    ListView: Django's generic ListView
    """
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'
    context_object_name = 'courses'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    """
    OwnerCourseEditMixin: composed of OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin & OwnerEditMixin
      - OwnerMixin: ensures that the user only see his created Courses
      - LoginRequiredMixin: ensures a user is logged in before viewing a page
      - PermissionRequiredMixin: checks if the user accessing a view has all given permissions.
         Superusers automatically have all permissions.
      - OwnerEditMixin: this saves the instance of a form to the current logged in user

    CreateView: Django's generic CreateView
    """
    permission_required = 'courses.add_course'


class CourseUpdateView(OwnerCourseEditMixin, UpdateView):
    """
    OwnerCourseEditMixin: composed of OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin & OwnerEditMixin
       - OwnerMixin: ensures that the user only see his created Courses
       - LoginRequiredMixin: ensures a user is logged in before viewing a page
       - PermissionRequiredMixin: checks if the user accessing a view has all given permissions.
          Superusers automatically have all permissions.
       - OwnerEditMixin: this saves the instance of a form to the current logged in user

    UpdateView: Django's generic UpdateView
    """
    permission_required = 'courses.change_course'


class CourseDeleteView(OwnerCourseMixin, DeleteView):
    """
    OwnerCourseMixin: composed of OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin & OwnerEditMixin
       - OwnerMixin: ensures that the user only see his created Courses
       - LoginRequiredMixin: ensures a user is logged in before viewing a page
       - PermissionRequiredMixin: checks if the user accessing a view has all given permissions.
        Superusers automatically have all permissions.

    DeleteView: Django's generic DeleteView which expects a user's confirmation to delete
    """
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'
