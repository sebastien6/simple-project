# Project

The application is a simple web server using python flask, redis, sqlalquemy.

EXTERNAL API:
    The application depends on three external API providers. Key for those providers have to be set in .env file:

    environment variable: GEOLOC_KEY
    API Provider: https://api.ipdata.co/

    environment variable: CURRENCY_KEY
    API Provider: https://free.currencyconverterapi.com/api

    environment variable: WEATHER_KEY
    API Provider: http://api.openweathermap.org/

DATABASE:
    The application is using PostgresSQL database as relational database to store information about user, and geolocation
    Redis is used to store user sessions and cache API request to external API provider (exception of geolocation)

AUTHENTICATION:
    webapp is based on database authentication only. No external provider set.

KEY MISSING ELEMENTS:
    - error handling
    - unit testing
    - Higher security (HTTPS, password encryption by key instead of hash, ...)