app: python-virtualenv dist/menu_temp.app/Contents/MacOS/menu_temp

dist/menu_temp.app/Contents/MacOS/menu_temp: menu_temp.py requirements.txt
	python setup.py py2app

clean:
	rm -rf build dist .eggs .DS_Store *.egg-info

distclean: clean
	pyenv virtualenv-delete -f menutemp-3.10.17
	rm -f .python-version

configure: python-virtualenv

python-virtualenv: .python-version

.python-version:
	@if ! pyenv versions --bare | grep -qx "3.10.17"; then \
		pyenv install 3.10.17; \
	fi
	@if ! pyenv virtualenvs --bare | grep -qx "menutemp-3.10.17"; then \
		pyenv virtualenv 3.10.17 menutemp-3.10.17; \
	fi
	pyenv local menutemp-3.10.17
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

.PHONY: app clean distclean debug install uninstall
