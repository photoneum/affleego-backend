# django-template-boilerplate

Django Template
This project was generated with [`wemake-django-template`](https://github.com/wemake-services/wemake-django-template), but modified by Emmanuel Anebi, to use Nginx over Caddy for request proxy and other suitable configurations.

Current template version is: [bc12b3d](https://github.com/wemake-services/wemake-django-template/tree/bc12b3d15dc90f8e5b2e42b22bab2d1ef5251a55). See what is [updated](https://github.com/wemake-services/wemake-django-template/compare/bc12b3d15dc90f8e5b2e42b22bab2d1ef5251a55...master) since then.


[![wemake.services](https://img.shields.io/badge/%20-wemake.services-green.svg?label=%20&logo=data%3Aimage%2Fpng%3Bbase64%2CiVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAMAAAAoLQ9TAAAABGdBTUEAALGPC%2FxhBQAAAAFzUkdCAK7OHOkAAAAbUExURQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAP%2F%2F%2F5TvxDIAAAAIdFJOUwAjRA8xXANAL%2Bv0SAAAADNJREFUGNNjYCAIOJjRBdBFWMkVQeGzcHAwksJnAPPZGOGAASzPzAEHEGVsLExQwE7YswCb7AFZSF3bbAAAAABJRU5ErkJggg%3D%3D)](https://wemake-services.github.io)
[![wemake-python-styleguide](https://img.shields.io/badge/style-wemake-000000.svg)](https://github.com/wemake-services/wemake-python-styleguide)


## Prerequisites

You will need:

- `python3.12` (see `pyproject.toml` for exact version), use `pyenv install`
- `postgresql` (see `docker-compose.yml` for exact version)
- Latest `docker`


## Development

When developing locally, we use:

- [`editorconfig`](http://editorconfig.org/) plugin (**required**)
- [`poetry`](https://github.com/python-poetry/poetry) (**required**)
- [`pyenv`](https://github.com/pyenv/pyenv)


## Documentation

Full documentation is available here: [`docs/`](docs).

### Mailhog

Mailhog is a simple SMTP server that captures emails sent from the application.

To start mailhog, run `docker compose -f docker-compose.mailhog.yml -p mailhog-standalone up -d`.

To stop mailhog, run `docker compose -f docker-compose.mailhog.yml -p mailhog-standalone down`.
