from setuptools import setup, find_packages

if __name__ == "__main__":
    readme = ""
    with open("README.md") as f:
        readme = f.read()

    requirements = []
    with open('requirements.txt') as f:
        requirements = f.read().splitlines()

    setup(
        name='iiconstructor_levenshtain',
        version='0.0',
        description='Parts of project "interactive instructons constructor"',
        long_description=readme,
        author='Nikolay Ivantsov',
        author_email='mikolainer@mail.ru',
        packages= ['iiconstructor_levenshtain'],
        install_requires=requirements,
    )