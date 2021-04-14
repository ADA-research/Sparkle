### Installation

Before starting Sparkle, please install the following packages with the specific versions:

1. Install Python 3.9 -- other 3.x versions may work, but were not tested
	* with anaconda:

		`conda create -n <env_name> python=3.9`

		`conda activate <env_name>`

2. Install swig version 3.0
	* with anaconda:

		`conda install swig=3.0`

3. Install first set of required python packages:
	* `pip install -r requirements_first.txt`
	* or with anaconda:

		`/home/<username>/<anaconda_dir>/envs/<env_name>/bin/pip install -r requirements_first.txt`

4. Install second set of required python packages:
	* `pip install -r requirements_second.txt`
	* or with anaconda:

		`/home/<username>/<anaconda_dir>/envs/<env_name>/bin/pip install -r requirements_second.txt`

5. Install other requirements if they are not on your system yet:
	* `epstopdf`
	* `LaTeX`
	* `BibTeX`
	* `gnuplot`
