import concurrent.futures
import requests
import urllib.parse
import time
import argparse
import random
import re
import urllib3

# Suppress SSL warnings when interacting with proxies or missing certs
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

print(r"""
██████╗  █████╗ ██████╗  █████╗ ██╗  ██╗██╗   ██╗███╗   ██╗████████╗
██╔══██╗██╔══██╗██╔══██╗██╔══██╗██║  ██║██║   ██║████╗  ██║╚══██╔══╝
██████╔╝███████║██████╔╝███████║███████║██║   ██║██╔██╗ ██║   ██║   
██╔═══╝ ██╔══██║██╔══██╗██╔══██║██╔══██║██║   ██║██║╚██╗██║   ██║   
██║     ██║  ██║██║  ██║██║  ██║██║  ██║╚██████╔╝██║ ╚████║   ██║   
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   

               >> Enhanced Archive Crawler & JS Endpoint Spider <<
""")

def fetch_archived_urls(domain, since_year):
    """Queries the Wayback Machine's CDX API and filters entries based on the user-defined year."""
    if since_year == 0:
        print(f"[*] Querying historical archives (Time-filtering: DISABLED - Fetching ALL history)...")
    else:
        print(f"[*] Querying historical archives (Time-filtering: {since_year}-2026)...")
        
    cdx_url = f"http://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&fl=original,timestamp&collapse=urlkey"
    
    try:
        response = requests.get(cdx_url, timeout=15)
        if response.status_code != 200:
            print("[-] Failed to retrieve data from Archive network.")
            return []
        
        raw_data = response.json()
        if len(raw_data) <= 1:
            return []
            
        valid_urls = []
        for row in raw_data[1:]:
            url = row[0]
            timestamp = row[1]  # Format: "YYYYMMDDhhmmss"
            
            # If since_year is 0, allow everything. Otherwise, apply the cutoff.
            if since_year == 0 or int(timestamp[:4]) >= since_year:
                valid_urls.append(url)
                
        return valid_urls
    except Exception as e:
        print(f"[-] Network error gathering archive logs: {e}")
        return []

def scrape_live_javascript_routes(target_domain, session):
    """Scrapes the live homepage for scripts to extract client-side frontend application routes."""
    print(f"[*] Extracting live client-side JavaScript bundles from homepage...")
    found_routes = set()
    homepage_url = f"https://{target_domain}"
    
    try:
        res = session.get(homepage_url, timeout=6, verify=False)
        js_src_urls = re.findall(r'src=["\']([^"\']+\.js)["\']', res.text)
        
        for js_url in js_src_urls:
            if js_url.startswith("//"):
                js_url = "https:" + js_url
            elif js_url.startswith("/"):
                js_url = homepage_url + js_url
            elif not js_url.startswith("http"):
                js_url = f"{homepage_url}/{js_url}"
                
            try:
                js_content = session.get(js_url, timeout=4, verify=False).text
                regex_api_patterns = re.findall(r'["\'](/api/[a-zA-Z0-9_\-/]+)["\']', js_content)
                for path in regex_api_patterns:
                    found_routes.add((path, "id"))
            except requests.RequestException:
                continue
    except Exception as e:
        print(f"[-] Warning: Failed to parse live JS routing map ({e})")
        
    return found_routes

def extract_paths_and_parameters(url_list, target_domain):
    """Parses a list of URLs and pairs parameters with their specific target directories."""
    unique_endpoints = set()
    for url in url_list:
        parsed_url = urllib.parse.urlparse(url)
        path = parsed_url.path
        query_string = parsed_url.query
        
        if not path:
            path = "/"
            
        if query_string:
            params = urllib.parse.parse_qs(query_string)
            for param_name in params.keys():
                unique_endpoints.add((path, param_name))
                
    return unique_endpoints

def verify_endpoint_behavior(session, target_domain, path, parameter_name, stealth_mode):
    """Worker Function: Evaluates endpoints safely using streaming and conditional stealth delays."""
    if stealth_mode:
        jitter = random.uniform(1.0, 3.0)
        time.sleep(jitter)

    base_url = f"https://{target_domain}{path}"
    test_payload = {parameter_name: "test_value_123"}
    
    prepared_request = requests.Request('GET', base_url, params=test_payload).prepare()
    full_url = prepared_request.url
    
    try:
        start = time.time()
        response = session.get(base_url, params=test_payload, timeout=5, stream=True, verify=False)
        latency = (time.time() - start) * 1000
        response.close() 
        
        return {
            "full_url": full_url,
            "status_code": response.status_code,
            "latency_ms": round(latency, 2),
            "error": None
        }
    except requests.RequestException:
        return {
            "full_url": full_url,
            "status_code": 999, 
            "latency_ms": 0,
            "error": "Connection drop"
        }

