import os
import re
import time
import random
import urllib.parse
from playwright.sync_api import sync_playwright
from google import genai
from colorama import init, Fore, Style

init(autoreset=True)

# ─────────────────────────────────────────────
#              PATH SETUP
# ─────────────────────────────────────────────
script_dir     = os.path.dirname(os.path.abspath(__file__))
CATEGORIES_DIR = os.path.join(script_dir, "dorks_categories")
KEY_FILE       = os.path.join(script_dir, ".gemini_key")

# ─────────────────────────────────────────────
#              COLOR SHORTCUTS
# ─────────────────────────────────────────────
C = Fore.CYAN    + Style.BRIGHT
G = Fore.GREEN   + Style.BRIGHT
Y = Fore.YELLOW  + Style.BRIGHT
R = Fore.RED     + Style.BRIGHT
B = Fore.BLUE    + Style.BRIGHT
M = Fore.MAGENTA + Style.BRIGHT
W = Style.RESET_ALL

# ─────────────────────────────────────────────
#              ASCII BANNER
# ─────────────────────────────────────────────
BANNER = f"""
{C}
  ╔═════════════════════════════════════════════════════════════════╗
  ║                                                                 ║
  ║   ██████╗  ██████╗██╗     ██╗ ██████╗███████╗██████╗ ███████╗   ║
  ║  ██╔═══██╗██╔════╝██║     ██║██╔════╝██╔════╝██╔══██╗██╔════╝   ║
  ║  ██║   ██║██║     ██║     ██║██║     ███████╗██████╔╝█████╗     ║
  ║  ██║   ██║██║     ██║     ██║██║     ╚════██║██╔══██╗██╔══╝     ║
  ║  ╚██████╔╝╚██████╗███████╗██║╚██████╗███████║██║  ██║███████╗   ║
  ║   ╚═════╝  ╚═════╝╚══════╝╚═╝ ╚═════╝╚══════╝╚═╝  ╚═╝╚══════╝   ║
  ║                                                                 ║
  ║    ██████╗ ███████╗ ██████╗  ██████╗ ███╗   ██╗                 ║
  ║    ██╔══██╗██╔════╝██╔════╝ ██╔═══██╗████╗  ██║                 ║
  ║    ██████╔╝█████╗  ██║      ██║   ██║██╔██╗ ██║                 ║
  ║    ██╔══██╗██╔══╝  ██║      ██║   ██║██║╚██╗██║                 ║
  ║    ██║  ██║███████╗╚██████╗ ╚██████╔╝██║ ╚████║                 ║
  ║    ╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝                 ║
  ║                                                                 ║
  ║             [ Powered by AI Analysis & Auto-Dorking ]           ║
  ║                    [ by 70SNY_0XHUNTER ]                        ║
  ╚═════════════════════════════════════════════════════════════════╝
{W}"""

# ─────────────────────────────────────────────
#         SCAN MODE CONFIG
# ─────────────────────────────────────────────
SCAN_FILES = {
    "fast":   "Fast_Scan.txt",
    "normal": "Normal_Scan.txt",
    "deep":   "Deep_Scan.txt",
}

SCAN_LIMITS = {
    "fast":   8,
    "normal": 16,
    "deep":   30,
}

SCAN_DEPTH = {
    "fast":   1,
    "normal": 2,
    "deep":   4,
}

RESERVED_FILES = set(SCAN_FILES.values())

# ─────────────────────────────────────────────
#         USER-AGENT & VIEWPORT POOLS
# ─────────────────────────────────────────────
UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

VIEWPORT_POOL = [
    {"width": 1280, "height": 800},
    {"width": 1366, "height": 768},
    {"width": 1440, "height": 900},
    {"width": 1920, "height": 1080},
    {"width": 1024, "height": 768},
    {"width": 1600, "height": 900},
]





_EXCLUDED_KEYWORDS = [
    "tts", "audio", "image", "imagen", "veo",
    "embedding", "aqa", "robotics", "lyria",
    "computer-use", "deep-research", "nano",
    "gemma",
]


_PREFERRED_PREFIXES = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-3-flash",
    "gemini-3-pro",
    "gemini-2.0-flash",
    "gemini-flash-latest",
    "gemini-pro-latest",
]


def _is_text_model(name: str) -> bool:
    """تحقق إن الموديل مش صوت/صورة/فيديو."""
    n = name.lower()
    return not any(kw in n for kw in _EXCLUDED_KEYWORDS)


