from atproto_client.models.app.bsky.feed.defs import PostView
from rich.table import Table


def display_post(post: PostView) -> Table:
    """Display a post in the terminal as a table."""
    table = Table(title=f"{post.author.display_name} (@{post.author.handle})", show_header=True, expand=True)
    table.add_column("Post", style="white")
    table.add_column("Likes", justify="right", style="green")
    text = post.record.text if hasattr(post.record, "text") else ""
    likes = post.like_count or 0
    table.add_row(text, str(likes))
    return table
