
# Loudy

A simple python script that generates random HTTP/DNS traffic noise in the background while you go about your regular web browsing, to make your web traffic data less valuable for selling and for extra obscurity.

Tested with python 3

## Getting Started

These instructions will get you a copy of the project up and running on your local machine

### Dependencies

Install `requests` if you do not have it already installed, using `pip`:

```
pip install requests
pip install beautifulsoup4
```

### Usage

Clone the repository
```
git clone https://github.com/jackyes/loudy.git
```

Navigate into the `loudy` directory
```
cd loudy
```

Run the script

```
python loudy.py --config config.json
```

The program can accept a number of command line arguments:
```
$ python loudy.py --help
usage: loudy.py [-h] [--log -l] --config -c [--timeout -t]

optional arguments:
  -h, --help    show this help message and exit
  --log -l      logging level
  --config -c   config file
  --timeout -t  for how long the crawler should be running, in seconds
```
only the config file argument is required.

###  Output
```
$ docker run jackyes/loudy
INFO:root:Visiting https://moz.com/domain-analysis/mega.nz
INFO:root:Visiting https://berkeley.edu
INFO:root:Visiting https://give.berkeley.edu/?sc=111443
INFO:root:Visiting https://dac.berkeley.edu/web-accessibility
INFO:root:Visiting https://dac.berkeley.edu/campus-events/coming-events
INFO:root:Visiting http://www.dsp.berkeley.edu
INFO:root:Visiting http://www.dsp.berkeley.edu/campus-resources/community-partners
INFO:root:Visiting http://axisdance.org
INFO:root:Visiting https://axisdance.org/calendar/category/axis-performances/axis-performances-online/
INFO:root:Visiting https://axisdance.org/presenters/
INFO:root:Visiting https://axisdance.org/feed/

...
```

## Run with image from dockerhub

`docker run jackyes/loudy`  
  
## Build Using Docker

1. Build the image

`docker build -t loudy .`

2. Create the container and run:

`docker run -it loudy --config config.json`

## Some examples

Some edge-cases examples are available on the `examples` folder. You can read more there [examples/README.md](examples/README.md).

## Special Thanks

* **Itay Hury** - *Initial work* - [1tayH](https://github.com/1tayH)

See also the list of [contributors](https://github.com/1tayH/Noisy/contributors) who participated to noisy original project.

## License

This project is licensed under the GNU GPLv3 License - see the [LICENSE](LICENSE) file for details