def _model_priority(name: str) -> int:
    """رقم أولوية أقل = أفضل."""
    n = name.lower()
    for i, prefix in enumerate(_PREFERRED_PREFIXES):
        if prefix in n:
            return i
    return len(_PREFERRED_PREFIXES)


def get_available_models(client) -> list:
  
    try:
        all_models = list(client.models.list())
        text_models = [
            m.name for m in all_models
            if _is_text_model(m.name)
        ]
     
        text_models.sort(key=_model_priority)
        return text_models
    except Exception as e:
        print(Y + f"  [!] Could not list models: {e}" + W)
        
        return [
            "models/gemini-2.5-flash",
            "models/gemini-2.0-flash",
            "models/gemini-flash-latest",
        ]


# ─────────────────────────────────────────────
#              UTILITY FUNCTIONS
# ─────────────────────────────────────────────
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print(BANNER)

def get_saved_api_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, 'r') as f:
            return f.read().strip()
    return None

def save_api_key(api_key):
    with open(KEY_FILE, 'w') as f:
        f.write(api_key)
    print(G + "  ✅ API Key saved locally for future use." + W)

def get_api_key_flow():
    api_key = get_saved_api_key()
    if not api_key:
        api_key = input(Y + "\n  [!] No saved key found. Enter Gemini API Key: " + W).strip()
        if api_key:
            save_choice = input(Y + "  [?] Save this key for future use? (y/n): " + W).lower()
            if save_choice == 'y':
                save_api_key(api_key)
        else:
            print(R + "  ❌ API Key is required for analysis." + W)
            return None
    else:
        print(G + "  ✅ Using saved API Key..." + W)
    return api_key

def load_unique_dorks(file_name, limit=None):
    path = os.path.join(CATEGORIES_DIR, file_name)
    with open(path, 'r', encoding='utf-8') as f:
        dorks = [line.strip() for line in f if line.strip()]
    seen   = set()
    unique = []
    for d in dorks:
        if d not in seen:
            seen.add(d)
            unique.append(d)
    if limit:
        unique = unique[:limit]
    return unique

def check_scan_file(mode_key):
    filename = SCAN_FILES[mode_key]
    path     = os.path.join(CATEGORIES_DIR, filename)
    if not os.path.exists(path):
        print(R + f"\n  [-] File not found: {path}" + W)
        return None
    return path

def print_progress(current, total, dork_preview=""):
    bar_len = 30
    filled  = int(bar_len * current / total) if total else 0
    bar     = "█" * filled + "░" * (bar_len - filled)
    pct     = int(100 * current / total) if total else 0
    preview = dork_preview[:40] + "..." if len(dork_preview) > 40 else dork_preview
    print(
        C + f"\n  [Processing {current}/{total}] " +
        G + f"[{bar}] {pct}%" +
        W + f"\n  {Y}Dork: {W}{preview}"
    )

def print_summary(all_results, mode_label):
    print()
    print(M + "  ╔" + "═" * 54 + "╗" + W)
    print(M + "  ║" + C + f"  📊  SCAN SUMMARY — {mode_label:<35}" + M + "║" + W)
    print(M + "  ╠" + "═" * 54 + "╣" + W)
    print(M + "  ║" + W + f"  Total Unique Results Found : " + G + f"{len(all_results):<24}" + M + "║" + W)
    print(M + "  ╚" + "═" * 54 + "╝" + W)
    print()

# ─────────────────────────────────────────────
#     COMPREHENSIVE SCAN SUB-QUERIES
# ─────────────────────────────────────────────
def build_comprehensive_queries(target):
    return [
        f'site:{target} ("contact" | "email" | "support" | "staff" | "about")',
        f'site:{target} filetype:txt ("readme" | "note" | "info" | "ver" | "test")',
        f'site:{target} filetype:pdf ("manual" | "guide" | "2025" | "2026" | "report")',
        f'site:{target} (filetype:doc | filetype:docx) ("list" | "form" | "table" | "user")',
        f'site:{target} (filetype:xls | filetype:xlsx) ("data" | "contact" | "client")',
        f'site:{target} intitle:"index of" ("public" | "files" | "upload" | "download")',
    ]

