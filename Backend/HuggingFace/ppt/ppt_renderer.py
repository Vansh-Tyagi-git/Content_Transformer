from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE


# ============================================================
# PRESENTATION COLORS
# ============================================================

COLORS = {
    "primary": RGBColor(31, 78, 121),
    "secondary": RGBColor(68, 114, 196),
    "accent": RGBColor(91, 155, 213),
    "dark": RGBColor(35, 35, 35),
    "gray": RGBColor(100, 100, 100),
    "light": RGBColor(242, 245, 248),
    "white": RGBColor(255, 255, 255),
    "green": RGBColor(46, 125, 50),
    "red": RGBColor(198, 40, 40),
    "blue_light": RGBColor(235, 242, 250),
    "red_light": RGBColor(245, 235, 235),
}


# ============================================================
# CONSTANTS
# ============================================================

SLIDE_WIDTH = 13.333
SLIDE_HEIGHT = 7.5

CONTENT_TOP = 1.45
CONTENT_BOTTOM = 6.65


# ============================================================
# BASIC HELPERS
# ============================================================

def set_background(
    slide,
    color=COLORS["white"]
):
    """
    Set slide background color.
    """

    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = color


def add_text(
    slide,
    text,
    x,
    y,
    width,
    height,
    font_size=24,
    bold=False,
    color=COLORS["dark"],
    alignment=PP_ALIGN.LEFT,
    valign=MSO_ANCHOR.TOP
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
    text_frame.vertical_anchor = valign
    text_frame.margin_left = Inches(0.03)
    text_frame.margin_right = Inches(0.03)
    text_frame.margin_top = Inches(0.02)
    text_frame.margin_bottom = Inches(0.02)

    paragraph = text_frame.paragraphs[0]

    paragraph.text = str(text)
    paragraph.alignment = alignment

    for run in paragraph.runs:

        run.font.name = "Aptos"
        run.font.size = Pt(font_size)
        run.font.bold = bold
        run.font.color.rgb = color

    return textbox


def add_title(
    slide,
    title
):
    """
    Add standard slide title.
    """

    add_text(
        slide,
        title,
        0.7,
        0.35,
        11.8,
        0.75,
        font_size=28,
        bold=True,
        color=COLORS["primary"],
        valign=MSO_ANCHOR.MIDDLE
    )


def add_footer(
    slide,
    slide_number
):
    """
    Add slide number.
    """

    add_text(
        slide,
        str(slide_number),
        12.25,
        7.05,
        0.45,
        0.25,
        font_size=10,
        color=COLORS["gray"],
        alignment=PP_ALIGN.RIGHT
    )


def add_bullet(
    slide,
    text,
    x,
    y,
    width,
    height,
    font_size=19,
    color=COLORS["dark"]
):
    """
    Add a bullet with automatic text wrapping.
    """

    circle = slide.shapes.add_shape(
        MSO_SHAPE.OVAL,
        Inches(x),
        Inches(y + 0.12),
        Inches(0.18),
        Inches(0.18)
    )

    circle.fill.solid()
    circle.fill.fore_color.rgb = COLORS["accent"]
    circle.line.fill.background()

    add_text(
        slide,
        text,
        x + 0.35,
        y,
        width - 0.35,
        height,
        font_size=font_size,
        color=color
    )


def add_panel(
    slide,
    x,
    y,
    width,
    height,
    color=COLORS["light"],
    line_color=None
):
    """
    Add a rounded panel.
    """

    box = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        Inches(x),
        Inches(y),
        Inches(width),
        Inches(height)
    )

    box.fill.solid()
    box.fill.fore_color.rgb = color

    if line_color:
        box.line.color.rgb = line_color
    else:
        box.line.fill.background()

    return box


# ============================================================
# TITLE SLIDE
# ============================================================

