from django.db import models
from django.contrib.auth.models import User

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from .fields import OrderField


class Subject(models.Model):  # parent to Course and Module classes
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title


class Course(models.Model):  # child to Subject and parent to Module
    owner = models.ForeignKey(User, related_name='courses_created', on_delete=models.CASCADE)  # instructor
    subject = models.ForeignKey(Subject, related_name='courses', on_delete=models.CASCADE)  # Subject
    title = models.CharField(max_length=200)  # course title
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)  # records when a Course is first created

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.title


class Module(models.Model):  # child to Module and grandchild to Subject
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)  # Course
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    # order each Module based on the Courses
    order = OrderField(blank=True, for_fields=['course'])

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.order}. {self.title}'


class Content(models.Model):  # represent the Modules' contents
    # module contains multiple contents
    module = models.ForeignKey(Module, related_name='contents', on_delete=models.CASCADE)

    # ForeignKey field to the ContentType model; limit_choices_to: is defined after creating the model
    # inheritance(Abstract) and its subclasses(Text, file, image & video)
    # limit_choices_to argument limits the ContentType objects,
    # 'model__in' field: used to filter queries to the ContentType objects with a model attribute such as
    # as 'text', 'video', 'image', or 'file'.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE,
                                     limit_choices_to={'model__in': ('text',
                                                                     'video',
                                                                     'image',
                                                                     'file')})
    # store the primary key of the related object
    object_id = models.PositiveIntegerField()

    # GenericForeignKey field to the related object combining the two previous fields
    # allows to retrieve or set the related object directly, its built on top of the other two fields.
    item = GenericForeignKey('content_type', 'object_id')

    # order each Content based on the Module
    order = OrderField(blank=True, for_fields=['module'])

    class Meta:
        ordering = ['order']


class ItemBase(models.Model):
    """
    ItemBase is an Abstract model(Useful when you want to put some common information into several models)
    Django will not create a database table for this Abstract model(ItemBase)

    since the owner field is defined in the Abstract class, Django provides a way of generating different related_names
    based on the subclasses(models) using the '%(class)s' placeholder. The reverse relationship for the child models
    would be text_related, file_related, image_related, and video_related, respectively.
    """
    # Stores which user created the content;
    owner = models.ForeignKey(User, related_name='%(class)s_related', on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class Text(ItemBase):
    """
    Text inherits from/is a subclass of the ItemBase model. Meaning it has the following fields(owner, title, created, updated)
    by default along with its content field.
    """
    content = models.TextField()


class File(ItemBase):
    """
    File inherits from/is a subclass of the ItemBase model.
    Meaning it has the following fields(owner, title, created, updated) by default along with its file field.
    """
    file = models.FileField(upload_to='files')


class Image(ItemBase):
    """
    Image inherits from/is a subclass of the ItemBase model.
    Meaning it has the following fields(owner, title, created, updated) by default along with its file field.
    """
    file = models.FileField(upload_to='images')


class Video(ItemBase):
    """
    Video inherits from/is a subclass of the ItemBase model.
    Meaning it has the following fields(owner, title, created, updated) by default along with its url field.
    """
    url = models.URLField()