# ─────────────────────────────────────────────
#    PLAYWRIGHT ISOLATED SESSION ENGINE
# ─────────────────────────────────────────────
def _playwright_search_isolated(query, num_results=20, depth=1):
    user_agent = random.choice(UA_POOL)
    viewport   = random.choice(VIEWPORT_POOL)

    encoded_query = urllib.parse.quote_plus(query)
    search_url    = f"https://duckduckgo.com/?q={encoded_query}&t=h_&ia=web"

    raw_results = []

    print(B + f"  [*] UA       : " + W + user_agent[:65] + "...")
    print(B + f"  [*] Viewport : " + W + f"{viewport['width']}x{viewport['height']}")

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(
                user_agent  = user_agent,
                viewport    = viewport,
                locale      = "en-US",
                timezone_id = "America/New_York",
            )
            page = context.new_page()

            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins',   { get: () => [1, 2, 3, 4, 5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
                window.chrome = { runtime: {} };
            """)

            print(B + "  [*] Engine   : " + G + "Playwright + DuckDuckGo (Isolated Session)" + W)

            try:
                page.goto(search_url, wait_until="networkidle", timeout=7000)
            except Exception:
                try:
                    page.goto(search_url, wait_until="domcontentloaded", timeout=7000)
                except Exception as e:
                    print(Y + f"  [!] Page load timeout — {e}" + W)

            try:
                page.wait_for_selector('article[data-testid="result"]', timeout=6000)
            except Exception:
                print(Y + "  [!] Results selector timeout — proceeding..." + W)

            scroll_pause = random.uniform(1000, 2000)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(scroll_pause)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
            page.wait_for_timeout(random.uniform(500, 900))
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(random.uniform(600, 1200))

            for load_round in range(depth):
                more_btn = page.query_selector("#more-results")
                if more_btn:
                    print(B + f"  [*] Loading more (Round {load_round+1}/{depth})..." + W)
                    try:
                        more_btn.click()
                        page.wait_for_load_state("networkidle", timeout=6000)
                        page.wait_for_timeout(random.uniform(800, 1500))
                        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                        page.wait_for_timeout(random.uniform(600, 1000))
                    except Exception as e:
                        print(Y + f"  [!] More-results error: {e}" + W)
                        break
                else:
                    print(Y + f"  [!] No #more-results button (Round {load_round+1})" + W)
                    break

            result_elements = page.query_selector_all('article[data-testid="result"]')
            print(B + f"  [*] Raw Elements: {Y}{len(result_elements)}{W}")

            for el in result_elements:
                if len(raw_results) >= num_results:
                    break
                try:
                    title_el = (
                        el.query_selector('h2 a[data-testid="result-title-a"]') or
                        el.query_selector('h2 a') or
                        el.query_selector('a[data-testid="result-title-a"]')
                    )
                    url_el = (
                        el.query_selector('a[data-testid="result-extras-url-link"]') or
                        el.query_selector('a[data-testid="result-title-a"]') or
                        title_el
                    )
                    snippet_el = (
                        el.query_selector('[data-result="snippet"]') or
                        el.query_selector('div[class*="snippet"]') or
                        el.query_selector('span[class*="snippet"]')
                    )

                    if not title_el:
                        continue

                    title = title_el.inner_text().strip()
                    href  = ""
                    if url_el:
                        href = url_el.get_attribute("href") or ""

                    if href.startswith("//duckduckgo.com/l/"):
                        parsed_href = urllib.parse.urlparse("https:" + href)
                        qs   = urllib.parse.parse_qs(parsed_href.query)
                        href = urllib.parse.unquote(qs.get("uddg", [href])[0])
                    elif href.startswith("/l/?"):
                        parsed_href = urllib.parse.urlparse("https://duckduckgo.com" + href)
                        qs   = urllib.parse.parse_qs(parsed_href.query)
                        href = urllib.parse.unquote(qs.get("uddg", [href])[0])

                    snippet = snippet_el.inner_text().strip() if snippet_el else ""

                    if not href or not title:
                        continue

                    raw_results.append({
                        "title":       title,
                        "url":         href,
                        "description": snippet,
                    })

                except Exception:
                    continue

            context.close()
            browser.close()

    except Exception as e:
        print(R + f"  ❌ Playwright Error: {e}" + W)

    print(B + f"  [*] Extracted: {G}{len(raw_results)}{W}")
    return raw_results

# ─────────────────────────────────────────────
#           SINGLE DORK SEARCH  (PUBLIC)
# ─────────────────────────────────────────────
def get_google_results(query, target, num_results=10, strict_mode=False):
    mode_label = "STRICT (exact domain)" if strict_mode else "Standard (domain filter)"

    print(B + f"\n  [*] Query  : " + C + query)
    print(B +  "  [*] Filter : " + Y + mode_label)
    print(B +  "  [*] Domain : " + M + f"[{target}]" + W)
    print()

    raw_results  = _playwright_search_isolated(query, num_results=num_results * 2, depth=1)
    raw_count    = len(raw_results)
    results_list = []

    for res in raw_results:
        url = res.get("url", "")
        if strict_mode:
            parsed   = urllib.parse.urlparse(url)
            hostname = parsed.hostname or ""
            if not (hostname == target.lower() or
                    hostname.endswith("." + target.lower())):
                continue
        else:
            if target.lower() not in url.lower():
                continue

        results_list.append(res)
        print(G + f"  ✅ [{len(results_list):02d}] " + W + res["title"][:60] + "...")

        if len(results_list) >= num_results:
            break

    filtered_out = raw_count - len(results_list)
    print(
        B + f"\n  [*] " + W +
        f"Raw: {Y}{raw_count}{W}  |  "
        f"Filtered: {R}{filtered_out}{W}  |  "
        f"Kept: {G}{len(results_list)}{W}"
    )
    return results_list

# ─────────────────────────────────────────────
#       AUTO SCAN ENGINE  (Fast/Normal/Deep)
# ─────────────────────────────────────────────
def run_auto_scan(target, mode_key):
    labels = {
        "fast":   ("⚡  FAST SCAN",   "Fast Scan"),
        "normal": ("🔍  NORMAL SCAN", "Normal Scan"),
        "deep":   ("🔬  DEEP SCAN",   "Deep Scan"),
    }

    icon_label, summary_label = labels[mode_key]
    scan_depth = SCAN_DEPTH[mode_key]
    scan_limit = SCAN_LIMITS[mode_key]

    clear_screen()
    print_banner()

    path = check_scan_file(mode_key)
    if not path:
        input(Y + "\n  [↩] Press Enter to go back..." + W)
        return

    dorks       = load_unique_dorks(SCAN_FILES[mode_key], limit=scan_limit)
    total       = len(dorks)
    all_results = []
    seen_urls   = set()

    print(M + f"  {icon_label} MODE" + W)
    print(B + "  " + "─" * 54 + W)
    print(B + "  [>] Target      : " + G + target + W)
    print(B + "  [>] Dorks Loaded: " + Y + str(total) + W)
    print(B + "  [>] Scan Depth  : " + C + str(scan_depth) + W)
    print(B + "  [>] Session Mode: " + M + "Isolated (Per-Dork Reset)" + W)
    print(B + "  " + "─" * 54 + W)

    for idx, raw_dork in enumerate(dorks, 1):
        clean_dork  = re.sub(r'site:\S+', '', raw_dork).strip()
        clean_dork  = re.sub(r'\s+', ' ', clean_dork)
        final_query = (
            clean_dork.format(t=target) if "{t}" in clean_dork
            else f"{clean_dork} site:{target}"
        )
        final_query = re.sub(r'\|\s*$', '', final_query).strip()
        final_query = re.sub(r'\s+',    ' ', final_query)

        print_progress(idx, total, final_query)

        try:
            raw        = _playwright_search_isolated(final_query, num_results=10, depth=scan_depth)
            found_this = 0

            for res in raw:
                url      = res.get("url", "")
                parsed   = urllib.parse.urlparse(url)
                hostname = parsed.hostname or ""
                if not (hostname == target.lower() or
                        hostname.endswith("." + target.lower())):
                    continue
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                all_results.append(res)
                found_this += 1
                print(G + f"    ✅ " + W + res["title"][:58] + "...")

            if found_this == 0:
                print(Y + "    ⚠️  No matching results for this dork." + W)

        except Exception as e:
            print(R + f"    ❌ Error on dork [{idx}]: {e}" + W)

        if idx < total:
            cooldown = random.uniform(1.0, 2.0)
            print(Y + f"\n  [~] Cooldown: {cooldown:.1f}s..." + W)
            time.sleep(cooldown)

    print_summary(all_results, summary_label)

    if all_results:
        print(G + "  " + "─" * 54 + W)
        print(G + f"  📋  ALL RESULTS — {summary_label}" + W)
        print(G + "  " + "─" * 54 + W)
        for i, r in enumerate(all_results):
            print(G + f"\n  [{i+1:02d}] " + W + r['title'])
            print(B +  "       URL : " + C + r['url'] + W)

        do_analyze = input(Y + "\n  [?] Run AI Analysis on these results? (y/n): " + W).lower()
        if do_analyze == 'y':
            api_key = get_api_key_flow()
            if api_key:
                analyze_with_ai(all_results, target, api_key)
    else:
        print(R + "  [-] No results found matching target domain." + W)

    print()
    next_action = input(
        Y + "  [?] (r) Run again | (b) Back | (q) Quit: " + W
    ).lower().strip()
    if next_action == 'q':
        print(G + "\n  [*] Goodbye! 👋" + W)
        exit(0)
    elif next_action == 'r':
        run_auto_scan(target, mode_key)

# ─────────────────────────────────────────────
#      COMPREHENSIVE SCAN  ⭐ SPECIAL
# ─────────────────────────────────────────────
def run_comprehensive_scan(target):
    queries = build_comprehensive_queries(target)

    clear_screen()
    print_banner()

    print(M + "  ⭐  [70SNY SPECIAL] COMPREHENSIVE SCAN MODE" + W)
    print(B + "  " + "─" * 54 + W)
    print(B + "  [>] Target  : " + G + target + W)
    print(B + "  [>] Queries : " + Y + f"{len(queries)} sub-queries" + W)
    print(B + "  [>] Session : " + M + "Isolated (Per-Query Reset)" + W)
    print(B + "  " + "─" * 54 + W)
    print(C + "\n  Sub-queries:" + W)
    for i, q in enumerate(queries, 1):
        print(Y + f"    {i}. " + W + q)
    print()

    print(Y + "  [?] Choose Execution Mode:" + W)
    print(G + "      1. " + W + "Automatic Scan  🤖")
    print(G + "      2. " + W + "Manual Mode (show queries) ✍️")
    print(R + "      b. " + W + "Back to Menu")

    mode = input(C + "\n  [>] Mode: " + W).lower().strip()

    if mode == '1':
        clear_screen()
        print_banner()
        print(M + "  ⭐  [COMPREHENSIVE SCAN] RUNNING...\n" + W)

        all_results = []
        seen_urls   = set()
        total       = len(queries)

        for idx, query in enumerate(queries, 1):
            print(C + f"\n  [{idx}/{total}] " + W + query)
            raw = _playwright_search_isolated(query, num_results=10, depth=1)

            for res in raw:
                url      = res.get("url", "")
                parsed   = urllib.parse.urlparse(url)
                hostname = parsed.hostname or ""
                if not (hostname == target.lower() or
                        hostname.endswith("." + target.lower())):
                    continue
                if url in seen_urls:
                    continue
                seen_urls.add(url)
                all_results.append(res)
                print(G + f"    ✅ " + W + res["title"][:55] + "...")

            if idx < total:
                cooldown = random.uniform(1.0, 2.0)
                print(Y + f"\n  [~] Cooldown: {cooldown:.1f}s..." + W)
                time.sleep(cooldown)

        print(B + f"\n  [*] Total Unique Results: {G}{len(all_results)}{W}")

        if all_results:
            print()
            print(G + "  " + "─" * 54 + W)
            print(G + "  📋  COMPREHENSIVE RESULTS (Strict Domain Filter)" + W)
            print(G + "  " + "─" * 54 + W)
            for i, r in enumerate(all_results):
                print(G  + f"\n  [{i+1:02d}] " + W + r['title'])
                print(B  +  "       URL: " + C + r['url'] + W)

            do_analyze = input(Y + "\n  [?] AI Analysis on these results? (y/n): " + W).lower()
            if do_analyze == 'y':
                api_key = get_api_key_flow()
                if api_key:
                    analyze_with_ai(all_results, target, api_key)
        else:
            print(R + "\n  [-] No results found matching target domain." + W)

        print()
        next_action = input(
            Y + "  [?] (r) Run again | (b) Back | (q) Quit: " + W
        ).lower().strip()
        if next_action == 'q':
            print(G + "\n  [*] Goodbye! 👋" + W)
            exit(0)
        elif next_action == 'r':
            run_comprehensive_scan(target)

    elif mode == '2':
        print()
        print(C + "  🚀  COPY & PASTE IN BROWSER (run each separately):" + W)
        print(B + "  " + "─" * 54 + W)
        for i, q in enumerate(queries, 1):
            print(Y + f"  [{i}] " + W + q)
        print(B + "  " + "─" * 54 + W)
        input(Y + "\n  [↩] Press Enter to continue..." + W)

# ─────────────────────────────────────────────
#    ✅ AI ANALYSIS ENGINE  (Auto Model Discovery)
# ─────────────────────────────────────────────
def analyze_with_ai(search_results, target, api_key):
    print()
    print(M + "  " + "─" * 54 + W)
    print(C +  "  🤖  AI ENGINE — ANALYZING THREATS..." + W)
    print(M + "  " + "─" * 54 + W)
    print()

    formatted_results = ""
    for i, res in enumerate(search_results):
        formatted_results += (
            f"\n[{i+1}] Title: {res['title']}\n"
            f"URL: {res['url']}\n"
            f"Snippet: {res['description']}\n"
        )

           
              # you can change this the prompt 

    prompt = f"""
