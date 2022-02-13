from django import template

register = template.Library()


@register.filter("remove_attr")
def remove_attr(field, attr):
    if attr in field.field.widget.attrs:
        del field.field.widget.attrs[attr]
    return field


@register.filter("getimg")
def getimg(field):
    field = field.split(" ")
    for f in field:
        if 'src' in f:
            field = """<img {0} style="
    width: 300px;
    height: 300px;
    margin-top: 10px;
    border-style: solid;
    border-radius: 20px;
">""".format(f)
            return field


@register.filter(name='add_attr')
def add_attr(field, css):
    attrs = {}
    definition = css.split(',')

    for d in definition:
        if ':' not in d:
            attrs['class'] = d
        else:
            key, val = d.split(':')
            attrs[key] = val

    return field.as_widget(attrs=attrs)
