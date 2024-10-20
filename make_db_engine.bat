mkdir .\engine
copy .\ii_constructor\apps\engine\index.py .\engine\index.py

mkdir .\engine\packages
xcopy .\ii_constructor\packages\core\ .\engine\packages\core\ /E
xcopy .\ii_constructor\packages\engine\ .\engine\packages\engine\ /E
xcopy .\ii_constructor\packages\server\ .\engine\packages\server\ /E
xcopy .\ii_constructor\packages\mysqlrepo\ .\engine\packages\mysqlrepo\ /E
xcopy .\ii_constructor\packages\levenshtain\ .\engine\packages\levenshtain\ /E

echo pymysql > .\engine\requirements.txt
echo Levenshtein >> .\engine\requirements.txt
echo -e ./packages/core >> .\engine\requirements.txt
echo -e ./packages/engine >> .\engine\requirements.txt
echo -e ./packages/server >> .\engine\requirements.txt
echo -e ./packages/mysqlrepo >> .\engine\requirements.txt
echo -e ./packages/levenshtain >> .\engine\requirements.txt

pause
