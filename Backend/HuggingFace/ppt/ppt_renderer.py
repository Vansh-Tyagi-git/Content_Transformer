from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.dml import MSO_LINE_DASH_STYLE


# ============================================================
# DESIGN SYSTEM
# ============================================================

COLOR_MAP = {
    "navy": "#17365D",
    "blue": "#2F75B5",
    "light blue": "#D9EAF7",
    "sky": "#5B9BD5",
    "teal": "#159A9C",
    "green": "#2E7D32",
    "red": "#C62828",
    "orange": "#ED7D31",
    "purple": "#8064A2",
    "dark": "#1F2937",
    "gray": "#6B7280",
    "light gray": "#F3F6F9",
    "white": "#FFFFFF",
    "black": "#111827",
}


def hex_to_rgb(hex_color):
    """
    Convert #RRGGBB to RGBColor.
    """
    hex_color = hex_color.replace("#", "")

    return RGBColor(
        int(hex_color[0:2], 16),
        int(hex_color[2:4], 16),
        int(hex_color[4:6], 16)
    )


def resolve_color(value, fallback):
    """
    Resolve a named color or hex color.
    """

    if not value:
        return fallback

    value = str(value).strip().lower()

    if value in COLOR_MAP:
        return hex_to_rgb(COLOR_MAP[value])

    if value.startswith("#") and len(value) == 7:
        return hex_to_rgb(value)

    return fallback


# ============================================================
# DEFAULT THEME
# ============================================================

DEFAULT_THEME = {
    "primary": hex_to_rgb(COLOR_MAP["navy"]),
    "accent": hex_to_rgb(COLOR_MAP["blue"]),
    "secondary": hex_to_rgb(COLOR_MAP["light blue"]),
    "dark": hex_to_rgb(COLOR_MAP["dark"]),
    "gray": hex_to_rgb(COLOR_MAP["gray"]),
    "light": hex_to_rgb(COLOR_MAP["light gray"]),
    "white": hex_to_rgb(COLOR_MAP["white"]),
    "black": hex_to_rgb(COLOR_MAP["black"]),
    "green": hex_to_rgb(COLOR_MAP["green"]),
    "red": hex_to_rgb(COLOR_MAP["red"]),
    "orange": hex_to_rgb(COLOR_MAP["orange"]),
    "purple": hex_to_rgb(COLOR_MAP["purple"]),
}


# ============================================================
# PRESENTATION DIMENSIONS
# ============================================================

SLIDE_WIDTH = 13.333
SLIDE_HEIGHT = 7.5

MARGIN_LEFT = 0.65
MARGIN_RIGHT = 0.65


# ============================================================
# THEME BUILDER
# ============================================================

def build_theme(presentation_data):
    """
    Build presentation theme from design_metadata.
    """

    theme = DEFAULT_THEME.copy()

    design = presentation_data.get(
        "design_metadata",
        {}
    )

    theme["primary"] = resolve_color(
        design.get("primary_color"),
        theme["primary"]
    )

    theme["accent"] = resolve_color(
        design.get("accent_color"),
        theme["accent"]
    )

    theme["secondary"] = resolve_color(
        design.get("secondary_color"),
        theme["secondary"]
    )

    return theme


# ============================================================
# BASIC SHAPE HELPERS
# ============================================================

def set_background(slide, color):
    """
    Set slide background.
    """

    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_rectangle(
    slide,
    x,
    y,
    width,
    height,
    fill_color,
    radius=False,
    line_color=None,
    transparency=0
):
    """
    Add rectangle / rounded rectangle.
    """

    shape_type = (
        MSO_SHAPE.ROUNDED_RECTANGLE
        if radius
        else MSO_SHAPE.RECTANGLE
    )

    shape = slide.shapes.add_shape(
        shape_type,
        Inches(x),
        Inches(y),
        Inches(width),
        Inches(height)
    )

    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color

    if transparency:
        shape.fill.transparency = transparency

    if line_color:
        shape.line.color.rgb = line_color
    else:
        shape.line.fill.background()

    return shape


def add_circle(
    slide,
    x,
    y,
    diameter,
    fill_color,
    line_color=None
):
    """
    Add circle.
    """

    shape = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(x),
        Inches(y),
        Inches(diameter),
        Inches(diameter)
    )

    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color

    if line_color:
        shape.line.color.rgb = line_color
    else:
        shape.line.fill.background()

    return shape


# ============================================================
# TEXT HELPERS
# ============================================================

