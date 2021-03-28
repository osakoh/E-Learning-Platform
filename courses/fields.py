from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class OrderField(models.PositiveIntegerField):
    """
    OrderField inherits from the PositiveIntegerField and an additional behavior is added to it.
    Additional behaviours:
    1) Automatically assign an order value when no specific order is provided: this field would automatically assign an
    order based on the last object's order to an object before saving it if no order was provided. i.e If there are
    two objects with order 1 and 2 respectively, when saving a third object, it automatically assigns the order 3 to it
    if no specific order has been provided.

    2) Order objects with respect to other fields: Modules will be ordered with respect to the Course they belong to and
    module contents will be ordered with respect to the module they belong to.
    """

    def __init__(self, for_fields=None, *args, **kwargs):
        """
        :param for_fields: an optional field. Allows the order to be gotten based on particular fields
        """
        self.for_fields = for_fields
        super().__init__(*args, **kwargs)

    def pre_save(self, model_instance, add):
        if getattr(model_instance, self.attname) is None:  # if no current value/order
            # no current value/order
            try:
                qs = self.model.objects.all()  # build a queryset to get the model the field belongs to

                if self.for_fields:  # if field(s) were given to which would be used to calculate the order
                    # filter by objects with the same field values
                    # for the fields in "for_fields"
                    query = {field: getattr(model_instance, field) for field in self.for_fields}
                    qs = qs.filter(**query)

                # else, get the order of the last item
                last_item = qs.latest(self.attname)
                value = last_item.order + 1
            except ObjectDoesNotExist:  # no model object has been created, this object becomes the first created object
                value = 0  # start the order from 0
            # assign the order to the field
            setattr(model_instance, self.attname, value)
            return value  # then return the value
        else:  # If the model instance has a value for the current field, you use it instead of calculating it.
            return super().pre_save(model_instance, add)
