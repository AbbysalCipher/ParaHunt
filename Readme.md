# ParaHunt v1.2

```text
██████╗  █████╗ ██████╗  █████╗ ██╗  ██╗██╗   ██╗███╗   ██╗████████╗
██╔══██╗██╔══██╗██╔══██╗██╔══██╗██║  ██║██║   ██║████╗  ██║╚══██╔══╝
██████╔╝███████║██████╔╝███████║███████║██║   ██║██╔██╗ ██║   ██║   
██╔═══╝ ██╔══██║██╔══██╗██╔══██║██╔══██║██║   ██║██║╚██╗██║   ██║   
██║     ██║  ██║██║  ██║██║  ██║██║  ██║╚██████╔╝██║ ╚████║   ██║   
╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝   ╚═╝   

               >> Passive Archive Crawler & Stealth Endpoint Spider <<
```
ParaHunt is a lightweight, high-velocity command-line utility written in Python. It discovers hidden directory paths and query parameters by scraping historical data from the Wayback Machine's CDX API, extracts unique endpoint combinations, and safely checks their current server status.

Equipped with both an aggressive multi-threaded mode and a highly randomized anti-ban stealth layer, ParaHunt balances raw speed with operational discretion.
## ✨ Key Features
* **Passive Reconnaissance:** Pulls historical endpoints from public archives first, saving you from aggressively brute-forcing the target web server.
* **HTTP Connection Pooling:** Reuses TCP connections via requests.Session() to cut network handshake latencies in half.
* **Stream Loading:** Inspects server headers (stream=True) instantly without wasting bandwidth or time downloading heavy HTML page bodies.
* **WAF/Anti-Ban Protections:** Features a dedicated --stealth mode that forces single-threaded, sequential requests coupled with randomized human-like delays (1.0s - 3.0s).
* **Browser Spoofing:** Injects realistic, modern Google Chrome headers to replace the default Python signature flag.
* **Flexible Output Formats:** Supports full structural visual reporting or raw endpoint generation ready to be piped into automation tools.

## 🚀 Installation & Requirements

Make sure you have Python 3.x installed on your system.

1. **Clone the repository:**
   ```bash
   git clone https://github.com/AbbysalCipher/ParaHunt.git
   cd ParaHunt
   ```
2. **Install dependencies:**
   This tool relies on the requests library. Install it using pip:
   ```bash
    pip install requests
   ```

## 🎮 Usage Guide

ParaHunt runs entirely through the command terminal. Use the -d flag to specify your target domain.

* **Options Manual:** To see all available configuration switches, run:
    ```bash
    python parahunt.py -h
    ```
* **High-Speed Loud Mode:** Best for local labs or owned infrastructure. Fires up concurrent execution workers to sweep targets aggressively.
    ```bash
    python parahunt.py -d scrapethissite.com -t 15
    ```
* **Anti-Ban Stealth Mode:** Best for production or protected systems. Forces the tool down to a single worker thread and randomizes delays to blend perfectly into organic visitor traffic.
    ```bash
    python parahunt.py --domain example.com --stealth
    ```
* **Raw Parameter Export:** Saves only the clean raw URLs into the file (no dashboards, metrics, or comment text)—ideal for automation chains.
    ```bash
    python parahunt.py -d scrapethissite.com --format raw
    ```

## 📊 Output Options

The tool exports its final file run to <target_domain>_harvested.txt.

* --format report (Default): Saves a detailed table layout detailing URLs alongside status flags and network latency metrics.

* --format raw: Saves a bare list of raw URLs (one per line) for seamless pipeline integration.

## 🛠️ Extensions: MethodFlipper (method_flipper.py)

ParaHunt pairs directly with MethodFlipper to bridge the gap between passive harvesting and active parameter auditing. MethodFlipper accepts a raw endpoint output file, maps hidden modification vectors, and triggers automated HTTP Method Tampering Matrix scans (POST, PUT, DELETE) to catch unprotected API entry points.

## Usage Setup:

* Run ParaHunt to collect clean base URLs:
    ```Bash
    python parahunt.py -d scrapethissite.com --format raw
    ```
* Fuzz alternate methods instantly using MethodFlipper:
    ```Bash
    python method_flipper.py -i scrapethissite.com_harvested.txt
    ```

## ⚖️ Disclaimer
* **This tool is built strictly for ethical security auditing, vulnerability research, and authorized penetration testing.**
* **Do not use it against systems without explicit permission.**
* **The developer assumes no liability for misuse or damage caused by this utility.**
