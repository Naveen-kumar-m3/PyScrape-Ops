# pyscrape_ops/cli.py
import yaml
import typer
from pathlib import Path
from .scraper import Scraper
from .processor import process_items
from .file_utils import save_records

app = typer.Typer(help="PyScrape Ops CLI")

@app.command()
def run_job(job: str = typer.Option(..., help="Path to job config YAML")):
    """
    Run one or more scraping jobs described in YAML.
    """
    job_path = Path(job)
    if not job_path.exists():
        typer.echo(f"Config not found: {job}")
        raise typer.Exit(code=1)

    cfg = yaml.safe_load(job_path.read_text())
    for j in cfg.get("jobs", []):
        name = j.get("name", "unnamed")
        url = j.get("url")
        selectors = j.get("selectors", {})
        output = j.get("output_csv", f"outputs/{name}.csv")
        rate = j.get("rate_limit_seconds", 1.0)

        typer.echo(f"[job] {name} -> {url}")

        s = Scraper()
        try:
            items = s.scrape_job(url, selectors, rate_limit_seconds=rate)
        except PermissionError as pe:
            typer.echo(f"[skipped] robots.txt disallows: {pe}")
            continue
        except Exception as e:
            typer.echo(f"[failed] {name}: {e}")
            continue

        df = process_items(items, dedupe=True)
        save_records(df.to_dict(orient="records"), output, fmt="csv")

        typer.echo(f"[done] saved {len(df)} rows to {output}")

if __name__ == "__main__":
    app()