def create_title_slide(
    prs,
    slide_data,
    presentation_data=None
):
    """
    Create title slide.
    """

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    set_background(
        slide,
        COLORS["primary"]
    )

    presentation_data = presentation_data or {}

    title = (
        presentation_data.get(
            "presentation_title"
        )
        or slide_data.get(
            "title",
            "Presentation"
        )
    )

    subtitle = (
        presentation_data.get(
            "presentation_subtitle",
            ""
        )
        or slide_data.get(
            "subtitle",
            ""
        )
    )

    # Decorative accent
    accent = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(1.0),
        Inches(2.05),
        Inches(1.2),
        Inches(0.08)
    )

    accent.fill.solid()
    accent.fill.fore_color.rgb = COLORS["accent"]
    accent.line.fill.background()

    add_text(
        slide,
        title,
        1.0,
        2.35,
        11.3,
        1.2,
        font_size=38,
        bold=True,
        color=COLORS["white"],
        alignment=PP_ALIGN.CENTER,
        valign=MSO_ANCHOR.MIDDLE
    )

    if subtitle:

        add_text(
            slide,
            subtitle,
            1.5,
            3.75,
            10.3,
            0.9,
            font_size=20,
            color=COLORS["white"],
            alignment=PP_ALIGN.CENTER,
            valign=MSO_ANCHOR.MIDDLE
        )

    return slide


# ============================================================
# KEY POINTS
# ============================================================

def create_key_points_slide(
    prs,
    slide_data
):
    """
    Create key-points slide.
    """

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    set_background(slide)

    add_title(
        slide,
        slide_data.get(
            "title",
            "Key Points"
        )
    )

    points = slide_data.get(
        "content",
        []
    )

    if not points:
        return slide

    max_items = min(
        len(points),
        7
    )

    available_height = 5.0
    item_height = min(
        0.72,
        available_height / max_items
    )

    font_size = 20

    if max_items >= 6:
        font_size = 18

    y = 1.55

    for point in points[:7]:

        add_bullet(
            slide,
            point,
            0.85,
            y,
            11.5,
            item_height,
            font_size=font_size
        )

        y += item_height + 0.12

    return slide


# ============================================================
# TWO COLUMN
# ============================================================

def create_two_column_slide(
    prs,
    slide_data
):
    """
    Create two-column slide.
    """

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    set_background(slide)

    add_title(
        slide,
        slide_data.get(
            "title",
            "Overview"
        )
    )

    left_content = slide_data.get(
        "left_content",
        []
    )

    right_content = slide_data.get(
        "right_content",
        []
    )

    create_column_panel(
        slide,
        0.7,
        1.5,
        5.8,
        4.9,
        left_content
    )

    create_column_panel(
        slide,
        6.8,
        1.5,
        5.8,
        4.9,
        right_content
    )

    return slide


def create_column_panel(
    slide,
    x,
    y,
    width,
    height,
    items,
    panel_color=COLORS["light"]
):
    """
    Create a column panel.
    """

    add_panel(
        slide,
        x,
        y,
        width,
        height,
        panel_color
    )

    if not items:
        return

    count = min(
        len(items),
        6
    )

    item_height = min(
        0.68,
        (height - 0.55) / count
    )

    font_size = 18 if count >= 5 else 19

    current_y = y + 0.4

    for item in items[:6]:

        add_bullet(
            slide,
            item,
            x + 0.25,
            current_y,
            width - 0.5,
            item_height,
            font_size=font_size
        )

        current_y += item_height + 0.08


# ============================================================
# THREE COLUMN
# ============================================================

def create_three_column_slide(
    prs,
    slide_data
):
    """
    Create three-column slide.
    """

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    set_background(slide)

    add_title(
        slide,
        slide_data.get(
            "title",
            "Key Areas"
        )
    )

    content = slide_data.get(
        "content",
        []
    )

    # Always render exactly three panels.
    for index in range(3):

        x = 0.55 + (index * 4.25)

        add_panel(
            slide,
            x,
            1.65,
            3.85,
            4.85,
            COLORS["light"]
        )

        if index >= len(content):
            continue

        item = content[index]

        if not isinstance(item, dict):
            item = {
                "title": "",
                "description": str(item)
            }

        heading = item.get(
            "title",
            ""
        )

        description = item.get(
            "description",
            ""
        )

        if heading:

            add_text(
                slide,
                heading,
                x + 0.25,
                2.05,
                3.35,
                0.7,
                font_size=20,
                bold=True,
                color=COLORS["primary"],
                alignment=PP_ALIGN.CENTER
            )

        add_text(
            slide,
            description,
            x + 0.35,
            2.9,
            3.15,
            2.7,
            font_size=17,
            alignment=PP_ALIGN.CENTER,
            valign=MSO_ANCHOR.MIDDLE
        )

    return slide