def add_text(
    slide,
    text,
    x,
    y,
    width,
    height,
    font_size=18,
    bold=False,
    color=None,
    alignment=PP_ALIGN.LEFT,
    font_name="Aptos",
    valign=MSO_ANCHOR.TOP,
    margin_left=0,
    margin_right=0,
    margin_top=0,
    margin_bottom=0
):
    """
    Add a formatted text box.
    """

    textbox = slide.shapes.add_textbox(
        Inches(x),
        Inches(y),
        Inches(width),
        Inches(height)
    )

    text_frame = textbox.text_frame

    text_frame.clear()
    text_frame.word_wrap = True

    text_frame.margin_left = Inches(margin_left)
    text_frame.margin_right = Inches(margin_right)
    text_frame.margin_top = Inches(margin_top)
    text_frame.margin_bottom = Inches(margin_bottom)

    text_frame.vertical_anchor = valign

    paragraph = text_frame.paragraphs[0]
    paragraph.text = str(text)
    paragraph.alignment = alignment

    if paragraph.runs:

        run = paragraph.runs[0]

        run.font.name = font_name
        run.font.size = Pt(font_size)
        run.font.bold = bold

        if color:
            run.font.color.rgb = color

    return textbox


def add_multiline_text(
    slide,
    lines,
    x,
    y,
    width,
    height,
    font_size=18,
    color=None,
    bullet=False,
    spacing=5
):
    """
    Add multiple lines.
    """

    textbox = slide.shapes.add_textbox(
        Inches(x),
        Inches(y),
        Inches(width),
        Inches(height)
    )

    frame = textbox.text_frame

    frame.clear()
    frame.word_wrap = True

    frame.margin_left = Inches(0)
    frame.margin_right = Inches(0)
    frame.margin_top = Inches(0)
    frame.margin_bottom = Inches(0)

    for index, line in enumerate(lines):

        if index == 0:
            paragraph = frame.paragraphs[0]
        else:
            paragraph = frame.add_paragraph()

        paragraph.text = str(line)

        if bullet:
            paragraph.text = f"• {line}"

        paragraph.space_after = Pt(spacing)

        if paragraph.runs:

            run = paragraph.runs[0]

            run.font.name = "Aptos"
            run.font.size = Pt(font_size)

            if color:
                run.font.color.rgb = color

    return textbox


# ============================================================
# SLIDE HEADER
# ============================================================

def add_slide_header(
    slide,
    slide_data,
    theme,
    slide_number=None
):
    """
    Modern slide header.
    """

    kicker = slide_data.get(
        "kicker",
        ""
    )

    title = slide_data.get(
        "title",
        ""
    )

    if kicker:

        add_text(
            slide,
            kicker.upper(),
            0.72,
            0.35,
            11.5,
            0.25,
            font_size=10,
            bold=True,
            color=theme["accent"]
        )

    title_y = 0.55 if kicker else 0.45

    add_text(
        slide,
        title,
        0.72,
        title_y,
        11.7,
        0.65,
        font_size=27,
        bold=True,
        color=theme["dark"]
    )

    # Accent line

    add_rectangle(
        slide,
        0.72,
        title_y + 0.68,
        0.8,
        0.055,
        theme["accent"]
    )

    if slide_number is not None:

        add_text(
            slide,
            f"{slide_number:02d}",
            12.0,
            0.42,
            0.65,
            0.3,
            font_size=10,
            bold=True,
            color=theme["gray"],
            alignment=PP_ALIGN.RIGHT
        )


# ============================================================
# FOOTER
# ============================================================

def add_footer(
    slide,
    slide_data,
    theme
):
    """
    Small source/takeaway footer.
    """

    source = slide_data.get(
        "source_reference",
        ""
    )

    if source:

        add_text(
            slide,
            source,
            0.72,
            7.08,
            6,
            0.2,
            font_size=8,
            color=theme["gray"]
        )


# ============================================================
# ICON SYSTEM
# ============================================================

def get_icon(index):
    """
    Simple editable visual symbols.

    These are deliberately text-based so the PPT remains
    completely editable and does not depend on external
    image assets.
    """

    icons = [
        "✓",
        "↗",
        "⚙",
        "◆",
        "●",
        "✓",
        "!",
        "◎",
        "→",
        "★",
    ]

    return icons[index % len(icons)]


def add_icon_badge(
    slide,
    x,
    y,
    color,
    index,
    diameter=0.55
):
    """
    Add a circular icon badge.
    """

    add_circle(
        slide,
        x,
        y,
        diameter,
        color
    )

    add_text(
        slide,
        get_icon(index),
        x,
        y + 0.01,
        diameter,
        diameter - 0.02,
        font_size=17,
        bold=True,
        color=DEFAULT_THEME["white"],
        alignment=PP_ALIGN.CENTER,
        valign=MSO_ANCHOR.MIDDLE
    )


