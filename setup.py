from setuptools import setup, find_packages

setup(
    name="flow_logger",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,  # Important for template files
    package_data={
        'flow_logger': ['templates/*.html'],  # Include HTML templates
    },
    install_requires=[
        'psutil',  # For system information
    ],
    author="573dave",
    author_email="573dave@github",
    description="A lightweight Python function call logger with HTML reporting",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/573dave/flow_logger",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
