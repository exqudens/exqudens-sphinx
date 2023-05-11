# exqudens-sphinx

##### links
- tables
    - [flat-table](https://koen.vervloesem.eu/blog/using-flat-tables-in-restructuredtext-with-sphinx-for-column-and-row-spans)
- traceability
    - [sphinxcontrib-traceability](https://pypi.org/project/sphinxcontrib-traceability)
    - [mlx.traceability](https://melexis.github.io/sphinx-traceability-extension/readme.html)
- builders
    - [docxbuilder](https://docxbuilder.readthedocs.io/en/latest/docxbuilder.html)
    - [rst2pdf](https://pypi.org/project/rst2pdf)

##### how-to-generate
```
py -m venv build/py-env
./build/py-env/Scripts/pip.exe install -U sphinx
./build/py-env/Scripts/pip.exe install -U linuxdoc
./build/py-env/Scripts/pip.exe install -U mlx.traceability
./build/py-env/Scripts/pip.exe install -U docxbuilder
./build/py-env/Scripts/pip.exe install -U rst2pdf
./build/py-env/Scripts/pip.exe freeze > requirements.txt
./build/py-env/Scripts/sphinx-quickstart.exe doc
```


##### how-to-build
```
py -m venv build/py-env
./build/py-env/Scripts/pip.exe install -r requirements.txt
./build/py-env/Scripts/sphinx-build.exe -b html doc/source build/doc/html
./build/py-env/Scripts/sphinx-build.exe -b docx doc/source build/doc/docx
./build/py-env/Scripts/sphinx-build.exe -b pdf doc/source build/doc/pdf
```
