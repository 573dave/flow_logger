from setuptools import setup, find_packages

setup(
    name="flow-logger",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,  # Important for template files
    package_data={
        'flow_logger': ['templates/*.html'],  # Include HTML templates
    },
    install_requires=[
        'psutil',  # For system information
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="A lightweight Python function call logger with HTML reporting",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/flow-logger",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)