ROLE: You are a Senior Cybersecurity Auditor & OSINT Expert.
TARGET: {target}

TASK: Perform a deep security analysis on the following discovered URLs. 
You must categorize each finding and evaluate the risk based on the Tech Stack identified (e.g., IIS 7.5, ASP.NET).

ANALYSIS GUIDELINES:
1. IDENTIFY: Exposed credentials, config files (.env, .config, .sql), admin portals, and directory listings.
2. EVALUATE: For each URL, determine the potential impact if an attacker exploits it.
3. NO FLUFF: Do not define what a PDF or a Login page is. Focus only on the security risk.

OUTPUT FORMAT PER FINDING:
──────────────────────────────────────────────────────
[SEVERITY] → URL: [URL]
• EXPOSURE: [What exact data/interface is leaked?]
• RISK: [How can this be exploited? e.g., Credential Brute-forcing, Information Disclosure]          
• REMEDIATION: [Immediate action to secure this point]
──────────────────────────────────────────────────────

SEVERITY SCALE:
- [CRITICAL]: Database dumps, Config files with passwords, Unprotected Admin Panels.
- [HIGH]: PII (Emails/Phones), Internal Path Disclosure, Server Version Leaks (e.g., Old IIS).
- [MEDIUM]: Sensitive documents (PDFs/XLSX) that shouldn't be public.
- [LOW/INFO]: General public data.

