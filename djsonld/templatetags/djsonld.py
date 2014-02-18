from django import template
from django.template.base import TagHelperNode, parse_bits
from ..coerce_type import coerce_type
from inspect import getargspec
from pyld import jsonld
import json

register = template.Library()


def assignment_tag_with_cdata(library, func=None, takes_context=None, name=None):
    def dec(func):
        params, varargs, varkw, defaults = getargspec(func)

        class AssignmentNode(TagHelperNode):
            def __init__(self, nodelist, takes_context, args, kwargs, target_var):
                super(AssignmentNode, self).__init__(takes_context, args, kwargs)
                self.nodelist = nodelist
                self.target_var = target_var

            def render(self, context):
                resolved_args, resolved_kwargs = self.get_resolved_arguments(context)
                resolved_kwargs['cdata'] = self.nodelist.render(context)
                context[self.target_var] = func(*resolved_args, **resolved_kwargs)
                return ''

        function_name = (name or
            getattr(func, '_decorated_function', func).__name__)

        end_name = "end{0}".format(function_name)

        def compile_func(parser, token):
            bits = token.split_contents()[1:]
            if len(bits) < 2 or bits[-2] != 'as':
                raise template.TemplateSyntaxError(
                    "'%s' tag takes at least 2 arguments and the "
                    "second last argument must be 'as'" % function_name)
            target_var = bits[-1]
            bits = bits[:-2]
            args, kwargs = parse_bits(parser, bits, params,
                varargs, varkw, defaults, takes_context, function_name)

            nodelist = parser.parse((end_name, ))
            parser.delete_first_token()

            return AssignmentNode(nodelist, takes_context, args, kwargs, target_var)

        compile_func.__doc__ = func.__doc__
        library.tag(function_name, compile_func)
        return func

    if func is None:
        # @register.assignment_tag(...)
        return dec
    elif callable(func):
        # @register.assignment_tag
        return dec(func)
    else:
        raise template.TemplateSyntaxError("Invalid arguments provided to assignment_tag_with_cdata")


@register.filter
def djsonld_coerce(x):
    return coerce_type(x)


@assignment_tag_with_cdata(register, name="djsonld_compact")
def compact(data, cdata=""):
    """Compacts a dict 

    >>> c = template.Context({
    ...   'story': {
    ...     '@context': {
    ...       'title': 'http://schema.org/headline',
    ...       'created': {
    ...           '@id': 'http://schema.org/dateCreated',
    ...           '@type': 'http://www.w3.org/2001/XMLSchema#dateTime'
    ...       },
    ...     },
    ...     'title': 'This is the title',
    ...     'created': '2014-02-14',
    ...   }
    ... })
    >>> t = template.Template('''
    ... {% load djsonld %}
    ... {% djsonld_compact story as sc %}{
    ...    "headline": "http://schema.org/headline",
    ...    "dateCreated": "http://schema.org/dateCreated"
    ... }{% enddjsonld_compact %}
    ... {{ sc.headline }}{{ sc.dateCreated|djsonld_coerce }}
    ... ''')
    >>> t.render(c).strip()
    u'This is the title2014-02-14'

    Notice that the schema:dateCreated value is still a string, you
    will still need to parse it using a filter.
    """
    context = json.loads(cdata)
    return jsonld.compact(data, context)
        

