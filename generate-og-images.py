#!/usr/bin/env python3
"""Generate Open Graph social sharing images for La Bible de l'IA (FR + EN)"""

from PIL import Image, ImageDraw, ImageFont
import os, math

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Brand colors
BG_COLOR = (26, 26, 46)        # #1a1a2e
GOLD = (201, 168, 76)           # #c9a84c
GOLD_LIGHT = (228, 199, 107)    # #e4c76b
WHITE = (255, 255, 255)
CREAM = (250, 248, 243)         # #faf8f3
TEXT_SECONDARY = (180, 180, 200)

def draw_diamond(draw, cx, cy, size, fill, opacity_layer=None):
    """Draw a diamond shape"""
    points = [
        (cx, cy - size),
        (cx + size * 0.6, cy),
        (cx, cy + size),
        (cx - size * 0.6, cy),
    ]
    draw.polygon(points, fill=fill)

def draw_grain_texture(img, intensity=15):
    """Add subtle grain texture"""
    import random
    random.seed(42)
    pixels = img.load()
    w, h = img.size
    for _ in range(w * h // 8):
        x = random.randint(0, w - 1)
        y = random.randint(0, h - 1)
        r, g, b = pixels[x, y][:3]
        noise = random.randint(-intensity, intensity)
        pixels[x, y] = (
            max(0, min(255, r + noise)),
            max(0, min(255, g + noise)),
            max(0, min(255, b + noise)),
        )

def draw_decorative_lines(draw, width, height):
    """Draw subtle decorative grid lines"""
    line_color = (40, 40, 65, 30)
    # Horizontal lines
    for y in range(0, height, 80):
        draw.line([(0, y), (width, y)], fill=(40, 40, 65), width=1)
    # Vertical lines
    for x in range(0, width, 80):
        draw.line([(x, 0), (x, height)], fill=(40, 40, 65), width=1)

def get_font(size, bold=False):
    """Get a font - try system fonts, fallback to default"""
    font_names = []
    if bold:
        font_names = [
            "C:/Windows/Fonts/georgiab.ttf",    # Georgia Bold
            "C:/Windows/Fonts/timesbd.ttf",      # Times New Roman Bold
            "C:/Windows/Fonts/arialbd.ttf",      # Arial Bold
        ]
    else:
        font_names = [
            "C:/Windows/Fonts/georgia.ttf",      # Georgia
            "C:/Windows/Fonts/times.ttf",         # Times New Roman
            "C:/Windows/Fonts/arial.ttf",          # Arial
        ]

    for font_path in font_names:
        try:
            return ImageFont.truetype(font_path, size)
        except (IOError, OSError):
            continue

    return ImageFont.load_default()

def generate_og_image(lang='fr', size=(1200, 630)):
    """Generate an OG image for the specified language"""
    width, height = size
    img = Image.new('RGB', (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # Background decorative grid
    draw_decorative_lines(draw, width, height)

    # Decorative diamonds scattered
    diamond_positions = [
        (100, 80, 25), (1100, 100, 20), (150, 550, 18),
        (1050, 530, 22), (950, 150, 15), (250, 180, 12),
        (800, 500, 16), (500, 80, 14), (700, 560, 13),
    ]
    for dx, dy, ds in diamond_positions:
        x = int(dx * width / 1200)
        y = int(dy * height / 630)
        # Faded gold diamonds
        faded_gold = (201, 168, 76)
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        points = [
            (x, y - ds),
            (x + int(ds * 0.6), y),
            (x, y + ds),
            (x - int(ds * 0.6), y),
        ]
        overlay_draw.polygon(points, fill=(201, 168, 76, 25))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)

    # Gold accent line at top
    draw.rectangle([(0, 0), (width, 4)], fill=GOLD)

    # Gold accent line at bottom
    draw.rectangle([(0, height - 4), (width, height)], fill=GOLD)

    # Central content area with subtle border
    margin_x = 80
    margin_y = 60
    # Subtle inner border
    border_rect = [margin_x, margin_y, width - margin_x, height - margin_y]
    draw.rectangle(border_rect, outline=(201, 168, 76, 40), width=1)

    # Corner ornaments (small L-shapes in gold)
    corner_size = 20
    corner_thickness = 2
    corners = [
        (margin_x, margin_y),                           # top-left
        (width - margin_x, margin_y),                   # top-right
        (margin_x, height - margin_y),                  # bottom-left
        (width - margin_x, height - margin_y),          # bottom-right
    ]

    # Top-left corner
    draw.line([(margin_x, margin_y), (margin_x + corner_size, margin_y)], fill=GOLD, width=corner_thickness)
    draw.line([(margin_x, margin_y), (margin_x, margin_y + corner_size)], fill=GOLD, width=corner_thickness)
    # Top-right corner
    draw.line([(width - margin_x, margin_y), (width - margin_x - corner_size, margin_y)], fill=GOLD, width=corner_thickness)
    draw.line([(width - margin_x, margin_y), (width - margin_x, margin_y + corner_size)], fill=GOLD, width=corner_thickness)
    # Bottom-left corner
    draw.line([(margin_x, height - margin_y), (margin_x + corner_size, height - margin_y)], fill=GOLD, width=corner_thickness)
    draw.line([(margin_x, height - margin_y), (margin_x, height - margin_y - corner_size)], fill=GOLD, width=corner_thickness)
    # Bottom-right corner
    draw.line([(width - margin_x, height - margin_y), (width - margin_x - corner_size, height - margin_y)], fill=GOLD, width=corner_thickness)
    draw.line([(width - margin_x, height - margin_y), (width - margin_x, height - margin_y - corner_size)], fill=GOLD, width=corner_thickness)

    # Central diamond icon (large, decorative)
    center_x = width // 2
    diamond_y = 180
    diamond_size = 55

    # Diamond glow effect
    for i in range(3, 0, -1):
        glow_size = diamond_size + i * 8
        glow_alpha = 15 - i * 4
        overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        pts = [
            (center_x, diamond_y - glow_size),
            (center_x + int(glow_size * 0.6), diamond_y),
            (center_x, diamond_y + glow_size),
            (center_x - int(glow_size * 0.6), diamond_y),
        ]
        od.polygon(pts, fill=(228, 199, 107, glow_alpha))
        img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
        draw = ImageDraw.Draw(img)

    # Main diamond
    pts = [
        (center_x, diamond_y - diamond_size),
        (center_x + int(diamond_size * 0.6), diamond_y),
        (center_x, diamond_y + diamond_size),
        (center_x - int(diamond_size * 0.6), diamond_y),
    ]
    draw.polygon(pts, fill=GOLD)

    # Diamond highlight
    pts_highlight = [
        (center_x, diamond_y - diamond_size + 5),
        (center_x + int(diamond_size * 0.3), diamond_y - 5),
        (center_x, diamond_y + 5),
        (center_x - int(diamond_size * 0.3), diamond_y - 5),
    ]
    draw.polygon(pts_highlight, fill=GOLD_LIGHT)

    # Title
    if lang == 'fr':
        title = "La Bible de l'IA"
        subtitle = "L'encyclopédie complète des outils\nd'intelligence artificielle"
        stats = "200 outils  •  16 catégories  •  71 comparatifs"
        url = "labibledelia.com"
    else:
        title = "The AI Bible"
        subtitle = "The complete encyclopedia\nof artificial intelligence tools"
        stats = "200 tools  •  16 categories  •  71 comparisons"
        url = "labibledelia.com/en"

    # Title font
    font_title = get_font(62, bold=True)
    font_subtitle = get_font(26, bold=False)
    font_stats = get_font(20, bold=True)
    font_url = get_font(18, bold=False)

    # Title
    title_y = 260
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    draw.text((center_x - tw // 2, title_y), title, fill=CREAM, font=font_title)

    # Decorative separator under title
    sep_y = title_y + 75
    sep_width = 200
    draw.line([(center_x - sep_width // 2, sep_y), (center_x + sep_width // 2, sep_y)], fill=GOLD, width=2)
    # Small diamond in center of separator
    sep_diamond = 6
    draw.polygon([
        (center_x, sep_y - sep_diamond),
        (center_x + sep_diamond, sep_y),
        (center_x, sep_y + sep_diamond),
        (center_x - sep_diamond, sep_y),
    ], fill=GOLD)

    # Subtitle
    subtitle_y = sep_y + 20
    for i, line in enumerate(subtitle.split('\n')):
        bbox = draw.textbbox((0, 0), line, font=font_subtitle)
        lw = bbox[2] - bbox[0]
        draw.text((center_x - lw // 2, subtitle_y + i * 34), line, fill=TEXT_SECONDARY, font=font_subtitle)

    # Stats bar
    stats_y = height - margin_y - 65

    # Stats background bar
    draw.rectangle([(margin_x + 1, stats_y - 5), (width - margin_x - 1, stats_y + 35)], fill=(30, 30, 55))

    bbox = draw.textbbox((0, 0), stats, font=font_stats)
    sw = bbox[2] - bbox[0]
    draw.text((center_x - sw // 2, stats_y), stats, fill=GOLD, font=font_stats)

    # URL in bottom corner
    bbox = draw.textbbox((0, 0), url, font=font_url)
    uw = bbox[2] - bbox[0]
    draw.text((width - margin_x - uw - 15, height - margin_y + 10), url, fill=(120, 120, 150), font=font_url)

    # Add grain texture
    draw_grain_texture(img, intensity=8)

    return img


def generate_twitter_image(lang='fr'):
    """Generate Twitter card image (1200x675 - 16:9)"""
    return generate_og_image(lang=lang, size=(1200, 675))


if __name__ == '__main__':
    output_dir = SCRIPT_DIR

    # Generate FR images
    print("Generating og-image-fr.png (1200x630)...")
    img_fr = generate_og_image(lang='fr', size=(1200, 630))
    img_fr.save(os.path.join(output_dir, 'og-image-fr.png'), 'PNG', optimize=True)

    # Generate EN images
    print("Generating og-image-en.png (1200x630)...")
    img_en = generate_og_image(lang='en', size=(1200, 630))
    img_en.save(os.path.join(output_dir, 'og-image-en.png'), 'PNG', optimize=True)

    # Generate Twitter variants
    print("Generating twitter-image-fr.png (1200x675)...")
    tw_fr = generate_twitter_image(lang='fr')
    tw_fr.save(os.path.join(output_dir, 'twitter-image-fr.png'), 'PNG', optimize=True)

    print("Generating twitter-image-en.png (1200x675)...")
    tw_en = generate_twitter_image(lang='en')
    tw_en.save(os.path.join(output_dir, 'twitter-image-en.png'), 'PNG', optimize=True)

    # Report sizes
    for f in ['og-image-fr.png', 'og-image-en.png', 'twitter-image-fr.png', 'twitter-image-en.png']:
        path = os.path.join(output_dir, f)
        size_kb = os.path.getsize(path) / 1024
        print(f"  {f}: {size_kb:.1f} KB")

    print("\nDone! All OG images generated.")
