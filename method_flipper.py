import argparse
import requests
import json
import urllib3
from urllib.parse import urlparse

# Suppress SSL certificate warnings for clean output
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def banner():
    print("""
    =================================================
       MethodFlipper v1.0 - ParaHunt API Extension   
       [+] Mapping Hidden POST, PUT, DELETE Routes   
    =================================================
    """)

def analyze_response(method, url, status_code):
    """Interprets the server's response to determine if the endpoint exists."""
    # Active endpoints accepting modification or auth errors
    if status_code in [200, 201, 204]:
        print(f"🔥 [SUCCESS] {method} {url} -> Status {status_code} (Endpoint accepts this method!)")
    elif status_code == 400:
        print(f"📡 [FOUND]   {method} {url} -> Status 400 (Bad Request - Route exists, wants proper JSON/Params!)")
    elif status_code in [401, 403]:
        print(f"🔒 [PROTECT] {method} {url} -> Status {status_code} (Route exists but requires Auth/Tokens!)")
    elif status_code == 405:
        print(f"🚫 [REFUSED] {method} {url} -> Status 405 (Method Not Allowed - Endpoint exists but rejects {method})")
    # Dead endpoints or standard rejections
    elif status_code == 404:
        # Standard not found means the method isn't supported here
        pass
    else:
        print(f"❓ [UNKNOWN] {method} {url} -> Status {status_code}")

def test_endpoints(input_file):
    methods_to_test = ["POST", "PUT", "DELETE"]
    dummy_payload = {"id": 1, "test": "fuzz"}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/json"
    }

    try:
        urls = []
        with open(input_file, 'r') as f:
            for line in f:
                cleaned_line = line.strip()
                
                # 1. Skip structural/decorative padding lines
                if not cleaned_line or cleaned_line.startswith("#") or cleaned_line.startswith("-") or cleaned_line.startswith("="):
                    continue
                    
                # 2. Skip table descriptions and logging headers
                if "directory target url" in cleaned_line.lower() or "latency" in cleaned_line.lower():
                    continue
                
                # 3. Handle lines containing a table delimiter pipe character (e.g. "url | status | latency")
                # Extract just the first part before the pipe
                if "|" in cleaned_line:
                    cleaned_line = cleaned_line.split("|")[0].strip()

                # Double check we actually have something left
                if cleaned_line:
                    urls.append(cleaned_line)
                    
    except FileNotFoundError:
        print(f"[-] Error: Input file '{input_file}' not found.")
        return

    print(f"[*] Loaded {len(urls)} base endpoints. Starting HTTP Method Tampering matrix...\n")

    # Use a session wrapper to optimize connection reuse
    with requests.Session() as session:
        session.headers.update(headers)
        
        for url in urls:
            # Simple sanitization to ensure we have a valid scheme
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "https://" + url

            for method in methods_to_test:
                try:
                    # Send request with a strict timeout so it doesn't hang
                    if method in ["POST", "PUT"]:
                        response = session.request(
                            method=method, 
                            url=url, 
                            json=dummy_payload, 
                            timeout=4, 
                            verify=False
                        )
                    else:  # DELETE usually doesn't send a JSON payload body
                        response = session.request(
                            method=method, 
                            url=url, 
                            timeout=4, 
                            verify=False
                        )

                    analyze_response(method, url, response.status_code)

                except requests.exceptions.RequestException:
                    # Gracefully skip connection drops, timeouts, or DNS resolution failures
                    pass

if __name__ == "__main__":
    banner()
    parser = argparse.ArgumentParser(description="Test alternative HTTP methods against passive crawl logs.")
    parser.add_argument("-i", "--input", required=True, help="Path to ParaHunt's harvested text file output")
    args = parser.parse_args()

    test_endpoints(args.input)