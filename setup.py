import setuptools

setuptools.setup(
    name="dota-scraper-baovien",  # Replace with your own username
    version="0.0.1",
    author="Bao Vien Ngo",
    author_email="baovienngo@gmail.com",
    description="A tool for scraping dota 2 matches for master thesis",
    packages=["d2scraper"],
    install_requires=['requests', "python-dotenv"]
)
