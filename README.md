# Daft assistant

**Daft assistant** is a Python script that automates the process of finding property to rent on [daft.ie](https://www.daft.ie/) by sending filtered ads to the chosen telegram accounts.

## Features

- Search the property to rent on the [daft.ie](https://www.daft.ie/) according to filters (min number of beds, max price, location) every 5 min
- Save found object links into listings.txt file
- Send found objects to specifed telegram user(s)
## Requirements

Daft assistant bot requires the following packages:

- Python 3.7 or higher

## Installation

To install Daft assistant bot, clone the repository and install the required packages:
```bash
git clone https://github.com/sokil747/Daft-assistant.git
cd Daft-assistant
pip install -r requirements.txt
```
Then copy and edit config file:
```bash
cp .daft-env-example .daft-env
nano .daft-env
```
