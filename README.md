# SlothCMS

SlothCMS is an experimental project during which I'd like to learn Python, Rust and VanillaJS and try to design a bigger app all on my own.

To activate this project's virtualenv, run `pipenv shell`.
Alternatively, run a command inside the virtualenv with `pipenv run`.

## Rust setup

Use `cargo build` to create a compiled library.

On Windows use `cp .\target\debug\toes.dll ..\..\toes.pyd` to make the library available.

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
- Python 3.8
- PostgreSQL 12
- Rust 1.54.0
- (optional, recommended) Gunicorn


### Bucket list
- multilingual blog ✅
- rss reader 🛠
- post scheduler 🛠
- twitter integration 🛠
- post formats ✅
- user management (not a priority)
- Toe compiler (Python) ✅
- Markdown compiler (Python) ✅
  - currently v2 (working name of Markdown dialect SlothMark)
- IndieWeb 🛠
- Toe compiler (Rust) 🛠
- Markdown compiler (Rust) 🛠