If no sensitive data is found, strictly output: "No sensitive data confirmed in these results."

RESULTS TO ANALYZE:
{formatted_results}
"""

   
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        print(R + f"  ❌ Failed to initialize Gemini client: {e}" + W)
        print(Y + "  [!] Skipping AI analysis — scan results above are still valid." + W)
        return


    print(B + "  [*] Discovering available models..." + W)
    models = get_available_models(client)

    if not models:
        print(R + "  ❌ No text models available for this API key." + W)
        print(Y + "  [!] Skipping AI analysis." + W)
        return

    print(B + f"  [*] Found {G}{len(models)}{B} text models — trying in order..." + W)

    response_text = None
    used_model    = None

    for model_name in models:
        try:
            print(B + f"  [*] Trying : " + C + model_name + W)
            response      = client.models.generate_content(
                model    = model_name,
                contents = prompt,
            )
            response_text = response.text
            used_model    = model_name
            break

        except Exception as e:
            err_str = str(e)
            if "404" in err_str or "NOT_FOUND" in err_str:
                print(Y + f"  [!] Not available — next..." + W)
                continue
            elif "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                print(Y + f"  [!] Rate limit — next..." + W)
                time.sleep(2)
                continue
            elif "401" in err_str or "API_KEY" in err_str.upper():
                print(R + "  ❌ Invalid API Key." + W)
                return
            elif "400" in err_str and "not support" in err_str.lower():
                print(Y + f"  [!] generateContent not supported — next..." + W)
                continue
            else:
                print(Y + f"  [!] Error: {err_str[:70]} — next..." + W)
                continue

    if response_text:
        print(B + f"\n  [*] Model Used : " + G + used_model + W)
        print()
        print(M + "  " + "=" * 20 + W)
        print(C  + "       [ AI SECURITY REPORT ]" + W)
        print(M + "  " + "=" * 20 + W)
        print()
        print(W + response_text)
        print()
        print(M + "  " + "─" * 54 + W)
    else:
        print(R + "  ❌ All available models failed." + W)
        print(Y + "  [!] Skipping AI analysis — scan results above are still valid." + W)

# ─────────────────────────────────────────────
#         DORK BROWSER & RUNNER  (Custom)
# ─────────────────────────────────────────────
def select_and_run_dork(target, all_dorks):
    start_index = 0
    page_size   = 15

    while True:
        clear_screen()
        print_banner()
        print(B + "  [>] Target: " + G + target + W + "\n")

        if start_index >= len(all_dorks):
            print(Y + "  ⚠️  No more dorks in this category." + W)
            input(Y + "\n  [↩] Press Enter to go back to category menu..." + W)
            return

        total         = len(all_dorks)
        batch_end     = min(start_index + page_size, total)
        current_batch = all_dorks[start_index: start_index + page_size]

        print(C + f"  📂  Dorks  {start_index+1}–{batch_end}  /  {total} total" + W)
        print(B + "  " + "─" * 54 + W)

        for i, dork in enumerate(current_batch):
            display_dork = (
                dork.format(t=target) if "{t}" in dork
                else f"{dork} site:{target}"
            )
            num_label = f"{start_index + i + 1:03d}."
            print(Y + f"  {num_label} " + C + display_dork + W)

        print(B + "\n  " + "─" * 54 + W)
        print(G + "  m. " + W + "More dorks")
        print(Y + "  b. " + W + "Back to menu")
        print(R + "  q. " + W + "Quit")

        user_input = input(C + "\n  [?] Pick Number / m / b / q: " + W).lower().strip()

        if user_input == 'q':
            print(G + "\n  [*] Goodbye! 👋" + W)
            exit(0)
        elif user_input == 'b':
            return
        elif user_input == 'm':
            next_start = start_index + page_size
            if next_start >= total:
                print(Y + "\n  ⚠️  No more dorks in this category." + W)
                input(Y + "  [↩] Press Enter to go back to category menu..." + W)
                return
            start_index = next_start

        elif user_input.isdigit():
            selected_idx = int(user_input) - 1
            if 0 <= selected_idx < total:
                raw_dork = all_dorks[selected_idx]
                clean_dork  = re.sub(r'site:\S+', '', raw_dork).strip()
                clean_dork  = re.sub(r'\s+', ' ', clean_dork)
                final_query = (
                    clean_dork.format(t=target) if "{t}" in clean_dork
                    else f"{clean_dork} site:{target}"
                )
                final_query = re.sub(r'\|\s*$', '', final_query).strip()
                final_query = re.sub(r'\s+',    ' ', final_query)

                print(Y + f"\n  [!] Selected: " + C + final_query + W)
                print()
                print(Y + "  [?] Choose Execution Mode:" + W)
                print(G + "      1. " + W + "Automatic Scan  🤖")
                print(G + "      2. " + W + "Manual Mode     ✍️")
                print(R + "      b. " + W + "Back")

                mode = input(C + "\n  [>] Mode: " + W).lower().strip()

                if mode == '1':
                    clear_screen()
                    print_banner()
                    print(B + "  [>] Target: " + G + target + W + "\n")

                    results = get_google_results(final_query, target, num_results=10)

                    if results:
                        print()
                        print(G + "  " + "─" * 54 + W)
                        print(G + "  📋  FILTERED RESULTS (Target Domain Only)" + W)
                        print(G + "  " + "─" * 54 + W)
                        for i, r in enumerate(results):
                            print(G + f"\n  [{i+1:02d}] " + W + r['title'])
                            print(B +  "       URL: " + C + r['url'] + W)

                        do_analyze = input(
                            Y + "\n  [?] AI Analysis on these results? (y/n): " + W
                        ).lower()
                        if do_analyze == 'y':
                            api_key = get_api_key_flow()
                            if api_key:
                                analyze_with_ai(results, target, api_key)
                    else:
                        print(R + "\n  [-] No results found matching target domain." + W)

                    print()
                    next_action = input(
                        Y + "  [?] (r) Another dork | (b) Back | (q) Quit: " + W
                    ).lower().strip()
                    if next_action == 'q':
                        print(G + "\n  [*] Goodbye! 👋" + W)
                        exit(0)
                    elif next_action == 'b':
                        return

                elif mode == '2':
                    print()
                    print(C + "  🚀  COPY & PASTE IN BROWSER:" + W)
                    print(B + "  " + "─" * 54 + W)
                    print(W + f"  {final_query}")
                    print(B + "  " + "─" * 54 + W)
                    input(Y + "\n  [↩] Press Enter to continue..." + W)
            else:
                print(R + "  ❌ Invalid number." + W)
                input(Y + "  [↩] Press Enter to continue..." + W)
        else:
            print(R + "  ❌ Invalid input." + W)
            input(Y + "  [↩] Press Enter to continue..." + W)

# ─────────────────────────────────────────────
#      CUSTOM CATEGORIES MENU
# ─────────────────────────────────────────────
def run_custom_categories(target):
    while True:
        clear_screen()
        print_banner()
        print(B + "  [>] Target: " + G + target + W + "\n")

        if not os.path.exists(CATEGORIES_DIR):
            print(R + f"  ❌ Error: Folder '{CATEGORIES_DIR}' not found!" + W)
            input(Y + "  [↩] Press Enter to go back..." + W)
            return

        all_files = [f for f in os.listdir(CATEGORIES_DIR) if f.endswith('.txt')]
        files     = [f for f in all_files if f not in RESERVED_FILES]

        print(C + "  [?] Custom Categories:" + W)
        print(B + "  " + "─" * 54 + W)
        print(M + "  ⭐  00. " + Y + "[70SNY SPECIAL] Comprehensive Scan" + W)
        print(B + "  " + "─" * 54 + W)

        if not files:
            print(Y + "  ⚠️  No custom category files found." + W)
        else:
            for i, file in enumerate(files):
                label = file.replace('.txt', '').replace('_', ' ').title()
                print(G + f"  {i+1:02d}. " + W + label)

        print(B + "\n  " + "─" * 54 + W)
        print(Y + "  b.  " + W + "Back to Main Menu")
        print(R + "  q.  " + W + "Quit")

        cat_input = input(C + "\n  [>] Select Category: " + W).lower().strip()

        if cat_input == 'q':
            print(G + "\n  [*] Goodbye! 👋" + W)
            exit(0)
        elif cat_input == 'b':
            return
        elif cat_input in ('0', '00'):
            run_comprehensive_scan(target)
        elif cat_input.isdigit():
            cat_choice = int(cat_input) - 1
            if 0 <= cat_choice < len(files):
                all_dorks = load_unique_dorks(files[cat_choice])
                select_and_run_dork(target, all_dorks)
            else:
                print(R + "  ❌ Invalid category number." + W)
                input(Y + "  [↩] Press Enter to retry..." + W)
        else:
            print(R + "  ❌ Invalid input." + W)
            input(Y + "  [↩] Press Enter to retry..." + W)

# ─────────────────────────────────────────────
#                 MAIN MENU
# ─────────────────────────────────────────────
def print_main_menu(target):
    print(B + "\n  [>] Target Set To ==> " + G + target + W)
    print()
    print(C + "  [?] Select Scan Mode:" + W)
    print(B + "  " + "─" * 54 + W)

    scan_modes = {
        "fast":   ("01", "⚡", "Fast Scan",   f"Top {SCAN_LIMITS['fast']} dorks"),
        "normal": ("02", "🔍", "Normal Scan", f"Top {SCAN_LIMITS['normal']} dorks"),
        "deep":   ("03", "🔬", "Deep Scan",   f"Top {SCAN_LIMITS['deep']} dorks"),
    }

    for key, (num, icon, label, desc) in scan_modes.items():
        print(M + f"  {icon}  {num}. " + Y + label + W + f"  —  {desc}")

    print(B + "  🗂️   04. " + Y + "Custom Categories" + W +
          "  —  Browse dorks manually")

    print(B + "\n  " + "─" * 54 + W)
    print(Y + "  t.  " + W + f"Change Target  (current: {G}{target}{W})")
    print(R + "  q.  " + W + "Quit")
    print(B + "  " + "─" * 54 + W)


def main():
    clear_screen()
    target = ""

    while True:
        clear_screen()
        print_banner()

        if not target:
            target = input(C + "  [+] Enter Target Domain (e.g., target.com): " + W).strip()
            if not target:
                print(R + "  [-] Target cannot be empty!" + W)
                input(Y + "  [↩] Press Enter to retry..." + W)
                continue

        if not os.path.exists(CATEGORIES_DIR):
            print(R + f"  ❌ Error: Folder '{CATEGORIES_DIR}' not found!" + W)
            input(Y + "  [↩] Press Enter to exit..." + W)
            break

        print_main_menu(target)

        choice = input(C + "\n  [>] Select Option: " + W).lower().strip()

        if choice in ('1', '01'):
            run_auto_scan(target, "fast")
        elif choice in ('2', '02'):
            run_auto_scan(target, "normal")
        elif choice in ('3', '03'):
            run_auto_scan(target, "deep")
        elif choice in ('4', '04'):
            run_custom_categories(target)
        elif choice == 't':
            target = ""
            continue
        elif choice == 'q':
            print(G + "\n  [*] Goodbye! 👋" + W)
            break
        else:
            print(R + "  ❌ Invalid input." + W)
            input(Y + "  [↩] Press Enter to retry..." + W)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(
            "\n\n" +
            Y  + "  [!] " +
            W  + "Ctrl+C detected — " +
            G  + "Exiting safely..." +
            W
        )
