/* McDo Radar — interface et sélection éditoriale. Les scores sont indicatifs. */
(() => {
  "use strict";
  const payload = window.RADAR_DATA || { articles: [] };
  const items = (payload.articles || []).filter(a => a && a.title && a.url && a.date);
  const tabs = ["Tout","France","Local","RH McDo","Concurrence","Inspiration RH","Campagnes créatives","Podcasts & interviews","Signaux sensibles","Sources suivies"];
  const modes = [
    { id:"all",label:"Toutes les actualités" },
    { id:"newsletter",label:"À mettre dans ma newsletter" },
    { id:"campaign",label:"Campagnes inspirantes" },
    { id:"studies",label:"Chiffres & études RH" },
    { id:"impact",label:"Impact potentiel pour McDo" }
  ];
  const catalogue = {
    1:[
      ["France Snacking","https://www.snacking.fr/"],["L’Express Franchise","https://lexpress-franchise.com/"],["L’Hôtellerie Restauration","https://www.lhotellerie-restauration.fr/"],
      ["Creapills","https://creapills.com/"],["L’ADN","https://www.ladn.eu/"],["Dans Ta Pub","https://www.danstapub.com/"],
      ["Stratégies","https://www.strategies.fr/"],["CB News","https://www.cbnews.fr/"],["HelloWork","https://www.hellowork.com/"],
      ["Culture RH","https://culture-rh.com/"],["Parlons RH","https://www.parlonsrh.com/"],["Apec","https://www.apec.fr/"],
      ["Dares","https://dares.travail-emploi.gouv.fr/"],["France Travail","https://www.francetravail.org/"],["LinkedIn Talent Solutions","https://business.linkedin.com/talent-solutions"],
      ["Le Journal des Entreprises","https://www.lejournaldesentreprises.com/"],["actu.fr","https://actu.fr/"],
      ["Great Place To Work","https://www.greatplacetowork.fr/"],["ChooseMyCompany","https://choosemycompany.com/"]
    ],
    2:[
      ["J’ai un pote dans la com","https://jai-un-pote-dans-la.com/"],["La Réclame","https://lareclame.fr/"],
      ["INfluencia","https://www.influencia.net/"],["Marketing Magazine","https://www.e-marketing.fr/"],
      ["Les Gens d’Internet","https://gensdinternet.fr/"],["Blog du Modérateur","https://www.blogdumoderateur.com/"],
      ["Maddyness","https://www.maddyness.com/"],["myRHline","https://myrhline.com/"],["RH Matin","https://www.rhmatin.com/"],
      ["Focus RH","https://www.focusrh.com/"],["Welcome to the Jungle","https://www.welcometothejungle.com/fr"],
      ["Siècle Digital","https://siecledigital.fr/"],["LSA","https://www.lsa-conso.fr/"],["ici","https://www.ici.fr/"],
      ["Little Black Book","https://lbbonline.com/"],["Marketing Dive","https://www.marketingdive.com/"],
      ["Creative Boom","https://www.creativeboom.com/"],["Digiday","https://digiday.com/"],
      ["Social Media Today","https://www.socialmediatoday.com/"],["Ads of the World","https://www.adsoftheworld.com/"],
      ["Cannes Lions","https://www.canneslions.com/"],["The Drum","https://www.thedrum.com/"],
      ["Adweek","https://www.adweek.com/"],["Campaign","https://www.campaignlive.co.uk/"],
      ["ANDRH","https://www.andrh.fr/"],["Courrier Cadres","https://www.courriercadres.com/"],
      ["Liaisons Sociales","https://www.liaisons-sociales.fr/"]
    ]
  };
  const podcastShows = [
    ["Passion DRH","https://www.parlonsrh.com/format/podcasts/"],
    ["Bougeons les lignes !","https://www.parlonsrh.com/format/podcasts/"],
    ["Le Super Daily","https://www.lesuperdaily.com/"],
    ["Le Talk Franchise","https://podcasts.apple.com/fr/search?term=Le%20Talk%20Franchise"],
    ["En toute franchise","https://podcasts.apple.com/fr/podcast/en-toute-franchise/id1873359743"],
    ["Génération Do It Yourself","https://www.gdiy.fr/"],
    ["Marketing Mania","https://marketingmania.fr/"]
  ];
  const $ = id => document.getElementById(id);
  const escape = s => String(s ?? "").replace(/[&<>"']/g,ch => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[ch]));
  const date = value => {
    const d=new Date(value);
    return Number.isNaN(+d)?"Date inconnue":d.toLocaleDateString("fr-FR",{day:"2-digit",month:"short",year:"numeric"});
  };
  const secs = a => Array.isArray(a.sections) && a.sections.length ? a.sections : [a.section];
  let section="Tout", mode="all",sort="relevance", visible=72;
  let saved;
  try { saved = new Set(JSON.parse(localStorage.getItem("mcdo-selected") || "[]")); } catch(e) { saved=new Set(); }
  const ed = a => a.editorial || {score:0,tags:[],source_tier:3,reason:"À qualifier",angle:"Vérifier la source et rechercher un angle éditorial."};
  const contains = (a,k)=> ed(a).tags && ed(a).tags.includes(k);
  function filterItems(){
    const keyword=$("search").value.toLocaleLowerCase("fr").trim();
    const media=$("source-filter").value,days=Number($("period").value);
    const filtered=items.filter(a=>{
      if(section!=="Tout" && section!=="Sources suivies" && !secs(a).includes(section))return false;
      if(mode!=="all"&&!contains(a,mode))return false;
      if(media && a.source!==media)return false;
      if(keyword && ![a.title,a.source,a.show,a.query,secs(a).join(" ")].join(" ").toLocaleLowerCase("fr").includes(keyword))return false;
      if((Date.now()-new Date(a.date).getTime())/86400000>days)return false;
      return true;
    });
    return filtered.sort((a,b)=>{
      if(sort==="relevance")return (ed(b).score||0)-(ed(a).score||0) || (+new Date(b.date))-(+new Date(a.date));
      if(sort==="source")return (ed(a).source_tier||3)-(ed(b).source_tier||3) || (+new Date(b.date))-(+new Date(a.date));
      return (+new Date(b.date))-(+new Date(a.date));
    });
  }
  function drawSelection(){
    const chosen=items.filter(a=>saved.has(a.url));
    $("selected-count").textContent=chosen.length;
    $("selected").innerHTML=chosen.length ?
      "<ol>"+chosen.map(a=>'<li><a target="_blank" rel="noopener noreferrer" href="'+escape(a.url)+'">'+escape(a.title)+'</a> — '+escape(a.show||a.source)+" · "+date(a.date)+"</li>").join("")+"</ol>" :
      '<p class="muted">Ajoute un article ou un podcast à ta sélection pour préparer ta newsletter.</p>';
    try {localStorage.setItem("mcdo-selected",JSON.stringify([...saved]));}catch(_){}
  }
  function drawSources(){
    const actual=items.reduce((map,a)=>{
      const k=(a.source||"").toLocaleLowerCase("fr");
      map.set(k,(map.get(k)||0)+1);return map;
    },new Map());
    const renderGroup=(level,list)=>
      '<div class="sources-tier"><h3>Priorité '+level+'</h3><p class="small-note">'+(level===1?
      "Au cœur des sujets McDo, RH et communication.":
      "Sources complémentaires et inspirations transversales.")+'</p><div class="source-tags">'+list.map(([name,url])=>{
        const n=name.toLocaleLowerCase("fr");
        let count=actual.get(n)||0;
        if(!count)for(const [key,val] of actual.entries())if(key.includes(n) || n.includes(key) && key.length>5){count+=val;}
        return '<a href="'+escape(url)+'" target="_blank" rel="noopener noreferrer">'+escape(name)+(count?' · '+count:' · en veille')+' ↗</a>';
      }).join("")+'</div></div>';
    $("source-catalogue").innerHTML=renderGroup(1,catalogue[1])+renderGroup(2,catalogue[2])+
    '<div class="sources-tier"><h3>Priorité 3</h3><p>Autres médias régionaux, généralistes et internationaux présents dans les résultats, pour compléter les signaux sans prendre toute la place.</p></div>'+
    '<div class="sources-tier"><h3>Podcasts suivis</h3><div class="source-tags">'+podcastShows.map(([name,url])=>'<a href="'+escape(url)+'" target="_blank" rel="noopener noreferrer">'+escape(name)+' ↗</a>').join("")+'</div></div>';
  }
  function drawMenus(){
    $("tabs").innerHTML=tabs.map(t=>
      '<button type="button" data-tab="'+escape(t)+'" class="'+(t===section?"active":"")+'">'+escape(t)+(t==="Sources suivies"?"":' <small>'+items.filter(a=>t==="Tout"||secs(a).includes(t)).length+'</small>')+"</button>"
    ).join("");
    $("editorial-filters").innerHTML=modes.map(f=>
      '<button type="button" data-mode="'+f.id+'" class="'+(mode===f.id?"active":"")+'">'+escape(f.label)+"</button>"
    ).join("");
  }
  function render(){
    drawMenus();
    $("inspiration").hidden=section!=="Inspiration RH";
    $("creative").hidden=section!=="Campagnes créatives";
    $("podcasts-panel").hidden=section!=="Podcasts & interviews";
    $("sources-panel").hidden=section!=="Sources suivies";
    $("articles-panel").hidden=section==="Sources suivies";
    if(section==="Sources suivies"){drawSelection();return;}
    const articles=filterItems();
    $("heading").textContent=section==="Tout"?"Toutes les actualités":section;
    $("count").textContent=articles.length+" résultat(s) · "+new Set(articles.map(a=>a.source)).size+
     " médias ou émissions · tri : "+(sort==="relevance"?"pertinence éditoriale":sort==="source"?"priorité du média":"date");
    $("cards").innerHTML=articles.length?articles.slice(0,visible).map(a=>{
      const e=ed(a),isPodcast=a.type==="podcast",category=secs(a).filter(x=>x!==a.section).slice(0,2);
      const extra=category.length?' <span class="also">'+category.map(escape).join(", ")+"</span>":"";
      const tier=e.source_tier||3, score=Number(e.score)||0;
      const tags=(e.tags||[]).map(t=>({newsletter:"Newsletter",campaign:"Campagne",studies:"Étude / chiffres",impact:"Impact McDo"}[t]||t));
      return '<article class="card"><div class="chip-row"><span class="tag">'+escape(a.section)+(isPodcast?" 🎧":"")+"</span>"+
        '<span class="source-tier">Source P'+tier+"</span>"+extra+'</div>'+
        '<div class="meta">'+date(a.date)+" · "+escape(a.show||a.source)+"</div>"+
        '<h3>'+escape(a.title)+'</h3>'+
        '<div class="editorial-summary"><strong>Intérêt potentiel · '+score+'/100</strong><p>'+escape(e.reason)+
        '</p><p class="angle">'+escape(e.angle)+'</p>'+
        (tags.length?'<div class="mini-tags">'+tags.map(t=>'<span>'+escape(t)+'</span>').join("")+"</div>":"")+'</div>'+
        '<footer><a href="'+escape(a.url)+'" target="_blank" rel="noopener noreferrer">'+(isPodcast?"Écouter / voir l’épisode ↗":"Lire l’article ↗")+'</a>'+
        '<button type="button" class="save" data-save="'+escape(a.url)+'">'+(saved.has(a.url)?"✓ Retirer":"＋ Sélectionner")+"</button></footer></article>";
    }).join(""):'<p>Aucun résultat avec ces filtres. Essaie une période plus longue ou « Toutes les actualités ».</p>';
    $("more").hidden=articles.length<=visible;
    $("more").textContent="Afficher "+Math.min(72,articles.length-visible)+" autres résultats ↓";
    drawSelection();
  }
  $("tabs").addEventListener("click",e=>{
    const b=e.target.closest("[data-tab]");if(!b)return;
    section=b.dataset.tab;visible=72;
    if(section==="Podcasts & interviews"&&Number($("period").value)<90)$("period").value="180";
    render();
  });
  $("editorial-filters").addEventListener("click",e=>{
    const b=e.target.closest("[data-mode]");if(!b)return;mode=b.dataset.mode;visible=72;render();
  });
  $("cards").addEventListener("click",e=>{
    const b=e.target.closest("[data-save]");if(!b)return;
    const url=b.dataset.save;saved.has(url)?saved.delete(url):saved.add(url);render();
  });
  ["search","source-filter","period","sort"].forEach(id=>$(id).addEventListener(id==="search"?"input":"change",()=>{sort=$("sort").value;visible=72;render();}));
  $("more").addEventListener("click",()=>{visible+=72;render();});
  $("clear").addEventListener("click",()=>{saved.clear();render();});
  $("copy").addEventListener("click",async()=>{
    const str=items.filter(a=>saved.has(a.url)).map(a=>a.title+"\n"+(a.show||a.source)+" · "+date(a.date)+
      "\n"+a.url+"\nAngle (suggestion) : "+ed(a).angle).join("\n\n");
    if(!str)return;
    try {await navigator.clipboard.writeText(str);$("copy").textContent="Sélection copiée ✓";}
    catch(e){prompt("Copier cette sélection :",str);}
  });
  $("refresh").addEventListener("click",()=>location.reload());
  $("total").textContent=items.length;
  $("new").textContent=payload.new_count??"—";
  $("coverage").textContent=(payload.sources_ok??"—")+" / "+(payload.sources_total??"—");
  $("status").textContent=payload.updated_at?
    "Dernière collecte "+new Date(payload.updated_at).toLocaleString("fr-FR",{timeZone:"Europe/Paris"})+
    " (Paris) · "+new Set(items.map(a=>a.source)).size+" médias/émissions représentés.":
    "Aucune collecte récente disponible.";
  const media=[...new Set(items.map(a=>a.source).filter(Boolean))].sort((a,b)=>a.localeCompare(b,"fr"));
  $("source-filter").innerHTML='<option value="">Tous les médias ('+media.length+')</option>'+
    media.map(m=>'<option value="'+escape(m)+'">'+escape(m)+"</option>").join("");
  drawSources();render();
})();