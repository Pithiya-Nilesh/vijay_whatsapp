from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in vijay_whatsapp/__init__.py
from vijay_whatsapp import __version__ as version

setup(
	name="vijay_whatsapp",
	version=version,
	description="This app for whatsapp integration using woonotif.",
	author="Nilesh Pithiya",
	author_email="nilesh@sanskartechnolab.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)
