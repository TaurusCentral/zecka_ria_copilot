from __future__ import annotations
import io, re, requests, pandas as pd
from datetime import date, timedelta

AMFI_LATEST = "https://www.amfiindia.com/spages/NAVAll.txt"
AMFI_HISTORY = "https://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx"

def fetch_latest_scheme_master(timeout=30) -> pd.DataFrame:
    text = requests.get(AMFI_LATEST, timeout=timeout).text
    rows=[]
    for line in text.splitlines():
        parts=line.split(';')
        if len(parts) >= 6 and parts[0].isdigit():
            rows.append({"scheme_code":parts[0],"isin_growth":parts[1],"isin_reinvestment":parts[2],"scheme_name":parts[3],"nav":parts[4],"date":parts[5]})
    return pd.DataFrame(rows)

def direct_growth_universe(df: pd.DataFrame) -> pd.DataFrame:
    m = df["scheme_name"].str.contains("direct", case=False, na=False) & df["scheme_name"].str.contains("growth", case=False, na=False)
    return df[m].copy()

def fetch_history_chunks(scheme_code: str, start: date, end: date, timeout=30) -> pd.DataFrame:
    # AMFI's public NAV interface documents a maximum 90-day history window. This helper respects that bound.
    # Endpoint response formats can change, so parsing is deliberately defensive.
    chunks=[]
    cur=start
    while cur <= end:
        stop=min(end, cur+timedelta(days=89))
        params={"frmdt":cur.strftime("%d-%b-%Y"),"todt":stop.strftime("%d-%b-%Y")}
        txt=requests.get(AMFI_HISTORY,params=params,timeout=timeout).text
        for line in txt.splitlines():
            parts=line.split(';')
            if len(parts)>=5 and parts[0].strip()==str(scheme_code):
                try: chunks.append({"scheme_code":scheme_code,"date":pd.to_datetime(parts[-1],dayfirst=True),"nav":float(parts[-2])})
                except Exception: pass
        cur=stop+timedelta(days=1)
    return pd.DataFrame(chunks).drop_duplicates("date").sort_values("date") if chunks else pd.DataFrame(columns=["scheme_code","date","nav"])
