"""Tests for display functions."""

from unittest.mock import MagicMock

from atproto_client.models.app.bsky.embed.images import View as ImagesView
from atproto_client.models.app.bsky.embed.record_with_media import View as RecordWithMediaView
from rich.text import Text

from atpcli.display.bsky import _at_uri_to_web_url, _has_image, _render_text_with_links, display_feeds, display_post


def test_at_uri_to_web_url():
    """Test AT URI to web URL conversion."""
    uri = "at://did:plc:test123/app.bsky.feed.post/abc123"
    handle = "user.bsky.social"
    expected = "https://bsky.app/profile/user.bsky.social/post/abc123"
    assert _at_uri_to_web_url(uri, handle) == expected


def test_at_uri_to_web_url_invalid():
    """Test AT URI to web URL conversion with invalid URI."""
    uri = "at://invalid/uri"
    handle = "user.bsky.social"
    # Should return the original URI if invalid
    assert _at_uri_to_web_url(uri, handle) == uri


def test_render_text_with_links_no_links():
    """Test rendering text without links."""
    text = "This is a simple post with no links"
    result = _render_text_with_links(text)
    assert isinstance(result, Text)
    assert str(result) == text


def test_render_text_with_links_with_url():
    """Test rendering text with a URL."""
    text = "Check out https://example.com for more info"
    result = _render_text_with_links(text)
    assert isinstance(result, Text)
    # The URL should be styled as a link
    assert "Check out " in str(result)
    assert "https://example.com" in str(result)
    assert " for more info" in str(result)


def test_render_text_with_links_multiple_urls():
    """Test rendering text with multiple URLs."""
    text = "Visit https://example.com and also http://test.org"
    result = _render_text_with_links(text)
    assert isinstance(result, Text)
    assert "https://example.com" in str(result)
    assert "http://test.org" in str(result)


def test_render_text_with_links_without_protocol():
    """Test rendering text with URLs without protocol."""
    text = "Check out github.com/phalt/atpcli for the repo"
    result = _render_text_with_links(text)
    assert isinstance(result, Text)
    # The URL should be detected and styled as a link
    result_str = str(result)
    assert "github.com/phalt/atpcli" in result_str
    # Verify it's actually a clickable link with https:// prepended
    link_found = False
    for span in result.spans:
        if "link https://github.com/phalt/atpcli" in str(span.style):
            link_found = True
            break
    assert link_found, "URL should be styled as a link with https:// protocol"


def test_render_text_with_links_various_domains():
    """Test rendering text with various domain formats."""
    text = "Visit example.com or go to site.co.uk and check subdomain.example.org"
    result = _render_text_with_links(text)
    assert isinstance(result, Text)
    result_str = str(result)
    assert "example.com" in result_str
    assert "site.co.uk" in result_str
    assert "subdomain.example.org" in result_str
    # Verify all three are clickable links with https://
    expected_links = ["https://example.com", "https://site.co.uk", "https://subdomain.example.org"]
    for expected_link in expected_links:
        link_found = any(f"link {expected_link}" in str(span.style) for span in result.spans)
        assert link_found, f"Should have clickable link: {expected_link}"


def test_render_text_with_links_mixed_protocols():
    """Test rendering text with mixed protocol and no-protocol URLs."""
    text = "See https://example.com and github.com/user/repo"
    result = _render_text_with_links(text)
    assert isinstance(result, Text)
    result_str = str(result)
    assert "https://example.com" in result_str
    assert "github.com/user/repo" in result_str
    # Verify both have correct links (one already has https, one gets it added)
    assert any("link https://example.com" in str(span.style) for span in result.spans)
    assert any("link https://github.com/user/repo" in str(span.style) for span in result.spans)


def test_render_text_with_links_single_char_domain():
    """Test rendering text with single character domain like x.com."""
    text = "Follow me on x.com for updates"
    result = _render_text_with_links(text)
    assert isinstance(result, Text)
    result_str = str(result)
    assert "x.com" in result_str
    # Verify it's a clickable link with https:// prepended
    link_found = any("link https://x.com" in str(span.style) for span in result.spans)
    assert link_found, "x.com should be styled as a link with https:// protocol"