# ============================================================
# CONTENT NORMALIZATION
# ============================================================

def normalize_content(content):
    """
    Convert content into consistent dictionaries.
    """

    if not content:
        return []

    normalized = []

    for item in content:

        if isinstance(item, dict):

            normalized.append({
                "title": str(
                    item.get("title", "")
                ),
                "description": str(
                    item.get("description", "")
                )
            })

        else:

            normalized.append({
                "title": "",
                "description": str(item)
            })

    return normalized


# ============================================================
# TAKEAWAY
# ============================================================

def add_takeaway(
    slide,
    takeaway,
    theme,
    x=0.72,
    y=6.35,
    width=11.9,
    height=0.55
):
    """
    Add a subtle takeaway banner.
    """

    if not takeaway:
        return

    add_rectangle(
        slide,
        x,
        y,
        width,
        height,
        theme["light"],
        radius=True
    )

    add_rectangle(
        slide,
        x,
        y,
        0.08,
        height,
        theme["accent"]
    )

    add_text(
        slide,
        takeaway,
        x + 0.25,
        y + 0.08,
        width - 0.45,
        height - 0.12,
        font_size=11,
        color=theme["dark"],
        valign=MSO_ANCHOR.MIDDLE
    )


# ============================================================
# TITLE SLIDE
# ============================================================

def create_title_slide(
    prs,
    slide_data,
    presentation_data,
    theme
):
    """
    Modern executive title slide.
    """

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    set_background(
        slide,
        theme["primary"]
    )

    # Decorative side panel

    add_rectangle(
        slide,
        0,
        0,
        0.22,
        SLIDE_HEIGHT,
        theme["accent"]
    )

    # Decorative circles

    add_circle(
        slide,
        10.7,
        -1.2,
        4.5,
        theme["accent"]
    )

    add_circle(
        slide,
        11.6,
        5.8,
        2.5,
        theme["secondary"]
    )

    # Small kicker

    kicker = slide_data.get(
        "kicker",
        ""
    )

    if kicker:

        add_text(
            slide,
            kicker.upper(),
            0.95,
            1.2,
            6,
            0.3,
            font_size=11,
            bold=True,
            color=theme["secondary"]
        )

    title = (
        slide_data.get("title")
        or presentation_data.get(
            "presentation_title",
            "Presentation"
        )
    )

    subtitle = (
        slide_data.get("subtitle")
        or presentation_data.get(
            "presentation_subtitle",
            ""
        )
    )

    # Main title

    add_text(
        slide,
        title,
        0.95,
        2.05,
        9.6,
        1.45,
        font_size=39,
        bold=True,
        color=theme["white"],
        valign=MSO_ANCHOR.MIDDLE
    )

    # Accent line

    add_rectangle(
        slide,
        0.95,
        3.7,
        1.15,
        0.07,
        theme["accent"]
    )

    if subtitle:

        add_text(
            slide,
            subtitle,
            0.95,
            4.05,
            8.8,
            0.7,
            font_size=19,
            color=theme["secondary"]
        )

    # Summary

    summary = presentation_data.get(
        "presentation_summary",
        ""
    )

    if summary:

        add_text(
            slide,
            summary,
            0.95,
            5.0,
            8.8,
            0.9,
            font_size=13,
            color=theme["white"]
        )

    # Theme label

    design = presentation_data.get(
        "design_metadata",
        {}
    )

    style = design.get(
        "presentation_style",
        ""
    )

    if style:

        add_text(
            slide,
            style.upper(),
            10.65,
            6.55,
            1.9,
            0.25,
            font_size=8,
            bold=True,
            color=theme["white"],
            alignment=PP_ALIGN.RIGHT
        )

    return slide


# ============================================================
# KEY POINTS
# ============================================================

