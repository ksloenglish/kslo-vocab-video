"""Safe text layout for every Miss K encouragement bubble.

Measure actual glyph bounds, shrink to fit a padded rectangle, and reject
unreadable/oversized copy instead of clipping it. Shared by render and preflight.
"""
from PIL import Image, ImageDraw

BUBBLE_W, BUBBLE_H = 1000, 300
BUBBLE_X, BUBBLE_Y = 150, 330
HEAD_RECT = (64, 48, 936, 166)
SUB_RECT = (64, 190, 936, 268)
SINGLE_RECT = (64, 80, 936, 220)
HEAD_MAX, HEAD_MIN = 128, 72
SUB_MAX, SUB_MIN = 50, 32


class PopupTextOverflow(ValueError):
    pass


def split_line(line):
    if '! ' in line:
        headline, subtitle = line.split('! ', 1)
        return headline + '!', subtitle
    if '. ' in line:
        headline, subtitle = line.split('. ', 1)
        return headline + '.', subtitle
    return line, ''


def glyph_sprite(text, face, color):
    """Rasterize with bearing-aware padding; return complete, uncropped ink."""
    left, top, right, bottom = face.getbbox(text, anchor='ls')
    guard = 8
    image = Image.new('RGBA', (max(1, right - left) + 2 * guard,
                               max(1, bottom - top) + 2 * guard), (0, 0, 0, 0))
    ImageDraw.Draw(image).text((guard - left, guard - top), text,
                              font=face, fill=color, anchor='ls')
    bbox = image.getchannel('A').getbbox()
    if bbox is None:
        raise PopupTextOverflow('Pop-up text has no visible glyphs.')
    if bbox[0] <= 0 or bbox[1] <= 0 or bbox[2] >= image.width or bbox[3] >= image.height:
        raise PopupTextOverflow('Font glyphs exceed their measured raster bounds.')
    return image.crop(bbox)


def fit_line(text, font_loader, font_key, color, rect, max_size, min_size, role):
    left, top, right, bottom = rect
    max_width, max_height = right - left, bottom - top
    for size in range(max_size, min_size - 1, -1):
        image = glyph_sprite(text, font_loader(font_key, size), color)
        if image.width <= max_width and image.height <= max_height:
            x = left + (max_width - image.width) // 2
            y = top + (max_height - image.height) // 2
            ink = (x, y, x + image.width, y + image.height)
            assert left <= ink[0] < ink[2] <= right
            assert top <= ink[1] < ink[3] <= bottom
            return image, dict(role=role, text=text, font_size=size,
                               safe_rect=list(rect), ink_bounds=list(ink), x=x, y=y)
    raise PopupTextOverflow(
        f'{role} does not fit {max_width}x{max_height} px at readable minimum '
        f'{min_size}px: {text!r}. Shorten or redesign the copy, show a mockup, '
        'and get approval; never crop, truncate, or silently hide words.')


def build_popup_text(line, font_loader, navy=(12, 28, 62), coral=(255, 112, 104)):
    headline, subtitle = split_line(line)
    if not headline.strip():
        raise PopupTextOverflow('An encouragement headline cannot be empty.')
    layer = Image.new('RGBA', (BUBBLE_W, BUBBLE_H), (0, 0, 0, 0))
    specifications = [('headline', headline.upper(), 'bebas', navy,
                       HEAD_RECT if subtitle else SINGLE_RECT, HEAD_MAX, HEAD_MIN)]
    if subtitle:
        specifications.append(('subtitle', subtitle, 'bold', coral,
                               SUB_RECT, SUB_MAX, SUB_MIN))
    placements = []
    for role, text, key, color, rect, maximum, minimum in specifications:
        image, metrics = fit_line(text, font_loader, key, color + (255,),
                                  rect, maximum, minimum, role)
        layer.alpha_composite(image, (metrics['x'], metrics['y']))
        placements.append(metrics)
    return layer, placements


def validate_popup_lines(lines, font_loader):
    """Validate all library messages, including ones absent from this unit."""
    report = {}
    for key, line in lines.items():
        _, placements = build_popup_text(line, font_loader)
        report[key] = placements
    return report
