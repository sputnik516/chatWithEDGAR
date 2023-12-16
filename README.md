# EDGAR AI - chat with SEC filings
Simple web UI frontend that provides answers to free-text questions
using SEC filing data as context.

## _Live demo: https://edgar-ai.streamlit.app/_

## Example usage:
**- Question:** _What was Microsoft's revenue in fiscal year 2022?_

**- Sample response:** _Microsoft's revenue in fiscal year 2022 was $198,270 million._




**- Question:** _How much R&D expense did TSLA have in each quarter of 2019?_

**- Sample response:** 
_The R&D expenses for TSLA in each quarter of 2019 were as follows:_
  
_- Q1 2019: $340.2 million_

_- Q2 2019: $323.9 million_

_- Q3 2019: $334 million. Please note that these figures are in millions of dollars._

## Install
- Clone this repo `git clone https://github.com/sputnik516/chatWithEDGAR.git`
- Create a new conda env and install all libraries listed in **requirements.txt**:
    
    `conda create -n edgar python=3.11.7 --file requirements.txt`

    `conda activate edgar`
- Install all libraries listed in **requirements.txt**
- Create a file `keys.py`, by making a copy of `keys_sample.py` and renaming it.
    Set the `OPEN_AI_KEY` and `KAYAI_API_KEY` to OpenAI and Kay.ai API keys, respectively
- Launch the streamlit server by running:

    `streamlit run streamlit_app.py`
    
Hint: if running in Pycharm debugger, then set the "Run/Debug Configuration" to:
    
- Script Name: [_path to streamlit executable, get it by running `which streamlit`_]
- Script Parameters: _run streamlit_app.py_

