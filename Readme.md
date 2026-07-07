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
ParaHunt is an advanced, high-velocity target intelligence tool written in Python. It maps application attack surfaces by harvesting historical routing parameters from public archives, crawling client-side application code on live web pages, and systematically identifying API endpoint exposure.

Equipped with connection pooling, modern anti-ban protections, and deep endpoint compilation features, ParaHunt balances raw speed with architectural discretion.

## ✨ Key Features
* **Passive Reconnaissance:** Pulls historical endpoints from public archives first, saving you from aggressively brute-forcing the target web server.
* **Dynamic Time-Filtering:** Features a configurable cutoff argument to discard stale or legacy application paths based on the crawl year, helping you avoid non-existent ghost routes.
* **Live JavaScript Bundle Crawling:** Scrapes live web homepages dynamically via Regex to pull client-side endpoints explicitly mapped within modern SPA frameworks (React, Angular, Vue, Next.js).
* **Session & Auth Injection:** Supports full credential or bearer token state persistence across concurrent execution routines via dynamic authorization string inputs.
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
* **Authenticated Surface Auditing:** Passes security tokens down to internal testing workers to bypass authentication gateways and evaluate protected areas.
```bash
python parahunt.py -d target.com -H "Authorization: Bearer eyJhbGciOi..."
```
* **Granular Time-Filtering Configuration:** Adjust or completely lift the archive search age boundary using the --since option.
```bash
# Precision Run (Filters targets 2022-present only - Default)
python parahunt.py -d target.com --since 2022

# Custom Boundary (Filters targets 2018-present only)
python parahunt.py -d target.com --since 2018

# Full Historical Depth Run (Disables filtering completely; pulls all recorded logs)
python parahunt.py -d target.com --since 0
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

ParaHunt pairs with MethodFlipper to turn passive target mapping into active HTTP Method Tampering Matrix Scans (POST, PUT, DELETE).

MethodFlipper automatically processes ParaHunt text output files, strips away visual padding rows, drops URL parameter strings to focus on root API routers, and sends expanded verification object dictionaries to bypass strict schema structure engines.

## How to Run the Automated Pipeline:

1. Extract a raw clean surface map from the target:
```bash
python parahunt.py -d target.com --format raw -H "Cookie: session=xyz123" --since 2022
```
2. Fuzz alternate mutation methods instantly via MethodFlipper using the same session states:
```bash
python method_flipper.py -i target.com_harvested.txt -H "Cookie: session=xyz123"
```

## ⚖️ Disclaimer
* **This tool is built strictly for ethical security auditing, vulnerability research, and authorized penetration testing.**
* **Do not use it against systems without explicit permission.**
* **The developer assumes no liability for misuse or damage caused by this utility.**