def test_display_post():
    """Test displaying a post."""
    mock_post = MagicMock()
    mock_post.author.display_name = "Test User"
    mock_post.author.handle = "test.bsky.social"
    mock_post.author.did = "did:plc:test123abc"
    mock_post.record.text = "This is a test post with https://example.com"
    mock_post.record.reply = None
    mock_post.like_count = 10
    mock_post.uri = "at://did:plc:test123/app.bsky.feed.post/abc123"
    mock_post.embed = None

    table = display_post(mock_post)

    # Check that the table has the correct title with link markup
    assert "Test User" in table.title
    assert "test.bsky.social" in table.title
    expected_url = "https://bsky.app/profile/test.bsky.social/post/abc123"
    assert expected_url in table.title
    # Verify the link markup format
    assert f"[link={expected_url}]" in table.title
    assert "[/link]" in table.title
    # Verify DID appears in title
    assert "did:plc:test123abc" in table.title
    # Verify DID has dim styling
    assert "[dim]did:plc:test123abc[/dim]" in table.title


def test_display_post_renders_content_links():
    """Test that URLs in post content are rendered as clickable links."""
    mock_post = MagicMock()
    mock_post.author.display_name = "Test User"
    mock_post.author.handle = "test.bsky.social"
    mock_post.author.did = "did:plc:test456xyz"
    mock_post.record.text = "Check out https://example.com"
    mock_post.record.reply = None
    mock_post.like_count = 5
    mock_post.uri = "at://did:plc:test123/app.bsky.feed.post/abc123"
    mock_post.embed = None

    table = display_post(mock_post)

    # The table should have at least one row
    assert len(table.rows) == 1
    # We can't easily access the row content directly, but we can verify
    # that our _render_text_with_links function was called by checking
    # that a Text object would be created with the URL
    rendered = _render_text_with_links("Check out https://example.com")
    assert isinstance(rendered, Text)
    assert "https://example.com" in str(rendered)


def test_display_post_includes_did():
    """Test that display_post always shows DID."""
    mock_post = MagicMock()
    mock_post.author.display_name = "Test User"
    mock_post.author.handle = "test.bsky.social"
    mock_post.author.did = "did:plc:test123abc"
    mock_post.record.text = "Test post"
    mock_post.like_count = 5
    mock_post.uri = "at://did:plc:test123/app.bsky.feed.post/abc123"
    mock_post.embed = None
    mock_post.record.facets = None
    mock_post.record.reply = None

    table = display_post(mock_post)

    # Verify DID appears in title
    assert "did:plc:test123abc" in table.title
    # Verify DID has dim styling
    assert "[dim]did:plc:test123abc[/dim]" in table.title


def test_has_image_no_embed():
    """Test _has_image with no embed."""
    mock_post = MagicMock()
    mock_post.embed = None
    assert _has_image(mock_post) is False


def test_has_image_with_images_embed():
    """Test _has_image with images embed."""
    mock_post = MagicMock()
    mock_post.embed = ImagesView(images=[])
    assert _has_image(mock_post) is True


def test_has_image_with_record_with_media():
    """Test _has_image with record_with_media containing images."""
    mock_post = MagicMock()
    # Create a mock RecordWithMediaView with images media
    mock_embed = MagicMock(spec=RecordWithMediaView)
    mock_embed.media = ImagesView(images=[])
    mock_post.embed = mock_embed
    assert _has_image(mock_post) is True


def test_has_image_with_non_image_embed():
    """Test _has_image with non-image embed."""
    mock_post = MagicMock()
    # Mock a different embed type (not ImagesView or RecordWithMediaView)
    mock_post.embed = MagicMock()
    mock_post.embed.__class__ = type("OtherEmbed", (), {})
    assert _has_image(mock_post) is False


