from setuptools import setup, find_packages

setup(
    name="llm-chunker",
    version="0.1.1",
    description="A semantic and legal text chunker based on LLM analysis",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="LLM Chunker Developer",
    author_email="example@email.com",
    url="https://github.com/your-repo/llm-chunker",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.9",
    install_requires=[
        "openai>=1.0.0",
        "nltk>=3.6",
    ],
    extras_require={
        "ollama": ["ollama"],
    },
)
