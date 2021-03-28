from django.contrib import admin

from .models import Subject, Course, Module


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):  # parent to Course and Module classes
    list_display = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}  # generate a slug automatically from the title


class ModuleInline(admin.StackedInline):  # child to Module and grandchild to Subject
    model = Module


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):  # child to Subject and parent to Module
    list_display = ['title', 'subject', 'created']
    list_filter = ['created', 'subject']
    search_fields = ['title', 'overview']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]  # adding the child model to the parent model
