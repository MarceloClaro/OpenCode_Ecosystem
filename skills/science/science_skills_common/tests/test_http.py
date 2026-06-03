import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import http_client


class TestHttpClientImport:
    def test_import(self):
        assert http_client is not None

    def test_http_client_class_exists(self):
        assert hasattr(http_client, "HttpClient")

    def test_http_error_class_exists(self):
        assert hasattr(http_client, "HttpError")

    def test_http_response_class_exists(self):
        assert hasattr(http_client, "HttpResponse")


class TestHttpClient:
    def setup_method(self):
        self.client = http_client.HttpClient(
            base_url="https://httpbin.org",
            qps=1.0,
        )

    def test_instantiated(self):
        assert self.client is not None

    def test_has_base_url(self):
        assert self.client.base_url == "https://httpbin.org"

    def test_has_hostname(self):
        assert self.client.hostname == "httpbin.org"

    def test_fetch_json_returns_data(self):
        data = self.client.fetch_json("/get")
        assert isinstance(data, dict)
        assert "url" in data

    def test_fetch_text_returns_string(self):
        text = self.client.fetch_text("/get")
        assert isinstance(text, str)

    def test_fetch_bytes_returns_bytes(self):
        data = self.client.fetch_bytes("/get")
        assert isinstance(data, bytes)

    def test_default_headers(self):
        resp = self.client.fetch("/get")
        assert resp.status_code == 200
        assert isinstance(resp.data, bytes)

    def test_base_url_validation(self):
        client = http_client.HttpClient("https://example.com/api", qps=2.0)
        assert client.hostname == "example.com"

    def test_bad_base_url_raises(self):
        with pytest.raises(ValueError):
            http_client.HttpClient("not-a-url", qps=1.0)