def create_key_points_slide(
    prs,
    slide_data,
    theme
):
    """
    Turn key points into visual cards.
    """

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    set_background(
        slide,
        theme["white"]
    )

    add_slide_header(
        slide,
        slide_data,
        theme,
        slide_data.get("slide_number")
    )

    items = normalize_content(
        slide_data.get("content", [])
    )

    count = len(items)

    if count == 0:
        return slide

    # --------------------------------------------------------
    # 2 items
    # --------------------------------------------------------

    if count == 2:

        card_width = 5.7

        for index, item in enumerate(items):

            x = 0.72 + index * 6.0

            add_content_card(
                slide,
                item,
                x,
                1.75,
                card_width,
                3.9,
                theme,
                index
            )

    # --------------------------------------------------------
    # 3 items
    # --------------------------------------------------------

    elif count == 3:

        card_width = 3.75

        for index, item in enumerate(items):

            x = 0.72 + index * 4.1

            add_content_card(
                slide,
                item,
                x,
                1.75,
                card_width,
                3.9,
                theme,
                index
            )

    # --------------------------------------------------------
    # 4 items
    # --------------------------------------------------------

    else:

        card_width = 5.7

        for index, item in enumerate(items[:4]):

            row = index // 2
            col = index % 2

            x = 0.72 + col * 6.0
            y = 1.65 + row * 2.35

            add_content_card(
                slide,
                item,
                x,
                y,
                card_width,
                2.0,
                theme,
                index,
                compact=True
            )

    add_takeaway(
        slide,
        slide_data.get("takeaway", ""),
        theme
    )

    return slide


# ============================================================
# CONTENT CARD
# ============================================================

def add_content_card(
    slide,
    item,
    x,
    y,
    width,
    height,
    theme,
    index,
    compact=False
):
    """
    Premium content card.
    """

    # Shadow-like background

    add_rectangle(
        slide,
        x + 0.04,
        y + 0.05,
        width,
        height,
        RGBColor(225, 230, 235),
        radius=True
    )

    # Main card

    add_rectangle(
        slide,
        x,
        y,
        width,
        height,
        theme["light"],
        radius=True
    )

    # Accent strip

    add_rectangle(
        slide,
        x,
        y,
        0.07,
        height,
        theme["accent"]
    )

    # Icon

    add_icon_badge(
        slide,
        x + 0.3,
        y + 0.3,
        theme["accent"],
        index
    )

    title = item.get(
        "title",
        ""
    )

    description = item.get(
        "description",
        ""
    )

    if title:

        add_text(
            slide,
            title,
            x + 1.0,
            y + 0.3,
            width - 1.3,
            0.5,
            font_size=18 if not compact else 15,
            bold=True,
            color=theme["dark"]
        )

    if description:

        add_text(
            slide,
            description,
            x + 0.35,
            y + 1.05 if not compact else y + 0.92,
            width - 0.7,
            height - 1.3,
            font_size=14 if not compact else 11,
            color=theme["gray"]
        )


# ============================================================
# TWO COLUMN
# ============================================================

def create_two_column_slide(
    prs,
    slide_data,
    theme
):
    """
    Executive two-column composition.
    """

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    set_background(
        slide,
        theme["white"]
    )

    add_slide_header(
        slide,
        slide_data,
        theme,
        slide_data.get("slide_number")
    )

    left = normalize_content(
        slide_data.get("left_content", [])
    )

    right = normalize_content(
        slide_data.get("right_content", [])
    )

    add_column_panel(
        slide,
        left,
        0.72,
        1.75,
        5.75,
        4.35,
        theme,
        "01",
        "FOCUS"
    )

    add_column_panel(
        slide,
        right,
        6.85,
        1.75,
        5.75,
        4.35,
        theme,
        "02",
        "FOCUS"
    )

    add_takeaway(
        slide,
        slide_data.get("takeaway", ""),
        theme
    )

    return slide


def add_column_panel(
    slide,
    items,
    x,
    y,
    width,
    height,
    theme,
    number,
    label
):
    """
    Large column panel.
    """

    add_rectangle(
        slide,
        x,
        y,
        width,
        height,
        theme["light"],
        radius=True
    )

    add_circle(
        slide,
        x + 0.3,
        y + 0.3,
        0.5,
        theme["primary"]
    )

    add_text(
        slide,
        number,
        x + 0.3,
        y + 0.31,
        0.5,
        0.45,
        font_size=10,
        bold=True,
        color=theme["white"],
        alignment=PP_ALIGN.CENTER,
        valign=MSO_ANCHOR.MIDDLE
    )

    add_text(
        slide,
        label,
        x + 1.0,
        y + 0.32,
        width - 1.3,
        0.35,
        font_size=10,
        bold=True,
        color=theme["accent"]
    )

    current_y = y + 1.05

    for index, item in enumerate(items[:5]):

        title = item.get("title", "")
        description = item.get("description", "")

        if title:

            add_text(
                slide,
                title,
                x + 0.35,
                current_y,
                width - 0.7,
                0.35,
                font_size=16,
                bold=True,
                color=theme["dark"]
            )

            current_y += 0.4

        add_text(
            slide,
            description,
            x + 0.35,
            current_y,
            width - 0.7,
            0.65,
            font_size=12,
            color=theme["gray"]
        )

        current_y += 0.9


