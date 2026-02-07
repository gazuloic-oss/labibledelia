const CATEGORIES = [
  {id:"chatbots",name:"Chatbots & AI Agents",icon:"💬",roman:"I",description:"Conversational assistants and autonomous agents",color:"var(--cat-chatbots)"},
  {id:"texte",name:"Text & Writing",icon:"✍️",roman:"II",description:"Automated writing, translation and proofreading",color:"var(--cat-texte)"},
  {id:"image",name:"Image & Design",icon:"🎨",roman:"III",description:"Image generation, editing, and transformation",color:"var(--cat-image)"},
  {id:"video",name:"Video",icon:"🎬",roman:"IV",description:"AI video creation and editing",color:"var(--cat-video)"},
  {id:"audio",name:"Audio & Voice",icon:"🎵",roman:"V",description:"Voice synthesis, music, and transcription",color:"var(--cat-audio)"},
  {id:"code",name:"Code & Development",icon:"💻",roman:"VI",description:"Programming assistants and dev tools",color:"var(--cat-code)"},
  {id:"marketing",name:"Marketing & Business",icon:"📈",roman:"VII",description:"Marketing, SEO, advertising and sales",color:"var(--cat-marketing)"},
  {id:"productivite",name:"Productivity",icon:"⚡",roman:"VIII",description:"Organization, presentations, and note-taking",color:"var(--cat-productivite)"},
  {id:"education",name:"Education & Training",icon:"🎓",roman:"IX",description:"Learning, tutoring, and academic research",color:"var(--cat-education)"},
  {id:"automation",name:"Automation",icon:"🔄",roman:"X",description:"Workflows, integrations, and automated agents",color:"var(--cat-automation)"},
  {id:"recherche",name:"Research & Science",icon:"🔬",roman:"XI",description:"Data analysis, publications, and scientific tools",color:"var(--cat-recherche)"},
  {id:"design-web",name:"Design & Websites",icon:"🎯",roman:"XII",description:"Website creation, prototyping, and UI/UX design",color:"var(--cat-design-web)"},
  {id:"reunions-email",name:"Meetings & Email",icon:"📧",roman:"XIII",description:"Meeting assistants, email, and communication",color:"var(--cat-reunions-email)"},
  {id:"carriere",name:"Career & Work Life",icon:"💼",roman:"XIV",description:"Resumes, job hunting, and professional development",color:"var(--cat-carriere)"},
  {id:"finance",name:"Finance & Business",icon:"📊",roman:"XV",description:"Accounting, prediction, and financial analysis",color:"var(--cat-finance)"},
  {id:"3d",name:"3D & Spatial",icon:"🧊",roman:"XVI",description:"3D model generation, textures and spatial scenes",color:"var(--cat-3d)"},
  {id:"sante",name:"AI & Healthcare",icon:"🏥",roman:"XVII",description:"Diagnostics, medical imaging and clinical AI tools",color:"var(--cat-sante)"},
  {id:"juridique",name:"AI & Legal",icon:"⚖️",roman:"XVIII",description:"Legal research, contract drafting and legal analysis",color:"var(--cat-juridique)"},
  {id:"service-client",name:"AI Customer Service",icon:"💬",roman:"XIX",description:"Support chatbots, ticketing and automated assistance",color:"var(--cat-service-client)"},
  {id:"data",name:"Data & Analytics",icon:"📊",roman:"XX",description:"Data analysis, visualization and augmented BI",color:"var(--cat-data)"}
];

/* TOOLS loaded from external file */
/* ============================================================
   ENGINE — Search, Filter, Render, Routes
   ============================================================ */

