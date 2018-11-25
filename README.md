# App backend

The webserver for managing users, carts, cart items and returning information like footprint per product from start to end date.


# Setup and run

Setup the environment variables:

```sh
cp .env.example .env
```

Start the PostgreSQL database:

```sh
docker-compose up
```

Start the Flask App Backend server:

```sh
pipenv install
pipenv run python app.py
```

The API server should now be available on `localhost:5000`!
