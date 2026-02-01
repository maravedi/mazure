import warnings
# Suppress pkg_resources deprecation warning from mongomock and others
warnings.filterwarnings("ignore", category=UserWarning, message=".*pkg_resources is deprecated.*")

from .cli.sync import app

if __name__ == "__main__":
    app()
