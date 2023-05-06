# exqudens-sphinx

##### how-to-generate

```
py -m venv build/py-env
./build/py-env/Scripts/pip.exe install -r requirements.txt
./build/py-env/Scripts/sphinx-quickstart.exe doc
```


##### how-to-build

```
py -m venv build/py-env
./build/py-env/Scripts/pip.exe install -r requirements.txt
./build/py-env/Scripts/sphinx-build.exe -b html doc/source build/doc/html
```