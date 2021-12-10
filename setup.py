import setuptools

setuptools.setup(
    name="dotez", 
    version="0.0.1",
    author="Bao Vien Ngo",
    author_email="baovienngo@gmail.com",
    description="Master Thesis",
    packages=["scraper", "position_optimizer"],
    install_requires=['requests', "python-dotenv", "ujson"]
)
