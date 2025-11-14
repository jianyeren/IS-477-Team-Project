#!/usr/bin/env python3
import argparse, io, json, zipfile, datetime as dt
from pathlib import Path
import numpy as np, pandas as pd, matplotlib.pyplot as plt
import requests

FARA_URL = "https://ers.usda.gov/sites/default/files/_laserfiche/DataFiles/80591/2019%20Food%20Access%20Research%20Atlas%20Data.zip"
PLACES_URL = ("https://data.cdc.gov/resource/swc5-untb.csv"
              "?$select=locationid,measureid,datavalue"
              "&$where=datavaluetypeid='CrudePrev'%20AND%20measureid%20in%20('OBESITY','DIABETES')")

def get(u): r=requests.get(u,timeout=240); r.raise_for_status(); return r.content
def zpad5(s): return s.astype(str).str.replace(r"\.0$","",regex=True).str.zfill(5)
def num(x): return pd.to_numeric(x, errors="coerce")

def load_fara(u):
    z=zipfile.ZipFile(io.BytesIO(get(u)))
    names=[n for n in z.namelist() if n.lower().endswith(".csv")]
    n=next((k for k in names if "tract" in k.lower()), names[0])
    df=pd.read_csv(z.open(n), dtype=str)
    tract=next(c for c in ["CensusTract","GEOID","TractFIPS","TractId","tract_fips"] if c in df)
    pop =next(c for c in ["Pop2010","TOTPOP","Population","pop"] if c in df)
    ind =next(c for c in ["LILATracts_1And10","LA1and10","lalowinc10","low_access_pct","fa_low_access_pct"] if c in df)
    d=pd.DataFrame({"fips":zpad5(df[tract].str[:5]),"pop":num(df[pop]).clip(lower=0),"fa":num(df[ind])})
    g=d.groupby("fips",as_index=False).apply(lambda s: pd.Series({"pop":s["pop"].sum(min_count=1),
                                                                  "fa_indicator": np.average(s["fa"], weights=np.where(s["pop"].isna(),0,s["pop"])) if s["pop"].fillna(0).sum()>0 else np.nan}))
    return g

def load_places(u):
    df=pd.read_csv(io.BytesIO(get(u)), dtype=str)
    df["locationid"]=zpad5(df["locationid"]); df["datavalue"]=num(df["datavalue"]); df["measureid"]=df["measureid"].str.upper()
    w=df.pivot_table(index="locationid", columns="measureid", values="datavalue", aggfunc="mean").reset_index().rename(columns={"locationid":"fips","OBESITY":"obesity","DIABETES":"diabetes"})
    if "obesity" not in w: w["obesity"]=np.nan
    if "diabetes" not in w: w["diabetes"]=np.nan
    return w

def filter_states(df, states):
    if not states: return df
    m=df["fips"].str[:2].isin(states); return df[m]

def dq(df, out):
    miss=df.isna().mean().sort_values(ascending=False).head(10).to_frame("missing_ratio")
    lines=[ "# Data Quality Summary",
            f"- rows: {len(df):,}",
            f"- columns: {len(df.columns)}",
            "","## Missingness top 10", miss.to_markdown(), "",
            "## Quick ranges" ]
    for c in ["fa_indicator","obesity","diabetes"]:
        if c in df: 
            v=pd.to_numeric(df[c], errors="coerce")
            if v.notna().any(): lines.append(f"- {c}: min={np.nanmin(v):.3f}, max={np.nanmax(v):.3f}")
    Path(out,"dq_summary.md").write_text("\n".join(lines), encoding="utf-8")
    Path(out,"missing_report.md").write_text(df.isna().sum().to_frame("missing").assign(ratio=lambda x:x["missing"]/len(df)).to_markdown(), encoding="utf-8")

def clean(df):
    x=df.copy()
    x["fips"]=zpad5(x["fips"])
    for c in ["fa_indicator","obesity","diabetes","pop"]:
        if c in x: x[c]=num(x[c])
    if (x["fips"].str.fullmatch(r"\d{5}")==False).any(): raise ValueError("invalid FIPS")
    if "pop" in x and (x["pop"]<0).any(): raise ValueError("negative population")
    return x

def viz(df, out, x="fa_indicator", y="obesity"):
    if x not in df or y not in df: return
    p=Path(out,"sample_scatter.png")
    plt.figure(figsize=(6.2,4.2), dpi=140); plt.scatter(df[x],df[y],alpha=0.65,edgecolor="white",linewidth=0.4)
    plt.xlabel(x.replace("_"," ")); plt.ylabel(y.replace("_"," ")); plt.title("Food access vs adult obesity pilot")
    plt.grid(True,alpha=0.25); plt.tight_layout(); plt.savefig(p); plt.close()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--fara-url",default=FARA_URL); ap.add_argument("--places-url",default=PLACES_URL)
    ap.add_argument("--states",default="IL"); ap.add_argument("--outdir",default="outputs_pilot"); ap.add_argument("--sample",type=int,default=0)
    a=ap.parse_args()
    out=Path(a.outdir); out.mkdir(parents=True, exist_ok=True); logs=out/"logs"; logs.mkdir(exist_ok=True)
    prov=logs/"provenance.jsonl"
    prov.write_text(json.dumps({"source":"USDA ERS FARA","url":a.fara_url,"accessed_at":dt.datetime.utcnow().isoformat()+"Z"})+"\n",encoding="utf-8")
    prov.open("a",encoding="utf-8").write(json.dumps({"source":"CDC PLACES","url":a.places_url,"accessed_at":dt.datetime.utcnow().isoformat()+"Z"})+"\n")

    fara=load_fara(a.fara_url)
    places=load_places(a.places_url)

    s=[s.strip().upper() for s in a.states.split(",") if s.strip()]
    map2={"AL":"01","AK":"02","AZ":"04","AR":"05","CA":"06","CO":"08","CT":"09","DE":"10","DC":"11","FL":"12","GA":"13","HI":"15","ID":"16","IL":"17","IN":"18","IA":"19","KS":"20","KY":"21","LA":"22","ME":"23","MD":"24","MA":"25","MI":"26","MN":"27","MS":"28","MO":"29","MT":"30","NE":"31","NV":"32","NH":"33","NJ":"34","NM":"35","NY":"36","NC":"37","ND":"38","OH":"39","OK":"40","OR":"41","PA":"42","RI":"44","SC":"45","SD":"46","TN":"47","TX":"48","UT":"49","VT":"50","VA":"51","WA":"53","WV":"54","WI":"55","WY":"56"}
    s=[map2.get(x, x.zfill(2) if x.isdigit() else x) for x in s]

    fara=fara.rename(columns={"fips":"fips"})
    places=places.rename(columns={"fips":"fips"})
    fara=filter_states(fara, s); places=filter_states(places, s)
    joined=fara.merge(places, on="fips", how="left", validate="one_to_one")
    if a.sample>0 and len(joined)>a.sample: joined=joined.sample(a.sample, random_state=42).sort_values("fips")

    dq(joined, out)
    cleaned=clean(joined)
    try:
        import pyarrow as pa, pyarrow.parquet as pq
        pq.write_table(pa.Table.from_pandas(cleaned), out/"final_join.parquet")
    except Exception:
        cleaned.to_csv(out/"final_join.csv", index=False)
    viz(cleaned, out)

if __name__=="__main__":
    main()