# ============================================================
# COMPARISON
# ============================================================

def create_comparison_slide(
    prs,
    slide_data
):
    """
    Create comparison slide.
    """

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    set_background(slide)

    add_title(
        slide,
        slide_data.get(
            "title",
            "Comparison"
        )
    )

    create_column_panel(
        slide,
        0.7,
        1.5,
        5.8,
        4.9,
        slide_data.get(
            "left_content",
            []
        ),
        COLORS["blue_light"]
    )

    create_column_panel(
        slide,
        6.8,
        1.5,
        5.8,
        4.9,
        slide_data.get(
            "right_content",
            []
        ),
        COLORS["red_light"]
    )

    return slide


# ============================================================
# PROCESS
# ============================================================

def create_process_slide(
    prs,
    slide_data
):
    """
    Create process slide.
    """

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    set_background(slide)

    add_title(
        slide,
        slide_data.get(
            "title",
            "Process"
        )
    )

    steps = slide_data.get(
        "content",
        []
    )

    if not steps:
        return slide

    steps = steps[:6]

    total = len(steps)

    available_width = 11.7
    gap = 0.15

    box_width = (
        available_width
        - (gap * (total - 1))
    ) / total

    y = 2.25

    for index, step in enumerate(steps):

        x = 0.8 + index * (
            box_width + gap
        )

        add_panel(
            slide,
            x,
            y,
            box_width,
            2.5,
            COLORS["light"],
            COLORS["accent"]
        )

        # Step number
        circle = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(x + box_width / 2 - 0.28),
            Inches(y - 0.35),
            Inches(0.56),
            Inches(0.56)
        )

        circle.fill.solid()
        circle.fill.fore_color.rgb = COLORS["primary"]
        circle.line.fill.background()

        add_text(
            slide,
            str(index + 1),
            x + box_width / 2 - 0.28,
            y - 0.29,
            0.56,
            0.4,
            font_size=16,
            bold=True,
            color=COLORS["white"],
            alignment=PP_ALIGN.CENTER,
            valign=MSO_ANCHOR.MIDDLE
        )

        add_text(
            slide,
            step,
            x + 0.18,
            y + 0.45,
            box_width - 0.36,
            1.45,
            font_size=16,
            alignment=PP_ALIGN.CENTER,
            valign=MSO_ANCHOR.MIDDLE
        )

    return slide


# ============================================================
# TIMELINE
# ============================================================

def create_timeline_slide(
    prs,
    slide_data
):
    """
    Create timeline slide.

    Uses alternating event positions to reduce overlap.
    """

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    set_background(slide)

    add_title(
        slide,
        slide_data.get(
            "title",
            "Timeline"
        )
    )

    events = slide_data.get(
        "content",
        []
    )

    if not events:
        return slide

    events = events[:6]

    # Horizontal timeline
    line = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE,
        Inches(1.0),
        Inches(3.55),
        Inches(11.2),
        Inches(0.06)
    )

    line.fill.solid()
    line.fill.fore_color.rgb = COLORS["accent"]
    line.line.fill.background()

    total = len(events)

    if total == 1:
        spacing = 0
    else:
        spacing = 10.5 / (total - 1)

    for index, event in enumerate(events):

        x = 1.15 + index * spacing

        circle = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(x - 0.2),
            Inches(3.28),
            Inches(0.45),
            Inches(0.45)
        )

        circle.fill.solid()
        circle.fill.fore_color.rgb = COLORS["primary"]
        circle.line.fill.background()

        if index % 2 == 0:

            text_y = 2.0

        else:

            text_y = 4.05

        add_text(
            slide,
            event,
            x - 0.55,
            text_y,
            1.35,
            1.0,
            font_size=14,
            alignment=PP_ALIGN.CENTER,
            valign=MSO_ANCHOR.MIDDLE
        )

    return slide


