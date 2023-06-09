import logging

import requests
import validators

logger = logging.getLogger(__name__)


def is_valid_github_url(url: str) -> bool:
    return bool(validators.url(url)) and is_github_url(url)


def is_url_accessible(url: str) -> bool:
    try:
        response = requests.get(url)
    except requests.exceptions.RequestException as e:
        logger.exception(e)
        return False
    return bool(response)


def is_github_url(url: str) -> bool:
    splitted_url = url.split("/")
    return len(splitted_url) > 2 and splitted_url[2] == "github.com"


def is_github_pull_request_url(url: str) -> bool:
    splitted_url = url.split("/")
    return len(splitted_url) == 7 and splitted_url[2] == "github.com" and splitted_url[5] == "pull"


def is_github_repo_url(url: str) -> bool:
    splitted_url = url.split("/")
    return len(splitted_url) == 5 and splitted_url[2] == "github.com"
