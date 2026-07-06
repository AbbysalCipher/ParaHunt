# ParaHunt v1.2

```text
██████╗  █████╗ ██████╗  █████╗ ███╗   ███╗██╗  ██╗██╗   ██╗███╗   ██╗████████╗
██╔══██╗██╔══██╗██╔══██╗██╔══██╗████╗ ████║██║  ██║██║   ██║████╗  ██║╚══██╔══╝
██████╔╝███████║██████╔╝███████║██╔████╔██║███████║██║   ██║██╔██╗ ██║   ██║   
██╔═══╝ ██╔══██║██╔══██╗██╔══██║██║╚██╔╝██║██╔══██║██║   ██║██║╚██╗██║   ██║   
██║     ██║  ██║██║  ██║██║  ██║██║ ╚═╝ ██║██║  ██║╚██████╔╝██║ ╚████║   ██║   
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   

               >> Passive Archive Crawler & Stealth Endpoint Spider <<

ParaHunt is a lightweight, high-velocity command-line utility written in Python. It discovers hidden directory paths and query parameters by scraping historical data from the Wayback Machine's CDX API, extracts unique endpoint combinations, and safely checks their current server status.

Equipped with both an aggressive multi-threaded mode and a highly randomized anti-ban stealth layer, ParaHunt balances raw speed with operational discretion.
✨ Key Features

    Passive Reconnaissance: Pulls historical endpoints from public archives first, saving you from aggressively brute-forcing the target web server.

    HTTP Connection Pooling: Reuses TCP connections via requests.Session() to cut network handshake latencies in half.

    Stream Loading: Inspects server headers (stream=True) instantly without wasting bandwidth or time downloading heavy HTML page bodies.

    WAF/Anti-Ban Protections: Features a dedicated --stealth mode that forces single-threaded, sequential requests coupled with randomized human-like delays (1.0s - 3.0s).

    Browser Spoofing: Injects realistic, modern Google Chrome headers to replace the default Python signature flag.

    Auto-Sanitized Input: Automatically handles accidental inclusions of protocol headers (http:// or https://) and trailing slashes.