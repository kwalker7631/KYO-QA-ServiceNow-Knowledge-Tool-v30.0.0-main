from setuptools import setup, find_packages

setup(
    name="kyo-qa-tool",
    version="25.1.1",
    description="Kyocera QA ServiceNow Knowledge Tool (PDF→Excel) with web UI",
    packages=find_packages(exclude=["web*", "tests*"]),
    include_package_data=True,
    install_requires=[
        "Flask>=2.0", "Werkzeug>=2.0",
        "openpyxl", "Pillow", "pywebview"
    ],
    entry_points={
        "console_scripts": [
            "kyo-qa=launch:main",
        ],
    },
)
