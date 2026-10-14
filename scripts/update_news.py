#!/usr/bin/env python3
"""McDo Radar : collecte quotidienne multi-sources (articles publics, RSS / Google Actualités).
Les liens vers les articles et les dates sont toujours conservés. Pas de scraping LinkedIn privé.
"""
import concurrent.futures as cf
import datetime as dt
import email.utils
import html
import json
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs" / "data"
ROOT.mkdir(parents=True, exist_ok=True)
NOW = dt.datetime.now(dt.timezone.utc)
MAX_DAYS = 180
MAX_ITEMS = 2300

# Sources prioritaires, consultées par recherches Google Actualités ciblées sur chaque domaine.
CREATIVE_MEDIA = [
    ("Creapills", "creapills.com"),
    ("L'ADN", "ladn.eu"),
    ("Dans Ta Pub", "danstapub.com"),
    ("Stratégies", "strategies.fr"),
    ("CB News", "cbnews.fr"),
    ("J'ai un pote dans la com", "jai-un-pote-dans-la.com"),
    ("La Réclame", "lareclame.fr"),
    ("INfluencia", "influencia.net"),
    ("Marketing Magazine", "e-marketing.fr"),
    ("Les Gens d'Internet", "lesgensdinternet.com"),
    ("Blog du Modérateur", "blogdumoderateur.com"),
    ("Siècle Digital", "siecledigital.fr"),
    ("The Drum", "thedrum.com"),
    ("Adweek", "adweek.com"),
    ("Campaign", "campaignlive.co.uk"),
]
RH_MEDIA = [
    ("HelloWorkplace / HelloWork", "helloworkplace.fr"),
    ("Culture RH", "culture-rh.com"),
    ("Parlons RH", "parlonsrh.com"),
    ("myRHline", "myrhline.com"),
    ("Focus RH", "focusrh.com"),
    ("RH Matin", "rhmatin.com"),
    ("Welcome to the Jungle", "welcometothejungle.com"),
    ("ANDRH", "andrh.fr"),
    ("Apec", "apec.fr"),
    ("Liaisons Sociales", "liaisons-sociales.fr"),
    ("Courrier Cadres", "courriercadres.com"),
]
DIRECT_FEEDS = [
    ("Creapills", "https://creapills.com/feed/", "Campagnes créatives"),
    ("Dans Ta Pub", "https://www.danstapub.com/feed/", "Campagnes créatives"),
    ("L'ADN", "https://www.ladn.eu/feed/", "Campagnes créatives"),
    ("La Réclame", "https://lareclame.fr/feed", "Campagnes créatives"),
    ("HelloWorkplace / HelloWork", "https://www.helloworkplace.fr/feed/", "Inspiration RH"),
    ("Culture RH", "https://culture-rh.com/feed/", "Inspiration RH"),
    ("Parlons RH", "https://www.parlonsrh.com/feed/", "Inspiration RH"),
    ("myRHline", "https://myrhline.com/feed/", "Inspiration RH"),
    ("Blog du Modérateur", "https://www.blogdumoderateur.com/feed/", "Campagnes créatives"),
]
BASE_QUERIES = {
    "France": [
        "McDonald's France actualité", "McDonald's France stratégie communication",
        "McDonald's France campagne publicité", "McDonald's France business restaurant",
    ],
    "Local": [
        "McDonald's ouverture restaurant France", "McDonald's franchisé restaurant région",
        "McDonald's recrutement restaurant ville France", "McDonald's restaurant équipes initiative locale",
    ],
    "RH McDo": [
        "McDonald's France recrutement emploi", "McDonald's France marque employeur équipiers",
        "McDonald's manager carrière formation alternance", "McDonald's salariés conditions de travail France",
        "McDonald's campagnes recrutement métiers France", "McDonald's apprentissage insertion alternance",
    ],
    "Concurrence": [
        "Burger King France campagne recrutement", "Burger King France publicité activation",
        "KFC France recrutement marque employeur", "KFC France publicité campagne",
        "Quick France restaurant recrutement", "Quick France campagne publicité",
        "Five Guys France emploi communication", "restauration rapide marque employeur campagne",
    ],
    "Inspiration RH": [
        "campagne recrutement originale entreprise marque employeur",
        "campagne communication RH métiers talents candidats",
        "campagne marque employeur film employés publicité",
        "expérience candidat recrutement parcours innovation",
        "salariés ambassadeurs employee advocacy marque employeur",
        "attractivité métiers recrutement jeunes TikTok",
        "étude baromètre employeur RH jeunes travail",
        "transparence salaire formation évolution carrière employeur",
        "qualité de vie au travail management engagement collaborateurs",
        "campagne RH creative recrutement affichage réseaux sociaux",
    ],
    "Campagnes créatives": [
        "campagne publicité créative France marque activation",
        "opération marketing créative insolite campagne 2026",
        "meilleures campagnes de publicité 2026 France",
        "campagne activation guerrilla marketing affichage",
        "publicité drôle décalée créative idée marque",
        "campagne créative employeur recrutement social media",
        "influence TikTok campagne marque nouveau format",
        "campagne de communication publicitaire McDonald's Burger King",
    ],
    "Signaux sensibles": [
        "McDonald's France polémique conditions de travail",
        "McDonald's France grève justice salariés",
        "McDonald's France boycott controverse",
        "Burger King KFC Quick polémique travail France",
    ],
}
# Publications LinkedIn publiques indexées par Google Actualités : couverture non exhaustive.
LINKEDIN_QUERIES = [
    ("Campagnes créatives", "site:linkedin.com/posts/danstapub campagne publicité"),
    ("Campagnes créatives", "site:linkedin.com/posts/gabriel-teisson créativité publicité"),
    ("Inspiration RH", "site:linkedin.com/posts marque employeur campagne recrutement"),
    ("Inspiration RH", "site:linkedin.com/posts communication RH expérience candidat"),
]
def clean(s):
    return html.unescape(re.sub("<[^>]+>", " ", s or "")).strip()
