# Building
Building should be as simple as running the `build.py` file.

Artifacts will be stored as `<appname>-<isodate>.zip` next to the project folder.

The prerequisites are:

- Install [pandoc](https://pandoc.org/) and [7-Zip](https://www.7-zip.org/) somewhere that your command line can find them
- Make sure your Python interpreter satisfies the [requirements file](./requirements.txt)
- Provide additional files in your project directory:
  - ./app.ico
  - ./bin-win32/7z.exe
  - ./bin-win32/innoextract.exe

If you have any trouble, create an issue.
Building should be made easy for interested parties.
