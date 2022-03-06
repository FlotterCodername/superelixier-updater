# Building

Building should be as simple as running the `build.py` file.

Artifacts will be stored as `<appname>-<isodate>.zip` next to the project folder.

The prerequisites are:

- Install [pandoc](https://pandoc.org/) and [7-Zip](https://www.7-zip.org/) somewhere that your command line can find them.
- This project uses [poetry](https://python-poetry.org/) to handle dependencies. Install poetry, then run ``poetry install`` to install the required packages.
- Provide additional files in your project directory:
    - ./assets/app.ico *Any ICO file you want*
    - ./bin-win32/7z.exe *from [7-Zip](https://www.7-zip.org/)*
    - ./bin-win32/innoextract.exe *from [innoextract](https://github.com/dscharrer/innoextract)*

If you have any trouble, create an issue. Building should be made easy for interested parties.
