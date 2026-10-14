#!/usr/bin/env python3
"""McDo Radar : collecte quotidienne multi-sources (articles publics, RSS / Google Actualités).
Les liens vers les articles et les dates sont toujours conservés. Pas de scraping LinkedIn privé.
"""
import concurrent.futures as cf
import datetime as dt
import email.utils
import html
import io
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
    ("Les Gens d'Internet", "gensdinternet.fr"),
    ("Blog du Modérateur", "blogdumoderateur.com"),
    ("Siècle Digital", "siecledigital.fr"),
    ("The Drum", "thedrum.com"),
    ("Adweek", "adweek.com"),
    ("Campaign", "campaignlive.co.uk"),
    ("Little Black Book", "lbbonline.com"),
    ("Marketing Dive", "marketingdive.com"),
    ("Creative Boom", "creativeboom.com"),
    ("Digiday", "digiday.com"),
    ("Social Media Today", "socialmediatoday.com"),
    ("Ads of the World", "adsoftheworld.com"),
    ("Cannes Lions", "canneslions.com"),
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
    ("Maddyness", "maddyness.com"),
    ("LinkedIn Talent Solutions", "business.linkedin.com"),
    ("DARES", "dares.travail-emploi.gouv.fr"),
    ("France Travail", "francetravail.org"),
    ("Great Place To Work", "greatplacetowork.fr"),
    ("ChooseMyCompany", "choosemycompany.com"),
    ("France Travail Statistiques", "statistiques.francetravail.org"),
]
SECTOR_MEDIA = [
    ("France Snacking", "snacking.fr", "Concurrence"),
    ("L'Express Franchise", "lexpress-franchise.com", "Local"),
    ("L'Hôtellerie Restauration", "lhotellerie-restauration.fr", "Inspiration RH"),
    ("Le Journal des Entreprises", "lejournaldesentreprises.com", "Local"),
    ("actu.fr", "actu.fr", "Local"),
    ("ici", "ici.fr", "Local"),
    ("LSA", "lsa-conso.fr", "Concurrence"),
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
        "baromètre emploi marque employeur jeunes 2026",
        "étude Dares recrutement attractivité métiers restauration",
        "France Travail intentions embauche restauration 2026",
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
        "campagne créative récompensée Cannes Lions communication marque",
        "publicité activation création TikTok France 2026",
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
    # Les feeds de podcasts peuvent dépasser la taille lue et finir au milieu
    # d'une CDATA : récupérer les items complets avant la coupure.
    try:
        root = ET.fromstring(raw)
        nodes = root.findall("./channel/item")
        if not nodes:
            nodes = root.findall(".//{http://www.w3.org/2005/Atom}entry")
    except ET.ParseError as error:
        nodes=[]
        try:
            for _, el in ET.iterparse(io.BytesIO(raw), events=("end",)):
                if el.tag in ("item","{http://www.w3.org/2005/Atom}entry"):
                    nodes.append(el)
        except ET.ParseError:
            pass
        if not nodes:
            raise error
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
        entry={"title":title,"url":link,"source":source,"date":date,
               "section":section,"sections":tags,"query":query,
               "channel":("RSS direct" if direct else "Google Actualités")}
        if "podcast" in title.casefold() and (source.casefold().startswith("parlons rh") or "parlonsrh.com" in link):
            entry["type"]="podcast"
            entry["show"]="Parlons RH"
            entry["sections"]=list(dict.fromkeys(tags+["Podcasts & interviews"]))
        out.append(entry)
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
    for source, domain, cat in SECTOR_MEDIA:
        results.append((cat, f"site:{domain} (McDonald's OR recrutement OR franchise OR restauration OR emploi OR restaurant)", source, False, None))
    results += [(cat,q,"LinkedIn",False,None) for cat,q in LINKEDIN_QUERIES]
    results += [(cat,f"Flux {name}",name,True,url) for name,url,cat in DIRECT_FEEDS]
    return results

# Catégorisation plus stricte : uniquement titre, source et métadonnées disponibles.
# Aucune analyse prétendue du texte intégral.
SOURCE_PRIORITY = {
  1: ["france snacking","snacking.fr","l'express franchise","l’hotellerie restauration",
      "l'hotellerie restauration","creapills","dans ta pub","l'adn","strategies",
      "cb news","hellowork","culture rh","parlons rh","mcdonald","apec",
      "dares","france travail","linkedin talent","le journal des entreprises",
      "actu.fr","great place to work","choosemycompany"],
  2: ["j'ai un pote","la reclame","influencia","marketing magazine","les gens d'internet",
      "blog du moderateur","rh matin","myrhline","focus rh","maddyness",
      "welcome to the jungle","little black book","marketing dive","creative boom",
      "digiday","social media today","ads of the world","cannes lions",
      "the drum","adweek","campaign","andrh","courrier cadres","lsa","siecle digital","ici"],
}
def normal(s):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFKD", str(s or "").casefold()) if not unicodedata.combining(c))
def match(text, pattern):
    return bool(re.search(pattern, normal(text)))
def source_rank(article):
    name=normal(article.get("source"))
    for level in (1,2):
        if any(tag in name for tag in SOURCE_PRIORITY[level]):
            return level
    return 3
MCDO = r"mcdonald|mcdo\b|mcjobs"
COMP = r"burger king|\bquick\b|\bkfc\b|five guys"
SECTOR = r"restaurant|restaurat|snacking|fast.food|franchise|hotellerie|foodservice"
RH_STRICT = r"recrut|emploi|embauch|salari|equipier|collaborat|manag|formation|alternan|apprent|candidat|carriere|talent|metier|marque employeur|experience candidat|rh\b|ressources humaines|qvct|travail|remuneration|salaire|mobilite interne|people review|soft skill|risques psychosociaux|\brps\b"
RH_PRIORITY = r"recrut|embauch|marque employeur|experience candidat|alternan|formation|manag|salari|equipier|candidat|engagement collaborat|carriere|attractivit|qvct|remuneration|salaire"
CREATIVE = r"campagne|publicit|activation|affichag|film publicitaire|\bspot\b|concept creati|brand content|operation marketing|communication creati|advertising|ads of the world|\bcreati|lance une campagne|partenariat publicitaire"
STUDY = r"etude|barometre|sondage|enquete|chiffres?|statistique|rapport|observatoire|tendance|indice|classement|donnees|resultats? de l.etude"
SENSITIVE = r"greve|justice|condamn|plainte|polemique|scandale|boycott|harcelement|accus|contamin|fermeture administrative|mobilisation syndical|casse sociale|inquietude|conflit social"
JOB_AD = r"\(?h/f\)?|\(?f/h\)?|offre d.emploi|postuler a l.offre|cdi a |cdd a |f/h\b|rejoignez notre equipe|hiring now|fiche metier|recrutement saison|recrutement hiver|recrute pour la saison|nous recrutons|offres? d.emploi a pourvoir"
CREATIVE_SOURCE_PATTERN = r"creapills|dans ta pub|l.adn|strategies|cb news|j.ai un pote|la reclame|lbb|influencia|marketing dive|creative boom|adweek|the drum|campaign uk"
def classify(article):
    title=normal(article.get("title")); source=normal(article.get("source"))
    original=article.get("section","")
    is_podcast=article.get("type")=="podcast" or original=="Podcasts & interviews"
    mcdo=match(title,MCDO)
    competitor=match(title,COMP)
    industry=match(title,SECTOR)
    hr=match(title,RH_STRICT)
    hr_priority=match(title,RH_PRIORITY)
    creative=match(title,CREATIVE)
    study=match(title,STUDY)
    sensitive=match(title,SENSITIVE)
    job_ad=match(title,JOB_AD)
    generic_creative=original in ("Campagnes créatives","Concurrence") and match(source,CREATIVE_SOURCE_PATTERN) and match(title,r"lance|devoile|imagine|invente|detourne|creation|collaboration|collab|affiche|revisite|surprend|nouvelle identite|spot|publicit|campagne|signe|fait devaler|transforme")
    # Ne pas traiter les offres individuelles comme des sujets d'actualité RH.
    if job_ad and not mcdo and not competitor:
        return None
    sections=[]
    if is_podcast:
        if not (hr or creative or industry or mcdo or competitor or match(title,r"tiktok|instagram|linkedin|gen z|reseaux|influence|marketing|communication")):
            return None
        sections=["Podcasts & interviews"]
    else:
        if mcdo:
            sections.append("France")
            if original=="Local" or match(title,r"ouvre|ouverture|inaugur|ville de|restaurants? de |local|franchise|equipier|commune|recrute a |implant"):
                sections.append("Local")
            if hr: sections.append("RH McDo")
            if sensitive: sections.append("Signaux sensibles")
        if competitor:
            sections.append("Concurrence")
            if sensitive: sections.append("Signaux sensibles")
        # La rubrique Local concerne les restaurants McDonald's, pas l'actualité locale généraliste.
        # Les études RH et campagnes publicitaires sont ouvertes à tous les secteurs.
        if hr and not mcdo and not competitor and original in ("Inspiration RH","Campagnes créatives"):
            sections.append("Inspiration RH")
        if (creative or generic_creative) and original in ("Campagnes créatives","Inspiration RH","France","Concurrence"):
            sections.append("Campagnes créatives")
        if study and hr and not mcdo and not competitor:
            sections.append("Inspiration RH")
        if not sections:
            return None
    # Une requête source dédiée McDo peut parfois servir une actualité non McDo;
    # ne conserver ces résultats que s'ils ont un intérêt explicite dans le titre.
    sections=list(dict.fromkeys(sections))
    if is_podcast: primary="Podcasts & interviews"
    elif "Signaux sensibles" in sections and original=="Signaux sensibles": primary="Signaux sensibles"
    elif "RH McDo" in sections and original=="RH McDo": primary="RH McDo"
    elif "Local" in sections and original=="Local": primary="Local"
    elif original in sections: primary=original
    else: primary=sections[0]
    article["sections"]=sections
    article["section"]=primary
    article["type"]="podcast" if is_podcast else "article"
    article["_signals"]={
        "mcdo":mcdo,"competitor":competitor,"industry":industry,"hr":hr,
        "rh_priority":hr_priority,"creative":creative or generic_creative,
        "study":study,"sensitive":sensitive,
    }
    return article
def editorial_metadata(article):
    s=article.pop("_signals",None)
    if s is None:
        # Historique enregistré : reclassifier chaque jour, ne pas conserver
        # des étiquettes issues d'une précédente version.
        reclassified=classify(article)
        if reclassified is None:return None
        s=article.pop("_signals")
    title=normal(article["title"])
    sections=article.get("sections",[])
    tier=source_rank(article)
    mcdo=s["mcdo"];competitor=s["competitor"];rh=s["hr"];creative=s["creative"];study=s["study"]
    days=max(0,(NOW-dt.datetime.fromisoformat(article["date"].replace("Z","+00:00"))).total_seconds()/86400)
    # L'intérêt du sujet pèse plus lourd que le prestige du média.
    score=14
    score+=24 if mcdo else 16 if competitor else 0
    score+=22 if rh and mcdo else 15 if s["rh_priority"] else 8 if rh else 0
    score+=17 if creative else 0
    score+=16 if study and rh else 5 if study else 0
    score+=10 if s["sensitive"] and (mcdo or competitor) else 0
    score+=8 if "Local" in sections and mcdo else 0
    score+=8 if s["industry"] and not (mcdo or competitor) else 0
    score+=6 if tier==1 else 3 if tier==2 else 0
    score+=12 if days<=7 else 8 if days<=21 else 4 if days<=45 else 0
    if article.get("type")=="podcast":score+=5
    score=min(100,score)
    tags=[]
    if creative and ("Campagnes créatives" in sections or mcdo or competitor):tags.append("campaign")
    if study and rh:tags.append("studies")
    if mcdo or competitor or (rh and (s["rh_priority"] or s["industry"])):tags.append("impact")
    if score>=62 and (mcdo or competitor or s["rh_priority"] or creative or study):
        tags.append("newsletter")
    if s["sensitive"] and (mcdo or competitor):reason="Signal sensible relatif à l'enseigne : vérification indispensable"
    elif mcdo:reason="Actualité McDo directement exploitable pour la veille"
    elif competitor:reason="Signal concurrentiel à comparer à McDo"
    elif study and rh:reason="Chiffres ou étude RH à vérifier avant publication"
    elif creative:reason="Idée de campagne ou dispositif créatif à explorer"
    elif s["rh_priority"]:reason="Pratique RH ou marque employeur potentiellement transposable"
    else:reason="Actualité sectorielle ou RH à qualifier"
    if s["sensitive"]:angle="À analyser : quels faits sont confirmés et quel est le contexte ?"
    elif study and rh:angle="À creuser : que révèle cette étude pour l'attractivité des métiers ?"
    elif creative and rh:angle="À creuser : quelle mécanique créative appliquer à un recrutement McDo ?"
    elif creative:angle="À creuser : quel format ou dispositif inspirant pour McDo ?"
    elif mcdo and rh:angle="À creuser : quelle preuve d'expérience collaborateur en tirer ?"
    elif mcdo:angle="À creuser : quel impact sur l'image de McDo ?"
    elif competitor:angle="À creuser : que fait différemment cette enseigne ?"
    elif rh:angle="À creuser : en quoi cette pratique est-elle utile aux managers ?"
    else:angle="À creuser : quel enseignement concret pour la communication ?"
    article["editorial"]={"score":score,"tags":tags,"source_tier":tier,
        "reason":reason,"angle":angle,
        "method":"Score automatique : titre, rubrique, date et source, sans lecture de l'article."}
    return article
def deduplicate(articles):
    # Déduplication des articles avec titre identique publié sur Google Actualités
    # et RSS direct. Préférer l'URL originale de l'éditeur.
    result={}
    for a in articles:
        base=normal(a.get("title",""))
        source=normal(a.get("source",""))
        # Fin de titre suffixée par le média : HelloWorkplace - HelloWorkplace
        parts=re.split(r"\s+[-–]\s+",base)
        if len(parts)>1 and (parts[-1] in source or source in parts[-1] or len(parts[-1])<15):
            base=" - ".join(parts[:-1])
        base=re.sub(r"[^a-z0-9]+","",base)
        if len(base)<24:base=re.sub(r"[^a-z0-9]+","",normal(a["title"]))
        current=result.get(base)
        if not current:
            result[base]=a;continue
        # Fusionner rubriques, conserver lien direct et classement de la meilleure version.
        best=a if a.get("channel")=="RSS direct" and current.get("channel")!="RSS direct" else current
        best["sections"]=list(dict.fromkeys(a.get("sections",[])+current.get("sections",[])))
        if "Podcasts & interviews" in best["sections"]:best["type"]="podcast"
        result[base]=best
    return list(result.values())
def weekly_picks(articles):
    # Semaine glissante pour fournir des pépites aussi le lundi matin.
    cutoff=NOW-dt.timedelta(days=7)
    candidates=[a for a in articles if dt.datetime.fromisoformat(a["date"].replace("Z","+00:00"))>=cutoff
        and a.get("editorial",{}).get("score",0)>=48 and a.get("type")!="podcast"
        and (match(a["title"],MCDO) or match(a["title"],COMP) or
             any(tag in a.get("editorial",{}).get("tags",[]) for tag in ("newsletter","campaign","studies")))]
    # Privilégier un angle RH/créatif ou une info McDo/secteur, et limiter la répétition.
    candidates.sort(key=lambda a:(a["editorial"]["score"],a["date"]),reverse=True)
    picks=[];counts={};media={};section_limits={
       "France":3,"Local":2,"RH McDo":3,"Concurrence":2,
       "Inspiration RH":4,"Campagnes créatives":4,"Signaux sensibles":2,
    }
    for a in candidates:
        key=a["section"];brand=normal(a["source"])
        if counts.get(key,0)>=section_limits.get(key,2) or media.get(brand,0)>=2:continue
        # Une seule entrée par sujet très proche.
        if any(len(set(normal(a["title"]).split())&set(normal(p["title"]).split())) >= min(6,len(normal(a["title"]).split())) for p in picks):
            continue
        picks.append({"title":a["title"],"url":a["url"],"source":a["source"],
          "date":a["date"],"section":a["section"],"score":a["editorial"]["score"],
          "reason":a["editorial"]["reason"],"angle":a["editorial"]["angle"]})
        counts[key]=counts.get(key,0)+1;media[brand]=media.get(brand,0)+1
        if len(picks)>=10:break
    return {"updated_at":NOW.isoformat(),"period_days":7,"count":len(picks),
        "method":"Top 10 de suggestions automatiques, fondées sur les titres, rubriques, sources et dates. À valider.",
        "items":picks}

PODCAST_SHOWS = [
    ("Passion DRH", "Passion DRH", True),
    ("Bougeons les lignes", "Bougeons les lignes Parlons RH", True),
    ("Le Super Daily", "Le Super Daily", True),
    ("Le Talk Franchise", "Le Talk Franchise", True),
    ("En toute franchise", "En toute franchise LE POST PODCAST", True),
    ("Génération Do It Yourself", "Génération Do It Yourself", False),
    ("Marketing Mania", "Marketing Mania", True),
]
PODCAST_RELEVANCE = re.compile(
    r"recrut|ressources humaines|marque employeur|salari|collaborat|travail|"
    r"carrière|alternance|manager|management|emploi|publicit|campagne|créati|"
    r"marketing|communication|social media|influence|marque|franchise|"
    r"restaur|snacking|consommation|burger|mcdonald|kfc|tiktok|linkedin",
    re.I
)
def podcast_work(item):
    label, term, specialised = item
    try:
        q=urllib.parse.urlencode({"term":term,"entity":"podcast","media":"podcast",
                                  "country":"fr","limit":"16"})
        found=json.loads(get("https://itunes.apple.com/search?"+q))
        collections=found.get("results", [])
        best=None
        for one in collections:
            name=(one.get("collectionName") or "").casefold()
            expected=label.casefold()
            # correspondance explicite : ne pas agréger des émissions homonymes
            if name==expected or name.startswith(expected+" -") or name.startswith(expected+" :") or name.startswith(expected+" !"):
                best=one
                break
        if best is None:
            return label, [], "Émission non trouvée dans le répertoire public"
        feed=best.get("feedUrl")
        if not feed: return label, [], "Flux public non communiqué par le répertoire"
        items=parse_rss(get(feed),"Podcasts & interviews",label,preferred_source=label,direct=True)
        output=[]
        for a in items[:24]:
            if not specialised and not PODCAST_RELEVANCE.search(a["title"]):
                continue
            a["type"]="podcast"
            a["show"]=label
            a["channel"]="Podcast RSS"
            a["sections"]=["Podcasts & interviews"]
            # À défaut de lien d'épisode, on conserve le lien produit par l'éditeur,
            # pas le lien direct vers un fichier audio hébergé.
            output.append(a)
        return label, output, None
    except Exception as e:
        return label, [], str(e)[:170]


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
    # Collecte indépendante des émissions : un échec podcast n'interrompt pas la veille presse.
    with cf.ThreadPoolExecutor(max_workers=4) as podcast_pool:
        for label, episodes, err in podcast_pool.map(podcast_work, PODCAST_SHOWS):
            if err:
                errors.append({"source":"Podcast : "+label,"error":err})
                continue
            successes+=1
            stats["Podcasts & interviews"]=stats.get("Podcasts & interviews",0)+1
            for a in episodes:
                k=key(a)
                if k in merged:
                    existing=merged[k]
                    existing["sections"]=list(dict.fromkeys(existing.get("sections",[existing.get("section","")])+["Podcasts & interviews"]))
                    existing["type"]="podcast"
                    existing["show"]=label
                else:
                    merged[k]=a
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
    # Reclasser l'ensemble de l'historique selon les critères stricts actuels.
    articles=[v for a in articles if (v:=classify(a)) is not None]
    articles=deduplicate(articles)
    for article in articles:
        editorial_metadata(article)
    articles.sort(key=lambda x:x["date"],reverse=True)
    articles=articles[:MAX_ITEMS]
    new_count=sum(key(a) not in previous for a in articles)
    info={"updated_at":NOW.isoformat(), "sources_ok":successes,
          "sources_total":len(full)+len(PODCAST_SHOWS), "source_names":sorted(set(a["source"] for a in articles)),
          "source_count":len(set(a["source"] for a in articles)),
          "source_priority_policy":"Sélection éditoriale indicative : score déterminé par titre, source, rubrique et date. Aucun contenu intégral analysé.",
          "new_count":new_count, "source_errors":errors[:18],
          "articles":articles}
    week=weekly_picks(articles)
    (ROOT/"weekly.json").write_text(json.dumps(week,ensure_ascii=False,indent=2),encoding="utf-8")
    (ROOT/"weekly.js").write_text("window.RADAR_WEEKLY = "+json.dumps(week,ensure_ascii=False,separators=(",",":"))+";",encoding="utf-8")
    path.write_text(json.dumps(info,ensure_ascii=False,indent=2),encoding="utf-8")
    (ROOT/"news.js").write_text("window.RADAR_DATA = "+json.dumps(info,ensure_ascii=False,separators=(",",":"))+";",encoding="utf-8")
    recent=NOW-dt.timedelta(hours=36)
    fresh=[a for a in articles if dt.datetime.fromisoformat(a["date"].replace("Z","+00:00"))>=recent]
    sections=list(BASE_QUERIES)+["Podcasts & interviews"]
    (ROOT/"brief.json").write_text(json.dumps({"updated_at":NOW.isoformat(),
       "sections":{c:[a for a in fresh if c in a.get("sections",[a["section"]])][:8] for c in sections}},
       ensure_ascii=False,indent=2),encoding="utf-8")
    print(f"COLLECTE : {successes}/{len(full)} flux ; {new_count} nouvelles actus ; {len(articles)} articles récents ; {len(set(a['source'] for a in articles))} médias représentés")
    if errors:
        print(f"ATTENTION : {len(errors)} sources indisponibles (non exhaustif):", errors[:3])
if __name__=="__main__":
    main()