const APP = {
  state: {
    search:'',
    filters:{categories:[],pricing:[],platforms:[],minRating:0},
    sort:'popularity',view:'grid',compareList:[],favorites:[],selectedTool:null,
    showComparator:false,currentPage:1,perPage:24
  },

  // --- Helpers ---
  norm(s){return (s||'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'')},
  getToolById(id){return TOOLS.find(t=>t.id===id)},
  getCatById(id){return CATEGORIES.find(c=>c.id===id)},
  stars(r){let s='';for(let i=1;i<=5;i++)s+=i<=Math.round(r)?'★':'☆';return s},
  catColor(id){const c=this.getCatById(id);return c?c.color:'#888'},

  // --- Search ---
  searchTools(query,tools){
    if(!query)return tools;
    const terms=this.norm(query).split(/\s+/).filter(Boolean);
    return tools.map(t=>{
      let score=0;
      terms.forEach(term=>{
        if(this.norm(t.name).includes(term))score+=10;
        if(this.norm(t.tagline).includes(term))score+=5;
        if(t.tags.some(tag=>this.norm(tag).includes(term)))score+=4;
        if(this.norm(t.company).includes(term))score+=3;
        if(this.norm(t.description).includes(term))score+=2;
        if(this.norm(t.category).includes(term))score+=3;
      });
      return{...t,_score:score};
    }).filter(t=>t._score>0).sort((a,b)=>b._score-a._score);
  },

  // --- Filter ---
  filterTools(tools){
    const f=this.state.filters;
    return tools.filter(t=>{
      if(f.categories.length&&!f.categories.includes(t.category))return false;
      if(f.pricing.length&&!f.pricing.includes(t.pricing))return false;
      if(f.platforms.length&&!f.platforms.some(p=>t.platforms.includes(p)))return false;
      if(f.minRating&&t.rating<f.minRating)return false;
      return true;
    });
  },

  // --- Sort ---
  sortTools(tools){
    const s=this.state.sort;
    return[...tools].sort((a,b)=>{
      if(s==='popularity')return b.popularity-a.popularity;
      if(s==='rating')return b.rating-a.rating;
      if(s==='name')return a.name.localeCompare(b.name);
      if(s==='newest')return b.launchYear-a.launchYear;
      return 0;
    });
  },

  // --- Get visible tools ---
  getVisibleTools(){
    let tools=this.state.search?this.searchTools(this.state.search,TOOLS):[...TOOLS];
    tools=this.filterTools(tools);
    tools=this.sortTools(tools);
    return tools;
  },

  // --- Render catalog ---
  renderCatalog(){
    const tools=this.getVisibleTools();
    const page=this.state.currentPage;
    const visible=tools.slice(0,page*this.state.perPage);
    const grid=document.getElementById('toolsGrid');
    grid.className='tools-grid'+(this.state.view==='list'?' list-view':'');
    grid.innerHTML=visible.map(t=>this.renderToolCard(t)).join('');
    document.getElementById('resultsCount').textContent=tools.length+' tool'+(tools.length>1?'s':'');
    const btn=document.getElementById('loadMoreBtn');
    btn.style.display=visible.length<tools.length?'block':'none';
    this.renderActiveFilters();
    this.updateCompareBadge();
  },

  renderToolCard(t){
    const cat=this.getCatById(t.category);
    const inCompare=this.state.compareList.includes(t.id);
    const isFav=this.state.favorites.includes(t.id);
    return`<a class="tool-card" href="/en/${t.id}/" onclick="event.preventDefault();APP.openTool('${t.id}')">
      <button class="tool-card-fav ${isFav?'active':''}" onclick="event.stopPropagation();event.preventDefault();APP.toggleFav('${t.id}')" title="${isFav?'Remove from favorites':'Add to favorites'}">${isFav?'♥':'♡'}</button>
      <button class="tool-card-compare ${inCompare?'added':''}" onclick="event.stopPropagation();event.preventDefault();APP.toggleCompare('${t.id}')" title="${inCompare?'Remove':'Add to comparator'}">${inCompare?'✓ Added':'+ Compare'}</button>
      <div class="tool-card-header">
        <div class="tool-card-icon">${t.icon}</div>
        <div class="tool-card-info">
          <div class="tool-card-name">${t.name}</div>
          <div class="tool-card-company">${t.company}</div>
        </div>
      </div>
      <div class="tool-card-tagline">${t.tagline}</div>
      <div class="tool-card-tags">
        <span class="tool-card-tag" style="background:${cat?cat.color:'#888'}">${cat?cat.name:t.category}</span>
      </div>
      <div class="tool-card-footer">
        <div class="tool-card-rating">
          <span class="tool-card-stars">${this.stars(t.rating)}</span>
          <span class="tool-card-rating-num">${t.rating}</span>
        </div>
        <span class="pricing-badge ${t.pricing}">${t.pricing==='gratuit'?'Free':t.pricing==='freemium'?'Freemium':t.pricing==='payant'?'Paid':'Free Trial'}</span>
      </div>
    </a>`;
  },

  // --- Render active filters ---
  renderActiveFilters(){
    const f=this.state.filters;const pills=[];
    f.categories.forEach(c=>{const cat=this.getCatById(c);if(cat)pills.push(`<span class="active-filter-pill" onclick="APP.removeFilter('categories','${c}')">${cat.icon} ${cat.name} <span class="x">×</span></span>`)});
    f.pricing.forEach(p=>pills.push(`<span class="active-filter-pill" onclick="APP.removeFilter('pricing','${p}')">${p} <span class="x">×</span></span>`));
    f.platforms.forEach(p=>pills.push(`<span class="active-filter-pill" onclick="APP.removeFilter('platforms','${p}')">${p} <span class="x">×</span></span>`));
    if(f.minRating)pills.push(`<span class="active-filter-pill" onclick="APP.removeFilter('minRating',0)">${f.minRating}+ stars <span class="x">×</span></span>`);
    document.getElementById('activeFilters').innerHTML=pills.join('');
  },

  removeFilter(type,val){
    if(type==='minRating'){this.state.filters.minRating=0}
    else{this.state.filters[type]=this.state.filters[type].filter(v=>v!==val)}
    this.state.currentPage=1;
    this.renderFilters();this.renderCatalog();
  },

  // --- Render filter sidebar ---
  renderFilters(){
    // Categories
    const catDiv=document.getElementById('filterCategories');
    const toolCounts={};CATEGORIES.forEach(c=>toolCounts[c.id]=0);
    TOOLS.forEach(t=>{if(toolCounts[t.category]!==undefined)toolCounts[t.category]++});
    catDiv.innerHTML=CATEGORIES.map(c=>`<label class="filter-option">
      <input type="checkbox" value="${c.id}" ${this.state.filters.categories.includes(c.id)?'checked':''} onchange="APP.toggleFilter('categories','${c.id}')">
      ${c.icon} ${c.name}<span class="filter-count">${toolCounts[c.id]}</span>
    </label>`).join('');
    // Pricing
    const prDiv=document.getElementById('filterPricing');
    const pricings=[{id:'gratuit',label:'🟢 Free'},{id:'freemium',label:'🟡 Freemium'},{id:'payant',label:'🔴 Paid'},{id:'essai',label:'🟣 Free Trial'}];
    prDiv.innerHTML=pricings.map(p=>`<label class="filter-option">
      <input type="checkbox" value="${p.id}" ${this.state.filters.pricing.includes(p.id)?'checked':''} onchange="APP.toggleFilter('pricing','${p.id}')">
      ${p.label}</label>`).join('');
    // Platforms
    const plDiv=document.getElementById('filterPlatforms');
    const plats=[{id:'web',label:'🌐 Web'},{id:'ios',label:'📱 iOS'},{id:'android',label:'🤖 Android'},{id:'api',label:'⚙️ API'}];
    plDiv.innerHTML=plats.map(p=>`<label class="filter-option">
      <input type="checkbox" value="${p.id}" ${this.state.filters.platforms.includes(p.id)?'checked':''} onchange="APP.toggleFilter('platforms','${p.id}')">
      ${p.label}</label>`).join('');
    // Stars
    const stDiv=document.getElementById('filterStars');
    stDiv.innerHTML='';for(let i=1;i<=5;i++){
      const star=document.createElement('span');star.className='filter-star'+(i<=this.state.filters.minRating?' filled':'');
      star.textContent='★';star.onclick=()=>{this.state.filters.minRating=i===this.state.filters.minRating?0:i;this.state.currentPage=1;this.renderFilters();this.renderCatalog()};
      stDiv.appendChild(star);
    }
  },

  toggleFilter(type,val){
    const arr=this.state.filters[type];
    const idx=arr.indexOf(val);
    if(idx>-1)arr.splice(idx,1);else arr.push(val);
    this.state.currentPage=1;this.renderCatalog();
  },

  resetFilters(){
    this.state.filters={categories:[],pricing:[],platforms:[],minRating:0};
    this.state.search='';this.state.currentPage=1;
    this.renderFilters();this.renderCatalog();
  },

  setView(v){
    this.state.view=v;
    document.getElementById('gridViewBtn').classList.toggle('active',v==='grid');
    document.getElementById('listViewBtn').classList.toggle('active',v==='list');
    this.renderCatalog();
    try{localStorage.setItem('bible-view',v)}catch(e){}
  },
  setSort(s){this.state.sort=s;this.state.currentPage=1;this.renderCatalog()},
  loadMore(){this.state.currentPage++;this.renderCatalog()},

  // --- TOC + Featured ---
  renderTOC(){
    const list=document.getElementById('tocList');
    list.innerHTML=CATEGORIES.map(c=>{
      const count=TOOLS.filter(t=>t.category===c.id).length;
      return`<li><a class="toc-item" href="/en/categorie/${c.id}/" onclick="event.preventDefault();APP.filterByCategory('${c.id}')">
        <span class="toc-roman">${c.roman}</span>
        <span class="toc-icon">${c.icon}</span>
        <span class="toc-info"><span class="toc-cat-name">${c.name}</span><span class="toc-cat-count">${count} tools</span></span>
      </a></li>`;
    }).join('');
  },
  renderToolOfDay(){
    const topTools=TOOLS.filter(t=>t.rating>=4.3&&t.popularity>=40);
    const day=Math.floor(Date.now()/86400000);
    const tool=topTools[day%topTools.length];
    const el=document.getElementById('toolOfDay');
    if(!el||!tool)return;
    el.innerHTML=`<span class="tool-of-day-badge">TOOL OF THE DAY</span><div class="tool-of-day-content"><span class="tool-of-day-icon">${tool.icon}</span><span class="tool-of-day-name">${tool.name}</span><span class="tool-of-day-tagline">${tool.tagline}</span></div><a class="tool-of-day-link" href="/en/${tool.id}/">Discover →</a>`;
  },
  renderFeatured(){
    const grid=document.getElementById('featuredGrid');
    const scored=[...TOOLS].map(t=>({...t,score:t.rating*(t.popularity/20)})).sort((a,b)=>b.score-a.score);
    const selected=[];const usedCats=new Set();
    for(const t of scored){if(selected.length>=8)break;if(!usedCats.has(t.category)){selected.push(t);usedCats.add(t.category);}}
    for(const t of scored){if(selected.length>=8)break;if(!selected.find(s=>s.id===t.id)){selected.push(t);}}
    grid.innerHTML=selected.map(t=>`<a class="featured-card" href="/en/${t.id}/" onclick="event.preventDefault();APP.openTool('${t.id}')">
      <div class="featured-card-header">
        <span class="featured-card-icon">${t.icon}</span>
        <div><div class="featured-card-name">${t.name}</div><div class="featured-card-company">${t.company}</div></div>
      </div>
      <div class="featured-card-tagline">${t.tagline}</div>
      <div class="featured-card-footer">
        <span class="featured-card-rating">${this.stars(t.rating)} ${t.rating}</span>
        <span class="editor-badge">✦ Editor's Pick</span>
      </div>
    </a>`).join('');
  },
  renderHeroCats(){
    document.getElementById('heroCats').innerHTML=CATEGORIES.map(c=>
      `<a class="hero-cat-pill" onclick="APP.filterByCategory('${c.id}')">${c.icon} ${c.name}</a>`
    ).join('');
  },
  // --- TRENDS ---
  showTrends(mode,e){
    document.querySelectorAll('.trends-tab').forEach(t=>t.classList.remove('active'));
    if(e)e.target.classList.add('active');
    else document.querySelector(`.trends-tab`)?.classList.add('active');
    let sorted=[];
    if(mode==='popular') sorted=[...TOOLS].sort((a,b)=>b.popularity-a.popularity).slice(0,15);
    else if(mode==='newest') sorted=[...TOOLS].filter(t=>t.launchYear>=2025).sort((a,b)=>b.launchYear-a.launchYear||b.popularity-a.popularity).slice(0,15);
    else if(mode==='rising') sorted=[...TOOLS].filter(t=>t.launchYear>=2025).sort((a,b)=>b.rating-a.rating||b.popularity-a.popularity).slice(0,15);
    else if(mode==='toprated') sorted=[...TOOLS].sort((a,b)=>b.rating-a.rating||b.popularity-a.popularity).slice(0,15);
    const list=document.getElementById('trendsList');
    list.innerHTML=sorted.map((t,i)=>{
      const badge=t.launchYear>=2025?'<span class="trends-badge new">2025+</span>':t.popularity>=85?'<span class="trends-badge hot">Popular</span>':'';
      return`<a class="trends-item" href="/en/${t.id}/" onclick="event.preventDefault();APP.openTool('${t.id}')">
        <span class="trends-rank ${i<3?'top3':''}">${i+1}</span>
        <span class="trends-icon">${t.icon}</span>
        <div class="trends-info"><div class="trends-name">${t.name}</div><div class="trends-tagline">${t.tagline}</div></div>
        <div class="trends-meta">
          ${badge}
          <span class="trends-rating">${this.stars(t.rating)} ${t.rating}</span>
          <span class="trends-pop">Pop. ${t.popularity}</span>
        </div>
      </a>`;
    }).join('');
  },
  renderTrends(){this.showTrends('popular');},

  // --- VERSUS ---
  renderVersus(){
    const pairs=[
      ['chatgpt','claude'],['chatgpt','gemini'],['chatgpt','perplexity'],['chatgpt','deepseek'],['chatgpt','grok'],
      ['claude','gemini'],['claude','perplexity'],['claude','deepseek'],['chatgpt','lechat'],
      ['midjourney','dalle3'],['midjourney','stablediffusion'],['midjourney','flux'],['dalle3','stablediffusion'],['dalle3','flux'],
      ['cursor','copilot-gh'],['cursor','windsurf'],['cursor','bolt'],['copilot-gh','windsurf'],['bolt','lovable'],['v0','bolt'],
      ['runway','pika'],['runway','kling'],['pika','kling'],['synthesia','heygen'],
      ['elevenlabs','murf'],['suno','udio'],
      ['jasper','copyai'],['jasper','writesonic'],['grammarly','deepl'],['grammarly','languagetool'],
      ['zapier','make'],['zapier','n8n'],['make','n8n'],
      ['gamma','tome'],['otter','fireflies'],['otter','fathom'],['fathom','tldv'],
      ['notebooklm','elicit'],['canvaai','firefly'],['removebg','clipdrop'],
      ['bolt','replit'],['framer','durable'],['superhuman','shortwave'],['teal','kickresume'],
      ['notionai','notionai-prod'],
      ['capcut','filmora'],['capcut','descript'],['capcut','veed'],
      ['cursor','zed'],['lovable','replit'],['claude-code','aider'],['coderabbit','copilot-gh'],
      ['chatgpt','meta-ai'],['deepseek','kimi'],['claude','cohere'],
      ['leonardo','midjourney'],['topaz','magnific'],['pixlr','canvaai'],
      ['meshy','tripo'],['meshy','kaedim'],
      ['motion','reclaim'],['clickupai','notionai-prod'],['beautifulai','gamma'],
      ['manychat','hubspotai'],['phantombuster','instantly'],
      ['manus','genspark'],['botpress','lindy'],
      ['photomath','socratic'],['quizizz','khanmigo'],
      ['wixai','framer'],['hostinger','durable'],
      ['sora','runway-gen3'],['sora','kling'],['runway-gen3','kling'],
      ['ollama','jan'],['groq','together'],['llama','qwen'],
      ['phind','perplexity'],['chatpdf','notebooklm'],
      ['codeium','supermaven'],['dify','flowise'],['crew-ai','langchain'],
      ['jasper-campaigns','typeface'],['surfer','frase']
    ];
    this._versusPairs=pairs;
    this._versusShown=12;
    this._renderVersusCards();
  },
  _renderVersusCards(){
    const pairs=this._versusPairs;
    const grid=document.getElementById('versusGrid');
    const shown=pairs.slice(0,this._versusShown);
    grid.innerHTML=shown.map(([a,b])=>{
      const tA=this.getToolById(a),tB=this.getToolById(b);
      if(!tA||!tB) return '';
      const slug=a+'-vs-'+b;
      return`<a class="versus-card" href="/en/comparer/${slug}/">
        <div class="versus-icons">${tA.icon} <span class="versus-vs">VS</span> ${tB.icon}</div>
        <div class="versus-names">${tA.name} vs ${tB.name}</div>
        <div class="versus-cat">${this.getCatById(tA.category)?.name||''}</div>
      </a>`;
    }).join('');
    const btn=document.getElementById('versusLoadMore');
    if(this._versusShown<pairs.length){
      const remaining=pairs.length-this._versusShown;
      btn.innerHTML=`<button class="btn-load-more" onclick="APP.loadMoreVersus()">Load more comparisons (${remaining} remaining)</button>`;
    }else{btn.innerHTML='';}
  },
  loadMoreVersus(){
    this._versusShown=this._versusPairs.length;
    this._renderVersusCards();
  },

  // --- BLOG / GUIDES ---
  renderBlog(){
    const articles=[
      {slug:'chatgpt-guide-complet',emoji:'🤖',tag:'Guide',title:'ChatGPT: The Complete Beginner\'s Guide for 2026',desc:'Master ChatGPT from A to Z: prompt techniques, real-world use cases, and tips to get the most out of the world\'s most popular AI.',time:'12 min'},
      {slug:'claude-guide-complet',emoji:'🤖',tag:'Guide',title:'Claude by Anthropic: The Complete Guide to the Most Reliable AI',desc:'Discover Claude 3.5/4, its unique capabilities, Artifacts, Projects, and why it rivals ChatGPT.',time:'11 min'},
      {slug:'chatgpt-vs-claude-vs-gemini',emoji:'🆚',tag:'Comparison',title:'ChatGPT vs Claude vs Gemini: Which Chatbot to Choose?',desc:'Detailed analysis of the three AI conversation giants. Strengths, weaknesses and use cases.',time:'10 min'},
      {slug:'midjourney-vs-dalle-vs-stable-diffusion',emoji:'🎨',tag:'Comparison',title:'Midjourney vs DALL-E 3 vs Stable Diffusion: The Definitive Comparison',desc:'Side-by-side comparison of the 3 major AI image generators. Style, quality, pricing.',time:'10 min'},
      {slug:'deepseek-revolution-ia-open-source',emoji:'🔓',tag:'Analysis',title:'DeepSeek: The Open-Source Revolution Shaking Up AI',desc:'How DeepSeek-R1 changed the game against GPT-4 and Claude. Industry implications.',time:'10 min'},
      {slug:'meilleurs-generateurs-images-ia',emoji:'🎨',tag:'Creative',title:'The 10 Best AI Image Generators in 2026',desc:'From Midjourney to Flux, discover the tools to create stunning visuals with AI.',time:'11 min'},
      {slug:'generer-videos-ia-guide',emoji:'🎬',tag:'Creative',title:'Generating Videos with AI: The Complete 2026 Guide',desc:'Runway, Pika, Kling, Luma: compare the best AI video generation tools.',time:'10 min'},
      {slug:'creer-musique-ia-suno-udio',emoji:'🎵',tag:'Creative',title:'Creating Music with AI: Guide to Suno, Udio and Alternatives',desc:'Compose full tracks with AI. Musical prompting, copyright, use cases.',time:'9 min'},
      {slug:'elevenlabs-clonage-voix-ia',emoji:'🎙️',tag:'Audio',title:'ElevenLabs: The Complete Guide to AI Voice Cloning',desc:'Clone your voice, create podcasts and dubbing. Everything about AI voice synthesis.',time:'10 min'},
      {slug:'cursor-vs-github-copilot',emoji:'💻',tag:'Dev',title:'Cursor vs GitHub Copilot: The AI Code Assistant Duel',desc:'Complete comparison of AI-powered IDEs for developers.',time:'9 min'},
      {slug:'construire-agent-ia-guide',emoji:'🤖',tag:'Dev',title:'Build Your Own AI Agent in 2026: A Practical Guide',desc:'LangChain, CrewAI, AutoGPT, n8n: choose your framework and deploy your agents.',time:'11 min'},
      {slug:'ia-design-web-2026',emoji:'🎨',tag:'Design',title:'AI is Revolutionizing Web Design: v0, Bolt.new, Framer AI',desc:'Build complete websites with AI. Comparison of tools changing web development.',time:'10 min'},
      {slug:'ia-productivite-personnelle',emoji:'⚡',tag:'Productivity',title:'10x Your Productivity with AI: The 2026 Practical Guide',desc:'Notion AI, Otter, Gamma, Zapier: save hours every week with AI.',time:'10 min'},
      {slug:'automatiser-workflow-ia',emoji:'🚀',tag:'Productivity',title:'How to Automate Your Workflow with AI',desc:'Zapier, Make, n8n: create smart automations without coding.',time:'11 min'},
      {slug:'ia-marketing-digital-guide',emoji:'📈',tag:'Marketing',title:'AI for Digital Marketing: Tools and Strategies for 2026',desc:'SEO, ads, social media, email: transform your marketing with the best AI tools.',time:'10 min'},
      {slug:'meilleurs-outils-ia-redaction',emoji:'✍️',tag:'Writing',title:'The Best AI Writing Tools in 2026',desc:'Jasper, Copy.ai, Writesonic, Grammarly: which tool for which writing need?',time:'10 min'},
      {slug:'ia-education-revolutionne-apprentissage',emoji:'🎓',tag:'Education',title:'How AI Is Revolutionizing Education in 2026',desc:'Khanmigo, Duolingo Max, NotebookLM: personalized learning powered by AI.',time:'10 min'},
      {slug:'perplexity-ia-moteur-recherche-futur',emoji:'🔍',tag:'Analysis',title:'Perplexity AI: Has the Search Engine of the Future Arrived?',desc:'How Perplexity is changing online search. Comparison with Google and ChatGPT.',time:'9 min'},
      {slug:'meilleurs-outils-ia-gratuits',emoji:'🆓',tag:'Budget',title:'The Best 100% Free AI Tools',desc:'No need to pay to use AI. Here are the most powerful free tools available.',time:'10 min'},
      {slug:'securite-confidentialite-outils-ia',emoji:'🔒',tag:'Guide',title:'AI Tools Security and Privacy: What You Need to Know',desc:'Data, GDPR, self-hosting: protect yourself when using AI daily.',time:'9 min'}
    ];
    this._blogArticles=articles;
    this._blogShown=6;
    this._renderBlogCards();
  },
  _renderBlogCards(){
    const articles=this._blogArticles;
    const shown=articles.slice(0,this._blogShown);
    document.getElementById('blogGrid').innerHTML=shown.map(a=>
      `<a href="/en/blog/${a.slug}/" class="blog-card">
        <div class="blog-card-emoji">${a.emoji}</div>
        <div class="blog-card-tag">${a.tag}</div>
        <div class="blog-card-title">${a.title}</div>
        <div class="blog-card-desc">${a.desc}</div>
        <div class="blog-card-meta"><span>📖 ${a.time} read</span><span>•</span><span>February 2026</span></div>
      </a>`
    ).join('');
    const btn=document.getElementById('blogLoadMore');
    if(btn){
      if(this._blogShown<articles.length){
        const remaining=articles.length-this._blogShown;
        btn.innerHTML=`<button class="btn-load-more" onclick="APP.loadMoreBlog()">See more articles (${remaining} remaining)</button>`;
      }else{btn.innerHTML='';}
    }
  },
  loadMoreBlog(){
    this._blogShown=this._blogArticles.length;
    this._renderBlogCards();
  },

  renderFooterCats(){
    const col=document.getElementById('footerCategories');
    col.innerHTML='<h4>Categories</h4>'+CATEGORIES.map(c=>
      `<a href="#catalogue" onclick="APP.filterByCategory('${c.id}')">${c.icon} ${c.name}</a>`
    ).join('');
  },
  filterByCategory(id){
    this.state.filters.categories=[id];this.state.currentPage=1;
    this.renderFilters();this.renderCatalog();
    document.getElementById('catalogue').scrollIntoView({behavior:'smooth'});
  },

  // --- Tool Detail Modal ---
  openTool(id){
    const t=this.getToolById(id);if(!t)return;
    const cat=this.getCatById(t.category);
    const alts=t.alternatives.map(aid=>{const a=this.getToolById(aid);return a?`<a class="modal-seealso-chip" href="/en/${a.id}/" onclick="event.preventDefault();APP.openTool('${a.id}')">${a.icon} ${a.name}</a>`:''}).join('');
    document.getElementById('modalContent').innerHTML=`
      <button class="modal-close" onclick="APP.closeTool()">✕</button>
      <div class="modal-breadcrumb"><a href="#" onclick="APP.closeTool();return false">Home</a> › <a href="#" onclick="APP.closeTool();APP.filterByCategory('${t.category}');return false">${cat?cat.name:''}</a> › ${t.name}</div>
      <div class="modal-body">
        <div class="modal-main">
          <h2>${t.icon} ${t.name}</h2>
          <div class="modal-company">by ${t.company} · Launched in ${t.launchYear}</div>
          <div class="modal-desc">${t.description}</div>
          <div class="modal-section-title">Features</div>
          <ul class="modal-features">${t.features.map(f=>'<li>'+f+'</li>').join('')}</ul>
          <div class="modal-section-title">Pricing</div>
          <div class="modal-pricing-note">${t.pricingNote}</div>
          <div class="modal-section-title">Pros & Cons</div>
          <div class="modal-proscons">
            <div class="modal-pros"><h4>Pros</h4><ul>${t.pros.map(p=>'<li>'+p+'</li>').join('')}</ul></div>
            <div class="modal-cons"><h4>Cons</h4><ul>${t.cons.map(c=>'<li>'+c+'</li>').join('')}</ul></div>
          </div>
          <div class="modal-section-title">Use Cases</div>
          <ul class="modal-usecases">${t.useCases.map(u=>'<li>'+u+'</li>').join('')}</ul>
          <div class="modal-verdict">"${t.verdict}"</div>
          ${alts?'<div class="modal-section-title">See Also</div><div class="modal-seealso">'+alts+'</div>':''}
          <div class="modal-section-title">Share</div>
          <div class="share-buttons">
            <button class="share-btn" onclick="APP.shareUrl('twitter','${t.id}','${t.name.replace(/'/g,"\\'")}')">𝕏 Twitter</button>
            <button class="share-btn" onclick="APP.shareUrl('linkedin','${t.id}','${t.name.replace(/'/g,"\\'")}')">in LinkedIn</button>
            <button class="share-btn" onclick="APP.shareUrl('facebook','${t.id}','${t.name.replace(/'/g,"\\'")}')">f Facebook</button>
            <button class="share-btn" onclick="APP.shareUrl('whatsapp','${t.id}','${t.name.replace(/'/g,"\\'")}')">📱 WhatsApp</button>
            <button class="share-btn" onclick="APP.shareUrl('telegram','${t.id}','${t.name.replace(/'/g,"\\'")}')">✈️ Telegram</button>
            <button class="share-btn" onclick="APP.copyLink('${t.id}',this)">🔗 Copy link</button>
          </div>
        </div>
        <aside class="infobox">
          <div class="infobox-icon">${t.icon}</div>
          <div class="infobox-title">${t.name}</div>
          <div class="infobox-row"><span class="infobox-key">Developer</span><span class="infobox-val">${t.company}</span></div>
          <div class="infobox-row"><span class="infobox-key">Launch</span><span class="infobox-val">${t.launchYear}</span></div>
          <div class="infobox-row"><span class="infobox-key">Price</span><span class="infobox-val"><span class="pricing-badge ${t.pricing}">${t.pricing}</span></span></div>
          <div class="infobox-row"><span class="infobox-key">Rating</span><span class="infobox-val" style="color:var(--star-filled)">${this.stars(t.rating)} ${t.rating}/5</span></div>
          <div class="infobox-row"><span class="infobox-key">Category</span><span class="infobox-val" style="color:${cat?cat.color:''}">${cat?cat.name:''}</span></div>
          <div class="infobox-row"><span class="infobox-key">Platforms</span><div class="infobox-platforms">${t.platforms.map(p=>'<span class="infobox-platform">'+p+'</span>').join('')}</div></div>
          <a class="infobox-cta" href="${t.url}" target="_blank" rel="nofollow noopener">Visit ${t.name} →</a>
          <button class="infobox-compare-btn" onclick="APP.toggleCompare('${t.id}');APP.closeTool()">${this.state.compareList.includes(t.id)?'✓ In comparator':'+ Add to comparator'}</button>
        </aside>
      </div>`;
    const _overlay=document.getElementById('modalOverlay');_overlay.classList.add('open');
    document.body.style.overflow='hidden';
    this._trapFocus(_overlay);
    history.replaceState(null,null,'#/tool/'+t.id);
  },
  closeTool(){
    const _overlay=document.getElementById('modalOverlay');_overlay.classList.remove('open');
    document.body.style.overflow='';
    this._releaseFocus(_overlay);
    history.replaceState(null,null,location.pathname);
  },

  // --- Comparator ---
  toggleCompare(id){
    const idx=this.state.compareList.indexOf(id);
    const t=this.getToolById(id);
    if(idx>-1){this.state.compareList.splice(idx,1);this.showToast('➖',`${t?t.name:'Tool'} removed from comparator`)}
    else if(this.state.compareList.length<3){this.state.compareList.push(id);this.showToast('⚖️',`${t?t.name:'Tool'} added to comparator`)}
    else{this.showToast('⚠️','Maximum 3 tools to compare');return}
    this.renderCatalog();this.renderCompareTray();
    try{localStorage.setItem('bible-compare',JSON.stringify(this.state.compareList))}catch(e){}
  },
  renderCompareTray(){
    const tray=document.getElementById('compareTray');
    const items=document.getElementById('compareTrayItems');
    if(this.state.compareList.length===0){tray.classList.remove('visible');return}
    tray.classList.add('visible');
    items.innerHTML=this.state.compareList.map(id=>{
      const t=this.getToolById(id);
      return t?`<span class="compare-tray-item">${t.icon} ${t.name} <span class="remove" onclick="APP.toggleCompare('${id}')">×</span></span>`:'';
    }).join('');
    this.updateCompareBadge();
  },
  updateCompareBadge(){
    const badge=document.getElementById('navCompareBadge');
    const n=this.state.compareList.length;
    badge.textContent=n;badge.style.display=n>0?'inline':'none';
  },
  openComparator(){
    if(this.state.compareList.length<2){alert('Select at least 2 tools to compare.');return}
    this.renderComparatorTable();
    const _co=document.getElementById('comparatorOverlay');_co.classList.add('open');
    document.body.style.overflow='hidden';
    this._trapFocus(_co);
  },
  closeComparator(){
    const _co=document.getElementById('comparatorOverlay');_co.classList.remove('open');
    document.body.style.overflow='';
    this._releaseFocus(_co);
  },
  openPage(id){
    const map={contact:'pageContact',legal:'pageLegal',privacy:'pagePrivacy',submit:'pageSubmit'};
    const el=document.getElementById(map[id]);
    if(el){el.classList.add('open');document.body.style.overflow='hidden';this._trapFocus(el)}
  },
  closePage(id){
    const map={contact:'pageContact',legal:'pageLegal',privacy:'pagePrivacy',submit:'pageSubmit'};
    const el=document.getElementById(map[id]);
    if(el){el.classList.remove('open');document.body.style.overflow='';this._releaseFocus(el)}
  },
  renderComparatorTable(){
    const tools=this.state.compareList.map(id=>this.getToolById(id)).filter(Boolean);
    const allFeatures=[...new Set(tools.flatMap(t=>t.features))];
    const table=document.getElementById('comparatorTable');
    let html='<thead><tr><th></th>';
    tools.forEach(t=>{html+=`<th><div class="comparator-tool-header"><span class="comparator-tool-icon">${t.icon}</span><span class="comparator-tool-name">${t.name}</span></div></th>`});
    html+='</tr></thead><tbody>';
    const rows=[
      {label:'Developer',fn:t=>t.company},
      {label:'Launch',fn:t=>t.launchYear},
      {label:'Price',fn:t=>`<span class="pricing-badge ${t.pricing}">${t.pricing}</span>`},
      {label:'Pricing',fn:t=>`<span style="font-size:.75rem">${t.pricingNote}</span>`},
      {label:'Rating',fn:t=>`<span style="color:var(--star-filled)">${this.stars(t.rating)} ${t.rating}</span>`},
      {label:'Platforms',fn:t=>t.platforms.map(p=>`<span class="infobox-platform">${p}</span>`).join(' ')},
    ];
    rows.forEach(r=>{html+=`<tr><td>${r.label}</td>`;tools.forEach(t=>{html+=`<td>${r.fn(t)}</td>`});html+='</tr>'});
    allFeatures.slice(0,12).forEach(f=>{
      html+=`<tr><td style="font-size:.8rem">${f}</td>`;
      tools.forEach(t=>{html+=`<td>${t.features.includes(f)?'<span class="comp-check">✓</span>':'<span class="comp-cross">✗</span>'}</td>`});
      html+='</tr>';
    });
    html+=`<tr><td>Verdict</td>`;tools.forEach(t=>{html+=`<td style="font-style:italic;font-size:.82rem;color:var(--ink-secondary)">"${t.verdict}"</td>`});html+='</tr>';
    html+='</tbody>';table.innerHTML=html;
  },

  // --- Search overlay ---
  openSearch(){
    const _so=document.getElementById('searchOverlay');_so.classList.add('open');
    const input=document.getElementById('searchModalInput');input.value='';input.focus();
    this.renderSearchResults('');
    this._trapFocus(_so);
  },
  closeSearch(){const _so=document.getElementById('searchOverlay');_so.classList.remove('open');this._releaseFocus(_so)},
  renderSearchResults(query){
    const container=document.getElementById('searchResults');
    if(!query){container.innerHTML='<div class="search-empty">Type to search among '+TOOLS.length+' AI tools</div>';return}
    const results=this.searchTools(query,TOOLS).slice(0,8);
    if(!results.length){const esc=query.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');container.innerHTML='<div class="search-empty">No results for "'+esc+'"</div>';return}
    container.innerHTML=results.map(t=>{
      const cat=this.getCatById(t.category);
      return`<a class="search-result-item" href="/en/${t.id}/" onclick="event.preventDefault();APP.closeSearch();APP.openTool('${t.id}')" style="text-decoration:none;color:inherit">
        <span class="search-result-icon">${t.icon}</span>
        <div><div class="search-result-name">${t.name}</div><div class="search-result-cat">${cat?cat.name:''}</div></div>
        <div class="search-result-meta"><span class="pricing-badge ${t.pricing}" style="font-size:.6rem">${t.pricing}</span></div>
      </a>`;
    }).join('');
  },

  // --- Newsletter ---
  submitNewsletter(e){
    e.preventDefault();
    const form=document.getElementById('newsletterForm');
    const btn=form.querySelector('button');
    btn.disabled=true;btn.textContent='Sending...';
    fetch('/api/submit.php',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},
      body:new URLSearchParams(new FormData(form)).toString()
    }).then(r=>{
      if(r.ok){form.style.display='none';document.getElementById('newsletterSuccess').style.display='block';}
      else{throw new Error('err');}
    }).catch(()=>{
      document.getElementById('newsletterError').style.display='block';
      btn.disabled=false;btn.textContent='Subscribe';
    });
  },
  submitForm(e,formId,btnLabel){
    e.preventDefault();
    const form=document.getElementById(formId);
    const btn=form.querySelector('button[type=submit]');
    const origLabel=btnLabel||btn.textContent;
    btn.disabled=true;btn.textContent='Sending...';
    fetch('/api/submit.php',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},
      body:new URLSearchParams(new FormData(form)).toString()
    }).then(r=>{
      if(r.ok){
        form.querySelector('.form-success').style.display='block';
        btn.style.display='none';
        Array.from(form.querySelectorAll('input:not([type=hidden]),textarea,select')).forEach(el=>el.disabled=true);
      } else{throw new Error('err');}
    }).catch(()=>{
      const err=form.querySelector('.form-error');if(err)err.style.display='block';
      btn.disabled=false;btn.textContent=origLabel;
    });
  },

  // --- Scroll helpers ---
  scrollTo(id){document.getElementById(id)?.scrollIntoView({behavior:'smooth'})},

  // --- Toast notification ---
  showToast(icon,msg){
    let t=document.getElementById('toastNotif');
    if(!t){t=document.createElement('div');t.id='toastNotif';t.className='toast';document.body.appendChild(t)}
    t.innerHTML=`<span class="toast-icon">${icon}</span>${msg}`;
    t.classList.add('visible');
    clearTimeout(this._toastTimer);
    this._toastTimer=setTimeout(()=>t.classList.remove('visible'),2500);
  },

  // --- Skeleton loading ---
  renderSkeletons(n=12){
    return Array(n).fill('').map(()=>`<div class="skeleton-card"><div class="skeleton-icon"></div><div class="skeleton-line w60"></div><div class="skeleton-line w80"></div><div class="skeleton-line w40"></div></div>`).join('');
  },

  // --- Animated Counters ---
  animateCounters(){
    document.querySelectorAll('.hero-stat .num[data-count]').forEach(el=>{
      const target=parseInt(el.dataset.count,10);
      const duration=1800;
      const start=performance.now();
      const step=(now)=>{
        const elapsed=now-start;
        const progress=Math.min(elapsed/duration,1);
        const ease=1-Math.pow(1-progress,3);
        el.textContent=Math.round(target*ease);
        if(progress<1)requestAnimationFrame(step);
        else el.textContent=target;
      };
      requestAnimationFrame(step);
    });
  },

  // --- Dark/Light Theme ---
  toggleTheme(){
    const html=document.documentElement;
    const current=html.getAttribute('data-theme');
    const next=current==='dark'?'light':'dark';
    html.setAttribute('data-theme',next);
    document.getElementById('themeToggle').textContent=next==='dark'?'☀️':'🌙';
    try{localStorage.setItem('bible-theme',next)}catch(e){}
  },
  restoreTheme(){
    try{
      const t=localStorage.getItem('bible-theme');
      if(t){document.documentElement.setAttribute('data-theme',t);document.getElementById('themeToggle').textContent=t==='dark'?'☀️':'🌙'}
    }catch(e){}
  },

  // --- Favorites ---
  toggleFav(id){
    const idx=this.state.favorites.indexOf(id);
    const t=this.getToolById(id);
    if(idx>-1){this.state.favorites.splice(idx,1);this.showToast('💔',`${t?t.name:'Tool'} removed from favorites`)}
    else{this.state.favorites.push(id);this.showToast('❤️',`${t?t.name:'Tool'} added to favorites`)}
    this.renderCatalog();this.updateFavCount();
    try{localStorage.setItem('bible-favs',JSON.stringify(this.state.favorites))}catch(e){}
  },
  updateFavCount(){
    const badge=document.getElementById('navFavCount');
    if(!badge)return;
    const n=this.state.favorites.length;
    badge.textContent=n;badge.style.display=n>0?'inline-block':'none';
  },
  showFavorites(){
    if(this.state.favorites.length===0){
      alert('No favorites yet. Click ♡ to add a tool.');return;
    }
    this.state.filters={categories:[],pricing:[],platforms:[],minRating:0};
    this.state.search='';this.state.currentPage=1;
    const filtered=TOOLS.filter(t=>this.state.favorites.includes(t.id));
    const grid=document.getElementById('toolsGrid');
    const count=document.getElementById('resultsCount');
    grid.innerHTML=filtered.map(t=>this.renderToolCard(t)).join('');
    count.textContent=filtered.length+' favorite'+(filtered.length>1?'s':'');
    document.getElementById('loadMoreBtn').style.display='none';
    document.getElementById('catalogue').scrollIntoView({behavior:'smooth'});
  },

  // --- Share/Export ---
  shareUrl(platform,toolId,toolName){
    const url=encodeURIComponent(window.location.origin+'/en/'+toolId+'/');
    const text=encodeURIComponent(toolName+' — Discover this AI tool on The AI Bible');
    let shareLink='';
    switch(platform){
      case 'twitter':shareLink='https://twitter.com/intent/tweet?url='+url+'&text='+text;break;
      case 'linkedin':shareLink='https://www.linkedin.com/sharing/share-offsite/?url='+url;break;
      case 'facebook':shareLink='https://www.facebook.com/sharer/sharer.php?u='+url;break;
      case 'whatsapp':shareLink='https://wa.me/?text='+text+'%20'+url;break;
      case 'telegram':shareLink='https://t.me/share/url?url='+url+'&text='+text;break;
    }
    if(shareLink)window.open(shareLink,'_blank','noopener,width=600,height=400');
  },
  copyLink(toolId,btn){
    const url=window.location.origin+'/en/'+toolId+'/';
    navigator.clipboard.writeText(url).then(()=>{
      this.showToast('🔗','Link copied to clipboard');
      btn.classList.add('share-btn-copied');
      setTimeout(()=>btn.classList.remove('share-btn-copied'),2000);
    }).catch(()=>{prompt('Copy this link:',url)});
  },

  // --- Route handling ---
  handleRoute(){
    const hash=location.hash.slice(1);
    if(!hash)return;
    const m=hash.match(/^\/tool\/(.+)$/);
    if(m&&m[1])setTimeout(()=>this.openTool(m[1]),300);
    const mc=hash.match(/^\/category\/(.+)$/);
    if(mc&&mc[1])setTimeout(()=>this.filterByCategory(mc[1]),300);
  },


  // --- Focus Trap for Modals ---
  _trapFocus(el){
    const focusable=el.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])');
    if(!focusable.length)return;
    const first=focusable[0],last=focusable[focusable.length-1];
    this._trapHandler=e=>{
      if(e.key!=='Tab')return;
      if(e.shiftKey){if(document.activeElement===first){e.preventDefault();last.focus()}}
      else{if(document.activeElement===last){e.preventDefault();first.focus()}}
    };
    el.addEventListener('keydown',this._trapHandler);
    first.focus();
  },
  _releaseFocus(el){
    if(this._trapHandler)el.removeEventListener('keydown',this._trapHandler);
  },

  // --- Init ---
  init(){
    // Restore state
    try{
      const v=localStorage.getItem('bible-view');if(v)this.state.view=v;
      const c=localStorage.getItem('bible-compare');if(c)this.state.compareList=JSON.parse(c);
      const f=localStorage.getItem('bible-favs');if(f)this.state.favorites=JSON.parse(f);
    }catch(e){}
    // Restore theme
    this.restoreTheme();
    this.renderHeroCats();
    this.renderTOC();
    this.renderToolOfDay();
    this.renderFeatured();
    this.renderFilters();
    this.renderCatalog();
    this.renderCompareTray();
    this.renderTrends();
    this.renderVersus();
    this.renderBlog();
    this.renderFooterCats();
    this.handleRoute();
    this.updateFavCount();
    // View toggle
    if(this.state.view==='list')this.setView('list');
    // Animate hero counters on scroll
    const heroObs=new IntersectionObserver(entries=>{
      entries.forEach(e=>{if(e.isIntersecting){this.animateCounters();heroObs.disconnect()}});
    },{threshold:.3});
    const heroStats=document.querySelector('.hero-stats');
    if(heroStats)heroObs.observe(heroStats);
    // Init scroll-reveal observer after all dynamic content is rendered
    const observer=new IntersectionObserver(entries=>{
      entries.forEach(e=>{if(e.isIntersecting)e.target.classList.add('visible')});
    },{threshold:.1});
    document.querySelectorAll('.reveal').forEach(el=>observer.observe(el));
  }
};

