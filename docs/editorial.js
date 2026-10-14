/* McDo Radar — consultation, Top 10, recherche combinée et newsletter. */
(() => {
  "use strict";
  const $ = id => document.getElementById(id);
  const data = window.RADAR_DATA || {articles:[]};
  const items = (data.articles||[]).filter(a => a && a.title && a.url && a.date);
  const week = window.RADAR_WEEKLY || {items:[]};
  const sections = ["✦ Les 10 pépites","Toutes les actus","France","Local","RH McDo","Concurrence","Inspiration RH","Campagnes créatives","Podcasts & interviews","Signaux sensibles","Sources suivies"];
  const modes = [
    ["all","Toutes les actualités"],
    ["newsletter","À mettre dans ma newsletter"],
    ["campaign","Campagnes inspirantes"],
    ["studies","Chiffres & études RH"],
    ["impact","Impact potentiel pour McDo"]
  ];
  const sources = {
    "Priorité 1 — Au cœur des sujets":[
      ["France Snacking","https://www.snacking.fr/"],
      ["L’Express Franchise","https://lexpress-franchise.com/"],
      ["L’Hôtellerie Restauration","https://www.lhotellerie-restauration.fr/"],
      ["Creapills","https://creapills.com/"],["L’ADN","https://www.ladn.eu/"],
      ["Dans Ta Pub","https://www.danstapub.com/"],["Stratégies","https://www.strategies.fr/"],
      ["CB News","https://www.cbnews.fr/"],["HelloWork","https://www.hellowork.com/"],
      ["Culture RH","https://culture-rh.com/"],["Parlons RH","https://www.parlonsrh.com/"],
      ["Apec","https://www.apec.fr/"],["Dares","https://dares.travail-emploi.gouv.fr/"],
      ["France Travail","https://www.francetravail.org/"],["Le Journal des Entreprises","https://www.lejournaldesentreprises.com/"],
      ["actu.fr","https://actu.fr/"],["Great Place To Work","https://www.greatplacetowork.fr/"],
      ["ChooseMyCompany","https://choosemycompany.com/"]
    ],
    "Priorité 2 — Inspirations et tendances":[
      ["J’ai un pote dans la com","https://jai-un-pote-dans-la.com/"],
      ["La Réclame","https://lareclame.fr/"],["INfluencia","https://www.influencia.net/"],
      ["Marketing Magazine","https://www.e-marketing.fr/"],["Les Gens d’Internet","https://gensdinternet.fr/"],
      ["Blog du Modérateur","https://www.blogdumoderateur.com/"],["Maddyness","https://www.maddyness.com/"],
      ["myRHline","https://myrhline.com/"],["RH Matin","https://www.rhmatin.com/"],
      ["Focus RH","https://www.focusrh.com/"],["Welcome to the Jungle","https://www.welcometothejungle.com/fr"],
      ["Siècle Digital","https://siecledigital.fr/"],["LSA","https://www.lsa-conso.fr/"],
      ["Little Black Book","https://lbbonline.com/"],["Marketing Dive","https://www.marketingdive.com/"],
      ["Creative Boom","https://www.creativeboom.com/"],["Digiday","https://digiday.com/"],
      ["Social Media Today","https://www.socialmediatoday.com/"],
      ["Ads of the World","https://www.adsoftheworld.com/"],["Cannes Lions","https://www.canneslions.com/"],
      ["The Drum","https://www.thedrum.com/"],["Adweek","https://www.adweek.com/"],
      ["Campaign","https://www.campaignlive.co.uk/"],["ANDRH","https://www.andrh.fr/"],
      ["Courrier Cadres","https://www.courriercadres.com/"],
      ["LinkedIn Talent Solutions","https://business.linkedin.com/talent-solutions"]
    ]
  };
  const normalize = txt => String(txt||"").normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase();
  const escape = str => String(str??"").replace(/[&<>"']/g,x=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[x]));
  const fmt = date => new Date(date).toLocaleDateString("fr-FR",{day:"numeric",month:"short",year:"numeric"});
  const tags = a => a.editorial?.tags || [];
  const tier = a => a.editorial?.source_tier||3;
  const score = a => a.editorial?.score||0;
  const headings = a => a.sections?.length?a.sections:[a.section];
  const isPodcast = a => a.type==="podcast" || headings(a).includes("Podcasts & interviews");
  const isMcDo = a => /mcdonald|mcdo\b|mcjobs/i.test(normalize(a.title));
  const isCompetition = a => /\bburger king\b|\bkfc\b|\bquick\b|\bfive guys\b/i.test(normalize(a.title));
  const whatBrand = a => {
    const t=normalize(a.title);
    if(/mcdonald|mcdo\b|mcjobs/.test(t))return "mcdo";
    if(/burger king/.test(t))return "burger king";
    if(/\bkfc\b/.test(t))return "kfc";
    if(/\bquick\b/.test(t))return "quick";
    if(/five guys/.test(t))return "five guys";
    return "other";
  };
  const articleByUrl = new Map(items.map(a=>[a.url,a]));
  let tab="✦ Les 10 pépites", mode="all", shown=60;
  let selected;
  try {selected=new Set(JSON.parse(localStorage.getItem("mcdo-selected")||"[]"))}catch(e){selected=new Set()}
  const saveState=()=>{try{localStorage.setItem("mcdo-selected",JSON.stringify([...selected]))}catch(e){}};
  function updateSelected(){
    const arr=items.filter(a=>selected.has(a.url));
    $("selected-count").textContent=arr.length;
    $("selected-list").innerHTML=arr.length?
      "<ol>"+arr.map(a=>'<li><a href="'+escape(a.url)+'" target="_blank" rel="noopener noreferrer">'+escape(a.title)+"</a> · "+escape(a.show||a.source)+" · "+fmt(a.date)+"</li>").join("")+"</ol>":
      "<p>Aucun article sélectionné. Ajoute tes sujets préférés depuis une pépite ou une carte.</p>";
    saveState();
  }
  function nav(){
    $("tabs").innerHTML=sections.map(t=>{
      const count=t==="✦ Les 10 pépites"?weeklyList().length:
        t==="Sources suivies"?null:items.filter(a=>t==="Toutes les actus"||headings(a).includes(t)).length;
      return '<button type="button" data-tab="'+escape(t)+'" class="'+(t===tab?"active":"")+'">'+escape(t)+(count!==null?' <small>'+count+"</small>":"")+"</button>";
    }).join("");
  }
  function editorialFilters(){
    $("editorial-filters").innerHTML=modes.map(([id,label])=>
      '<button type="button" class="'+(mode===id?"active":"")+'" data-mode="'+id+'">'+escape(label)+"</button>"
    ).join("");
  }
  function weeklyList(){
    if(Array.isArray(week.items) && week.items.length)return week.items;
    const from=Date.now()-7*86400000;
    const match=items.filter(a=>+new Date(a.date)>=from&&!isPodcast(a)&&score(a)>=56)
       .sort((a,b)=>score(b)-score(a) || +new Date(b.date)-+new Date(a.date));
    const picks=[];const counts=new Map();
    for(const a of match){
      const k=a.section;
      if((counts.get(k)||0)>=3)continue;
      picks.push(a);counts.set(k,(counts.get(k)||0)+1);
      if(picks.length===10)break;
    }
    return picks;
  }
  function weekly(){
    const list=weeklyList();
    $("weekly-range").textContent="7 derniers jours · "+list.length+" sujet"+(list.length>1?"s":"");
    $("weekly-cards").innerHTML=list.length?list.map((a,i)=>{
      const e=a.editorial||a;
      const source=a.source||"Média";const reason=e.reason||"Sujet à lire pour la newsletter";
      const angle=e.angle||"À creuser : quel intérêt pour McDo ?";
      return '<article class="week-card"><div class="week-num">'+String(i+1).padStart(2,"0")+'</div>'+
        '<div><div class="meta">'+escape(source)+" · "+fmt(a.date)+" · "+escape(a.section||"Veille")+'</div>'+
        '<h3>'+escape(a.title)+'</h3>'+
        '<p class="article-note">'+escape(reason)+'</p><p class="angle">'+escape(angle)+'</p>'+
        '<div class="week-actions"><a href="'+escape(a.url)+'" target="_blank" rel="noopener noreferrer">Lire l’article ↗</a>'+
        '<button type="button" class="mini-btn" data-save="'+escape(a.url)+'">'+(selected.has(a.url)?"✓ Sélectionné":"+ Newsletter")+"</button></div></div></article>";
    }).join(""):'<p class="empty">Aucune pépite validable sur les 7 derniers jours pour le moment. Consulte « Toutes les actus ».</p>';
  }
  function sourceCatalog(){
    const result=Object.entries(sources).map(([group,entries])=>
      '<section class="source-tier"><h3>'+escape(group)+'</h3>'+
      '<p>Recherches et flux publics ciblés. Certains titres ne sont pas indexés ou nécessitent un abonnement.</p>'+
      '<div class="source-tags">'+entries.map(([title,url])=>'<a href="'+escape(url)+'" target="_blank" rel="noopener noreferrer">'+escape(title)+" ↗</a>").join("")+"</div></section>"
    ).join("");
    $("source-catalogue").innerHTML=result+
      '<section class="source-tier"><h3>Priorité 3 — Veille élargie</h3><p>Autres médias généralistes, locaux et internationaux présents dans les résultats ; priorité ajustée selon le sujet.</p></section>'+
      '<section class="source-tier"><h3>Podcasts & interviews</h3><p>Épisodes publics de Passion DRH, Bougeons les lignes, Le Super Daily, Génération Do It Yourself, En toute franchise et Le Talk Franchise (selon disponibilité des flux).</p></section>';
  }
  function filterRows(){
    const q=normalize($("search").value).trim();
    const media=$("source-filter").value, brand=$("brand-filter").value;
    const type=$("type-filter").value,days=Number($("period").value),order=$("sort").value;
    const list=items.filter(a=>{
      if(tab!=="Toutes les actus"&&!headings(a).includes(tab))return false;
      if(mode!=="all"&&!tags(a).includes(mode))return false;
      if(media&&a.source!==media)return false;
      if(brand&&whatBrand(a)!==brand)return false;
      if(type&&(type==="podcast"?!isPodcast(a):isPodcast(a)))return false;
      if(Date.now()-new Date(a.date).getTime()>days*86400000)return false;
      if(q&&!normalize([a.title,a.source,a.show,headings(a).join(" ")].join(" ")).includes(q))return false;
      return true;
    });
    list.sort((a,b)=>{
      if(order==="relevance")return score(b)-score(a)||+new Date(b.date)-+new Date(a.date);
      if(order==="source")return tier(a)-tier(b)||+new Date(b.date)-+new Date(a.date);
      return +new Date(b.date)-+new Date(a.date);
    });
    return list;
  }
  function drawFeed(){
    const all=filterRows(),page=all.slice(0,shown);
    $("heading").textContent=tab;
    $("filter-count").textContent=all.length+" résultat"+(all.length>1?"s":"")+" dans la sélection";
    $("count").textContent=all.length+" actualité"+(all.length>1?"s":"")+" · "+new Set(all.map(a=>a.source)).size+" sources · filtre strict sur les titres et catégories";
    $("cards").innerHTML=page.length?page.map(a=>{
      const e=a.editorial||{};
      const isPod=isPodcast(a);
      const hint=e.angle||"À creuser : quel intérêt concret pour McDo ?";
      return '<article class="card"><div class="chip-row"><span class="tag">'+escape(a.section)+(isPod?" 🎧":"")+'</span>'+
        '<span class="tag soft">Source P'+tier(a)+"</span></div>"+
        '<div class="meta">'+fmt(a.date)+" · "+escape(a.show||a.source)+'</div>'+
        '<h3>'+escape(a.title)+'</h3>'+
        '<div class="reason">'+escape(e.reason||"À qualifier")+'</div>'+
        '<div class="angle">'+escape(hint)+'</div>'+
        '<div class="card-actions"><a href="'+escape(a.url)+'" target="_blank" rel="noopener noreferrer">'+(isPod?"Écouter ↗":"Lire ↗")+'</a>'+
        '<button class="mini-btn" type="button" data-save="'+escape(a.url)+'">'+(selected.has(a.url)?"✓ Sélectionné":"+ Newsletter")+"</button></div></article>";
    }).join(""):'<p class="empty">Aucun résultat avec cette combinaison. Essaie une autre période, une autre marque ou réinitialise les filtres.</p>';
    $("more").hidden=all.length<=shown;
    $("more").textContent="Afficher "+Math.min(60,all.length-shown)+" résultats de plus ↓";
  }
  function paint(){
    nav();editorialFilters();
    $("weekly-panel").hidden=tab!=="✦ Les 10 pépites";
    $("sources-panel").hidden=tab!=="Sources suivies";
    $("browser-panel").hidden=tab==="✦ Les 10 pépites"||tab==="Sources suivies";
    if(tab==="✦ Les 10 pépites")weekly();
    else if(tab!=="Sources suivies")drawFeed();
    updateSelected();
  }
  function changeSave(url){
    selected.has(url)?selected.delete(url):selected.add(url);
    paint();
  }
  $("tabs").addEventListener("click",e=>{
    const b=e.target.closest("[data-tab]");if(!b)return;
    tab=b.dataset.tab;shown=60;
    if(tab==="Podcasts & interviews")$("period").value="180";
    paint();
  });
  $("editorial-filters").addEventListener("click",e=>{
    const b=e.target.closest("[data-mode]");if(!b)return;
    mode=b.dataset.mode;shown=60;paint();
  });
  document.addEventListener("click",e=>{
    const b=e.target.closest("button[data-save]");
    if(b)changeSave(b.dataset.save);
  });
  ["search","brand-filter","source-filter","type-filter","period","sort"].forEach(id=>{
    $(id).addEventListener(id==="search"?"input":"change",()=>{shown=60;paint()});
  });
  $("reset").addEventListener("click",()=>{
    mode="all";shown=60;$("search").value="";$("brand-filter").value="";
    $("source-filter").value="";$("type-filter").value="";
    $("period").value="30";$("sort").value="date";paint();
  });
  $("more").addEventListener("click",()=>{shown+=60;paint()});
  $("clear").addEventListener("click",()=>{selected.clear();paint()});
  $("copy").addEventListener("click",async()=>{
    const arr=items.filter(a=>selected.has(a.url));
    if(!arr.length)return;
    const msg=arr.map(a=>a.title+"\n"+(a.show||a.source)+" · "+fmt(a.date)+"\n"+a.url+
      "\nSuggestion d’angle (à vérifier) : "+(a.editorial?.angle||"À qualifier")).join("\n\n");
    try {await navigator.clipboard.writeText(msg);$("copy").textContent="Copié ✓";}
    catch(e){window.prompt("Copier la sélection",msg);}
  });
  const media=[...new Set(items.map(a=>a.source).filter(Boolean))].sort((a,b)=>a.localeCompare(b,"fr"));
  $("source-filter").innerHTML='<option value="">Tous les médias ('+media.length+')</option>'+
    media.map(m=>'<option value="'+escape(m)+'">'+escape(m)+"</option>").join("");
  $("total").textContent=items.length;
  $("new").textContent=data.new_count||0;
  $("coverage").textContent=(data.sources_ok??"—")+" / "+(data.sources_total??"—");
  const updated=data.updated_at?new Date(data.updated_at):null;
  const old=updated&&Date.now()-updated.getTime()>48*3600000;
  $("status").textContent=updated?
    (old?"Dernière collecte ancienne : ":"Mise à jour : ")+updated.toLocaleString("fr-FR",{timeZone:"Europe/Paris"}):
    "En attente de données.";
  sourceCatalog();paint();
})();