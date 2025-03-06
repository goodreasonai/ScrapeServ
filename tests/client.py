import requests
from requests_toolbelt.multipart.decoder import MultipartDecoder
import sys
import json
from requests.structures import CaseInsensitiveDict
from dataclasses import dataclass, field


@dataclass
class ScrapeResponse():
    url: str | None = None
    status: int | None = None
    error: str | None = None
    headers: CaseInsensitiveDict | None = None
    metadata: CaseInsensitiveDict | None = None
    content: bytes | None = None
    content_headers: CaseInsensitiveDict | None = None
    mime_type: str | None = None
    screenshot_contents: list[bytes] = field(default_factory=lambda: [])
    screenshot_headers: list[CaseInsensitiveDict] = field(default_factory=lambda: [])


def _byte_dict_to_str(dict: dict):
    return {k.decode('utf-8'): v.decode('utf-8') for k, v in dict.items()}

def scrape(url: str, dim: tuple[int, int] | None=None, img_type: str | None=None, wait: int | None=None, max_screenshots: int | None=None, actions: list[dict] | None=None) -> ScrapeResponse:
    data = {
        'url': url,
        **{k: v for k, v in {
            'browser_dim': dim,
            'wait': wait,
            'max_screenshots': max_screenshots,
            'actions': actions
        }.items() if v is not None}
    }
    headers = {} if img_type is None else {
        'Accept': f'image/{img_type}'  # Determines the file type for the screenshots
    }

    # Make the request to the API
    response = requests.post('http://localhost:5006/scrape', json=data, headers=headers, timeout=30)

    if response.status_code != 200:  # Handle errors
        my_json = response.json()
        message = my_json['error']
        return ScrapeResponse(error=message)
    else:  # Scrape went through
        decoder = MultipartDecoder.from_response(response)  # Response is type multipart/mixed
        resp = ScrapeResponse()
        for i, part in enumerate(decoder.parts):
            if i == 0:  # First is some JSON containing headers, status code, and other metadata
                json_part = json.loads(part.content)
                req_status = json_part['status']  # An integer
                resp.url = json_part['url']
                req_headers: dict = json_part['headers']  # Headers from the request made to your URL
                metadata = json_part['metadata']  # For reference, information like the number of screenshots and their compressed / uncompressed sizes
                mime_type = req_headers['content-type'].split(';')[0].strip()
                resp.mime_type = mime_type
                resp.metadata = CaseInsensitiveDict(metadata)
                resp.headers = CaseInsensitiveDict(req_headers)
                resp.status = req_status
            elif i == 1:  # Next is the actual content of the page
                content = part.content
                headers = _byte_dict_to_str(part.headers)  # Will contain info about the content (text/html, application/pdf, etc.)
                resp.content = content
                resp.content_headers = CaseInsensitiveDict(headers)
            else:  # Other parts are screenshots, if they exist
                img = part.content
                headers = _byte_dict_to_str(part.headers)  # Will tell you the image format
                resp.screenshot_contents.append(img)
                resp.screenshot_headers.append(CaseInsensitiveDict(headers))

        return resp
