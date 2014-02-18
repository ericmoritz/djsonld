# djsonld

Support for JSON-LD in Django templates.

## Why?

Ever have to change the name of the context variable? Did you have to change a ton of templates?

Well djsonld helps with that.

`JSON-LD` provides a mechanism for adding semantics to JSON.  This can be utilized to
name dict keys with meaningful IRIs and map them to short names in the template.

### view code

If the view describes its data using a JSON-LD context, we can give meaning to the fields.

```python
def story(request, id):
    return render_to_response(
        "stories/details.html",
		{
		    'story': {
			   '@context': {
			       'title': 'http://schema.org/headline'
			   },
			   'title': 'This is a test'
            }
	    },
		context_instance=Context(request)
	)
```	

We say that the `{{ story.title }}` field is a `http://schema.org/headline` property.

Now in the template, we can say that we want any `http://schema.org/headline` property in
the `{{ story }}` dict to be called `headline`:

```html
{% load djsonld %}
{% djsonld_compact story as sc %}
{
   "headline": "http://schema.org/headline"
}
{% enddjsonld_compact %}
<h1>{{ sc.headline }}</h1>
```

The amazing thing about this is we've just decoupled the template from the view.

The view can now change the name of the `http://schema.org/headline` field and the
template will continue to work.

```python
def story(request, id):
    return render_to_response(
        "stories/details.html",
		{
		    'story': {
			   '@context': {
			       'headline': 'http://schema.org/headline'
			   },
			   # What idiot called this 'title'?
			   'headline': 'This is a test'
            }
	    },
		context_instance=Context(request)
	)
```	

Even though the template's context changed, the fully qualified name
of the field stayed the same and therefore, the short name in the
template is the same.

## type coercion

JSON-LD enables the ablity to do type conversion by using the `@type` directive in
the `@context`.

`JSON-LD` compaction does not automatically convert types to their
native Python types but you can use the `djsonld_coerce` filter to
coerce the type encoded value to a native Python value:

```html
{% load djsonld %}
{% djsonld_compact story as sc %}
{
   "@type": "http://schema.org/CreativeWork",
   "created": {
       "@id": "http://schema.org/dateCreated",
	   "@type": "http://www.w3.org/2001/XMLSchema#dateTime"
    }
}
{% enddjsonld_compact %}
<span>{{ sc.created|djsonld_coerce|date:"Y" }}</span>
```
## Semantic encoding

**TODO**: This is a work in progress

When your data is encoded with `JSON-LD` it is easy to encode that data in your
template with semantic markup such as `HTML5 microdata` or `RDFa`.

### HTML5 microdata

JSON-LD provides enough information to utilize HTML5 microdata with your template variables.

```html
{% load djsonld %}

{% djsonld_compact story as sc %}
{
   "created": {
       "@id": "http://schema.org/dateCreated",
	   "@type": "http://www.w3.org/2001/XMLSchema#dateTime"
    }
}
{% enddjsonld_compact %}
<div itemscope itemtype="{{ ... }}">
    <time itemprop="{{ ... }}" datetime="{{ ... }}">{{ sc.created|djsonld_coerce|date:"Y" }}</time>
</div>
```

### RDFa

You can also easily use RDFa with JSON-LD encoded template variables:

```html
{% load djsonld %}

{% djsonld_compact story as sc %}
{
   "created": {
       "@id": "http://schema.org/dateCreated",
	   "@type": "http://www.w3.org/2001/XMLSchema#dateTime"
    }
}
{% enddjsonld_compact %}
<div about="{{ ... }}">
    <time property="{{ ... }}"
	      typeof="{{ ... }}"
		  content="{{ ... }}">{{ sc.created|djsonld_coerce|date:"Y" }}</time>
</div>
```
