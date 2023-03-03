# SlothCMS

[![CodeQL](https://github.com/xgebi/Sloth/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/xgebi/Sloth/actions/workflows/codeql-analysis.yml) 

SlothCMS is an experimental project during which I'd like to learn Python, Rust and VanillaJS and try to design a bigger app all on my own.

To activate this project's virtualenv, run `pipenv shell`.
Alternatively, run a command inside the virtualenv with `pipenv run`.


### Accessing Rust functions

```
import toes

toes.parse_markdown_to_html(string)
toes.generate_post()
toes.generate_post_type()
toes.generate_all()
```


## Requirements
- Python 3.10
- PostgreSQL 12
- (optional, recommended) Gunicorn
