import mistune

from personal_site.mistune import BlogRenderer


def test_markdown_image_links_to_asset_in_new_tab():
    markdown = mistune.create_markdown(renderer=BlogRenderer(escape=False))

    html = markdown('![A useful diagram](/static/diagram.png "Diagram")')

    assert html == (
        '<p><a href="/static/diagram.png" target="_blank" '
        'rel="noopener noreferrer"><img src="/static/diagram.png" '
        'alt="A useful diagram" title="Diagram" /></a></p>\n'
    )


def test_markdown_image_uses_sanitized_url_for_link_and_image():
    markdown = mistune.create_markdown(renderer=BlogRenderer(escape=False))

    html = markdown("![Unsafe](javascript:alert(1))")

    assert 'href="#harmful-link"' in html
    assert 'src="#harmful-link"' in html
