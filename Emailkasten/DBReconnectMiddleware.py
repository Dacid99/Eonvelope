import time

from django.db import OperationalError, connection

from .constants import DatabaseConfiguration


class DBReconnectMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        max_retries = DatabaseConfiguration.RECONNECT_RETRIES  # Set the maximum number of retries
        delay = DatabaseConfiguration.RECONNECT_DELAY        # Delay in seconds between retries

        for attempt in range(max_retries):
            try:
                # Try to connect to the database
                with connection.cursor():
                    break  # If connection succeeds, exit the loop
            except OperationalError:
                if attempt == max_retries - 1:
                    raise  # Raise the error if the maximum retries are exceeded
                time.sleep(delay)  # Wait before retrying

        # Process the request
        response = self.get_response(request)
        return response