def main():
    parser = argparse.ArgumentParser(
        description="ParaHunt: Multi-threaded Parameter Harvester Script",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument("-d", "--domain", type=str, required=True, help="Target domain to audit")
    parser.add_argument("-t", "--threads", type=int, default=20, help="Number of concurrent execution threads")
    parser.add_argument("--stealth", action="store_true", help="Enable anti-ban stealth protections")
    parser.add_argument("-f", "--format", choices=["report", "raw"], default="report", help="Output file format.")
    parser.add_argument("-H", "--header", type=str, help="Pass custom authenticated sessions (e.g., 'Authorization: Bearer <token>')")
    parser.add_argument("--since", type=int, default=2022, help="Filter out archive URLs older than this year. Set to 0 to fetch entire history.")
    args = parser.parse_args()
    
    target = args.domain.replace("https://", "").replace("http://", "").strip("/")
    worker_threads = 1 if args.stealth else args.threads

    shared_session = requests.Session()
    shared_session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    })
    
    if args.header and ":" in args.header:
        h_key, h_val = args.header.split(":", 1)
        shared_session.headers.update({h_key.strip(): h_val.strip()})
        print(f"[🔒] Auth Header Loaded: Injecting custom context to scanner sessions.")

    # 1. Gather Historical Data with dynamic custom year filter
    archived_urls = fetch_archived_urls(target, args.since)
    endpoint_pairs = extract_paths_and_parameters(archived_urls, target)
    
    # 2. Extract live frontend JS paths
    live_js_endpoints = scrape_live_javascript_routes(target, shared_session)
    
    # Merge datasets together to drop duplications
    final_endpoint_matrix = endpoint_pairs.union(live_js_endpoints)
    print(f"[+] Combined Endpoint Catalog: {len(final_endpoint_matrix)} targets isolated.")
    
    if not final_endpoint_matrix:
        print("[-] No valid endpoint patterns identified.")
        shared_session.close()
        return

    # 3. Active Mapping Sweep
    print(f"\n[*] Auditing endpoints concurrently using [{worker_threads}] workers...")
    all_results = []
    
    adapter = requests.adapters.HTTPAdapter(pool_connections=worker_threads, pool_maxsize=worker_threads)
    shared_session.mount('https://', adapter)
    shared_session.mount('http://', adapter)

    with concurrent.futures.ThreadPoolExecutor(max_workers=worker_threads) as executor:
        futures = {
            executor.submit(verify_endpoint_behavior, shared_session, target, path, param, args.stealth): (path, param) 
            for path, param in final_endpoint_matrix
        }
        for future in concurrent.futures.as_completed(futures):
            all_results.append(future.result())

    sorted_results = sorted(all_results, key=lambda x: x["status_code"])
    shared_session.close()

    # 4. Save Clean Manifest
    safe_filename = target.replace(":", "_")
    output_filename = f"{safe_filename}_harvested.txt"
    
    with open(output_filename, "w", encoding="utf-8") as f:
        if args.format == "report":
            f.write("====================================================================================================\n")
            f.write(f" PARAHUNT HARVEST REPORT FOR: {target}\n")
            f.write("====================================================================================================\n")
            f.write(" Constructed Directory Target URL with parameter                  | status   | latency\n")
            f.write("----------------------------------------------------------------------------------------------------\n")
            for res in sorted_results:
                f.write(f" {res['full_url']} | {res['status_code']} | {res['latency_ms']}ms\n")
            f.write("----------------------------------------------------------------------------------------------------\n")
            f.write(f" Total Unique Endpoints Found: {len(sorted_results)}\n")
        elif args.format == "raw":
            for res in sorted_results:
                f.write(f"{res['full_url']}\n")

    print(f"[+] Output successfully saved to {output_filename} in '{args.format}' format!")

if __name__ == "__main__":
    main()