# PolyConf

## Design

* Config reads data sources with _zero schema knowledge_
    - There are cases where at least _some_ incoming config is required
        + sql/sqlite would need a path; probably a table name, maybe some field names
    - Unless extremely easy, obvious, or naturally supported, many types will remain **strings**.
        + Type casting is the applications domain, typically with `pydantic` models.
    - If not natively/naturally supported, implicit nesting follows the dunder IFS convention.
* Config reads a source to scrape config-like data and return a mapping
* Some sources support native nesting and some do not
    - [X] JSON, TOML, YAML files
    - [X] HTTP GET (using a serialization like above)
    - [X] Command source (should return a serialization like above).
    - [ ] Environment variables
    - [ ] Files like `.envrc` (because they contain environment variables)
    - [ ] SQL (and/or sqlite) is TBD.  It's likely possible but high effort (and low priority).
* Config returns a _mapping_, intended to be consumed, transformed, validated, etc. by an application.
* Config takes a _layered_ approach, where the result is an applied view of a hierarchy of read values.
    - NOTE: This is natively supported with `collections.ChainMap`
* Config captures metadata regarding _where_ a value came from
    - The intent is to aid debugging.
      With so many potential data sources, it could be difficult to discern where a value came from.
    - Two views should be possible:
        1. A 2-col table that only shows the winning source for each field.
        2. An n-col table that shows `X` for every source that provided a value.
           The cols are in hierarchical order so the "winner" is the `X` furthest to the left (or right; TBD)


### Conventions

* In _ALL_ cases, _always_:
    - Source config fields/names are `UPPERCASE`
        + Inspired by `flask.Config`
        + Provides a way to return _ignored_ "fields"
            * the most useful example being a python object/module config source.
        + This does not apply to the result `Config` object in the APP,
          because it only contains the desired fields already.
* Implicit nesting in sources that don't support nesting
    - IFS is double-underscores.
        + Other symbols were considered, but to have the best x-source compatibility,
          I chose to double-up the underscore.


### Choices

* The hierarchy order and/or membership is _NOT_ (currently) configurable.
    - It _IS_ recognized as a valuable feature,
      it's just postponed because I expect it to require an unreasonable amount of effort.


### Returned Mapping

The returned mapping is essentially a list of "datums" where each "datum" has... 

```python
reader = ConfigReader(
    # runtime config goes_here
    app_name="widget",
    trim_prefix=True,
    given={
        "THIS": "this",
        "WIDGET_THAT": "that",
    },
)
result: ConfigResult = reader.read()

assert result.raw == {
    "version": "v1",  # The schema is versioned!
    "status": "ok",   # TBD: return exception objects when not "ok"?
    "result_list": [
        {"key": "FOO", "value": "foo", "sources": ["file_yaml://.../foo.yaml"]},
        {"key": "BAR", "value": "bar", "sources": ["http://x.y/z", "env://WIDGET_BAR"]},
        {
            "key": "LOREM",
            "value": {
                "key": "IPSUM",
                "value": "ipsum",
                "sources": ["sql://..."],
            },
            "sources": ["sql://..."],
        },
        {"key": "THIS", "value": "this", "sources": ["given://THIS"]},
        {"key": "THAT", "value": "that", "sources": ["given://WIDGET_THAT"]},
    ],
}

assert result.version == "v1"
assert result.ok == True
assert result.as_list == [
    {"key": "FOO", "value": "foo", "sources": ["file_yaml://.../foo.yaml"]},
    {"key": "BAR", "value": "bar", "sources": ["http://x.y/z", "env://WIDGET_BAR"]},
    {"key": "LOREM", "value": "(truncated)", "sources": ["sql://..."]},
    {"key": "THIS", "value": "this", "sources": ["given://THIS"]},
    {"key": "THAT", "value": "that", "sources": ["given://WIDGET_THAT"]},
]
assert result.as_obj == {
    "FOO": "foo",
    "BAR": "bar",
    "LOREM": {
        "IPSUM": "ipsum",
    },
    "THIS": "this",
    "THAT": "that",
}
```

* `app_name` affects things like XDG paths, env var prefix, etc.
* `trim_prefix` removes the app name prefix from keys.
* `version` is checked.
* Key names are uppercase!  It's up to the application to ETL the result.


## TODO

* Prob clear by now but this package is intended to be spun out into its own project for an app to use.
* Ideas for new sources
    - Python object (which can also be a module)
        + Reference `flask.Config`
    - Other remotes:
        + AWS: S3, DynamoDB, etc.
    - CSV file
    - CLI options
        + As opposed to other sources, this would be known and provided.
          The goal is to allow CLI options to participate in the layered result
          and thus also the debugging tools.
        + Maybe generalize as "Given" or "Known"?
    - Thinking outside the box.  These are low priority, unrealistic, or silly -- more of a brainstorming exercise.
        + Interactive prompt
        + Image or Text processing
        + XML
        + Git repo
        + Hashicorp Vault
        + Kubernetes `ConfigMap` (or other resource)
        + Config itself as a long-running HTTP service, listening for triggers
        + Spring Cloud Config (and "Config Server")
        + Redis
    - ...
* Also inspired by `flask.Config`, generalize the "file" source, so it takes a `load` function.
* Provide way to only query a single source, ad hoc.
* With many sources, the dependency tree may explode.
    - Consider a plugin architecture, separating out the sources into projects.
    - Consider "optional groups" (I can't recall the real name): `config[yaml]`, `config[http]`, `config[s3]`
    - For the sake of simplicity, I'll defer until later.
