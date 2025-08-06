import pytest
import httpx
from unittest.mock import MagicMock
# We need to import the function from the script to test it
from serve_retrieve_github_stars import get_stars_for_repo

@pytest.fixture
def mock_httpx_client():
    """
    This fixture creates a mock of httpx.Client.
    Using a fixture allows us to reuse this mock setup across multiple tests.
    """
    return MagicMock(spec=httpx.Client)

def test_get_stars_for_repo_success(mock_httpx_client):
    """
    Tests the success case where the GitHub API returns a valid response.
    """
    # Arrange: Set up the mock response
    repo_name = "prefectHQ/prefect"
    expected_star_count = 9999

    mock_api_response = MagicMock()
    mock_api_response.json.return_value = {"stargazers_count": expected_star_count}

    # Configure the mock client's get method to return our mock response
    mock_httpx_client.get.return_value = mock_api_response

    # Act: Call the function we are testing.
    # We use .fn() to call the original Python function directly,
    # bypassing the Prefect task machinery for this unit test.
    actual_star_count = get_stars_for_repo.fn(client=mock_httpx_client, repo=repo_name)

    # Assert: Verify the outcome
    # 1. Check that the function returned the correct value.
    assert actual_star_count == expected_star_count
    # 2. Check that the http client was called with the correct URL.
    mock_httpx_client.get.assert_called_once_with(f"https://api.github.com/repos/{repo_name}")
    # 3. Check that our error handling function was called.
    mock_api_response.raise_for_status.assert_called_once()


def test_get_stars_for_repo_api_error(mock_httpx_client):
    """
    Tests the failure case where the GitHub API returns an error.
    """
    # Arrange: Set up the mock to simulate an API error
    repo_name = "a/non-existent-repo"

    # Configure the mock client's get method to raise an HTTPStatusError,
    # which is what httpx does on a 4xx or 5xx response when raise_for_status() is called.
    mock_api_response = MagicMock()
    mock_api_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Not Found", request=MagicMock(), response=MagicMock()
    )
    mock_httpx_client.get.return_value = mock_api_response

    # Act & Assert:
    # We expect an HTTPStatusError to be raised by our function.
    # pytest.raises serves as a context manager to catch and verify the exception.
    with pytest.raises(httpx.HTTPStatusError):
        get_stars_for_repo.fn(client=mock_httpx_client, repo=repo_name)
