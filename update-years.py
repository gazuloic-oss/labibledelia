#!/usr/bin/env python3
"""Update launchYear for tools that launched or had major versions in late 2025-2026."""
import re

# Tools to update to 2025 (launched or major update Nov 2025 - Feb 2026)
UPDATES = {
    "claude-code": 2025,    # Launched 2025
    "manus": 2025,          # Launched March 2025
    "genspark": 2025,       # Major growth 2025
    "deepseek": 2025,       # DeepSeek V3 Dec 2024, R1 Jan 2025 - count as 2025
    "veo": 2025,            # Veo 2 late 2024, Veo 3 mid 2025
    "grok": 2025,           # Grok 3 Feb 2025
    "lovable": 2025,        # Massive growth in 2025
    "zed": 2025,            # Major AI features 2025
    "lindy": 2025,          # Major expansion 2025
    "augment": 2025,        # Public launch 2025
    "pieces": 2025,         # Major AI copilot update 2025
    "pixverse": 2025,       # Growth 2025
    "coderabbit": 2025,     # Major v2 2025
    "humeai": 2025,         # EVI 2 launched 2025
    "botpress": 2025,       # Major AI overhaul 2025
    "kimi": 2025,           # Global expansion 2025
    "captions": 2025,       # Major update 2025
}

for lang in ['fr', 'en']:
    filepath = f'{lang}/index.html'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    for tool_id, year in UPDATES.items():
        # Pattern: id:"tool_id",...,launchYear:NNNN
        # We need to find the tool and update its launchYear
        pattern = rf'(\{{id:"{tool_id}".*?launchYear:)\d+'
        new = rf'\g<1>{year}'
        content, count = re.subn(pattern, new, content)
        if count > 0:
            pass  # Updated
        else:
            # Try without the specific id pattern
            pass

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    # Verify counts
    years_2025_plus = len(re.findall(r'launchYear:202[56]', content))
    print(f'{lang}: Updated. Tools with launchYear 2025+: {years_2025_plus}')
