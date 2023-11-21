""" A fake vcf file generator"""

from importlib import metadata as importlib_metadata


def get_version() -> str:
    """
    Retrieve the version of the package.

    Returns:
        str: The version of the package, or 'unknown' if the version cannot be found.
    """
    try:
        return importlib_metadata.version(__name__)
    except importlib_metadata.PackageNotFoundError:  # pragma: no cover
        return "unknown"


version: str = get_version()
