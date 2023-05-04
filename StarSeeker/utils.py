import random
import string
import user.models

from django.contrib import messages
from django.utils.text import slugify


def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def unique_slug_generator(instance, new_slug=None):
    if new_slug is not None:
        slug = new_slug
    else:
        slug = slugify(instance.name)

    Klass = instance.__class__
    qs_exists = Klass.objects.filter(userlink=slug).exists()
    if qs_exists:
        new_slug = "{slug}-{randstr}".format(
            slug=slug,
            randstr=random_string_generator(size=5)
        )
        return unique_slug_generator(instance, new_slug=new_slug)
    return slug


def delete_django_messages(request):
    storage = messages.get_messages(request)
    for _ in storage:
        pass
    if len(storage._loaded_messages):
        del storage._loaded_messages[:]

def load_state_city():
    statecitydata = {}
    states = user.models.State.objects.values_list(
        'name', flat=True).order_by('name')

    cities = []
    for state in states:
        state_cities = list(user.models.City.objects.filter(state__name=state).values_list(
            'name', flat=True).order_by('name'))
        statecitydata[state] = state_cities
        cities.extend(state_cities)

    return statecitydata, cities