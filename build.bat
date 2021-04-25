pyinstaller main.py -F
rmdir build /s /q
xcopy config dist\config /E /Y /I
del dist\config\auth.json
del dist\config\local.json
del dist\config\eula.json
xcopy docs dist\docs /E /Y /I
xcopy bin-win32 dist\bin-win32 /E /Y /I
cd dist
del ..\..\superelixier-releases\superelixier-updater.zip
7z -tzip u ..\..\superelixier-releases\superelixier-updater.zip * -m0=Deflate -mx9
cd ..
rmdir dist /s /q
exit