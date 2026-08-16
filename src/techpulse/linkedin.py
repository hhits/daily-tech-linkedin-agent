import json
import time
import urllib.error
import urllib.request


class LinkedInPublisher:
    def __init__(self, access_token: str, organization_id: str, version: str = "202607", request=None):
        self.access_token = access_token
        self.organization_id = organization_id
        self.version = version
        self.request = request or self._request

    @staticmethod
    def _request(method, url, headers, body):
        req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return response.status, json.loads(response.read().decode() or "{}")
        except urllib.error.HTTPError as exc:
            payload = exc.read().decode(errors="replace")
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                payload = {"message": payload}
            return exc.code, payload

    def publish(self, post: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Linkedin-Version": self.version,
            "X-Restli-Protocol-Version": "2.0.0",
        }
        body = {
            "author": f"urn:li:organization:{self.organization_id}",
            "commentary": post,
            "visibility": "PUBLIC",
            "distribution": {"feedDistribution": "MAIN_FEED", "targetEntities": [], "thirdPartyDistributionChannels": []},
            "lifecycleState": "PUBLISHED",
            "isReshareDisabledByAuthor": False,
        }
        last_error = None
        for attempt in range(3):
            status, payload = self.request("POST", "https://api.linkedin.com/rest/posts", headers, body)
            if 200 <= status < 300:
                return payload.get("id") or payload.get("x-restli-id") or payload.get("entity")
            last_error = payload
            if status not in (429, 500, 502, 503, 504):
                break
            if attempt < 2:
                time.sleep(2**attempt)
        raise RuntimeError(f"LinkedIn publish failed ({status}): {last_error}")
