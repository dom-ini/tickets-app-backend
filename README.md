# Tickts
## Project description

Detailed information about this project are included in [the front-end repository](https://github.com/dom-ini/tickets-app-frontend/).

## Links
### Project website
https://tickets-app-frontend.vercel.app/

### Front-end repository
https://github.com/dom-ini/tickets-app-frontend/

## Tech stack
- Python 3.10
- FastAPI
- PostgreSQL 15
- Docker

## Getting started
In the project directory, create *.env* file and add the required values (you can see *.env.example* file for reference).

Run `docker-compose up` to run the development server.

Access the API documentation at http://localhost:8000/docs#/.

To fill the database with example data, run `python ./cli.py populate-db ./example_data.json` and `python ./cli.py regenerate-image-urls` in the web container terminal.

To create an user, run `python ./cli.py create-user` or `python ./cli.py create-superuser`.

To run tests, run these commands in the web container terminal:
- `make unit` - for unit tests,
- `make integration` - for integration tests,
- `make test` - for all tests.
