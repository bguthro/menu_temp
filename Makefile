app:
	python setup.py py2app -A

clean:
	rm -rf build dist .eggs .DS_Store *.egg-info

python-virtualenv:
	pyenv install 3.10
	pyenv virtualenv 3.10.17 menutemp-3.10.17
	pyenv local menutemp-3.10.17
	python -m pip install --upgrade pip
	python -m pip install -r requirements.txt

run: app
	./dist/menu_temp.app/Contents/MacOS/menu_temp