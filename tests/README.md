# Tests

These tests use `pytest`. You can install all requirements from teh `requirements.txt` file like:

```
python3 -m pip install -r requirements.txt
```

The tests assume that ScapeServ is running at `http://localhost:5006` without any API key.

## How tests work

`pytest` will run any function named in the form `test_*` in any file with a name in the form of either `test_*` or `*_test.py`.

In order to run tests that involve calling 3rd party APIs, you'll need to create a `.env` like:

```
OPENAI_API_KEY="..."
BING_API_KEY="..."
```

By default, a model is placed in `lm.py` for testing; swap this model out with another you may have access to.

In order to run tests that involve a ScrapeServ server, you'll need to run that server at `http://localhost:5006`.

`pytest` is invoked like:

```
pytest tests
```

or 

```
pytest .
```

to run all tests (from outside `tests` and within `tests`, respectively)

or like:

```
pytest test_lm.py
```

to invoke only one module's tests.

And to invoke a single test within a module:

```
pytest test_scraper.py::test_scrape_serv
```

See more information on invoking pytest [here](https://docs.pytest.org/en/stable/how-to/usage.html#usage).
