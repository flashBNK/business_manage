def make_email(index: int = 1) -> str:
    return f"user{index}@example.com"


def make_password() -> str:
    return "StrongPassword123!"


def make_check_account_payload(email: str | None = None) -> dict:
    return {"email": email or make_email()}


def make_sign_up_payload(
    email: str,
    password: str | None = None,
    first_name: str = "John",
    last_name: str = "Doe",
    company_name: str | None = None
) -> dict:
    return {
        "email": email,
        "password": password or make_password(),
        "first_name": first_name,
        "last_name": last_name,
        "company_name": company_name,
    }


def make_login_payload(email: str, password: str | None = None) -> dict:
    return {"email": email, "password": password or make_password()}
