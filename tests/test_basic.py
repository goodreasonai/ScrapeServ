from .client import scrape

def test_basic():
    resp = scrape("https://goodreason.ai")
    assert(resp.status == 200)
    assert(len(resp.content))
    mime_type = resp.mime_type
    assert(mime_type == 'text/html')

    # Content type info essentially gets repeated in the content section - make sure it's the same
    resp.content_headers.get('Content-Type')
    mime_type_from_content_headers = resp.content_headers.get('Content-Type').split(';')[0].strip()
    assert(mime_type_from_content_headers == mime_type)
    
    assert(len(resp.screenshot_contents) > 1)
    assert(len(resp.screenshot_headers) > 1)
    assert(len(resp.screenshot_contents) == len(resp.screenshot_headers))

    meta = resp.metadata
    n_screenshots = meta.get('truncated_screenshots_n')
    assert(len(resp.screenshot_contents) == n_screenshots)

