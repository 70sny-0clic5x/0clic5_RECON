# Øclic5Recon (70SNY_0xHUNTER)
### Advanced AI-Driven OSINT & Automated Dorking Framework

**Øclic5Recon** is a high-performance reconnaissance framework designed for penetration testers and bug bounty hunters. It automates the discovery of exposed assets and sensitive data by combining stealthy browser automation with Google Gemini AI for real-time threat analysis.

```text
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

```

## Technical Core Components

### 1. Stealth Execution Engine
* **Engine:** Playwright (Chromium) with advanced anti-detection.
* **Fingerprinting:** Randomized User-Agents, Viewports, and Chrome runtime spoofing.
* **Bypass:** Automated `navigator.webdriver` evasion and fake plugin injection.

### 2. AI Security Analysis (Gemini 1.5 Flash)
The integrated AI engine performs deep inspection of search results to categorize risks:
* **Critical:** Credential leaks, `.env`, `web.config`, and SQL dumps.
* **High:** Admin portals, PII (Emails/Phones), and legacy server versions (e.g., IIS 7.5).
* **Medium/Low:** Sensitive documentation (PDF/XLSX) and directory listings.

### 3. Scan Modifiers
| Mode | Dork Count | Depth | Description |
| :--- | :--- | :--- | :--- |
| **Fast** | 8 | 1 | Surface-level reconnaissance. |
| **Normal** | 16 | 2 | Standard asset mapping. |
| **Deep** | 30 | 4 | Exhaustive sensitive data discovery. |

---

## Directory Structure
```text
project/
├── main.py              # Entry point
├── .gemini_key          # Local API storage
└── dorks_categories/    # Dork database (Fast, Normal, Deep)
```
## Deployment & Setup

### Prerequisites
* **Python 3.9+**
* **Playwright**
* **Google Gemini API Key**

### Installation
```bash
# Clone the repository
git clone <repository-url>

# Install required modules
pip install playwright colorama google-generativeai

# Initialize browser binaries
playwright install
```
Execution
```bash
python main.py
```
## 🔍 Usage Instructions

1. **Enter target domain**  
   _(e.g., `target.edu.eg`)_

2. **Select scan intensity**  
   - Fast  
   - Normal  
   - Deep
   - Custom Categories 

3. **Review AI-generated Security Report**  
   - Exposure Analysis  
   - Risk Assessment  
   - Remediation Recommendations  

---

## ⚠️ Security Policy

This tool is strictly for **Authorized Penetration Testing and Ethical Hacking**.

The developer (**70SNY_0XHUNTER**) is **not responsible** for misuse or unauthorized targeting.
---

##  About the Author