# ============================================================
# COMPARISON
# ============================================================

def create_comparison_slide(
    prs,
    slide_data,
    theme
):
    """
    Comparison with contrasting visual panels.
    """

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    set_background(
        slide,
        theme["white"]
    )

    add_slide_header(
        slide,
        slide_data,
        theme,
        slide_data.get("slide_number")
    )

    left = normalize_content(
        slide_data.get("left_content", [])
    )

    right = normalize_content(
        slide_data.get("right_content", [])
    )

    add_rectangle(
        slide,
        0.7,
        1.65,
        5.85,
        4.6,
        RGBColor(237, 244, 251),
        radius=True
    )

    add_rectangle(
        slide,
        6.78,
        1.65,
        5.85,
        4.6,
        RGBColor(252, 241, 241),
        radius=True
    )

    # Center divider

    add_rectangle(
        slide,
        6.55,
        2.1,
        0.22,
        3.7,
        theme["white"]
    )

    add_text(
        slide,
        "A",
        0.95,
        1.95,
        0.5,
        0.4,
        font_size=13,
        bold=True,
        color=theme["primary"]
    )

    add_text(
        slide,
        "B",
        7.03,
        1.95,
        0.5,
        0.4,
        font_size=13,
        bold=True,
        color=theme["red"]
    )

    render_simple_items(
        slide,
        left,
        1.0,
        2.55,
        5.15,
        theme,
        color=theme["primary"]
    )

    render_simple_items(
        slide,
        right,
        7.08,
        2.55,
        5.15,
        theme,
        color=theme["red"]
    )

    add_takeaway(
        slide,
        slide_data.get("takeaway", ""),
        theme
    )

    return slide


def render_simple_items(
    slide,
    items,
    x,
    y,
    width,
    theme,
    color
):
    """
    Render comparison items.
    """

    current_y = y

    for index, item in enumerate(items[:5]):

        add_icon_badge(
            slide,
            x,
            current_y,
            color,
            index,
            diameter=0.38
        )

        title = item.get("title", "")
        description = item.get("description", "")

        text = (
            f"{title}: {description}"
            if title
            else description
        )

        add_text(
            slide,
            text,
            x + 0.58,
            current_y - 0.01,
            width - 0.6,
            0.75,
            font_size=13,
            color=theme["dark"]
        )

        current_y += 0.75


# ============================================================
# THREE COLUMN
# ============================================================

def create_three_column_slide(
    prs,
    slide_data,
    theme
):
    """
    Three-card executive layout.
    """

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    set_background(
        slide,
        theme["white"]
    )

    add_slide_header(
        slide,
        slide_data,
        theme,
        slide_data.get("slide_number")
    )

    items = normalize_content(
        slide_data.get("content", [])
    )

    card_width = 3.75

    for index, item in enumerate(items[:3]):

        add_content_card(
            slide,
            item,
            0.72 + index * 4.1,
            1.8,
            card_width,
            3.85,
            theme,
            index
        )

    add_takeaway(
        slide,
        slide_data.get("takeaway", ""),
        theme
    )

    return slide


# ============================================================
# PROCESS
# ============================================================

def create_process_slide(
    prs,
    slide_data,
    theme
):
    """
    Horizontal process diagram.
    """

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    set_background(
        slide,
        theme["white"]
    )

    add_slide_header(
        slide,
        slide_data,
        theme,
        slide_data.get("slide_number")
    )

    items = normalize_content(
        slide_data.get("content", [])
    )

    count = len(items)

    if count == 0:
        return slide

    # Connector line

    add_rectangle(
        slide,
        1.25,
        3.45,
        10.8,
        0.05,
        theme["secondary"]
    )

    step_width = 11.3 / count

    for index, item in enumerate(items):

        x = 0.85 + index * step_width

        # Number

        add_circle(
            slide,
            x + 0.65,
            3.05,
            0.8,
            theme["primary"]
        )

        add_text(
            slide,
            str(index + 1),
            x + 0.65,
            3.12,
            0.8,
            0.5,
            font_size=17,
            bold=True,
            color=theme["white"],
            alignment=PP_ALIGN.CENTER
        )

        title = item.get(
            "title",
            ""
        )

        description = item.get(
            "description",
            ""
        )

        if title:

            add_text(
                slide,
                title,
                x,
                2.05,
                2.15,
                0.55,
                font_size=15,
                bold=True,
                color=theme["dark"],
                alignment=PP_ALIGN.CENTER
            )

        add_text(
            slide,
            description,
            x,
            4.05,
            2.15,
            1.15,
            font_size=11,
            color=theme["gray"],
            alignment=PP_ALIGN.CENTER
        )

    add_takeaway(
        slide,
        slide_data.get("takeaway", ""),
        theme
    )

    return slide


