
A Back End API to Hit Leela Chess Zero Through a REST Endpoint
========================================================================
AHN, Nov 2019

This repo contains a flask based python back end to run lc0 as a REST service.

A GUI front end that works with this can be found at
https://github.com/hauensteina/nibbler.git .

This is now fully functional.

Overview
----------

In addition to the files in this repo (lc0-server), you need the lc0 source, binary, and weights.

You can get a clone from Nov 8, 2019, including a compiled binary for Ubuntu
and the best weights file like this:

```bash
$ cd lc0-server
$ aws s3 cp s3://ahn-uploads/lc0-server/lc0.tar.gz .
$ tar zxf lc0.tar.gz
```

If prefer to do things yourself, lc0 is at

```bash
$ cd lc0-server
$ git clone https://github.com/LeelaChessZero/lc0.git
```

Then follow the build instructions in lc0/README.md .

The best weights are at

```bash
$ wget --output-document best-network https://lczero.org/get_network?sha=8e36e7bb2f857eadf3163cb5d6cc3c5800fac0eba5951f8b1e51e3b732ee938b
```
This is network 10968 from Aug 2018, which was still the best available in Nov 2019 .

To start the server for testing, say

```bash
python lc0_server.py
```

The server expects the lc0 binary and the weights in the folder

```bash
./lc0/build/release
```

The name of the weights file does not matter, lc0 auto detects it.

To test whether the server works locally, in a separate window, type:

```bash
$ curl -d  '{"cmds":[ "ucinewgame", "position startpos moves b2b4", "go nodes 1" ]}' -H "Content-Type: application/json" -X POST http://127.0.0.1:3718/send_cmd
```

I might have a globally accessible version of the server running. Try

```bash
$ curl -d '{"cmds":[ "ucinewgame", "position startpos moves b2b4", "go nodes 1" ]}' -H "Content-Type: application/json" -X POST https://ahaux.com/lc0-server/send_cmd
```

Internals
-----------

The apache2 config on ahaux.com (marfa) forwards lc0-server to port 3719:

```bash
$ cat /etc/apache2/sites-available/ahaux.conf
<VirtualHost *:443>
    SSLEngine On
    SSLCertificateFile /etc/ssl/certs/ahaux.com.crt
    SSLCertificateKeyFile /etc/ssl/private/ahaux.com.key
    SSLCACertificateFile /etc/ssl/certs/ca-certificates.crt

    ServerAdmin admin@ahaux.com
    ServerName www.ahaux.com
    DocumentRoot /var/www/ahaux
    ErrorLog /var/www/ahaux/log/error.log
    CustomLog /var/www/ahaux/log/access.log combined

   <Proxy *>
        Order deny,allow
          Allow from all
    </Proxy>
    ProxyPreserveHost On
    <Location "/lc0-server">
          ProxyPass "http://127.0.0.1:3719/"
          ProxyPassReverse "http://127.0.0.1:3719/"
    </Location>

</VirtualHost>
```

Deployment Process for lc0-server
-------------------------------------

First time install on the server (marfa):

```bash
# cd /var/www
# git clone https://github.com/hauensteina/lc0-server.git
# cd lc0-server
# aws s3 cp s3://ahn-uploads/lc0-server/lc0.tar.gz .
# tar zxf lc0.tar.gz
```

The service configuration is in

`/etc/systemd/system/lc0-server.service`:

```
[Unit]
Description=lc0-server
After=network.target

[Service]
User=ahauenst
Restart=on-failure
WorkingDirectory=/var/www/lc0-server
ExecStart=/home/ahauenst/miniconda/envs/venv-dlgo/bin/gunicorn -c /var/www/lc0-server/gunicorn.conf -b 0.0.0.0:3719 -w 1 lc0_server:app

[Install]
WantedBy=multi-user.target
```

Enable the service with

# systemctl daemon-reload
# systemctl enable lc0-server
# systemctl start lc0-server

Test with curl:

```bash
$ curl -d '{"cmds":[ "ucinewgame", "position startpos moves b2b4", "go nodes 1" ]}' -H "Content-Type: application/json" -X POST https://ahaux.com/lc0-server/send_cmd
```


=== The End ===
