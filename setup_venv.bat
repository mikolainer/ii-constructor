python -m venv venv
call .\venv\Scripts\activate.bat
pip install -e .\ii_constructor\packages\core
pip install -e .\ii_constructor\packages\levenshtain
pip install -e .\ii_constructor\packages\mariarepo
pip install -e .\ii_constructor\packages\mysqlrepo
pip install -e .\ii_constructor\packages\inmemoryrepo
pip install -e .\ii_constructor\packages\gui

pause