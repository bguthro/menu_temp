app:
	python setup.py py2app

clean:
	rm -rf build dist .eggs .DS_Store *.egg-info

python-virtualenv:
	pyenv install 3.10.16
	pyenv virtualenv 3.10.16 menutemp-3.10.16
	pyenv local menutemp-3.10.16
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

debug: app
	./dist/menu_temp.app/Contents/MacOS/menu_temp

install: app
	cp -r dist/menu_temp.app /Applications/

uninstall:
	rm -rf /Applications/menu_temp.app

run: install
	open /Applications/menu_temp.app

.PHONY: app clean python-virtualenv debug install uninstall
