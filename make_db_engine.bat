mkdir .\engine
::mkdir .\engine\iiconstructor_core\infrastructure
::mkdir .\engine\iiconstructor_core\domain

xcopy .\ii_constructor\packages\core\iiconstructor_core\ .\engine\iiconstructor_core\ /E

echo pymysql > ./engine/requirements.txt
echo Levenshtein >> ./engine/requirements.txt

copy .\ii_constructor\apps\engine\index.py .\engine\index.py
copy .\ii_constructor\packages\mysqlrepo\iiconstructor_mysqlrepo\__ini__.py .\engine\mysqlrepo.py
copy .\ii_constructor\packages\levenshtain\iiconstructor_levenshtain\__init__.py .\engine\iiconstructor_levenshtain.py

pause
