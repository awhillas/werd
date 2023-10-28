# werd

[![PyPI](https://img.shields.io/pypi/v/werd.svg)](https://pypi.org/project/werd/)
[![Changelog](https://img.shields.io/github/v/release/awhillas/werd?include_prereleases&label=changelog)](https://github.com/awhillas/werd/releases)
[![Tests](https://github.com/awhillas/werd/workflows/Test/badge.svg)](https://github.com/awhillas/werd/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/awhillas/werd/blob/master/LICENSE)


CLI tool for static website generation with a focus on translation to any number of languages via AI

- Free software: MIT license
- Documentation: [https://werd.readthedocs.io](https://werd.readthedocs.io)

## Features

- Translate content, marked up in markdown, into as many languages as desired (or at least as many as OpenAI's ChatGPT can translate into)
- Render content as HTML using Jinja2 templates (partially finished)

## Installation

Install this tool using `pip`:

    pip install werd

## Usage

For help, run:

    werd --help

You can also use:

    python -m werd --help

## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:

    cd werd
    python -m venv venv
    source venv/bin/activate

Now install the dependencies and test dependencies:

    pip install -e '.[test]'

To run the tests:

    pytest

## TODOs
In order of most likely to-do to least

- [ ] Refactor to use [click](https://click.palletsprojects.com/)
- [ ] Refactor commands to more uniform OOP to make shared state easier
- [ ] Commands
    - [ ] **translate**
        - [ ] Blog filename parser
        - [ ] Error page content
        - [ ] Parallel inference requests to speed up translations
        - [ ] force generate all languages --flag
        - [ ] force generate 1 language --flag
        - [X] translate file names to be used for navigation.
        - [X] content using OpenAI
    - [ ] render **HTML** using theme
        - [ ] Non-content driven pages i.e.
            - [ ] Site index language selection list
            - [ ] blog index
            - [X] site root redirect to language page
            - [X] home/landing page
        - [ ] Error page, list content in all languages
        - [X] navigation
        - [X] Switch language
        - [X] 1-to-1 rendering of content to a page using Jinja2 theme templates
    - [ ] **go** - translate and render in one command
    - [ ] **deploy**
        - [ ] to S3 bucket or
        - [ ] Github pages?
        - [ ] ftp?
    - [ ] **scaffold** - setup content, templates directories and config file.
- [ ] Documentation site (using werd and translated)

## Credits

This project was bootstrapped from the [cookiecutter](https://cookiecutter.readthedocs.io/) template <https://github.com/simonw/click-app>.

The name `werd` was the result of the letters being close together on the keyboard and it not being taken as a package on pipy