# ============================================================
# TIMELINE
# ============================================================

def create_timeline_slide(
    prs,
    slide_data,
    theme
):
    """
    Modern timeline.
    """

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    set_background(
        slide,
        theme["white"]
    )

    add_slide_header(
        slide,
        slide_data,
        theme,
        slide_data.get("slide_number")
    )

    events = normalize_content(
        slide_data.get("content", [])
    )

    if not events:
        return slide

    y_line = 3.55

    add_rectangle(
        slide,
        1.0,
        y_line,
        11.2,
        0.055,
        theme["accent"]
    )

    count = len(events)

    spacing = (
        10.7 / max(count - 1, 1)
    )

    for index, event in enumerate(events):

        x = 1.0 + index * spacing

        add_circle(
            slide,
            x,
            y_line - 0.25,
            0.55,
            theme["primary"]
        )

        title = event.get(
            "title",
            ""
        )

        description = event.get(
            "description",
            ""
        )

        # Alternate above/below

        if index % 2 == 0:

            text_y = 1.9

        else:

            text_y = 4.05

        add_text(
            slide,
            title,
            x - 0.45,
            text_y,
            1.45,
            0.45,
            font_size=13,
            bold=True,
            color=theme["dark"],
            alignment=PP_ALIGN.CENTER
        )

        add_text(
            slide,
            description,
            x - 0.65,
            text_y + 0.5,
            1.85,
            0.8,
            font_size=10,
            color=theme["gray"],
            alignment=PP_ALIGN.CENTER
        )

    add_takeaway(
        slide,
        slide_data.get("takeaway", ""),
        theme
    )

    return slide


# ============================================================
# STATISTICS
# ============================================================

def create_statistics_slide(
    prs,
    slide_data,
    theme
):
    """
    Large-number statistics layout.
    """

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    set_background(
        slide,
        theme["white"]
    )

    add_slide_header(
        slide,
        slide_data,
        theme,
        slide_data.get("slide_number")
    )

    statistics = slide_data.get(
        "content",
        []
    )

    if not statistics:
        return slide

    count = len(statistics)

    card_width = 11.9 / min(count, 4)

    for index, stat in enumerate(statistics[:4]):

        x = 0.72 + index * card_width

        add_rectangle(
            slide,
            x,
            1.8,
            card_width - 0.2,
            3.7,
            theme["light"],
            radius=True
        )

        if isinstance(stat, dict):

            value = stat.get(
                "value",
                ""
            )

            label = stat.get(
                "label",
                ""
            )

        else:

            value = str(stat)
            label = ""

        add_text(
            slide,
            value,
            x + 0.15,
            2.35,
            card_width - 0.5,
            0.9,
            font_size=31,
            bold=True,
            color=theme["primary"],
            alignment=PP_ALIGN.CENTER
        )

        add_text(
            slide,
            label,
            x + 0.2,
            3.45,
            card_width - 0.6,
            1.0,
            font_size=13,
            color=theme["gray"],
            alignment=PP_ALIGN.CENTER
        )

    add_takeaway(
        slide,
        slide_data.get("takeaway", ""),
        theme
    )

    return slide


# ============================================================
# QUOTE
# ============================================================

def create_quote_slide(
    prs,
    slide_data,
    theme
):
    """
    Quote layout.
    """

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    set_background(
        slide,
        theme["primary"]
    )

    kicker = slide_data.get(
        "kicker",
        "QUOTE"
    )

    add_text(
        slide,
        kicker.upper(),
        0.8,
        0.55,
        3,
        0.3,
        font_size=10,
        bold=True,
        color=theme["secondary"]
    )

    content = slide_data.get(
        "content",
        []
    )

    if isinstance(content, list):

        quote = " ".join(
            str(item)
            for item in content
        )

    else:

        quote = str(content)

    add_text(
        slide,
        "“",
        1.0,
        1.55,
        1.0,
        1.0,
        font_size=70,
        bold=True,
        color=theme["accent"]
    )

    add_text(
        slide,
        quote,
        1.65,
        2.05,
        10.0,
        2.5,
        font_size=27,
        color=theme["white"],
        alignment=PP_ALIGN.CENTER,
        valign=MSO_ANCHOR.MIDDLE
    )

    return slide


# ============================================================
# RECOMMENDATIONS
# ============================================================