# ============================================================
# STATISTICS
# ============================================================

def create_statistics_slide(
    prs,
    slide_data
):
    """
    Create statistics slide.
    """

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    set_background(slide)

    add_title(
        slide,
        slide_data.get(
            "title",
            "Key Statistics"
        )
    )

    statistics = slide_data.get(
        "content",
        []
    )

    if not statistics:
        return slide

    statistics = statistics[:5]

    total = len(statistics)

    gap = 0.2

    available_width = 11.8

    box_width = (
        available_width
        - (gap * (total - 1))
    ) / total

    for index, statistic in enumerate(
        statistics
    ):

        x = 0.7 + index * (
            box_width + gap
        )

        add_panel(
            slide,
            x,
            2.0,
            box_width,
            3.6,
            COLORS["light"]
        )

        if isinstance(statistic, dict):

            value = statistic.get(
                "value",
                ""
            )

            label = statistic.get(
                "label",
                ""
            )

        else:

            value = str(statistic)
            label = ""

        add_text(
            slide,
            value,
            x + 0.15,
            2.65,
            box_width - 0.3,
            0.9,
            font_size=30,
            bold=True,
            color=COLORS["primary"],
            alignment=PP_ALIGN.CENTER,
            valign=MSO_ANCHOR.MIDDLE
        )

        if label:

            add_text(
                slide,
                label,
                x + 0.2,
                3.7,
                box_width - 0.4,
                1.25,
                font_size=15,
                alignment=PP_ALIGN.CENTER,
                valign=MSO_ANCHOR.MIDDLE
            )

    return slide


# ============================================================
# QUOTE
# ============================================================

