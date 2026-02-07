#!/usr/bin/env python3
"""
Refactoring script for La Bible de l'IA:
1. Extract TOOLS array into tools-fr.json / tools-en.json
2. Extract CSS into shared styles.css
3. Extract JS into app-fr.js / app-en.js
4. Add role="dialog" + aria-modal + focus trap to modals
5. Throttle scroll listener, replace pageYOffset with scrollY
6. Create basic Service Worker
7. Rebuild HTML files with external references
"""
import os
import re
import json

BASE = os.path.dirname(os.path.abspath(__file__))

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"  Written: {path} ({len(content):,} bytes)")

def extract_tools_json(html, lang):
    """Extract the TOOLS array from HTML and save as JSON."""
    # Find the TOOLS array between "const TOOLS = [" and "];\n"
    match = re.search(r'const TOOLS\s*=\s*\[', html)
    if not match:
        print(f"  WARNING: TOOLS array not found in {lang}")
        return html, None

    start = match.start()
    # Find the matching closing bracket
    bracket_start = html.index('[', start)
    depth = 0
    i = bracket_start
    while i < len(html):
        if html[i] == '[':
            depth += 1
        elif html[i] == ']':
            depth -= 1
            if depth == 0:
                break
        i += 1

    tools_str = html[bracket_start:i+1]
    # The JS array ends with "];" - we need just the array
    end_pos = i + 1
    # Skip the semicolon after ]
    while end_pos < len(html) and html[end_pos] in ';\n\r ':
        end_pos += 1

    # Parse the JS array - it uses unquoted keys, so we need to convert to valid JSON
    # Add quotes around unquoted keys
    json_str = re.sub(r'(?<=[{,])\s*([a-zA-Z_]\w*)\s*:', r' "\1":', tools_str)
    # Replace single quotes with double quotes (but not inside already double-quoted strings)
    # This is tricky - let's just use a direct approach

    # Actually, let's save as JS module instead for simplicity and avoid JSON parsing issues
    tools_js_content = f"const TOOLS = {tools_str};\n"

    # Replace the TOOLS definition in HTML with a reference
    # Find the full block: "const TOOLS = [...];""
    full_match = html[start:end_pos]
    new_html = html[:start] + "/* TOOLS loaded from external file */\n" + html[end_pos:]

    return new_html, tools_js_content

def extract_css(html):
    """Extract the <style> block from HTML."""
    match = re.search(r'<style>\s*(.*?)\s*</style>', html, re.DOTALL)
    if not match:
        return html, None

    css_content = match.group(1)
    # Replace the <style> block with a <link> to external CSS
    new_html = html[:match.start()] + '<link rel="stylesheet" href="/styles.css">' + html[match.end():]

    return new_html, css_content

def extract_js(html, lang):
    """Extract the <script> block (the main APP engine) from HTML."""
    # Find the main script block (the one with CATEGORIES and APP)
    # It starts after the search overlay and before </body>
    match = re.search(r'<script>\s*/\*\s*={10,}.*?DATA \+ ENGINE.*?={10,}\s*\*/(.*?)</script>', html, re.DOTALL)
    if not match:
        print(f"  WARNING: Main script block not found in {lang}")
        return html, None

    js_content = match.group(1).strip()

    # Replace with external script reference
    # We need the TOOLS file loaded first, then the app
    tools_file = f"/tools-{lang}.js"
    app_file = f"/app-{lang}.js"

    new_html = (html[:match.start()] +
                f'<script src="{tools_file}"></script>\n' +
                f'<script src="{app_file}"></script>' +
                html[match.end():])

    return new_html, js_content

def add_dialog_roles(html):
    """Add role='dialog' and aria-modal='true' to modal overlays."""
    # Tool detail modal
    html = html.replace(
        '<div class="modal-overlay" id="modalOverlay"',
        '<div class="modal-overlay" id="modalOverlay" role="dialog" aria-modal="true" aria-label="Tool details"'
    )
    # Search overlay
    html = html.replace(
        '<div class="search-overlay" id="searchOverlay"',
        '<div class="search-overlay" id="searchOverlay" role="dialog" aria-modal="true" aria-label="Search"'
    )
    # Comparator overlay
    html = html.replace(
        '<div class="comparator-overlay" id="comparatorOverlay"',
        '<div class="comparator-overlay" id="comparatorOverlay" role="dialog" aria-modal="true" aria-label="Comparator"'
    )
    # Page overlays (contact, legal, privacy, submit)
    for page_id in ['pageContact', 'pageLegal', 'pagePrivacy', 'pageSubmit']:
        html = html.replace(
            f'<div class="page-overlay" id="{page_id}"',
            f'<div class="page-overlay" id="{page_id}" role="dialog" aria-modal="true"'
        )
    return html

