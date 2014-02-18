from decimal import Decimal
import isodate


def coerce_type(x):
    """
    Attempt use type coercion on known types
    <http://www.w3.org/TR/json-ld/#type-coercion>, otherwse the @value is returned

    Currently supports all the XMLSchema built-in primative datatypes:

    http://www.w3.org/TR/xmlschema-2/#built-in-primitive-datatypes

    ## Untyped values are passed through as-is:

    >>> coerce_type(1)
    1

    >>> coerce_type(u'1')
    u'1'

    ## Strings

    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#string',
    ...    '@value': u'string'}
    ... )
    u'string'


    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#string',
    ...    '@value': 1}
    ... )
    u'1'

    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#string',
    ...    '@value': True}
    ... )
    u'true'


    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#string',
    ...    '@value': False}
    ... )
    u'false'


    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#boolean',
    ...    '@value': '1'}
    ... )
    True

    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#boolean',
    ...    '@value': '0'}
    ... )
    False

    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#boolean',
    ...    '@value': 'true'}
    ... )
    True

    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#boolean',
    ...    '@value': 'false'}
    ... )
    False

    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#boolean',
    ...    '@value': '???'}
    ... )
    False

    ## decimal

    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#decimal',
    ...    '@value': '0.1'}
    ... )
    Decimal('0.1')


    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#decimal',
    ...    '@value': 'xxx'}
    ... )
    Traceback (most recent call last):
        ...
    ValueError: Could not coerce 'xxx' to 'http://www.w3.org/2001/XMLSchema#decimal': InvalidOperation("Invalid literal for Decimal: 'xxx'",)

    ## float
    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#float',
    ...    '@value': '0.1'}
    ... )
    0.1


    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#float',
    ...    '@value': 'xxx'}
    ... )
    Traceback (most recent call last):
        ...
    ValueError: Could not coerce 'xxx' to 'http://www.w3.org/2001/XMLSchema#float': ValueError('could not convert string to float: xxx',)

    ## double
    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#double',
    ...    '@value': '0.1'}
    ... )
    0.1


    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#double',
    ...    '@value': 'xxx'}
    ... )
    Traceback (most recent call last):
        ...
    ValueError: Could not coerce 'xxx' to 'http://www.w3.org/2001/XMLSchema#double': ValueError('could not convert string to float: xxx',)

    ## duration
    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#duration',
    ...    '@value': 'P5Y'}
    ... )
    isodate.duration.Duration(0, 0, 0, years=5, months=0)

    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#duration',
    ...    '@value': 'xxx'}
    ... )
    Traceback (most recent call last):
        ...
    ValueError: Could not coerce 'xxx' to 'http://www.w3.org/2001/XMLSchema#duration': ISO8601Error("Unable to parse duration string 'xxx'",)
    
    
    """
    if isinstance(x, dict):
        type_iri = x.get("@type")
        value = x.get("@value")
    else:
        type_iri = None
        value = x

    def as_string():
        if isinstance(value, bool):
            # convert it to a valid http://www.w3.org/2001/XMLSchema#boolean string
            return unicode(value).lower()
        else:
            return unicode(value)

    def as_bool():
        return value in {"true", "1"}

    try:
        return {
            "http://www.w3.org/2001/XMLSchema#string": as_string,
            "http://www.w3.org/2001/XMLSchema#boolean": as_bool,
            "http://www.w3.org/2001/XMLSchema#decimal": lambda: Decimal(value),
            "http://www.w3.org/2001/XMLSchema#float": lambda: float(value),
            "http://www.w3.org/2001/XMLSchema#double": lambda: float(value),
            "http://www.w3.org/2001/XMLSchema#duration": lambda: isodate.parse_duration(
                value
            ),
        }.get(type_iri, lambda: value)()
    except Exception, e:
        raise ValueError("Could not coerce {!r} to {!r}: {!r}".format(
            value,
            type_iri,
            e
        ))
