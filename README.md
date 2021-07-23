# Transkribus Web Client written in Python

(Tested with Python 3.8 on Windows and Linux.)

## Installation
* Clone this repository.
* Create a new environment with Python 3.8 using [venv](https://docs.python-guide.org/dev/virtualenvs/) or [conda](https://docs.anaconda.com/), e.g. `conda create --name dh_blog python=3.8`.
* Activate the new environment, e.g. `conda activate dh_blog`.
* Use pip to install the `requirements.txt`: `pip install -r requirements.txt`.

## Usage
* Read the documentation on https://dhlab.hypotheses.org/2114
* Execute the astronauts script with `python astronauts.py`.
* Before running `transkribus_api_template.py`, you have to modify lines 17 and 18 according to the credentials of your Transkribus account. Then run `python transkribus_api_template.py`.
* `transkribus_client.ipynb` is a [Jupyter notebook](https://jupyter.org/). Install Jupyter on your machine to play around with this notebook. Like in `transkribus_api_template.py`, you have to enter your credentials in the indicated lines. Follow the descriptions and inline comments in the notebook. 
* `transkribus_web.py` is a Python module containing the `Transkribus_Web` class ready to be imported into your code (`form transkribus_web.py import Transkribus_Web`)
