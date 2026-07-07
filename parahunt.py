import concurrent.futures
import requests
import urllib.parse
import time
import argparse
import random

# ==============================================================================
#                 PARAHUNT v1.2 - BLOCK STYLE ENHANCED
# ==============================================================================
print(r"""
██████╗  █████╗ ██████╗  █████╗ ██╗  ██╗██╗   ██╗███╗   ██╗████████╗
██╔══██╗██╔══██╗██╔══██╗██╔══██╗██║  ██║██║   ██║████╗  ██║╚══██╔══╝
██████╔╝███████║██████╔╝███████║███████║██║   ██║██╔██╗ ██║   ██║   
██╔═══╝ ██╔══██║██╔══██╗██╔══██║██╔══██║██║   ██║██║╚██╗██║   ██║   
██║     ██║  ██║██║  ██║██║  ██║██║  ██║╚██████╔╝██║ ╚████║   ██║   
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   

               >> Passive Archive Crawler & Stealth Endpoint Spider <<
""")

def fetch_archived_urls(domain):
    """Queries the Wayback Machine's CDX API to pull historical URLs."""
    print(f"[*] Extracting historical directory footprints for: {domain}")
    cdx_url = f"http://web.archive.org/cdx/search/cdx?url={domain}/*&output=json&fl=original&collapse=urlkey"
    
    try:
        response = requests.get(cdx_url, timeout=15)
        if response.status_code != 200:
            print("[-] Failed to retrieve data from Archive network.")
            return []
        
        raw_data = response.json()
        if len(raw_data) <= 1:
            return []
            
        return [row[0] for row in raw_data[1:]]
    except Exception as e:
        print(f"[-] Network connection error gathering archive logs: {e}")
        return []

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
                
    return sorted(list(unique_endpoints))

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
        response = session.get(base_url, params=test_payload, timeout=5, stream=True)
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
    # === HELP ENGINE ===
    parser = argparse.ArgumentParser(
        description="ParaHunt: Multi-threaded Parameter Harvester Script",
        epilog="""Examples:
  py parahunt.py -d scrapethissite.com -t 15
  py parahunt.py --domain example.com --stealth""",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Options manual declaration
    parser.add_argument("-d", "--domain", type=str, required=True, help="Target domain to audit (e.g., example.com or localhost:8888)")
    parser.add_argument("-t", "--threads", type=int, default=20, help="Number of concurrent execution threads (default: 20)")
    parser.add_argument("--stealth", action="store_true", help="Enable anti-ban stealth protections (Single-threaded + Random delays)")
    parser.add_argument("-f", "--format", choices=["report", "raw"], default="report", help="Output file format. 'report' includes decorations/metadata, 'raw' saves URLs only.")
    args = parser.parse_args()
    
    # Clean the input domain text just in case the user accidentally provides http:// or https://
    target = args.domain.replace("https://", "").replace("http://", "").strip("/")
    
    worker_threads = 1 if args.stealth else args.threads
    stealth_active = args.stealth

    archived_urls = fetch_archived_urls(target)
    print(f"[+] Total archived URLs extracted: {len(archived_urls)}")
    
    endpoint_pairs = extract_paths_and_parameters(archived_urls, target)
    print(f"[+] Isolated {len(endpoint_pairs)} unique directory-parameter combinations.")
    
    if not endpoint_pairs:
        print("[-] No directory query parameters discovered. Try another domain.")
        return

    if stealth_active:
        print("\n[🛡️] STEALTH MODE ACTIVE: Running single-threaded with randomized human-like delays.")
    else:
        print(f"\n[*] LOUD MODE: Auditing endpoints concurrently using [{worker_threads}] aggressive workers...")
        
    all_results = []
    start_bench = time.time()

    with requests.Session() as shared_session:
        shared_session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })

        adapter = requests.adapters.HTTPAdapter(pool_connections=worker_threads, pool_maxsize=worker_threads)
        shared_session.mount('https://', adapter)
        shared_session.mount('http://', adapter)

        with concurrent.futures.ThreadPoolExecutor(max_workers=worker_threads) as executor:
            futures = {
                executor.submit(verify_endpoint_behavior, shared_session, target, path, param, stealth_active): (path, param) 
                for path, param in endpoint_pairs
            }
            
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                all_results.append(result)

    sorted_results = sorted(all_results, key=lambda x: x["status_code"])
    end_bench = time.time()

    # Dynamic filename cleanup for Windows-safe names if ports are used (like localhost:8888)
    safe_filename = target.replace(":", "_")
    output_filename = f"{safe_filename}_harvested.txt"
    
    with open(output_filename, "w", encoding="utf-8") as f:
        if args.format == "report":
            # Format 1: Beautiful full visual report (Default)
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
            # Format 2: RAW URLS ONLY (Perfect for piping into MethodFlipper!)
            for res in sorted_results:
                f.write(f"{res['full_url']}\n")

    print(f"[+] Output successfully saved to {output_filename} in '{args.format}' format!")

if __name__ == "__main__":
    main()