def parse_date(s):
    try:
        v = email.utils.parsedate_to_datetime(s)
        return (v if v.tzinfo else v.replace(tzinfo=dt.timezone.utc)).astimezone(dt.timezone.utc).isoformat()
    except Exception:
        try: return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(dt.timezone.utc).isoformat()
        except Exception: return NOW.isoformat()
def get(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; McDoRadar/2.0; public RSS editorial watch)",
        "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*"
    })
    with urllib.request.urlopen(req, timeout=16) as res:
        return res.read(1800000)
def search_feed(query):
    p=urllib.parse.urlencode({"q":query, "hl":"fr", "gl":"FR", "ceid":"FR:fr"})
    return get("https://news.google.com/rss/search?"+p)
def parse_rss(raw, section, query, preferred_source=None, direct=False):
    root = ET.fromstring(raw)
    nodes = root.findall("./channel/item")
    if not nodes:
        nodes = root.findall(".//{http://www.w3.org/2005/Atom}entry")
    out=[]
    for node in nodes[:24]:
        title = clean(node.findtext("title") or node.findtext("{http://www.w3.org/2005/Atom}title"))
        link = (node.findtext("link") or "").strip()
        if not link:
            x = node.find("{http://www.w3.org/2005/Atom}link")
            link = (x.get("href") or "").strip() if x is not None else ""
        if not title or not link.startswith(("http://","https://")): continue
        link = re.sub(r"[?&]oc=5$", "", link)
        source_node = node.find("source")
        source = (preferred_source if direct else (
            clean(source_node.text) if source_node is not None else preferred_source
        )) or urllib.parse.urlparse(link).netloc.replace("www.", "")
        date_text = (node.findtext("pubDate") or
          node.findtext("{http://www.w3.org/2005/Atom}published") or
          node.findtext("{http://www.w3.org/2005/Atom}updated") or "")
        date = parse_date(date_text)
        if not date_text: continue  # ne pas inventer de date de publication
        tags = [section]
        hay = title.lower()
        if section == "Campagnes créatives" and re.search(r"recrut|marque employeur|candidat|alternance|collaborat",hay):
            tags.append("Inspiration RH")
        if section == "Inspiration RH" and re.search(r"campagne|publicit|activation|affichag|film |vidéo|tiktok|créati",hay):
            tags.append("Campagnes créatives")
        out.append({"title":title,"url":link,"source":source,"date":date,
                    "section":section,"sections":tags,"query":query,
                    "channel":("RSS direct" if direct else "Google Actualités")})
    return out
def key(article):
    # Regrouper URL identiques. Les libellés de source restent préservés.
    return re.sub(r"/$", "", article["url"].split("?")[0]).lower()
