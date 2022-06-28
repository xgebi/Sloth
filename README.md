# SlothCMS

[![CodeQL](https://github.com/xgebi/Sloth/actions/workflows/codeql-analysis.yml/badge.svg)](https://github.com/xgebi/Sloth/actions/workflows/codeql-analysis.yml) 

SlothCMS is an experimental project during which I'd like to learn Python, Rust and VanillaJS and try to design a bigger app all on my own.

To activate this project's virtualenv, run `pipenv shell`.
Alternatively, run a command inside the virtualenv with `pipenv run`.

## Rust setup

Toes live in `rust/toes`.

Use `cargo build` to create a compiled library for development purposes. For production use `cargo build --release`.


On Windows use `cp .\target\<target>\toes.dll ..\..\toes.pyd` to make the library available.

On Linux TBD.

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
- Rust 1.54.0
- (optional, recommended) Gunicorn

### TO-DO List
- app.lists
- app.settings.integration
- app.libraries deletion
- app.rss
- scheduling


### Bucket list
- multilingual blog ✅
- rss reader ❌
- post scheduler 
- twitter integration 
- post formats ✅
- user management (not a priority)
- Toe compiler (Python) ✅
- Markdown compiler (Python) ✅
  - currently v2 (working name of Markdown dialect SlothMark)
- IndieWeb 
- Toe compiler (Rust) 🛠
- Markdown compiler (Rust) 🛠
- Dockerization 🛠
- CSRF
- Custom WSGI framework