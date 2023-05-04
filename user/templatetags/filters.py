from django import template
from urllib.parse import urlencode

register = template.Library()

@register.filter(name='show_first_error')
def show_first_error(dictionary):
    return list(dictionary.values())[0][0]

@register.filter(name='fake_name')
def fake_name(full_name):
    try: 
        first_name, last_name = (full_name.split())
        fake_first_name = first_name[:2] + 'xxxx'
        fake_last_name = 'xxxx' + last_name[-3:]
        fake_full_name = fake_first_name + ' ' + fake_last_name
        return fake_full_name
    except:
        return full_name

@register.simple_tag(takes_context=True)
def url_replace(context, field, value):
    dict_ = context['request'].GET.copy()
    dict_[field] = value
    return urlencode(dict_)