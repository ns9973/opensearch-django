from django import template

register = template.Library()


@register.filter(name="get_source")
def get_source(d, k):
    return d.get(k, None)


@register.filter(name="get_value")
def get_value(d, k):
    return d.get(k, None)


@register.filter(name="concat_feature_terms")
def concat_feature_terms(d, k):
    temp_array = [item[0] for item in d[k]]
    return "".join(temp_array)
