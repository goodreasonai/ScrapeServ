from .client import scrape

"""
curl -i -s -X POST "http://localhost:5006/scrape" \
    -H "Content-Type: application/json" \
    -d '{"url": "https://goodreason.ai", "actions": [{"action": "click_link", "args": {"text": "Careers"}}]}' \
    | ripmime -i - -d outfolder --formdata --no-nameless
"""
def test_click_link():
    url = "https://goodreason.ai"
    resp = scrape(url, actions=[
        {
            'action': 'click_link',
            'args': {
                'text': "Careers"
            }
        }
    ])
    assert(resp.status == 200)
    assert(resp.mime_type == 'text/html')
    assert(len(resp.screenshot_contents) >= 1)
    html = resp.content.decode()
    assert('Careers at GoodReason' in html)
    assert(resp.url == 'https://goodreason.ai/careers.html')


"""
curl -i -s -X POST "http://localhost:5006/scrape" \
    -H "Content-Type: application/json" \
    -d '{"url": "https://goodreason.ai", "actions": [{"action": "click_link", "args": {"text": "Blog"}}, {"action": "click_link", "args": {"text": "No thanks"}}, {"action": "click_link", "args": {"text": "About"}}]}' \
    | ripmime -i - -d outfolder --formdata --no-nameless
"""
def test_click_multiple_links():
    url = "https://goodreason.ai"
    resp = scrape(url, actions=[
        {
            'action': 'click_link',
            'args': {
                'text': "Blog"
            }
        },
        {
            'action': 'click_link',
            'args': {
                'text': "No thanks"
            }
        },
        {
            'action': 'click_link',
            'args': {
                'text': "About"
            }
        }
    ])
    assert(resp.status == 200)
    assert(resp.mime_type == 'text/html')
    assert(len(resp.screenshot_contents) >= 1)
    html = resp.content.decode()
    assert('Why subscribe?' in html)
    assert(resp.url == 'https://blog.goodreason.ai/about')
    

"""
curl -i -s -X POST "http://localhost:5006/scrape" \
    -H "Content-Type: application/json" \
    -d '{"url": "https://goodreason.ai", "actions": [{"action": "click_link", "args": {"text": "Vanilla Milkshake"}}]}' \
    | ripmime -i - -d outfolder --formdata --no-nameless
"""
def test_bad_click():
    url = "https://goodreason.ai"
    resp = scrape(url, actions=[
        {
            'action': 'click_link',
            'args': {
                'text': "Vanilla milkshake"
            }
        }
    ])
    assert(resp.error)
    assert("Vanilla milkshake" in resp.error)