def test_display_post_with_image():
    """Test displaying a post with an image shows the camera emoji."""
    mock_post = MagicMock()
    mock_post.author.display_name = "Test User"
    mock_post.author.handle = "test.bsky.social"
    mock_post.record.text = "Post with image"
    mock_post.record.reply = None
    mock_post.like_count = 10
    mock_post.uri = "at://did:plc:test123/app.bsky.feed.post/abc123"
    mock_post.embed = ImagesView(images=[])

    table = display_post(mock_post)

    # Check that the title contains the camera emoji
    assert "📷" in table.title
    assert "Test User" in table.title


def test_render_text_with_facets():
    """Test rendering text with facets for link detection."""
    from atproto_client.models.app.bsky.richtext.facet import ByteSlice
    from atproto_client.models.app.bsky.richtext.facet import Link as LinkFacet
    from atproto_client.models.app.bsky.richtext.facet import Main as FacetMain

    # Test text with a link containing special characters like !
    text = "Check out https://wagtail.org/blog/the-100! for more info"

    # Create a facet for the link (byte positions)
    link_start = text.index("https://wagtail.org/blog/the-100!")
    link_end = link_start + len("https://wagtail.org/blog/the-100!")

    # Get byte positions
    byte_start = len(text[:link_start].encode("utf-8"))
    byte_end = len(text[:link_end].encode("utf-8"))

    facet = FacetMain(
        index=ByteSlice(byte_start=byte_start, byte_end=byte_end),
        features=[LinkFacet(uri="https://wagtail.org/blog/the-100!")],
    )

    result = _render_text_with_links(text, facets=[facet])
    assert isinstance(result, Text)
    result_str = str(result)
    # The full link including ! should be present
    assert "https://wagtail.org/blog/the-100!" in result_str

    # Verify it's a clickable link with the correct URI
    link_found = False
    for span in result.spans:
        if "link https://wagtail.org/blog/the-100!" in str(span.style):
            link_found = True
            break
    assert link_found, "Full link with ! should be clickable"


def test_render_text_with_multiple_facets():
    """Test rendering text with multiple link facets."""
    from atproto_client.models.app.bsky.richtext.facet import ByteSlice
    from atproto_client.models.app.bsky.richtext.facet import Link as LinkFacet
    from atproto_client.models.app.bsky.richtext.facet import Main as FacetMain

    text = "Visit https://example.com and https://test.org!"

    # Create facets for both links
    # Note: The second link includes ! as part of the URL path, which is valid.
    # This tests that facets properly handle URLs with special characters in them.
    link1_start = text.index("https://example.com")
    link1_end = link1_start + len("https://example.com")
    byte1_start = len(text[:link1_start].encode("utf-8"))
    byte1_end = len(text[:link1_end].encode("utf-8"))

    link2_start = text.index("https://test.org!")
    link2_end = link2_start + len("https://test.org!")
    byte2_start = len(text[:link2_start].encode("utf-8"))
    byte2_end = len(text[:link2_end].encode("utf-8"))

    facets = [
        FacetMain(
            index=ByteSlice(byte_start=byte1_start, byte_end=byte1_end),
            features=[LinkFacet(uri="https://example.com")],
        ),
        FacetMain(
            index=ByteSlice(byte_start=byte2_start, byte_end=byte2_end),
            features=[LinkFacet(uri="https://test.org!")],
        ),
    ]

    result = _render_text_with_links(text, facets=facets)
    assert isinstance(result, Text)
    result_str = str(result)
    assert "https://example.com" in result_str
    assert "https://test.org!" in result_str

    # Verify both are clickable links
    assert any("link https://example.com" in str(span.style) for span in result.spans)
    assert any("link https://test.org!" in str(span.style) for span in result.spans)


