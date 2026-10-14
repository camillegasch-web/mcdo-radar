#!/usr/bin/env python3
"""Collecte quotidienne de titres publics via flux Google Actualités RSS. Sans clé API."""
import datetime as dt
import email.utils
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "data"
ROOT.mkdir(parents=True, exist_ok=True)
QUERIES = {
 "France": ['McDonald’s France actualité', 'McDonald’s France restaurants campagne', 'McDonald’s France communication stratégie'],
 "Local": ['McDonald’s ouverture restaurant France', 'McDonald’s restaurant franchisé région', 'McDonald’s recrutement restaurant ville France'],
 "RH McDo": ['McDonald’s France recrutement emploi', 'McDonald’s France marque employeur équipiers', 'McDonald’s alternance formation manager France', 'McDonald’s conditions de travail salariés'],
 "Concurrence": ['Burger King France recrutement campagne', 'KFC France restaurant RH', 'Quick France recrutement', 'Five Guys France emploi marque employeur'],
 "Inspiration RH": ['campagne marque employeur 2026 France', 'campagne recrutement originale entreprise', 'communication recrutement TikTok marque employeur', 'RH tendances recrutement étude France', 'expérience candidat recrutement entreprise', 'engagement collaborateurs QVCT', 'employee advocacy marque employeur LinkedIn', 'campagne communication RH employeur', 'insertion formation alternance recrutement'],
 "Signaux sensibles": ['McDonald’s France controverse conditions de travail', 'McDonald’s France grève justice salariés', 'Burger King KFC Quick polémique travail France']
}
def parsedate(s):
 try:
  d=email.utils.parsedate_to_datetime(s)
  return d.astimezone(dt.timezone.utc).isoformat() if d.tzinfo else d.replace(tzinfo=dt.timezone.utc).isoformat()
 except Exception:
  return dt.datetime.now(dt.timezone.utc).isoformat()
def feed(q):
 params=urllib.parse.urlencode({"q":q,"hl":"fr","gl":"FR","ceid":"FR:fr"})
 req=urllib.request.Request("https://news.google.com/rss/search?"+params,headers={"User-Agent":"Mozilla/5.0 (compatible; McDoRadar/1.0)"})
 with urllib.request.urlopen(req,timeout=20) as response:
  raw=response.read(1500000)
 return ET.fromstring(raw).findall("./channel/item")
def main():
 path=ROOT/"news.json"
 try: old=json.loads(path.read_text(encoding="utf-8"))
 except Exception: old={"articles":[]}
 prev={x.get("url"):x for x in old.get("articles",[]) if x.get("url")}
 success=0
 errors=[]
 found=0
 for section, queries in QUERIES.items():
  for q in queries:
   try:
    items=feed(q)
    success+=1
    for el in items[:18]:
     link=(el.findtext("link") or "").strip()
     if not link: continue
     title=(el.findtext("title") or "").strip()
     source=el.findtext("source") or "Google Actualités"
     if not title or link in prev: continue
     prev[link]={"title":title,"url":link,"source":source,"date":parsedate(el.findtext("pubDate") or ""),"section":section,"query":q}
     found+=1
   except Exception as e: errors.append(q+": "+str(e)[:130])
   time.sleep(.12)
 if success==0:
  raise RuntimeError("Aucun flux RSS accessible : anciennes données conservées. "+("; ".join(errors[:3])))
 cutoff=dt.datetime.now(dt.timezone.utc)-dt.timedelta(days=90)
 def recent(a):
  try:return dt.datetime.fromisoformat(a["date"].replace("Z","+00:00"))>=cutoff
  except: return False
 articles=sorted(filter(recent,prev.values()),key=lambda x:x["date"],reverse=True)[:750]
 now=dt.datetime.now(dt.timezone.utc).isoformat()
 payload={"updated_at":now,"sources_ok":success,"sources_total":sum(map(len,QUERIES.values())),"new_count":found,"articles":articles}
 path.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")
 (ROOT/"news.js").write_text("window.RADAR_DATA = "+json.dumps(payload,ensure_ascii=False)+";",encoding="utf-8")
 fresh=[a for a in articles if (dt.datetime.now(dt.timezone.utc)-dt.datetime.fromisoformat(a["date"].replace("Z","+00:00"))).total_seconds()<36*3600]
 (ROOT/"brief.json").write_text(json.dumps({"updated_at":now,"sections":{k:[a for a in fresh if a["section"]==k][:5] for k in QUERIES}},ensure_ascii=False,indent=2),encoding="utf-8")
 print(f"Collecte réussie : {success} flux, {found} nouveaux articles, {len(articles)} conservés.")
 if errors: print("Flux indisponibles (couverture partielle):",len(errors))
if __name__=="__main__": main()
