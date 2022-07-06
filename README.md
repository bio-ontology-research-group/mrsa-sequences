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

5. **Test the tool.** Try running:

```sh
python uploader/main.py --help
```

6. **Set Arvados API Token.** Before uploading the sequence files, you need to set arvados api token value to environment variable ARVADOS_API_TOKEN. It will look something as the following:
```sh
export ARVADOS_API_TOKEN=2jv9346o396exampledonotuseexampledonotuseexes7j1ld
```

You can find the arvados token at [current token link](https://workbench.cborg.cbrc.kaust.edu.sa/current_token) in your user profile menu on [arvados web portal](https://workbench.cborg.cbrc.kaust.edu.sa/).

# Usage

Run the uploader with a FASTA or FASTQ reads gzipped files and accompanying metadata file in YAML:

```sh
python uploader/main.py reads1.fastq.gz reads2.fastq.gz metadata.yaml
```

You can find the example files on mrsa [web uploader](https://mrsa.cborg.cbrc.kaust.edu.sa/upload/). Here are the links to example files:

- Example [fastq read file 1](https://mrsa.cborg.cbrc.kaust.edu.sa/static/reads1.fastq.gz)
- Example [fastq read file 2](https://mrsa.cborg.cbrc.kaust.edu.sa/static/reads2.fastq.gz)
- Example [Metadata file](https://mrsa.cborg.cbrc.kaust.edu.sa/static/metadata.yaml)

Once the sequence is uploaded, you can see the status of the job in state.json file.

