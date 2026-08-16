from techpulse.linkedin import LinkedInPublisher


def test_publish_builds_organization_post_request():
    captured = {}

    def request(method, url, headers, body):
        captured.update(method=method, url=url, headers=headers, body=body)
        return 201, {"id": "urn:li:share:123"}

    publisher = LinkedInPublisher("token", "456", "202607", request)
    result = publisher.publish("Hello H&H IT Solutions")
    assert result == "urn:li:share:123"
    assert captured["method"] == "POST"
    assert captured["url"].endswith("/rest/posts")
    assert captured["body"]["author"] == "urn:li:organization:456"
    assert captured["body"]["commentary"] == "Hello H&H IT Solutions"
