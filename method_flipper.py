import argparse
import requests
import json
import urllib3
from urllib.parse import urlparse, urlunparse

# Suppress SSL certificate warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def banner():
    print("""
    =================================================
       MethodFlipper v2.0 - ParaHunt API Extension   
       [+] Mapping Hidden POST, PUT, DELETE Routes   
    =================================================
    """)

def analyze_response(method, url, status_code):
    """Interprets the server's response to determine if the endpoint exists."""
    if status_code in [200, 201, 204]:
        print(f"🔥 [SUCCESS] {method} {url} -> Status {status_code} (Endpoint accepts this method!)")
    elif status_code == 400:
        print(f"📡 [FOUND]   {method} {url} -> Status 400 (Bad Request - Route exists, wants proper structural schema!)")
    elif status_code in [401, 403]:
        print(f"🔒 [PROTECT] {method} {url} -> Status {status_code} (Route exists but requires active session auth!)")
    elif status_code == 405:
        print(f"🚫 [REFUSED] {method} {url} -> Status 405 (Method Not Allowed - Endpoint exists but explicitly bars {method})")
    elif status_code == 404:
        pass  # Ignore default dead parameters or non-existent routes
    else:
        print(f"❓ [UNKNOWN] {method} {url} -> Status {status_code}")

def clean_url_for_tampering(raw_url):
    """Strips query parameters to properly fuzz the root API routing controller."""
    parsed = urlparse(raw_url)
    # Rebuild URL dropping the query arguments string entirely
    clean_url = urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))
    return clean_url

def test_endpoints(input_file, custom_header):
    methods_to_test = ["POST", "PUT", "DELETE"]
    
    # Robust validation schema matrix to satisfy typical validation engines
    expanded_dummy_payload = {
        "id": 1, 
        "user_id": 1,
        "status": "active", 
        "email": "test@domain.local",
        "username": "admin",
        "uuid": "00000000-0000-0000-0000-000000000000"
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/json"
    }

    try:
        urls = set()
        with open(input_file, 'r') as f:
            for line in f:
                cleaned_line = line.strip()
                
                # Skip visual report components completely if user parsed standard format
                if not cleaned_line or cleaned_line.startswith("#") or cleaned_line.startswith("-") or cleaned_line.startswith("="):
                    continue
                if "directory target url" in cleaned_line.lower() or "latency" in cleaned_line.lower():
                    continue
                if "|" in cleaned_line:
                    cleaned_line = cleaned_line.split("|")[0].strip()

                if cleaned_line:
                    # Clean trailing parameters and track uniquely
                    urls.add(clean_url_for_tampering(cleaned_line))
    except FileNotFoundError:
        print(f"[-] Error: Input file '{input_file}' not found.")
        return

    print(f"[*] Loaded {len(urls)} base endpoints. Executing HTTP Method Tampering matrix...\n")

    with requests.Session() as session:
        session.headers.update(headers)
        
        # Inject custom session headers if passed
        if custom_header and ":" in custom_header:
            h_key, h_val = custom_header.split(":", 1)
            session.headers.update({h_key.strip(): h_val.strip()})
            print(f"[🔒] MethodFlipper session authenticated using custom injected key header.\n")
        
        for url in urls:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "https://" + url

            for method in methods_to_test:
                try:
                    if method in ["POST", "PUT"]:
                        response = session.request(
                            method=method, 
                            url=url, 
                            json=expanded_dummy_payload, 
                            timeout=4, 
                            verify=False
                        )
                    else:
                        response = session.request(
                            method=method, 
                            url=url, 
                            timeout=4, 
                            verify=False
                        )

                    analyze_response(method, url, response.status_code)

                except requests.exceptions.RequestException:
                    pass

if __name__ == "__main__":
    banner()
    parser = argparse.ArgumentParser(description="Test alternative HTTP methods against passive crawl logs.")
    parser.add_argument("-i", "--input", required=True, help="Path to ParaHunt's harvested text file output")
    parser.add_argument("-H", "--header", type=str, help="Pass authorization strings to authenticate testing requests")
    args = parser.parse_args()

    test_endpoints(args.input, args.header)