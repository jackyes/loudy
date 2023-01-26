# Examples

## Run multiple containers using `docker-compose`

`docker-compose` is useful if you want to run more than one container at the same time, to generate more noise. To do so, simply run the following commands:
```
$ cd examples/docker-compose
$ docker-compose build
$ docker-compose up --scale loudy=<number-of-containers>
```

## Set loudy to run automatically via systemd

You can use systemd to start loudy.py automatically on every boot. The provided
example service assumes that you have the script copied to /opt/loudy and that
loudy.py and config.json are readable by the 'loudy' user. You can change these
values to suit your needs.

To configure the service:
```
$ sudo cp examples/systemd/loudy.service /etc/systemd/system
$ sudo systemctl daemon-reload
$ sudo systemctl enable loudy && sudo systemctl start loudy
```

You can view the script's output by running:
```
$ journalctl -f -n loudy
```
