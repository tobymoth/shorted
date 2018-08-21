# `shorted`

URL shortener sample code.

## Install

The distribution consists of two docker containers:
1. The web service - implemented in `flask` and listening on `localhost:5000`.
2. A standard postgres container with a `urls` table added for looking up full URLs from their short equivalents.

These containers are orchestrated by `docker-compose` (a poor man's `kubernetes`). Therefore, in order to install:

1. Download [`docker`](https://www.docker.com/products/docker-engine)
1. The download may bundle `docker-compose`. If not, install [`docker-compose`](https://docs.docker.com/compose/install/)

## Running it

Helper commands are bundled in a `Makefile`. The steps are:

1. `make build` - to build the shorted web service
2. `make up` - to start both the backend database and the web service
3. Optionally `make test` - to run the linting and `pytest` tests

## The Requirements

The challenge was to create a URL shortening service which is capable of processing 1,000 requests per second.
The following is a summary of the specification broken down into a table. Each requirement `A_B_C` has a corresponding test `test_a_b_c` [here](tests/test_shorted.py).

Requirement              | Method | Status Code | Error           | Description
-------------------------|--------|-------------|-----------------|------------
CREATE_SHORT_URL         | POST   | 201         | -               | Create as per spec
CONTENT_TYPE_IS_JSON     | POST   | 400         | INVALID_CONTENT | Content type must be `application/json`
INVALID_SCHEMA           | POST   | 400         | INVALID_SCHEMA  | JSON must be an object with a `url` property
INVALID_URL              | POST   | 400         | INVALID_URL     | URL must look plausible
CONFLICT                 | POST   | 400         | CONFLICT        | Explained [below](#Sizing-And-Conflicts)
REDIRECT_TO_ORIGINAL_URL | GET    | 302         | -               | Get as per spec
NO_SUCH_SHORTCUT         | GET    | 404         | NO_SUCH_SHORTCUT| We have not created this link

As the API in the specification consists of just two routes - a `POST` and a `GET` - the matrix
maps according to method.

Errors are transmitted within a JSON payload of the form:

```JSON
{
    "error": "ERROR_CODE",
    "description": "For the humans among us"
}
```

## Sizing And Conflicts

We are supposed to deal with up to 1000 requests per second.
This means 1000 * 30 * 24 * 3600 requests per month ~= 2.5 billion requests per month.

First let's consider storage. If each URL is, say, 100 characters then we are looking
at an upper bound of about 1 terabyte per annum although of course we expect many of
the requests to be redirections rather than requests for new short URLs.

Now let's consider the size of our short URLs.
For shortening, many existing services seem to be returning base 62 keys of length 10.
If we pretend that we have base 64 encodings (near enough for these estimates) then
each character gives 6 bits, for a total of 60 bits.

2 ^ 60 = (2^10)^6 ~= (10^3)^6 = 10^18

This is easily a large enough space to deal with our (10 ^ 9) * 2.5 requests per month.
There is a chance that we will get a conflict i.e. have two different URLs sharing
the same key, but it is of the order of 10^9 per month.

## Choosing An Algorithm

We could yield unique short URLs by tracking some sequence number somewhere but this
is not a scaleable solution. An obvious alternative is to go with:

```python
def make_short_url(long_url):
    return base62(some_cryptographicish_hash(long_url))[:10]
```

I chose `md5sum` with 128 bits - which is more than the 60 bits we need.

## Scaling The Solution - With Reality Checks

Can `postgres` deal with this many requests? Maybe. The `auth` service
where I currently work originally (before I rewrote it) had to create up to 1,000 rows per second
and it just about handled it. However, the data in the `shortener` service
has the unhappy property from a caching point of view that the keys are randomly
distributed. This means that large chunks of the index will be in memory at any one time.

Let's step away for a moment and imagine that we REALLY were thinking about
building a service like this. In reality, it's pretty unlikely to have high
demand immediately. I'd therefore generally implement a first cut around technologies
my team were very familiar with and start generating statistics to help us
work out what our eventual architecture might require.

If most requests were GETs, and generally most GETs had been seen quite recently,
then, say, a `REDIS` cache might be worthwhile and in fact postgres might be good enough.

If write demand really started hitting 1000 requests per second on a regular basis,
then it would be worth looking in detail at NoSQL options. Depending on where and how
we deployed we might consider e.g. Amazon Dynamo, BigTable or Cassandra.

If writes only rarely hit these sorts of numbers or if we needed to pipe
many of our requests to some analytics platform (and how else are we going to make money?)
then it might be worth moving to a [CQRS architecture](https://martinfowler.com/bliki/CQRS.html).

It's worth bearing in mind that in a real solution we would probably have logged in users
generating URLs so we would be able to shard our data on a per-user basis.

Scaling at the web service level is straightforward as the service is stateless. We
can use e.g. `gunicorn` with `eventlet` monkey patching to get scaling on the host level
and Amazon ALBs to get scaling across multiple hosts. This does lead to many
connections to `postgres` but we can manage that with [PgBouncer](https://pgbouncer.github.io).

## Notes On The Implementation - And What Wasn't Implemented

The structure is somewhat overboard for the scale of the problem, but it fits a
general sort of micro-service template. We have blueprints in [routes](app/routes)
and the implementation core in [shorted](app/shorted).

I didn't put in `gunicorn`, but it would hook in at the
[entrypoint](app/app).

Schema validation could be handled with `jsonschema`.

`paver` is a more python-centric solution than `Makefile`. I would use it on a real project.

I'm a big fan of `mypy`. All the functions are typed.

`sqlalchemy` is only used in this service because it has a nice `text` wrapper.
Generally I also use its pooling. Transactions are always created
within explicit context managers to save on the pool issuing needless
rollbacks when objects are returned.
