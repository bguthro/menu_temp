app: configure dist/menu_temp.app/Contents/MacOS/menu_temp

dist/menu_temp.app/Contents/MacOS/menu_temp: menu_temp.py requirements.txt
	python setup.py py2app

clean:
	rm -rf build dist .eggs .DS_Store *.egg-info

distclean: clean
	pyenv virtualenv-delete -f menutemp-3.10.17
	rm -f .python-version

configure: python-virtualenv install-config

python-virtualenv: .python-version

.python-version:
	@if ! pyenv versions --bare | grep -qx "3.10.16"; then \
		pyenv install 3.10.16; \
	fi
	@if ! pyenv virtualenvs --bare | grep -qx "menutemp-3.10.16"; then \
		pyenv virtualenv 3.10.16 menutemp-3.10.16; \
	fi
	pyenv local menutemp-3.10.16
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

install-config:
	@if [ -f $$HOME/.ambient-config.json ]; then \
		echo "$$HOME/.ambient-config.json already exists. Skipping."; \
	else \
		if [ -z "$(API_KEY)" ]; then \
			echo "Error: API_KEY is not set. Usage: make $@ API_KEY=your_key APP_KEY=your_app_key"; \
			exit 1; \
		fi; \
		if [ -z "$(APP_KEY)" ]; then \
			echo "Error: APP_KEY is not set. Usage: make $@ API_KEY=your_key APP_KEY=your_app_key"; \
			exit 1; \
		fi; \
		echo "Installing config file to $$HOME/.ambient-config.json"; \
		sed -e "s|YOUR_API_KEY_FROM_AMBIENT_WEATHER|$(API_KEY)|g" -e "s|YOUR_APP_KEY_FROM_AMBIENT_WEATHER|$(APP_KEY)|g" ambient_config.json.example > $$HOME/.ambient-config.json; \
	fi
debug: app
	./dist/menu_temp.app/Contents/MacOS/menu_temp

install: app
	cp -r dist/menu_temp.app /Applications/

uninstall:
	rm -rf /Applications/menu_temp.app

run: install
	open /Applications/menu_temp.app

.PHONY: app clean distclean debug install uninstall install-config python-virtualenv