def work(job):
    section, q, source, direct, url = job
    try:
        raw = get(url) if direct else search_feed(q)
        found=parse_rss(raw, section, q, preferred_source=source, direct=direct)
        return job, found, None
    except Exception as e:
        return job, [], str(e)[:170]
def jobs():
    results=[]
    for cat, queries in BASE_QUERIES.items():
        results += [(cat,q,None,False,None) for q in queries]
    for source,domain in CREATIVE_MEDIA:
        results.append(("Campagnes créatives",f"site:{domain} (campagne OR publicité OR marketing OR créativit\u00e9)",source,False,None))
    for source,domain in RH_MEDIA:
        results.append(("Inspiration RH",f"site:{domain} (recrutement OR marque employeur OR RH OR carrière)",source,False,None))
    results += [(cat,q,"LinkedIn",False,None) for cat,q in LINKEDIN_QUERIES]
    results += [(cat,f"Flux {name}",name,True,url) for name,url,cat in DIRECT_FEEDS]
    return results
def main():
    path=ROOT/"news.json"
    try: old=json.loads(path.read_text(encoding="utf-8"))
    except Exception: old={"articles":[]}
    merged={}
    for a in old.get("articles",[]):
        if not a.get("url") or not a.get("date"): continue
        a["sections"]=list(dict.fromkeys(a.get("sections") or [a.get("section","France")]))
        merged[key(a)]=a
    previous=set(merged)
    full=jobs()
    successes=0; errors=[]; stats={}; domains=set()
    with cf.ThreadPoolExecutor(max_workers=6) as pool:
        for j, entries, err in pool.map(work,full):
            section, query, source, direct, url=j
            if err:
                errors.append({"source":source or query,"error":err})
                continue
            successes+=1
            stats[section]=stats.get(section,0)+1
            for a in entries:
                k=key(a)
                if k in merged:
                    old_item=merged[k]
                    old_item["sections"]=list(dict.fromkeys((old_item.get("sections") or [old_item["section"]])+a["sections"]))
                    # Préférer l'URL et le média de l'éditeur en cas de flux direct.
                    if direct:
                        old_item["url"]=a["url"]
                        old_item["source"]=a["source"]
                        old_item["channel"]=a["channel"]
                else: merged[k]=a
                domains.add(a["source"])
    if successes==0:
        raise RuntimeError("Aucun flux disponible. Historique conservé. Erreurs: "+str(errors[:3]))
    cutoff=NOW-dt.timedelta(days=MAX_DAYS)
    articles=[]
    for a in merged.values():
        try:
            when=dt.datetime.fromisoformat(a["date"].replace("Z","+00:00"))
            if when.tzinfo and cutoff <= when <= NOW+dt.timedelta(hours=6):
                articles.append(a)
        except (ValueError,TypeError): pass
    articles.sort(key=lambda x:x["date"],reverse=True)
    articles=articles[:MAX_ITEMS]
    new_count=sum(key(a) not in previous for a in articles)
    info={"updated_at":NOW.isoformat(), "sources_ok":successes,
          "sources_total":len(full), "source_names":sorted(set(a["source"] for a in articles)),
          "source_count":len(set(a["source"] for a in articles)),
          "new_count":new_count, "source_errors":errors[:18],
          "articles":articles}
    path.write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding="utf-8")
    (ROOT/"news.js").write_text("window.RADAR_DATA = "+json.dumps(info,ensure_ascii=False,separators=(",",":"))+";",encoding="utf-8")
    recent=NOW-dt.timedelta(hours=36)
    fresh=[a for a in articles if dt.datetime.fromisoformat(a["date"].replace("Z","+00:00"))>=recent]
    sections=list(BASE_QUERIES)
    (ROOT/"brief.json").write_text(json.dumps({"updated_at":NOW.isoformat(),
       "sections":{c:[a for a in fresh if c in a.get("sections",[a["section"]])][:8] for c in sections}},
       ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"COLLECTE : {successes}/{len(full)} flux ; {new_count} nouvelles actus ; {len(articles)} articles récents ; {len(set(a['source'] for a in articles))} médias représentés")
    if errors:
        print(f"ATTENTION : {len(errors)} sources indisponibles (non exhaustif):", errors[:3])
if __name__=="__main__":
    main()
