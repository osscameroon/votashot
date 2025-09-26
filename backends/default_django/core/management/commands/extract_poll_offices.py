from __future__ import annotations

import re
import sys
from dataclasses import dataclass
import json
from pathlib import Path
import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction  # noqa: F401  (kept for backward compat; no DB writes)

from core.models import PollOffice


# Lazy import so the module remains importable without the dependency
def _import_pdfplumber():  # pragma: no cover - thin wrapper
    try:
        import pdfplumber  # type: ignore

        return pdfplumber
    except Exception as exc:  # pragma: no cover
        raise RuntimeError(
            "pdfplumber is required. Install it with `uv add pdfplumber`."
        ) from exc


def _strip_accents(s: str) -> str:
    import unicodedata

    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch))


def _norm(s: Optional[str]) -> str:
    if s is None:
        return ""
    s = str(s).strip()
    if not s:
        return ""
    s = _strip_accents(s).lower()
    s = re.sub(r"\s+", " ", s)
    s = s.strip(" :;,.|/\\-\u00a0")
    return s


HEADER_SYNONYMS: Dict[str, set[str]] = {
    # Column that previously looked like an identifier is actually voters count
    "voters_count": {
        "id",  # per user feedback: this column is voters count
        "identifier",
        "identifiant",
        "identifiant bv",
        "code",
        "ref",
        "reference",
        "numero",
        "num",
        "n",
        "n°",
        "no",
        "numéro",
        "nº",
        # Add common voters count headers
        "voters",
        "voters count",
        "registered voters",
        "electeurs",
        "electeurs inscrits",
        "inscrits",
        "effectif",
        "nb electeurs",
        "nbre electeurs",
        "nbre d'electeurs",
        "nombre d'electeurs",
        "nombre d inscrits",
        "nb inscrits",
        "electeurs total",
        "total electeurs",
        "effectif count",
    },
    "name": {
        "name",
        "nom",
        "libelle",
        "libellé",
        "bureau",
        "bureau de vote",
        "bureau de vote polling station",
        "bv",
        "office",
        "poll office",
        "intitule",
        "intitulé",
        "centre",
        "lieu",
    },
    "country": {"country", "pays"},
    "state": {"state", "etat", "province"},
    "region": {"region", "région"},
    "city": {"city", "ville", "commune"},
    # Don't map DEPARTEMENT/DEPARTMENT to county (not equivalent)
    "county": {"county"},
    "district": {"district", "arrondissement", "quartier", "zone", "localite", "localité"},
}


NUMBER_RE = re.compile(r"[0-9]+")


def parse_int_loose(value: str) -> Optional[int]:
    # Keep digits only for robustness (handles 1 234 or 1,234)
    digits = "".join(ch for ch in value if ch.isdigit())
    try:
        return int(digits) if digits else None
    except Exception:
        return None