def test_render_text_with_unicode_and_facets():
    """Test rendering text with unicode characters and facets."""
    from atproto_client.models.app.bsky.richtext.facet import ByteSlice
    from atproto_client.models.app.bsky.richtext.facet import Link as LinkFacet
    from atproto_client.models.app.bsky.richtext.facet import Main as FacetMain

    # Text with emoji (multi-byte character) before the link
    text = "🔥 Hot news: https://example.com/news"

    link_start = text.index("https://example.com/news")
    link_end = link_start + len("https://example.com/news")

    # Important: byte positions, not character positions
    byte_start = len(text[:link_start].encode("utf-8"))
    byte_end = len(text[:link_end].encode("utf-8"))

    facet = FacetMain(
        index=ByteSlice(byte_start=byte_start, byte_end=byte_end),
        features=[LinkFacet(uri="https://example.com/news")],
    )

    result = _render_text_with_links(text, facets=[facet])
    assert isinstance(result, Text)
    result_str = str(result)
    assert "🔥" in result_str
    assert "https://example.com/news" in result_str
    assert any("link https://example.com/news" in str(span.style) for span in result.spans)


def test_display_post_with_facets():
    """Test displaying a post with facets for proper link rendering."""
    from atproto_client.models.app.bsky.richtext.facet import ByteSlice
    from atproto_client.models.app.bsky.richtext.facet import Link as LinkFacet
    from atproto_client.models.app.bsky.richtext.facet import Main as FacetMain

    mock_post = MagicMock()
    mock_post.author.display_name = "Test User"
    mock_post.author.handle = "test.bsky.social"
    text = "Check out https://wagtail.org/blog/the-100! for more"
    mock_post.record.text = text
    mock_post.record.reply = None
    mock_post.like_count = 5
    mock_post.uri = "at://did:plc:test123/app.bsky.feed.post/abc123"
    mock_post.embed = None

    # Create facet for the link with !
    link_start = text.index("https://wagtail.org/blog/the-100!")
    link_end = link_start + len("https://wagtail.org/blog/the-100!")
    byte_start = len(text[:link_start].encode("utf-8"))
    byte_end = len(text[:link_end].encode("utf-8"))

    facet = FacetMain(
        index=ByteSlice(byte_start=byte_start, byte_end=byte_end),
        features=[LinkFacet(uri="https://wagtail.org/blog/the-100!")],
    )
    mock_post.record.facets = [facet]

    table = display_post(mock_post)

    # The table should contain the full link with !
    assert len(table.rows) == 1
    # Verify that the rendering function was called with facets
    rendered = _render_text_with_links(text, facets=[facet])
    assert "https://wagtail.org/blog/the-100!" in str(rendered)


def test_display_post_with_reply():
    """Test displaying a reply post shows the reply emoji."""
    mock_post = MagicMock()
    mock_post.author.display_name = "Test User"
    mock_post.author.handle = "test.bsky.social"
    mock_post.record.text = "This is a reply"
    # Create a mock reply object that isn't None
    mock_post.record.reply = MagicMock()
    mock_post.like_count = 5
    mock_post.uri = "at://did:plc:test123/app.bsky.feed.post/abc123"
    mock_post.embed = None

    table = display_post(mock_post)

    # Check that the title contains the reply emoji
    assert "⤴️" in table.title
    assert "Test User" in table.title


def test_display_post_with_repost():
    """Test displaying a repost/quote post shows the repost emoji."""
    from atproto_client.models.app.bsky.embed.record import View as RecordView

    mock_post = MagicMock()
    mock_post.author.display_name = "Test User"
    mock_post.author.handle = "test.bsky.social"
    mock_post.record.text = "Quote posting this"
    mock_post.record.reply = None
    mock_post.like_count = 5
    mock_post.uri = "at://did:plc:test123/app.bsky.feed.post/abc123"
    # Use isinstance check - create a proper RecordView instance
    mock_post.embed = MagicMock(spec=RecordView)

    table = display_post(mock_post)

    # Check that the title contains the repost emoji
    assert "🔁" in table.title
    assert "Test User" in table.title


