from django import template
from django.template.base import TagHelperNode, parse_bits
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


@assignment_tag_with_cdata(register)
def compact(data, cdata=""):
    """
    >>> c = template.Context({
    ...   'story': {
    ...     '@context': {
    ...       'title': 'http://schema.org/headline',
    ...     },
    ...     'title': 'This is the title',
    ...   }
    ... })
    >>> t = template.Template('''
    ... {% load djsonld %}
    ... {% compact story as story_compact %}{
    ...    "headline": "http://schema.org/headline"
    ... }{% endcompact %}
    ... {{ story_compact.headline }}
    ... ''')
    >>> t.render(c).strip()
    u'This is the title'
    """
    context = json.loads(cdata)
    return jsonld.compact(data, context)