def add_focus_trap_to_js(js_content):
    """Add focus trap utility and integrate it into modal open/close functions."""

    focus_trap_code = """
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
"""

    # Insert focus trap methods before the init method
    js_content = js_content.replace(
        '  // --- Init ---\n  init(){',
        focus_trap_code + '\n  // --- Init ---\n  init(){'
    )

    # Add focus trap to openTool
    js_content = js_content.replace(
        "document.getElementById('modalOverlay').classList.add('open');\n    document.body.style.overflow='hidden';",
        "const _overlay=document.getElementById('modalOverlay');_overlay.classList.add('open');\n    document.body.style.overflow='hidden';\n    this._trapFocus(_overlay);"
    )

    # Add release to closeTool
    js_content = js_content.replace(
        "document.getElementById('modalOverlay').classList.remove('open');\n    document.body.style.overflow='';",
        "const _overlay=document.getElementById('modalOverlay');_overlay.classList.remove('open');\n    document.body.style.overflow='';\n    this._releaseFocus(_overlay);"
    )

    # Add focus trap to openSearch
    js_content = js_content.replace(
        "document.getElementById('searchOverlay').classList.add('open');",
        "const _so=document.getElementById('searchOverlay');_so.classList.add('open');"
    )
    # Fix the input focus line that follows
    js_content = js_content.replace(
        "const _so=document.getElementById('searchOverlay');_so.classList.add('open');\n    const input=document.getElementById('searchModalInput');input.value='';input.focus();\n    this.renderSearchResults('');",
        "const _so=document.getElementById('searchOverlay');_so.classList.add('open');\n    const input=document.getElementById('searchModalInput');input.value='';input.focus();\n    this.renderSearchResults('');\n    this._trapFocus(_so);"
    )

    # Add release to closeSearch
    js_content = js_content.replace(
        "closeSearch(){document.getElementById('searchOverlay').classList.remove('open')}",
        "closeSearch(){const _so=document.getElementById('searchOverlay');_so.classList.remove('open');this._releaseFocus(_so)}"
    )

    # Add focus trap to openComparator
    js_content = js_content.replace(
        "document.getElementById('comparatorOverlay').classList.add('open');\n    document.body.style.overflow='hidden';",
        "const _co=document.getElementById('comparatorOverlay');_co.classList.add('open');\n    document.body.style.overflow='hidden';\n    this._trapFocus(_co);"
    )

    # Add release to closeComparator
    js_content = js_content.replace(
        "document.getElementById('comparatorOverlay').classList.remove('open');\n    document.body.style.overflow='';",
        "const _co=document.getElementById('comparatorOverlay');_co.classList.remove('open');\n    document.body.style.overflow='';\n    this._releaseFocus(_co);"
    )

    # Add focus trap to openPage
    js_content = js_content.replace(
        "if(el){el.classList.add('open');document.body.style.overflow='hidden'}",
        "if(el){el.classList.add('open');document.body.style.overflow='hidden';this._trapFocus(el)}"
    )

    # Add release to closePage
    js_content = js_content.replace(
        "if(el){el.classList.remove('open');document.body.style.overflow=''}",
        "if(el){el.classList.remove('open');document.body.style.overflow='';this._releaseFocus(el)}"
    )

    return js_content

def fix_scroll_listener(js_content):
    """Replace pageYOffset with scrollY and add rAF throttle."""
    old_scroll = """// --- Global events ---
window.addEventListener('scroll',()=>{
  const h=document.documentElement.scrollHeight-window.innerHeight;
  document.getElementById('scrollProgress').style.width=(window.pageYOffset/h)*100+'%';
  const nav=document.getElementById('nav');
  if(window.pageYOffset>400)nav.classList.add('visible');else nav.classList.remove('visible');
});"""

    new_scroll = """// --- Global events ---
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
});"""

    return js_content.replace(old_scroll, new_scroll)

def create_service_worker():
    """Create a basic Service Worker for offline cache."""
    return """// Service Worker — La Bible de l'IA
const CACHE_NAME = 'bible-ia-v1';
const STATIC_ASSETS = [
  '/styles.css',
  '/favicon.svg',
  '/manifest.json'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  // Network-first for HTML, cache-first for static assets
  const url = new URL(event.request.url);
  if (event.request.destination === 'document') {
    event.respondWith(
      fetch(event.request).catch(() => caches.match(event.request))
    );
  } else if (STATIC_ASSETS.some(a => url.pathname === a) || url.pathname.endsWith('.js') || url.pathname.endsWith('.css')) {
    event.respondWith(
      caches.match(event.request).then(cached =>
        cached || fetch(event.request).then(response => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
          return response;
        })
      )
    );
  } else {
    event.respondWith(fetch(event.request));
  }
});
"""

