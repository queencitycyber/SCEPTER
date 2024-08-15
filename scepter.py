import asyncio
import json
import re
import logging
from urllib.parse import urlparse, urljoin
from typing import List, Dict, Any

import click
import yaml
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TaskID
from rich.logging import RichHandler

# Setup logging
logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

log = logging.getLogger("rich")

# Load MFA providers from YAML file
with open('providers.yaml', 'r') as file:
    MFA_PROVIDERS = yaml.safe_load(file)

console = Console()

def ensure_url_scheme(url: str) -> str:
    parsed = urlparse(url)
    if not parsed.scheme:
        return f"https://{url}"
    return url

async def get_js_urls(page) -> List[str]:
    return await page.evaluate("""
        () => Array.from(document.getElementsByTagName('script'))
                .filter(script => script.src)
                .map(script => script.src)
    """)

async def analyze_content(content: str, url: str) -> set:
    detected_providers = set()
    for provider, patterns in MFA_PROVIDERS.items():
        for pattern in patterns:
            if re.search(pattern, content, re.IGNORECASE) or re.search(pattern, url, re.IGNORECASE):
                detected_providers.add(provider)
                break  # Move to the next provider once we've found a match
    return detected_providers

async def process_url(url: str, browser, progress: Progress, task_id: TaskID, verbose: bool) -> Tuple[str, List[str], Dict[str, Any]]:
    detected_providers = set()
    debug_info = {"js_urls": [], "errors": []}
    
    url = ensure_url_scheme(url)
    
    try:
        context = await browser.new_context(ignore_https_errors=True)
        page = await context.new_page()
        response = await page.goto(url, wait_until='networkidle', timeout=30000)
        
        if verbose:
            debug_info["status"] = response.status
            debug_info["headers"] = dict(response.headers)
        
        content = await page.content()
        detected_providers.update(await analyze_content(content, url))
        
        js_urls = await get_js_urls(page)
        for js_url in js_urls:
            try:
                js_content = await page.evaluate(f'() => fetch("{js_url}").then(r => r.text())')
                detected_providers.update(await analyze_content(js_content, js_url))
                if verbose:
                    debug_info["js_urls"].append(js_url)
            except Exception as e:
                log.warning(f"Error fetching {js_url}: {str(e)}")
                if verbose:
                    debug_info["errors"].append(f"Error fetching {js_url}: {str(e)}")
        
    except PlaywrightTimeoutError:
        log.error(f"Timeout error while processing {url}")
        debug_info["errors"].append(f"Timeout error while processing {url}")
    except Exception as e:
        log.error(f"Error processing {url}: {str(e)}")
        debug_info["errors"].append(f"Error processing {url}: {str(e)}")
    finally:
        await context.close()
        progress.update(task_id, advance=1)
    
    return url, list(detected_providers), debug_info

async def main(urls: List[str], output_format: str, verbose: bool):
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        
        with Progress() as progress:
            main_task = progress.add_task("[cyan]Processing URLs...", total=len(urls))
            tasks = [process_url(url, browser, progress, main_task, verbose) for url in urls]
            results = await asyncio.gather(*tasks)
        
        await browser.close()
    
    if output_format == 'json':
        json_results = {url: {"providers": providers, "debug_info": debug_info} for url, providers, debug_info in results}
        console.print_json(json.dumps(json_results, indent=2))
    else:
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("URL", style="dim", width=50)
        table.add_column("Detected Providers", style="dim")
        table.add_column("Status", style="dim")
        
        for url, providers, debug_info in results:
            status = "Success" if not debug_info["errors"] else "Failed"
            table.add_row(url, ", ".join(providers) if providers else "None", status)
        
        console.print(table)
        
        if verbose:
            console.print("\n[bold]Verbose Output:[/bold]")
            for url, providers, debug_info in results:
                console.print(f"\n[bold]URL:[/bold] {url}")
                console.print(f"[bold]Status:[/bold] {debug_info.get('status', 'N/A')}")
                console.print("[bold]Headers:[/bold]")
                for key, value in debug_info.get('headers', {}).items():
                    console.print(f"  {key}: {value}")
                console.print("[bold]JavaScript URLs:[/bold]")
                for js_url in debug_info.get('js_urls', []):
                    console.print(f"  {js_url}")
                if debug_info.get('errors'):
                    console.print("[bold]Errors:[/bold]")
                    for error in debug_info['errors']:
                        console.print(f"  {error}")

@click.command()
@click.option('--url', '-u', help='Single URL to process')
@click.option('--input', '-i', help='Input file containing URLs, one per line')
@click.option('--output', '-o', type=click.Choice(['text', 'json']), default='text', help='Output format (text or json)')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.option('--log-level', type=click.Choice(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']), default='INFO', help='Set the logging level')
def cli(url: str, input: str, output: str, verbose: bool, log_level: str):
    """SCEPTER: Stealthy Credential Expert Probing Tool for Enumeration and Reconnaissance"""
    logging.getLogger().setLevel(log_level)
    
    urls = []
    
    if url:
        urls = [url]
    elif input:
        try:
            with open(input, 'r') as f:
                urls = [line.strip() for line in f if line.strip()]
        except IOError:
            log.error(f"Unable to read file {input}")
            return
    else:
        log.error("Please provide either a URL (-u) or an input file (-i).")
        return
    
    if not urls:
        log.error("No URLs provided.")
        return
    
    asyncio.run(main(urls, output, verbose))

if __name__ == "__main__":
    cli()
