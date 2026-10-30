import pytest

from bbor_client.conf import API_URL_DOCKER, API_URL_LOCAL, API_URL_MDX
from bbor_client.util import api_url


@pytest.mark.parametrize('server, expected', [
    ('mdx', API_URL_MDX),
    ('local', API_URL_LOCAL),
    ('docker', API_URL_DOCKER),
    ('http://api.example.org', 'http://api.example.org'),
    ('https://api.example.org/', 'https://api.example.org'),
    ('https://api.example.org:8443/prefix', 'https://api.example.org:8443/prefix'),
])
def test_api_url_accepts_names_and_urls(server, expected):
    assert api_url(server) == expected


@pytest.mark.parametrize('server', ['dev', 'api.example.org', 'ftp://api.example.org', ''])
def test_api_url_rejects_other_values(server):
    with pytest.raises(ValueError):
        api_url(server)
