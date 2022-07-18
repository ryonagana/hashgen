cd .env\Scripts\

pyinstaller --onefile --noconsole  ../../run.py --distpath ../../dist/ --workpath ../../build/ --specpath ../../

cd ../../dist
ren run.exe hashgen.exe
cd ../
del dist/
python release.py

PAUSE