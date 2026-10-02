from fastapi import APIRouter, Depends, HTTPException
from httpx import RequestError
from pydantic import ValidationError
from supabase_auth.errors import (
    AuthApiError,
    AuthInvalidCredentialsError,
    AuthUnknownError,
    AuthRetryableError,
    AuthWeakPasswordError,
)
from dependencies.F_auth import get_current_user
from models.F_account_data import RegisterData, LoginData
from services.F_auth_service import register_user, login_user
router = APIRouter()

@router.post("/api/auth/register")
def register(data: RegisterData):
    try:
        register_user(str(data.email), data.password)

    except AuthInvalidCredentialsError as error:
        raise HTTPException(
            status_code=422,
            detail="Email and password are required",
        ) from error

    except AuthWeakPasswordError as error:
        raise HTTPException(
            status_code=422,
            detail="Password does not meet the security requirements",
        ) from error

    except (RequestError, AuthRetryableError) as error:
        raise HTTPException(
            status_code=503,
            detail="Authentication service unavailable. Try again later",
        ) from error

    except (AuthUnknownError, ValidationError) as error:
        raise HTTPException(
            status_code=502,
            detail="Invalid response from authentication service",
        ) from error

    except AuthApiError as error:
        status = error.status
        if status not in (400, 403, 422, 429):
            status = 502

        raise HTTPException(
            status_code=status,
            detail="Registration could not be completed",
        ) from error

    return {
        "message": (
            "Registration request accepted. "
            "Check your email if confirmation is required."
        )
    }


@router.post("/api/auth/login")
def login(data: LoginData):
    try:
        response = login_user(str(data.email), data.password)

    except AuthInvalidCredentialsError as error:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
        ) from error

    except AuthWeakPasswordError as error:
        raise HTTPException(
            status_code=422,
            detail="Password does not meet the security requirements",
        ) from error

    except (RequestError, AuthRetryableError) as error:
        raise HTTPException(
            status_code=503,
            detail="Authentication service unavailable. Try again later",
        ) from error

    except (AuthUnknownError, ValidationError) as error:
        raise HTTPException(
            status_code=502,
            detail="Invalid response from authentication service",
        ) from error

    except AuthApiError as error:
        if error.code == "email_not_confirmed":
            raise HTTPException(
                status_code=403,
                detail="Confirm your email before signing in",
            ) from error

        if error.code == "invalid_credentials":
            raise HTTPException(
                status_code=401,
                detail="Invalid email or password",
            ) from error

        status = error.status
        if status not in (400, 401, 403, 422, 429):
            status = 502

        raise HTTPException(
            status_code=status,
            detail="Sign-in could not be completed",
        ) from error

    if response.session is None:
        raise HTTPException(
            status_code=502,
            detail="No session returned",
        )

    return {
        "access_token": response.session.access_token,
        "token_type": response.session.token_type,
        "expires_in": response.session.expires_in,
    }


@router.get("/api/auth/me")
def me(user=Depends(get_current_user)):
    return {
        "id": user.id,
        "email": user.email,
    }