def create_quote_slide(
    prs,
    slide_data
):
    """
    Create quote slide.
    """

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    set_background(
        slide,
        COLORS["light"]
    )

    add_title(
        slide,
        slide_data.get(
            "title",
            "Quote"
        )
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

    quote = quote.strip()

    # Avoid double quoting.
    if (
        quote.startswith('"')
        and quote.endswith('"')
    ):
        formatted_quote = quote
    else:
        formatted_quote = f'"{quote}"'

    add_text(
        slide,
        formatted_quote,
        1.2,
        2.15,
        10.8,
        2.6,
        font_size=28,
        color=COLORS["primary"],
        alignment=PP_ALIGN.CENTER,
        valign=MSO_ANCHOR.MIDDLE
    )

    return slide


# ============================================================
# RECOMMENDATIONS
# ============================================================

def create_recommendations_slide(
    prs,
    slide_data
):
    """
    Create recommendations slide.
    """

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    set_background(slide)

    add_title(
        slide,
        slide_data.get(
            "title",
            "Recommendations"
        )
    )

    recommendations = slide_data.get(
        "content",
        []
    )

    recommendations = recommendations[:7]

    if not recommendations:
        return slide

    count = len(recommendations)

    item_height = min(
        0.72,
        4.8 / count
    )

    y = 1.55

    for index, recommendation in enumerate(
        recommendations,
        start=1
    ):

        circle = slide.shapes.add_shape(
            MSO_SHAPE.OVAL,
            Inches(0.8),
            Inches(y),
            Inches(0.48),
            Inches(0.48)
        )

        circle.fill.solid()
        circle.fill.fore_color.rgb = COLORS["primary"]
        circle.line.fill.background()

        add_text(
            slide,
            str(index),
            0.8,
            y + 0.02,
            0.48,
            0.38,
            font_size=14,
            bold=True,
            color=COLORS["white"],
            alignment=PP_ALIGN.CENTER,
            valign=MSO_ANCHOR.MIDDLE
        )

        add_text(
            slide,
            recommendation,
            1.55,
            y - 0.02,
            10.6,
            item_height,
            font_size=18,
            valign=MSO_ANCHOR.MIDDLE
        )

        y += item_height + 0.12

    return slide


# ============================================================
# CONCLUSION
# ============================================================

def create_conclusion_slide(
    prs,
    slide_data
):
    """
    Create conclusion slide.
    """

    slide = prs.slides.add_slide(
        prs.slide_layouts[6]
    )

    set_background(
        slide,
        COLORS["primary"]
    )

    add_text(
        slide,
        slide_data.get(
            "title",
            "Key Takeaway"
        ),
        1.0,
        1.45,
        11.3,
        0.9,
        font_size=32,
        bold=True,
        color=COLORS["white"],
        alignment=PP_ALIGN.CENTER,
        valign=MSO_ANCHOR.MIDDLE
    )

    content = slide_data.get(
        "content",
        []
    )

    if isinstance(content, list):

        content = "\n".join(
            str(item)
            for item in content
        )

    add_text(
        slide,
        str(content),
        1.4,
        2.65,
        10.5,
        2.6,
        font_size=24,
        color=COLORS["white"],
        alignment=PP_ALIGN.CENTER,
        valign=MSO_ANCHOR.MIDDLE
    )

    return slide


# ============================================================
# SLIDE ROUTER
# ============================================================

def create_slide(
    prs,
    slide_data,
    presentation_data=None
):
    """
    Route slide data to renderer.
    """

    layout = slide_data.get(
        "layout",
        "key_points"
    )

    renderers = {
        "title": create_title_slide,
        "key_points": create_key_points_slide,
        "two_column": create_two_column_slide,
        "three_column": create_three_column_slide,
        "comparison": create_comparison_slide,
        "process": create_process_slide,
        "timeline": create_timeline_slide,
        "statistics": create_statistics_slide,
        "quote": create_quote_slide,
        "recommendations": create_recommendations_slide,
        "conclusion": create_conclusion_slide,
    }

    renderer = renderers.get(
        layout,
        create_key_points_slide
    )

    if layout == "title":

        return renderer(
            prs,
            slide_data,
            presentation_data
        )

    return renderer(
        prs,
        slide_data
    )


# ============================================================
# MAIN RENDER FUNCTION
# ============================================================

def render_ppt(
    presentation_data,
    output_path
):
    """
    Convert presentation JSON into an editable .pptx file.
    """

    if not isinstance(
        presentation_data,
        dict
    ):
        raise ValueError(
            "presentation_data must be a dictionary"
        )

    slides = presentation_data.get(
        "slides",
        []
    )

    if not isinstance(slides, list):
        raise ValueError(
            "slides must be a list"
        )

    if not slides:
        raise ValueError(
            "Presentation contains no slides"
        )

    # --------------------------------------------------------
    # Create presentation
    # --------------------------------------------------------

    prs = Presentation()

    prs.slide_width = Inches(
        SLIDE_WIDTH
    )

    prs.slide_height = Inches(
        SLIDE_HEIGHT
    )

    # --------------------------------------------------------
    # Remove default slide if necessary.
    #
    # python-pptx normally creates a presentation with
    # zero slides, but this keeps the function defensive.
    # --------------------------------------------------------

    # --------------------------------------------------------
    # Create slides
    # --------------------------------------------------------

    for slide_data in slides:

        if not isinstance(
            slide_data,
            dict
        ):
            raise ValueError(
                "Each slide must be a dictionary"
            )

        slide = create_slide(
            prs,
            slide_data,
            presentation_data
        )

        slide_number = slide_data.get(
            "slide_number"
        )

        layout = slide_data.get(
            "layout"
        )

        if (
            slide_number
            and layout != "title"
        ):

            add_footer(
                slide,
                slide_number
            )

    # --------------------------------------------------------
    # Save
    # --------------------------------------------------------

    prs.save(
        output_path
    )

    return output_path