def create_recommendations_slide(
    prs,
    slide_data,
    theme
):
    """
    Recommendations as action cards.
    """

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    set_background(
        slide,
        theme["white"]
    )

    add_slide_header(
        slide,
        slide_data,
        theme,
        slide_data.get("slide_number")
    )

    items = normalize_content(
        slide_data.get("content", [])
    )

    current_y = 1.75

    for index, item in enumerate(items[:5]):

        add_circle(
            slide,
            0.8,
            current_y,
            0.55,
            theme["primary"]
        )

        add_text(
            slide,
            str(index + 1),
            0.8,
            current_y + 0.04,
            0.55,
            0.4,
            font_size=12,
            bold=True,
            color=theme["white"],
            alignment=PP_ALIGN.CENTER
        )

        title = item.get(
            "title",
            ""
        )

        description = item.get(
            "description",
            ""
        )

        if title:

            add_text(
                slide,
                title,
                1.65,
                current_y - 0.02,
                3.8,
                0.35,
                font_size=16,
                bold=True,
                color=theme["dark"]
            )

            add_text(
                slide,
                description,
                5.0,
                current_y - 0.02,
                7.2,
                0.55,
                font_size=13,
                color=theme["gray"]
            )

        else:

            add_text(
                slide,
                description,
                1.65,
                current_y,
                10.2,
                0.55,
                font_size=15,
                color=theme["dark"]
            )

        current_y += 0.9

    add_takeaway(
        slide,
        slide_data.get("takeaway", ""),
        theme
    )

    return slide


# ============================================================
# GOVERNANCE / VISUAL PROCESS
# ============================================================

def create_governance_visual(
    prs,
    slide_data,
    theme
):
    """
    Specialized visual composition for governance /
    responsible AI type slides.

    This is useful when the LLM asks for a process visual
    but the source does not provide literal process steps.
    """

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    set_background(
        slide,
        theme["white"]
    )

    add_slide_header(
        slide,
        slide_data,
        theme,
        slide_data.get("slide_number")
    )

    # Left side: concept

    add_rectangle(
        slide,
        0.75,
        1.75,
        4.0,
        4.25,
        theme["light"],
        radius=True
    )

    add_circle(
        slide,
        2.05,
        2.35,
        1.4,
        theme["primary"]
    )

    add_text(
        slide,
        "AI",
        2.05,
        2.68,
        1.4,
        0.5,
        font_size=23,
        bold=True,
        color=theme["white"],
        alignment=PP_ALIGN.CENTER
    )

    add_text(
        slide,
        "Responsible\nImplementation",
        1.25,
        4.05,
        3.0,
        0.9,
        font_size=20,
        bold=True,
        color=theme["dark"],
        alignment=PP_ALIGN.CENTER
    )

    # Right side: governance pillars

    content = normalize_content(
        slide_data.get("content", [])
    )

    x = 5.35
    y = 1.75

    for index, item in enumerate(content[:4]):

        add_content_card(
            slide,
            item,
            x,
            y,
            3.55,
            1.85,
            theme,
            index,
            compact=True
        )

        x += 3.75

        if index == 1:

            x = 5.35
            y = 3.9

    add_takeaway(
        slide,
        slide_data.get("takeaway", ""),
        theme
    )

    return slide


# ============================================================
# CONCLUSION
# ============================================================

def create_conclusion_slide(
    prs,
    slide_data,
    theme
):
    """
    Strong executive conclusion.
    """

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    set_background(
        slide,
        theme["primary"]
    )

    # Accent block

    add_rectangle(
        slide,
        0,
        0,
        0.22,
        7.5,
        theme["accent"]
    )

    kicker = slide_data.get(
        "kicker",
        "CONCLUSION"
    )

    add_text(
        slide,
        kicker.upper(),
        0.9,
        0.75,
        3.0,
        0.3,
        font_size=10,
        bold=True,
        color=theme["secondary"]
    )

    title = slide_data.get(
        "title",
        "Key Takeaway"
    )

    add_text(
        slide,
        title,
        0.9,
        1.35,
        10.8,
        0.9,
        font_size=34,
        bold=True,
        color=theme["white"]
    )

    content = normalize_content(
        slide_data.get("content", [])
    )

    if content:

        description = content[0].get(
            "description",
            ""
        )

    else:

        description = ""

    add_rectangle(
        slide,
        0.9,
        2.7,
        11.2,
        2.25,
        RGBColor(255, 255, 255),
        radius=True
    )

    add_text(
        slide,
        description,
        1.35,
        3.15,
        10.3,
        1.35,
        font_size=22,
        bold=False,
        color=theme["dark"],
        alignment=PP_ALIGN.CENTER,
        valign=MSO_ANCHOR.MIDDLE
    )

    takeaway = slide_data.get(
        "takeaway",
        ""
    )

    if takeaway:

        add_text(
            slide,
            takeaway,
            1.2,
            5.55,
            10.8,
            0.7,
            font_size=15,
            bold=True,
            color=theme["secondary"],
            alignment=PP_ALIGN.CENTER
        )

    return slide


