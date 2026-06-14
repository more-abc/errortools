import namebyauthor as na  # type: ignore

__author__: str = "Evan Yang"
__author_email__: str = "quantbit@126.com"
__copyright__: str = "Copyright 2026 (C) aiwonderland Evan Yang"
__description__: str = "errortools - a toolset for working with Python exceptions and warnings and logging."
__license__: str = "MIT"
__title__: str = "errortools"
__url__: str = "https://github.com/more-abc/errortools"

__fullname__ = na.generate_name(__title__, __author__)
__slug__ = na.generate_slug(__title__, __author__)
__signature__ = na.generate_signature(__title__, __author__)
__uid__ = na.generate_id(__title__, __author__)

if __name__ == "__main__":
    show_items: list[tuple[str, str]] = [
        ("author", __author__),
        ("author email", __author_email__),
        ("title", __title__),
        ("description", __description__),
        ("license", __license__),
        ("url", __url__),
        ("fullname", __fullname__),
        ("slug", __slug__),
        ("signature", __signature__),
        ("uid", __uid__),
    ]

    for label, value in show_items:
        print(f"{label}: {value}")