// --- Global events ---
let _scrollTicking=false;
window.addEventListener('scroll',()=>{
  if(_scrollTicking)return;
  _scrollTicking=true;
  requestAnimationFrame(()=>{
    const h=document.documentElement.scrollHeight-window.innerHeight;
    document.getElementById('scrollProgress').style.width=(window.scrollY/h)*100+'%';
    const nav=document.getElementById('nav');
    if(window.scrollY>400)nav.classList.add('visible');else nav.classList.remove('visible');
    _scrollTicking=false;
  });
});
/* observer is initialized inside APP.init() after dynamic rendering */
document.addEventListener('keydown',e=>{
  if((e.metaKey||e.ctrlKey)&&e.key==='k'){e.preventDefault();APP.openSearch()}
  if(e.key==='Escape'){APP.closeSearch();APP.closeTool();APP.closeComparator();['contact','legal','privacy','submit'].forEach(p=>APP.closePage(p))}
});
document.getElementById('heroSearchInput').addEventListener('focus',function(){this.blur();APP.openSearch()});
document.getElementById('searchModalInput').addEventListener('input',function(){APP.renderSearchResults(this.value)});
window.addEventListener('hashchange',()=>APP.handleRoute());
document.addEventListener('DOMContentLoaded',()=>APP.init());

    // Register Service Worker
    if('serviceWorker' in navigator){navigator.serviceWorker.register('/sw.js').catch(()=>{})}