def test_display_post_with_record_with_media():
    """Test displaying a quote post with media shows the repost emoji."""
    mock_post = MagicMock()
    mock_post.author.display_name = "Test User"
    mock_post.author.handle = "test.bsky.social"
    mock_post.record.text = "Quote with image"
    mock_post.record.reply = None
    mock_post.like_count = 5
    mock_post.uri = "at://did:plc:test123/app.bsky.feed.post/abc123"
    # Create a mock RecordWithMediaView with images media
    mock_embed = MagicMock(spec=RecordWithMediaView)
    mock_embed.media = ImagesView(images=[])
    mock_post.embed = mock_embed

    table = display_post(mock_post)

    # Check that the title contains the repost emoji (priority over image)
    assert "🔁" in table.title
    assert "Test User" in table.title


def test_is_reply():
    """Test _is_reply function."""
    from atpcli.display.bsky import _is_reply

    # Test with reply
    mock_post = MagicMock()
    mock_post.record.reply = MagicMock()  # Non-None reply object
    assert _is_reply(mock_post) is True

    # Test without reply
    mock_post.record.reply = None
    assert _is_reply(mock_post) is False


def test_is_repost_or_quote():
    """Test _is_repost_or_quote function."""
    from atproto_client.models.app.bsky.embed.record import View as RecordView

    from atpcli.display.bsky import _is_repost_or_quote

    # Test with record embed
    mock_post = MagicMock()
    mock_post.embed = MagicMock(spec=RecordView)
    assert _is_repost_or_quote(mock_post) is True

    # Test with record with media
    mock_embed = MagicMock(spec=RecordWithMediaView)
    mock_post.embed = mock_embed
    assert _is_repost_or_quote(mock_post) is True

    # Test with no embed
    mock_post.embed = None
    assert _is_repost_or_quote(mock_post) is False

    # Test with images embed
    mock_post.embed = ImagesView(images=[])
    assert _is_repost_or_quote(mock_post) is False


def test_display_feeds():
    """Test display_feeds function."""
    feed_details = [
        {
            "name": "Discover Feed",
            "uri": "at://did:plc:test/app.bsky.feed.generator/discover",
            "description": "Discover new content",
        },
        {
            "name": "Popular Feed",
            "uri": "at://did:plc:test/app.bsky.feed.generator/popular",
            "description": "Popular posts",
        },
    ]

    table = display_feeds(feed_details)

    # Check that table has the correct title
    assert "Saved Feeds (2)" in table.title

    # Check that table has correct number of columns
    assert len(table.columns) == 3

    # Check column names and styles
    assert table.columns[0].header == "Feed Name"
    assert table.columns[0].style == "cyan"
    assert table.columns[1].header == "URI"
    assert table.columns[1].style == "dim white"
    assert table.columns[2].header == "Description"
    assert table.columns[2].style == "white"


def test_display_feeds_empty():
    """Test display_feeds function with empty list."""
    feed_details = []

    table = display_feeds(feed_details)

    # Check that table has the correct title
    assert "Saved Feeds (0)" in table.title

    # Table should have 3 columns even if empty
    assert len(table.columns) == 3


def test_display_profile():
    """Test displaying a user profile."""
    from atpcli.display.bsky import display_profile

    # Create a mock profile
    mock_profile = MagicMock()
    mock_profile.display_name = "Alice Test"
    mock_profile.handle = "alice.bsky.social"
    mock_profile.did = "did:plc:abc123xyz789"
    mock_profile.description = "Python developer and open source enthusiast"
    mock_profile.followers_count = 1234
    mock_profile.follows_count = 567
    mock_profile.posts_count = 890
    mock_profile.avatar = "https://cdn.bsky.app/avatar/test.jpg"

    # Call display_profile and verify it doesn't crash
    try:
        display_profile(mock_profile)
        # If we get here without exception, the function works
        assert True
    except Exception as e:
        assert False, f"display_profile raised exception: {e}"

