from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy

from django.forms.models import modelform_factory
from django.apps import apps

from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.base import TemplateResponseMixin, View

from braces.views import CsrfExemptMixin, JsonRequestResponseMixin

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .models import Course, Module, Content
from .forms import ModuleFormSet

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


# *********************************************** Course Module *******************************************************
class CourseModuleUpdateView(TemplateResponseMixin, View):
    """
    CourseModuleUpdateView: inherits from 'TemplateResponseMixin & View'.
        it handles the formset to add, update, and delete modules for a specific course

    TemplateResponseMixin: renders templates and returns an HTTP response.
        Requires 'template_name' attribute and the 'render_to_response()'
    View: a simple parent class for all views(['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'])
    """
    template_name = 'courses/manage/module/formset.html'
    course = None

    def get_formset(self, data=None):
        """
        data: is optional and set to None, because get_formset is used as a base for either get / post request i.e to
        avoid repeating the code to build the formset
        This assigns a course instance to every ModuleFormset
        """
        return ModuleFormSet(instance=self.course, data=data)

    def dispatch(self, request, pk):
        """
        dispatch(): takes an HTTP request and delegates a lowercase method (get/post) that matches the HTTP method used
        retrieves the current Course id belonging to the current user(owner=request.user), this makes it impossible
        to change the id to view another user's form.
        """
        self.course = get_object_or_404(Course, id=pk, owner=request.user)
        return super().dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        """
        get: for creating a new Formset
        self.get_formset(): gets a fresh formset with no data
        render_to_response: passes the context i.e Course instance(self.course) and formset(formset)
        """
        formset = self.get_formset()
        return self.render_to_response({'course': self.course, 'formset': formset})

    def post(self, request, *args, **kwargs):
        """
        self.get_formset(): gets a fresh formset with no data and then pass the Post request as the data
            saves the formset if valid and redirects to the Course list(manage_course_list); If the formset is not valid,
            render the template to display errors.
        render_to_response: passes the context i.e Course instance(self.course) and formset(formset)
        """
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course': self.course, 'formset': formset})


# *********************************************** Course Module *******************************************************

# ********************************************** Module content ******************************************************
class ContentCreateUpdateView(TemplateResponseMixin, View):
    """
    TemplateResponseMixin: renders templates and returns an HTTP response.
        Requires 'template_name' attribute and the 'render_to_response()'

    View: a simple parent class for all views(['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'])
    """
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    def get_model(self, model_name):
        """
        model_name: retrieves the app in which the models would be generated dynamically
        """
        if model_name in ['text', 'video', 'image', 'file']:  # check if the model name is in this list
            # use Django apps module to get the app and the class
            return apps.get_model(app_label='courses', model_name=model_name)
        return None  # return None if the model name is not in the list defined above

    def get_form(self, model, *args, **kwargs):
        """
        model: current model used to generate a modelform
        modelform_factory: generates model form classes dynamically,
        i.e you don't need to define a model form every time you register a model in the Django admin
        """
        Form = modelform_factory(model, exclude=['owner', 'order', 'created', 'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        """

        dispatch(): takes an HTTP request and delegates a lowercase method (get/post) that matches the HTTP method used
        :param module_id: the Module ID in which the content would be associated with
        :param model_name: the model name of the content to create/update
        :param id: ID of the object being updated, if no ID(id=None), then a new object will be created
        """
        self.module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        self.model = self.get_model(model_name)

        if id:
            self.obj = get_object_or_404(self.model, id=id, owner=request.user)
        return super().dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        """
        get: executed when a GET request is received; used to view a 'detailed' page of an object
        render_to_response: passes the context i.e form instance(form) and the object being viewed(self.obj)
        """
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})

    def post(self, request, module_id, model_name, id=None):
        """
        self.get_form(): gets a fresh form with no data, receives the submitted data(data=request.POST) and
        files(files=request.FILES)
        render_to_response: passes the context i.e form instance(form) and object being created/updated(self.obj)
        """
        form = self.get_form(self.model, instance=self.obj, data=request.POST, files=request.FILES)

        if form.is_valid():  # checks if the form is valid for 'updating'
            obj = form.save(commit=False)  # if valid, assigned the validated form to 'obj'
            # then assign the parent class to the child class i.e assign the current user as the owner
            obj.owner = request.user
            obj.save()  # then save to DB
            if not id:  # if no ID was found, it means a new Content is to be created
                # new content is created with the current module(self.module) and its item(Text/file/image/video)
                Content.objects.create(module=self.module, item=obj)
            return redirect('module_content_list', self.module.id)  # return to the course list

        return self.render_to_response({'form': form, 'object': self.obj})  # show empty form if no data was supplied


class ContentDeleteView(View):
    """
    View: a simple parent class for all views(['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'])
    """

    def post(self, request, id):
        content = get_object_or_404(Content, id=id, module__course__owner=request.user)
        module = content.module  # get the module content to be deleted and store in variable module
        content.item.delete()  # delete the related(pk to module) object i.e (Text/Video/Image/File)
        content.delete()  # the delete the content itself
        return redirect('module_content_list', module.id)


class ModuleContentListView(TemplateResponseMixin, View):
    """
    TemplateResponseMixin: renders templates and returns an HTTP response.
        Requires 'template_name' attribute and the 'render_to_response()'
    View: a simple parent class for all views(['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'])
    """
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):  # get the module associated to the current logged in user
        module = get_object_or_404(Module, id=module_id, course__owner=request.user)
        # pass the module to 'content_list' page through the context(self.render_to_response)
        return self.render_to_response({'module': module})


class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    """
    CsrfExemptMixin: this stops Django from checking for the cross-site request forgery(CSRF) token in a POST request
    JsonRequestResponseMixin: parses request and response data as JSON and returns an
        HTTP response with application/json as the content type.
    View: a simple parent class for all views(['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'])
    """

    def post(self, request):
        # retrieves id & order from the json request
        for id, order in self.request_json.items():
            # filter the Module based on the id, assign the current user as the owner
            # and update the order based on the order in the post request
            Module.objects.filter(id=id, course__owner=request.user).update(order=order)
            print(f"ModuleOrderView: id:{id} - Order:{order}\n")
            # return a jsons request as OK
        return self.render_json_response({'saved': 'OK'})


class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    """
    CsrfExemptMixin: this stops Django from checking for the cross-site request forgery(CSRF) token in a POST request
    JsonRequestResponseMixin: parses request and response data as JSON and returns an
        HTTP response with application/json as the content type.
    View: a simple parent class for all views(['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace'])
    """

    def post(self, request):
        # retrieves id & order from the json request
        for id, order in self.request_json.items():
            # filter the Content based on the id, assign the current user as the owner
            # and update the order based on the order in the post request
            Content.objects.filter(id=id, module__course__owner=request.user).update(order=order)
            print(f"ModuleOrderView: id:{id} - Order:{order}\n")
            # return a jsons request as OK
        return self.render_json_response({'saved': 'OK'})

# ********************************************** Module content ******************************************************