def add_sw_registration(js_content):
    """Add Service Worker registration to the init function."""
    sw_reg = """
    // Register Service Worker
    if('serviceWorker' in navigator){navigator.serviceWorker.register('/sw.js').catch(()=>{})}"""

    # Add after the hashchange listener
    js_content = js_content.replace(
        "document.addEventListener('DOMContentLoaded',()=>APP.init());",
        "document.addEventListener('DOMContentLoaded',()=>APP.init());\n" + sw_reg
    )
    return js_content

def process_lang(lang):
    """Process one language version."""
    print(f"\n{'='*60}")
    print(f"Processing {lang.upper()} version")
    print(f"{'='*60}")

    html_path = os.path.join(BASE, lang, 'index.html')
    html = read_file(html_path)
    original_size = len(html)
    print(f"  Original HTML: {original_size:,} bytes")

    # 1. Extract CSS
    print("\n  [1/6] Extracting CSS...")
    html, css_content = extract_css(html)
    if css_content:
        # Only write CSS once (shared between FR and EN)
        css_path = os.path.join(BASE, 'styles.css')
        if lang == 'fr':  # Write CSS only on first pass
            write_file(css_path, css_content)
        print(f"  CSS extracted: {len(css_content):,} bytes")

    # 2. Extract TOOLS
    print("\n  [2/6] Extracting TOOLS...")
    html, tools_content = extract_tools_json(html, lang)
    if tools_content:
        tools_path = os.path.join(BASE, f'tools-{lang}.js')
        write_file(tools_path, tools_content)
        print(f"  TOOLS extracted: {len(tools_content):,} bytes")

    # 3. Extract JS
    print("\n  [3/6] Extracting JS engine...")
    html, js_content = extract_js(html, lang)
    if js_content:
        # 4. Add focus trap
        print("\n  [4/6] Adding focus trap...")
        js_content = add_focus_trap_to_js(js_content)

        # 5. Fix scroll listener
        print("\n  [5/6] Fixing scroll listener...")
        js_content = fix_scroll_listener(js_content)

        # 6. Add SW registration
        print("\n  [6/6] Adding Service Worker registration...")
        js_content = add_sw_registration(js_content)

        app_path = os.path.join(BASE, f'app-{lang}.js')
        write_file(app_path, js_content)

    # Add dialog roles to HTML
    print("\n  Adding role='dialog' to modals...")
    html = add_dialog_roles(html)

    # Write updated HTML
    write_file(html_path, html)
    new_size = len(html)
    saved = original_size - new_size
    print(f"\n  HTML reduced: {original_size:,} -> {new_size:,} bytes (saved {saved:,} bytes / {saved*100//original_size}%)")

def main():
    print("=" * 60)
    print("La Bible de l'IA — Refactoring Script")
    print("=" * 60)

    # Process EN only (FR already done)
    # process_lang('fr')
    process_lang('en')

    # Create Service Worker
    print(f"\n{'='*60}")
    print("Creating Service Worker...")
    sw_path = os.path.join(BASE, 'sw.js')
    write_file(sw_path, create_service_worker())

    # Summary
    print(f"\n{'='*60}")
    print("REFACTORING COMPLETE")
    print(f"{'='*60}")
    print("New files created:")
    print("  /styles.css          — Shared CSS")
    print("  /tools-fr.js         — French TOOLS data")
    print("  /tools-en.js         — English TOOLS data")
    print("  /app-fr.js           — French JS engine")
    print("  /app-en.js           — English JS engine")
    print("  /sw.js               — Service Worker")
    print("\nChanges applied to HTML:")
    print("  - <style> replaced with <link rel='stylesheet' href='/styles.css'>")
    print("  - TOOLS array replaced with <script src='/tools-{lang}.js'>")
    print("  - Main script replaced with <script src='/app-{lang}.js'>")
    print("  - role='dialog' + aria-modal='true' added to 7 modals")
    print("  - Focus trap added to all modal open/close functions")
    print("  - Scroll listener throttled with requestAnimationFrame")
    print("  - pageYOffset replaced with scrollY")
    print("  - Service Worker registration added")

if __name__ == '__main__':
    main()
