from setuptools import setup

if __name__ == "__main__":
    with open("README.md") as f:
        readme = f.read()

    with open('requirements.txt') as f:
        requirements = f.read().splitlines()

    setup(
        name='ii_constructor',
        version='0.0',
        description='Tool to create a skills for YandexAlice with GUI',
        long_description=readme,
        author='Nikolay Ivantsov',
        author_email='mikolainer@mail.ru',
        packages=['ii_constructor'],
        install_requires=requirements, #external packages as dependencies
    )