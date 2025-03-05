import requests
from requests_toolbelt.multipart.decoder import MultipartDecoder
import sys
import json
import mimetypes
import os
import argparse


"""

This client is made as a reference implementation for how your app might parse a response from the API

See the README for more info.

"""

# Set up argument parsing
parser = argparse.ArgumentParser(description='Scrape some URL.')
parser.add_argument('url', type=str, help='The URL to scrape')
parser.add_argument('--api-key', type=str, default="", help='The API key for your server, if set')
parser.add_argument('--out', type=str, default='output', help='The folder where output files should be stored (ideally blank)')
parser.add_argument('--img-type', type=str, default='jpeg', help='Image type for screenshots: jpeg, png, or webp')
parser.add_argument('--max-screenshots', type=int, default=None, help='The maximum number of screenshots that will be returned for a webpage')
parser.add_argument('--wait', type=int, default=None, help='The amount of time the browser will wait to take a screenshot after scrolling to each location, in milliseconds')
parser.add_argument('--dim', type=int, nargs=2, default=None, help='The width and height of the browser when it takes a screenshot')

args = parser.parse_args()

OUTFOLDER = args.out

data = {
    'url': args.url,  # Like https://goodreason.ai
    **{k: v for k, v in {
        'browser_dim': args.dim,
        'wait': args.wait,
        'max_screenshots': args.max_screenshots
    }.items() if v is not None}
}
headers = {
    'Authorization': f'Bearer {args.api_key}',  # Optional: if you're using an API key
    'Accept': f'image/{args.img_type}'  # Determines the file type for the screenshots
}

# Helper function to get the correct file extensions for the main resource and screenshots
# includes dot unless blank
def get_ext_from_headers(headers):
    content_type_bytes: bytes = headers[b'Content-Type']
    content_type = content_type_bytes.decode('utf-8')
    mime_type = content_type.split(';')[0].strip()
    extensions = mimetypes.guess_all_extensions(mime_type)
    if len(extensions):
        return f"{extensions[0]}"
    return ""

# Make the request to the API
response = requests.post('http://localhost:5006/scrape', json=data, headers=headers, timeout=30)

if response.status_code != 200:  # Handle errors
    my_json = response.json()
    message = my_json['error']
    print(f"Error scraping: {message}", file=sys.stderr)
else:  # Scrape went through
    decoder = MultipartDecoder.from_response(response)  # Response is type multipart/mixed
    resp = None
    for i, part in enumerate(decoder.parts):
        if i == 0:  # First is some JSON containing headers, status code, and other metadata
            json_part = json.loads(part.content)
            req_status = json_part['status']  # An integer
            req_headers: dict = json_part['headers']  # Headers from the request made to your URL
            _ = json_part['metadata']  # For reference, information like the number of screenshots and their compressed / uncompressed sizes
            
            print(f"Status Code: {req_status}", end="\n\n")
            print("\n".join([f"{k}: {v}" for k, v in req_headers.items()]))

        elif i == 1:  # Next is the actual content of the page
            if not os.path.exists(OUTFOLDER):
                os.mkdir(OUTFOLDER)
            
            content = part.content
            headers = part.headers  # Will contain info about the content (text/html, application/pdf, etc.)
            ext = get_ext_from_headers(headers)
            outfile = os.path.join(OUTFOLDER, f"main{ext}")
            with open(outfile, 'wb') as fhand:  # Save the file
                fhand.write(content)

            print(f"\nFile written to {outfile}.")

        else:  # Other parts are screenshots, if they exist
            img = part.content
            headers = part.headers  # Will tell you the image format
            ext = get_ext_from_headers(headers)
            outfile = os.path.join(OUTFOLDER, f"{i-1}{ext}")
            with open(outfile, 'wb') as fhand:
                fhand.write(img)
            
            print(f"Screenshot written to {outfile}.")

