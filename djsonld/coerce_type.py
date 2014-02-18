from decimal import Decimal
from dateutil import parser as dt_parser
import isodate
from urlparse import urlparse


def coerce_type(x):
    """
    Attempt use type coercion on known types
    <http://www.w3.org/TR/json-ld/#type-coercion>, otherwse the @value is returned

    Currently supports most of the XMLSchema built-in primative datatypes:

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
    ...    '@value': 'xxx'}
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
    
    
    ## dateTime
    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#dateTime',
    ...    '@value': '2014-02-18T16:07:52-05:00'}
    ... )
    datetime.datetime(2014, 2, 18, 16, 7, 52, tzinfo=tzoffset(None, -18000))

    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#dateTime',
    ...    '@value': 'xxx'}
    ... )
    Traceback (most recent call last):
        ...
    ValueError: Could not coerce 'xxx' to 'http://www.w3.org/2001/XMLSchema#dateTime': ValueError(u'unknown string format',)

    ## time
    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#time',
    ...    '@value': '16:07:52-05:00'}
    ... )
    datetime.time(16, 7, 52)

    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#time',
    ...    '@value': 'xxx'}
    ... )
    Traceback (most recent call last):
        ...
    ValueError: Could not coerce 'xxx' to 'http://www.w3.org/2001/XMLSchema#time': ValueError(u'unknown string format',)

    ## date
    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#date',
    ...    '@value': '2014-02-18T16:07:52-05:00'}
    ... )
    datetime.date(2014, 2, 18)

    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#date',
    ...    '@value': 'xxx'}
    ... )
    Traceback (most recent call last):
        ...
    ValueError: Could not coerce 'xxx' to 'http://www.w3.org/2001/XMLSchema#date': ValueError(u'unknown string format',)


    ## hexBinary
    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#hexBinary',
    ...    '@value': u'0FB7'}
    ... )
    '\\x0f\\xb7'

    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#hexBinary',
    ...    '@value': u'xxx'}
    ... )
    Traceback (most recent call last):
        ...
    ValueError: Could not coerce u'xxx' to 'http://www.w3.org/2001/XMLSchema#hexBinary': TypeError('Odd-length string',)

    ## base64Binary
    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#base64Binary',
    ...    '@value': 'aGVsbG8=\\n'}
    ... )
    'hello'

    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#base64Binary',
    ...    '@value': 'xxx'}
    ... )
    Traceback (most recent call last):
        ...
    ValueError: Could not coerce 'xxx' to 'http://www.w3.org/2001/XMLSchema#base64Binary': Error('Incorrect padding',)

    ## anyURI
    >>> coerce_type(
    ...   {'@type': 'http://www.w3.org/2001/XMLSchema#anyURI',
    ...    '@value': 'http://www.google.com/'}
    ... )
    ParseResult(scheme='http', netloc='www.google.com', path='/', params='', query='', fragment='')

    
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

    def as_datetime():
        return dt_parser.parse(value)

    def as_time():
        return as_datetime().time()

    def as_date():
        return as_datetime().date()

    def as_duration():
        return isodate.parse_duration(value)

    def as_binhex():
        return value.decode("hex")

    def as_base64():
        return value.decode("base64")

    def as_uri():
        return urlparse(value)

    try:
        return {
            "http://www.w3.org/2001/XMLSchema#string": as_string,
            "http://www.w3.org/2001/XMLSchema#boolean": as_bool,
            "http://www.w3.org/2001/XMLSchema#decimal": lambda: Decimal(value),
            "http://www.w3.org/2001/XMLSchema#float": lambda: float(value),
            "http://www.w3.org/2001/XMLSchema#double": lambda: float(value),
            "http://www.w3.org/2001/XMLSchema#duration": as_duration,
            "http://www.w3.org/2001/XMLSchema#dateTime": as_datetime,
            "http://www.w3.org/2001/XMLSchema#time": as_time,
            "http://www.w3.org/2001/XMLSchema#date": as_date,
            "http://www.w3.org/2001/XMLSchema#hexBinary": as_binhex,
            "http://www.w3.org/2001/XMLSchema#base64Binary": as_base64,
            "http://www.w3.org/2001/XMLSchema#anyURI": as_uri,
        }.get(type_iri, lambda: value)()
    except Exception, e:
        raise ValueError("Could not coerce {!r} to {!r}: {!r}".format(
            value,
            type_iri,
            e
        ))
