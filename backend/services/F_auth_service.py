from services.F_supabase_client import get_supabase_client
from supabase_auth.errors import AuthUnknownError

def register_user(email: str, password: str):
    client = get_supabase_client()

    try:
        response = client.auth.sign_up({
            "email": email,
            "password": password,
        })

        return response
    except (AttributeError, TypeError) as error:
        raise AuthUnknownError(
            "Invalid response from authentication service",
            error,
        ) from error
    finally:
        client.auth.close()


def login_user(email: str, password: str):
    client = get_supabase_client()

    try:
        response = client.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })

        return response
    except (AttributeError, TypeError) as error:
        raise AuthUnknownError(
            "Invalid response from authentication service",
            error,
        ) from error
    finally:
        client.auth.close()


def get_user_from_token(token: str):
    client = get_supabase_client()

    try:
        response = client.auth.get_user(token)

        if response is None:
            return None

        return response.user
    finally:
        client.auth.close()
