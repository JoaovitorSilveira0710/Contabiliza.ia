import re
from datetime import datetime
from typing import Dict, Optional

def _extract_text_from_pdf(path: str) -> str:
    try:
        from pdfminer.high_level import extract_text
        return extract_text(path) or ''
    except Exception:
        return ''

def _extract_text_from_image(path: str) -> str:
    # Try OCR if pytesseract is available; otherwise return empty
    try:
        import pytesseract  # type: ignore
        from PIL import Image  # type: ignore
        img = Image.open(path)
        return pytesseract.image_to_string(img) or ''
    except Exception:
        return ''

def _guess_method(text: str) -> Optional[str]:
    t = text.lower()
    if 'pix' in t:
        return 'pix'
    if 'ted' in t or 'transferência' in t or 'transferencia' in t:
        return 'bank_transfer'
    if 'dinheiro' in t or 'cash' in t:
        return 'money'
    if 'débito' in t or 'debito' in t:
        return 'debit_card'
    if 'crédito' in t or 'credito' in t:
        return 'credit_card'
    if 'boleto' in t:
        return 'boleto'
    return None

def _extract_amount(text: str) -> Optional[float]:
    # Capture amounts like R$ 1.234,56 or 1234,56
    # Replace dots in thousand separators and commas in decimals for parsing
    candidates = []
    # Look for patterns with optional currency symbol and thousand separators
    for m in re.finditer(r'(?:R\$\s*)?([0-9]{1,3}(?:\.[0-9]{3})*,[0-9]{2}|[0-9]+,[0-9]{2})', text):
        raw = m.group(1)
        try:
            val = float(raw.replace('.', '').replace(',', '.'))
            candidates.append(val)
        except Exception:
            continue
    if not candidates:
        # Fallback: dot decimal
        for m in re.finditer(r'(?:R\$\s*)?([0-9]+\.[0-9]{2})', text):
            try:
                candidates.append(float(m.group(1)))
            except Exception:
                continue
    if candidates:
        # Choose the largest sensible amount
        return max(candidates)
    return None

def _extract_date(text: str) -> Optional[str]:
    # Try dd/mm/yyyy, dd-mm-yyyy, yyyy-mm-dd
    patterns = [
        (r'(\d{2})/(\d{2})/(\d{4})', '%d/%m/%Y'),
        (r'(\d{2})-(\d{2})-(\d{4})', '%d-%m-%Y'),
        (r'(\d{4})-(\d{2})-(\d{2})', '%Y-%m-%d'),
    ]
    for pat, fmt in patterns:
        m = re.search(pat, text)
        if m:
            s = m.group(0)
            try:
                d = datetime.strptime(s, fmt).date()
                return d.isoformat()
            except Exception:
                continue
    return None

def _extract_txid(text: str) -> Optional[str]:
    m = re.search(r'txid\s*[:\-]?\s*([A-Za-z0-9\-]{6,})', text, flags=re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return None

def analyze_receipt(file_path: str, content_type: Optional[str] = None) -> Dict[str, Optional[str]]:
    """
    Analyze a receipt file (PDF or image) to infer payment data.
    Returns dict with possible keys: method, amount, payment_date, txid, raw_excerpt.
    """
    text = ''
    ct = (content_type or '').lower()
    try:
        if file_path.lower().endswith('.pdf') or 'pdf' in ct:
            text = _extract_text_from_pdf(file_path)
        else:
            text = _extract_text_from_image(file_path)
    except Exception:
        text = ''

    if not text:
        return {
            'method': None,
            'amount': None,
            'payment_date': None,
            'txid': None,
            'raw_excerpt': None
        }

    method = _guess_method(text)
    amount = _extract_amount(text)
    pay_date = _extract_date(text)
    txid = _extract_txid(text)

    # Compose a small excerpt for notes (limit size)
    excerpt = text.strip()
    excerpt = re.sub(r'\s+', ' ', excerpt)
    if len(excerpt) > 600:
        excerpt = excerpt[:600] + '...'

    return {
        'method': method,
        'amount': str(amount) if amount is not None else None,
        'payment_date': pay_date,
        'txid': txid,
        'raw_excerpt': excerpt,
    }
