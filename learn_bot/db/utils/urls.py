import requests
import validators


def is_valid_github_url(url: str) -> bool:
    return bool(validators.url(url))


def is_url_accessible(url: str) -> bool:
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException:
        return False
    return bool(response)
