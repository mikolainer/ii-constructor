from setuptools import setup

if __name__ == "__main__":
    with open("README.md") as f:
        readme = f.read()

    with open('requirements.txt') as f:
        requirements = f.read().splitlines()

    setup(
        name='alicetool',
        version='0.0',
        description='Tool to create a skills for YandexAlice with GUI',
        long_description=readme,
        author='Man Foo',
        author_email='mikolainer@mail.ru',
        packages=['alicetool'],
        install_requires=requirements, #external packages as dependencies
    )