# mrsa-sequences
Arvados sequence uploader and analyzer for MRSA project

## Installation
To get started, you need to install the uploader first and then run the main.py script in uploader directory.

1. **Download.** You can download the uploader by cloning the github repository using following command:

```sh
git clone https://github.com/bio-ontology-research-group/mrsa-sequences.git
```

2. **Prepare your system.** You need to make sure you have Python, and the ability to install modules such as `pycurl` and `pyopenssl`. On Ubuntu 18.04, you can run:

```sh
sudo apt update
sudo apt install -y virtualenv git libcurl4-openssl-dev build-essential python3-dev libssl-dev libxml2 libxslt1-dev
```
3. **Create and enter your virtualenv.** Go to downloaded uploader directory and make and enter a virtualenv:

```sh
virtualenv --python python3 venv
. venv/bin/activate
```
Note that you will need to repeat the `. venv/bin/activate` step from this directory to enter your virtualenv whenever you want to use the installed tool.

4. **Install the dependencies.** Once the virtualenv is setup, install the dependencies:

```sh
pip install -r requirements.txt
```