# ============================================================
# VISUAL TYPE DETECTION
# ============================================================

def should_use_governance_visual(
    slide_data
):
    """
    Detect slides where a diagram is more useful than
    ordinary cards.
    """

    visual = slide_data.get(
        "visual",
        {}
    )

    visual_type = str(
        visual.get("type", "")
    ).lower()

    description = str(
        visual.get("description", "")
    ).lower()

    if visual_type == "process":
        return True

    governance_words = [
        "governance",
        "responsible",
        "framework",
        "structured process",
    ]

    return any(
        word in description
        for word in governance_words
    )


# ============================================================
# SLIDE ROUTER
# ============================================================

def create_slide(
    prs,
    slide_data,
    presentation_data,
    theme
):
    """
    Main slide router.
    """

    layout = slide_data.get(
        "layout",
        "key_points"
    )

    if layout == "title":

        return create_title_slide(
            prs,
            slide_data,
            presentation_data,
            theme
        )

    if layout == "key_points":

        if should_use_governance_visual(
            slide_data
        ):

            return create_governance_visual(
                prs,
                slide_data,
                theme
            )

        return create_key_points_slide(
            prs,
            slide_data,
            theme
        )

    if layout == "two_column":

        return create_two_column_slide(
            prs,
            slide_data,
            theme
        )

    if layout == "three_column":

        return create_three_column_slide(
            prs,
            slide_data,
            theme
        )

    if layout == "comparison":

        return create_comparison_slide(
            prs,
            slide_data,
            theme
        )

    if layout == "process":

        return create_process_slide(
            prs,
            slide_data,
            theme
        )

    if layout == "timeline":

        return create_timeline_slide(
            prs,
            slide_data,
            theme
        )

    if layout == "statistics":

        return create_statistics_slide(
            prs,
            slide_data,
            theme
        )

    if layout == "quote":

        return create_quote_slide(
            prs,
            slide_data,
            theme
        )

    if layout == "recommendations":

        return create_recommendations_slide(
            prs,
            slide_data,
            theme
        )

    if layout == "conclusion":

        return create_conclusion_slide(
            prs,
            slide_data,
            theme
        )

    return create_key_points_slide(
        prs,
        slide_data,
        theme
    )


# ============================================================
# VALIDATION
# ============================================================

def validate_presentation_data(
    presentation_data
):
    """
    Validate the generated JSON before rendering.
    """

    if not isinstance(
        presentation_data,
        dict
    ):
        raise ValueError(
            "presentation_data must be a dictionary"
        )

    if not presentation_data.get(
        "presentation_title"
    ):
        raise ValueError(
            "Missing presentation_title"
        )

    slides = presentation_data.get(
        "slides"
    )

    if not isinstance(
        slides,
        list
    ) or not slides:

        raise ValueError(
            "Presentation contains no slides"
        )

    for index, slide in enumerate(slides):

        if not isinstance(
            slide,
            dict
        ):

            raise ValueError(
                f"Slide {index + 1} must be an object"
            )

        if "layout" not in slide:

            raise ValueError(
                f"Slide {index + 1} missing layout"
            )

        if "title" not in slide:

            raise ValueError(
                f"Slide {index + 1} missing title"
            )


# ============================================================
# MAIN RENDER FUNCTION
# ============================================================

def render_ppt(
    presentation_data,
    output_path
):
    """
    Render the AI-generated presentation JSON into
    a polished, editable PowerPoint presentation.
    """

    validate_presentation_data(
        presentation_data
    )

    theme = build_theme(
        presentation_data
    )

    prs = Presentation()

    # 16:9 widescreen

    prs.slide_width = Inches(
        SLIDE_WIDTH
    )

    prs.slide_height = Inches(
        SLIDE_HEIGHT
    )

    slides = presentation_data[
        "slides"
    ]

    for slide_data in slides:

        create_slide(
            prs,
            slide_data,
            presentation_data,
            theme
        )

        # Footer

        layout = slide_data.get(
            "layout"
        )

        if layout != "title":

            # The slide was just added.

            current_slide = prs.slides[-1]

            add_footer(
                current_slide,
                slide_data,
                theme
            )

    prs.save(
        output_path
    )

    return output_path