def clean_cell(cell: Optional[str]) -> str:
    if cell is None:
        return ""
    # Collapse whitespace and strip newlines
    value = str(cell).replace("\n", " ").replace("\r", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value


@dataclass
class ParsedRow:
    name: Optional[str] = None
    voters_count: Optional[int] = None
    country: Optional[str] = None
    state: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    county: Optional[str] = None
    district: Optional[str] = None


def map_headers(headers: Sequence[str]) -> Dict[int, str]:
    """Map header indexes to PollOffice fields using HEADER_SYNONYMS."""
    mapping: Dict[int, str] = {}
    for idx, raw in enumerate(headers):
        key = _norm(raw)
        if not key:
            continue
        for field, synonyms in HEADER_SYNONYMS.items():
            if key in synonyms:
                mapping[idx] = field
                break
    return mapping


def parse_row(cells: Sequence[str], header_map: Dict[int, str]) -> ParsedRow:
    pr = ParsedRow()
    # First pass: use header_map when available
    for idx, cell in enumerate(cells):
        value = clean_cell(cell)
        if not value:
            continue
        field = header_map.get(idx)
        if field and hasattr(pr, field):
            if field == "voters_count":
                pr.voters_count = parse_int_loose(value)
            else:
                setattr(pr, field, value)

    if not pr.name:
        # Use the longest textual cell as name
        text_cells = [clean_cell(c) for c in cells if c]
        if text_cells:
            pr.name = max(text_cells, key=len)
    return pr


def detect_voters_column(rows: List[List[str]]) -> Optional[int]:
    """Infer the voters_count column index by scanning numeric density.

    Heuristic: choose the column with the highest count of integers >= 50.
    If tie, choose the one with the highest median value.
    """
    if not rows:
        return None
    col_count = max(len(r) for r in rows)
    scores: List[int] = [0] * col_count
    values: List[List[int]] = [[] for _ in range(col_count)]
    for r in rows:
        for j in range(col_count):
            val = clean_cell(r[j]) if j < len(r) else ""
            iv = parse_int_loose(val)
            if iv is None:
                continue
            if iv >= 50:
                scores[j] += 1
                values[j].append(iv)
    if max(scores) == 0:
        return None
    # Pick best index by score then by median
    best_indices = [j for j, s in enumerate(scores) if s == max(scores)]
    if len(best_indices) == 1:
        return best_indices[0]
    # tie-breaker by median
    def median(nums: List[int]) -> float:
        if not nums:
            return 0.0
        ns = sorted(nums)
        n = len(ns)
        mid = n // 2
        if n % 2 == 1:
            return float(ns[mid])
        return (ns[mid - 1] + ns[mid]) / 2.0

    best_indices.sort(key=lambda j: median(values[j]), reverse=True)
    return best_indices[0] if best_indices else None


def parse_page_header_info(page) -> Dict[str, Optional[str]]:
    """Extract region and city from header text on the page.

    Looks for patterns like: "REGION: XXXX   DEPARTMENT: XXXX   COMMUNE: XXXX".
    Returns a dict with keys: region, city (any may be None).
    """
    try:
        text = page.extract_text() or ""
    except Exception:
        text = ""

    # Normalize to ASCII-ish for robust matching
    norm_text = _strip_accents(text).lower()
    # Collapse whitespace for easier regex
    norm_text = re.sub(r"\s+", " ", norm_text)

    out: Dict[str, Optional[str]] = {"region": None, "city": None}

    # Extract REGION and COMMUNE robustly (allowing hyphens etc.)
    def grab_after(label: str, next_labels: Sequence[str]) -> Optional[str]:
        pattern = rf"{label}\s*:\s*(.+?)(?=\s+(?:{'|'.join(next_labels)})\s*:|$)"
        mm = re.search(pattern, norm_text)
        return mm.group(1).strip() if mm else None

    region = grab_after(r"region", ["department", "departement", "commune"]) or None
    city = grab_after(r"commune", ["region", "department", "departement"]) or None
    out["region"] = region
    out["city"] = city
    return out


def iter_pdf_tables(pdf_path: Path) -> Iterable[Tuple[Dict[str, Optional[str]], List[List[str]]]]:
    pdfplumber = _import_pdfplumber()
    with pdfplumber.open(str(pdf_path)) as pdf:
        for page in pdf.pages:
            header_info = parse_page_header_info(page)
            # Try lattice (lines) first
            tables = page.extract_tables(
                table_settings={
                    "vertical_strategy": "lines",
                    "horizontal_strategy": "lines",
                }
            ) or []
            if not tables:
                # Fallback to stream (text)
                tables = page.extract_tables(
                    table_settings={
                        "vertical_strategy": "text",
                        "horizontal_strategy": "text",
                        "intersection_tolerance": 5,
                        "snap_tolerance": 3,
                        "min_words_vertical": 1,
                        "min_words_horizontal": 1,
                    }
                ) or []
            for table in tables:
                # Normalize cells immediately
                norm_table = [
                    [clean_cell(c) for c in row]
                    for row in table
                    if any(clean_cell(c) for c in row)
                ]
                yield header_info, norm_table


def derive_country_code(country: Optional[str], explicit_code: Optional[str]) -> str:
    if explicit_code:
        return _strip_accents(explicit_code).upper().strip()
    if not country:
        return "XX"
    lowered = _strip_accents(country).lower()
    if "cameroon" in lowered or "cameroun" in lowered:
        return "CM"
    # Use first two letters of the alphabetic part as a best-effort code
    letters = re.findall(r"[A-Za-z]", _strip_accents(country))
    code = ("".join(letters)[:2] or "XX").upper()
    return code


def normalize_component(value: Optional[str]) -> str:
    if not value:
        return ""
    v = _strip_accents(str(value))
    # Replace non-alphanumeric with '-'
    v = re.sub(r"[^A-Za-z0-9]+", "-", v)
    v = re.sub(r"-+", "-", v).strip("-")
    return v


def compose_identifier(country_code: str, region: Optional[str], city: Optional[str], name: str) -> str:
    parts = [country_code, normalize_component(region), normalize_component(city), normalize_component(name)]
    return "-".join([p for p in parts if p])


class Command(BaseCommand):
    help = (
        "Extract poll offices from all PDFs in settings.DOWNLOADS_DIR and "
        "export them to JSON without saving to the database."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--country",
            type=str,
            default=None,
            help="Default country to apply when missing in the PDF rows.",
        )
        # No DB writes; dry-run is implicit
        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Process at most N PDFs (by name order).",
        )
        parser.add_argument(
            "--out",
            type=str,
            default=None,
            help="Output JSON filepath (default: DOWNLOADS_DIR/poll_offices.json)",
        )
        parser.add_argument(
            "--country-code",
            type=str,
            default=None,
            help="Optional country code to use in identifiers (e.g., CM).",
        )

    def handle(self, *args, **options):
        logger = self._get_logger()
        downloads: Path = Path(getattr(settings, "DOWNLOADS_DIR", Path.cwd()))
        if not downloads.exists():
            self.stdout.write(self.style.ERROR(f"DOWNLOADS_DIR not found: {downloads}"))
            logger.error("DOWNLOADS_DIR not found: %s", downloads)
            sys.exit(1)

        # No DB writes; dry-run behavior is enforced
        default_country: Optional[str] = options.get("country")
        limit: Optional[int] = options.get("limit")
        out_path_opt: Optional[str] = options.get("out")
        country_code_opt: Optional[str] = options.get("country_code")
        logger.info("Start extract_poll_offices | downloads=%s | limit=%s | country=%s | country_code=%s", downloads, limit, default_country, country_code_opt)

        pdf_files = sorted([p for p in downloads.glob("*.pdf") if p.is_file()])
        if limit is not None:
            pdf_files = pdf_files[:limit]

        if not pdf_files:
            self.stdout.write(self.style.WARNING(f"No PDFs found in {downloads}"))
            logger.warning("No PDFs found in %s", downloads)
            return

        self.stdout.write(self.style.NOTICE(f"Scanning {len(pdf_files)} PDF(s) in {downloads}..."))
        logger.info("Scanning %d PDF(s)", len(pdf_files))

        skipped = 0
        collected: List[Tuple[PollOffice, Optional[int]]] = []

        for pdf_path in pdf_files:
            self.stdout.write(f"→ {pdf_path.name}")
            logger.info("Processing PDF: %s", pdf_path)
            try:
                page_no = 0
                for header_info, table in iter_pdf_tables(pdf_path):
                    page_no += 1
                    logger.debug("Page %d header: region=%s, city=%s", page_no, header_info.get("region"), header_info.get("city"))
                    if not table:
                        continue
                    # Determine header row: first row with >= 2 non-empty cells
                    header_idx = None
                    for i, row in enumerate(table):
                        non_empty = [c for c in row if c]
                        if len(non_empty) >= 2:
                            header_idx = i
                            break
                    if header_idx is None:
                        logger.debug("Page %d: No header row detected", page_no)
                        continue
                    headers = table[header_idx]
                    header_map = map_headers(headers)
                    logger.debug("Page %d header row: %s", page_no, headers)
                    logger.debug("Page %d header map: %s", page_no, header_map)
                    # Enforce known column positions when available: name -> 2nd col, voters_count -> 4th col
                    if len(headers) >= 2 and header_map.get(1) != "name":
                        logger.debug("Forcing column 2 as name per spec")
                        header_map[1] = "name"
                    if len(headers) >= 4 and header_map.get(3) != "voters_count":
                        logger.debug("Forcing column 4 as voters_count per spec")
                        header_map[3] = "voters_count"
                    # If voters_count not in headers, try to infer column index from data rows
                    voters_idx: Optional[int] = None
                    try:
                        # Prefer explicit header mapping
                        for idx, field in header_map.items():
                            if field == "voters_count":
                                voters_idx = idx
                                break
                        if voters_idx is None:
                            voters_idx = detect_voters_column(table[header_idx + 1 :])
                    except Exception:
                        voters_idx = None
                    logger.debug("Page %d voters_count column index: %s", page_no, str(voters_idx))

                    # Parse all subsequent rows
                    for row in table[header_idx + 1 :]:
                        pr = parse_row(row, header_map)
                        # If still missing, try to pull from inferred voters column
                        if pr.voters_count is None and voters_idx is not None and voters_idx < len(row):
                            pr.voters_count = parse_int_loose(clean_cell(row[voters_idx]))
                        # Last resort: take the largest integer in the row (>= 50 preferred)
                        if pr.voters_count is None:
                            numbers = [parse_int_loose(clean_cell(c)) for c in row]
                            numbers = [n for n in numbers if n is not None]
                            preferred = [n for n in numbers if n >= 50]
                            if preferred:
                                pr.voters_count = max(preferred)
                            elif numbers:
                                pr.voters_count = max(numbers)
                        logger.debug("Row raw: %s", row)
                        logger.debug("Parsed row -> name=%s, voters_count=%s, region=%s, city=%s", pr.name, pr.voters_count, pr.region, pr.city)
                        # Must have at least a name to be considered
                        if not pr.name:
                            skipped += 1
                            logger.debug("Skipping row due to missing name")
                            continue
                        # Title-case region and city per requirement
                        def title_or_none(v: Optional[str]) -> Optional[str]:
                            return v.title() if v else None

                        # Resolve region/city from row or page header
                        region_val = title_or_none(pr.region) or title_or_none(header_info.get("region")) or None
                        city_val = title_or_none(pr.city) or title_or_none(header_info.get("city")) or None

                        # Compose identifier: {country_code}-{region}-{city}-{name}
                        country_val = pr.country or default_country or ""
                        ccode = derive_country_code(country_val, country_code_opt)
                        comp_identifier = compose_identifier(ccode, region_val, city_val, pr.name)
                        logger.debug("Composed identifier: %s (cc=%s, region=%s, city=%s, name=%s)", comp_identifier, ccode, region_val, city_val, pr.name)

                        po = PollOffice(
                            name=pr.name,
                            identifier=comp_identifier,
                            country=pr.country or default_country or "",
                            state=pr.state or None,
                            region=region_val,
                            city=city_val,
                            county=pr.county or None,
                            district=pr.district or None,
                        )
                        collected.append((po, pr.voters_count))
            except Exception as exc:
                self.stdout.write(self.style.WARNING(f"  ! Failed to parse {pdf_path.name}: {exc}"))
                logger.exception("Failed to parse %s", pdf_path)
                continue

        if not collected:
            self.stdout.write(self.style.WARNING("No poll offices parsed from PDFs."))
            logger.warning("No poll offices parsed from PDFs")
            return

        # Compute duplicates before deduplication
        dup_map: Dict[str, List[Tuple[PollOffice, Optional[int]]]] = {}
        for po, voters_count in collected:
            key = (po.identifier or "").strip()
            if not key:
                continue
            dup_map.setdefault(key, []).append((po, voters_count))
        duplicates_only = {k: v for k, v in dup_map.items() if len(v) > 1}

        # Deduplicate by identifier, prefer first occurrence
        dedup: Dict[str, Tuple[PollOffice, Optional[int]]] = {}
        for po, voters_count in collected:
            key = po.identifier.strip()
            if not key:
                continue
            if key not in dedup:
                dedup[key] = (po, voters_count)

        self.stdout.write(self.style.NOTICE(f"Parsed {len(collected)} rows; {len(dedup)} unique by identifier."))
        logger.info("Parsed %d rows; %d unique identifiers", len(collected), len(dedup))

        # Always write JSON export
        out_path = Path(out_path_opt) if out_path_opt else (downloads / "poll_offices.json")
        try:
            payload = []
            for po, voters_count in sorted(dedup.values(), key=lambda x: (x[0].identifier or "")):
                payload.append(
                    {
                        "identifier": po.identifier,
                        "name": po.name,
                        "country": po.country or "",
                        "state": po.state,
                        "region": po.region,
                        "city": po.city,
                        "county": po.county,
                        "district": po.district,
                        "voters_count": voters_count,
                    }
                )
            out_path.parent.mkdir(parents=True, exist_ok=True)
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            self.stdout.write(self.style.SUCCESS(f"Exported {len(payload)} poll offices to {out_path}"))
            logger.info("Exported %d poll offices to %s", len(payload), out_path)
        except Exception as exc:
            self.stdout.write(self.style.WARNING(f"Failed to write JSON export to {out_path}: {exc}"))
            logger.exception("Failed to write JSON export to %s", out_path)

        # Preview a few lines for convenience
        preview = list(dedup.values())[:10]
        for po, voters_count in preview:
            self.stdout.write(
                f" - [{po.identifier}] {po.name} | {po.city or ''} {po.region or ''} {po.country or ''} | voters: {voters_count if voters_count is not None else 'N/A'}".strip()
            )
        self.stdout.write(self.style.SUCCESS(
            f"Done. Exported {len(dedup)} poll offices to JSON. Skipped rows: {skipped}."
        ))
        logger.info("Done. Exported %d poll offices. Skipped rows: %d", len(dedup), skipped)

        # Report duplicates
        if duplicates_only:
            self.stdout.write(self.style.WARNING(f"Duplicate identifiers found: {len(duplicates_only)}"))
            logger.warning("Duplicate identifiers found: %d", len(duplicates_only))
            for identifier, entries in duplicates_only.items():
                self.stdout.write(f"  {identifier}: {len(entries)} rows")
                logger.warning("Duplicate: %s has %d rows", identifier, len(entries))
                for po, voters_count in entries:
                    line = (
                        f"     - name={po.name} | region={po.region or ''} | city={po.city or ''} | "
                        f"country={po.country or ''} | voters_count={voters_count if voters_count is not None else 'N/A'}"
                    )
                    self.stdout.write(line)
                    logger.warning(line)
        else:
            self.stdout.write(self.style.SUCCESS("No duplicate identifiers detected."))
            logger.info("No duplicate identifiers detected")

    def _get_logger(self) -> logging.Logger:
        """Create or return a dedicated logger writing to logs/extract_poll_offices.log"""
        logger = logging.getLogger("core.extract_poll_offices")
        if getattr(logger, "_inited", False):
            return logger
        logger.setLevel(logging.DEBUG)
        try:
            logs_dir = getattr(settings, "LOGS_DIR", Path.cwd() / "logs")
            Path(logs_dir).mkdir(parents=True, exist_ok=True)
            handler = RotatingFileHandler(str(Path(logs_dir) / "extract_poll_offices.log"), maxBytes=5 * 1024 * 1024, backupCount=2)
            handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(message)s")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger._inited = True  # type: ignore[attr-defined]
        except Exception:
            # Fallback to console if file handler fails
            stream = logging.StreamHandler()
            stream.setLevel(logging.DEBUG)
            formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(message)s")
            stream.setFormatter(formatter)
            logger.addHandler(stream)
            logger._inited = True  # type: ignore[attr-defined]
        return logger
