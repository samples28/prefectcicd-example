import httpx
import os
import json
from prefect import flow, task
from prefect.client.schemas.schedules import IntervalSchedule
from datetime import timedelta


@task(log_prints=True, retries=3, retry_delay_seconds=5)
def get_stars_for_repo(client: httpx.Client, repo: str) -> int:
    """
    Given a GitHub repository, returns the number of stars.
    """
    try:
        response = client.get(f"https://api.github.com/repos/{repo}")
        response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        stargazer_count = response.json()["stargazers_count"]
        print(f"{repo} has {stargazer_count} stars")
        return stargazer_count
    except httpx.HTTPStatusError as e:
        print(f"Error fetching stars for {repo}: {e}")
        # Decide what to do on error, e.g., return a specific value or let the task fail
        # In this case, with retries, it will try again. If it ultimately fails, the task run will be marked as Failed.
        raise


@flow
def retrieve_github_stars(repos: list[str]):
    """
    A flow that retrieves the number of stars for a list of GitHub repositories.
    """
    with httpx.Client() as client:
        get_stars_for_repo.map(client=client, repo=repos)


if __name__ == "__main__":
    # Load the list of repositories from an environment variable.
    # The variable should contain a JSON string of a list of repos.
    # Example: '["prefectHQ/prefect", "prefectHQ/marvin"]'
    default_repos = '["python/cpython", "prefectHQ/prefect", "langgenius/dify"]'
    repos_json = os.getenv("REPOS", default_repos)
    try:
        repo_list = json.loads(repos_json)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in REPOS environment variable. Using default repos.")
        repo_list = json.loads(default_repos)

    retrieve_github_stars.serve(
        name="github-stars-flow",  # A name for the deployment
        parameters={"repos": repo_list},
        schedule=IntervalSchedule(interval=timedelta(minutes=10)),
    )
