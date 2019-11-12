
A back end API to hit Leela Chess Zero through a REST endpoint
========================================================================
AHN, Nov 2019

A GUI front end that works with this can be found at
`https://github.com/hauensteina/nibbler.git` .

It's currently all a work in progress, you might want to wait a week or so
before trying.

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

To start server for testing, say

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

There might be a globally accessible version of the server running already. Try

```bash
$ curl -d '{"cmds":[ "ucinewgame", "position startpos moves b2b4", "go nodes 1" ]}' -H "Content-Type: application/json" -X POST https://ahaux.com/lc0_server/send_cmd
```

Internals
-----------

The apache2 config on ahaux.com (marfa) forwards lc0_server to port 3719:

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
    <Location "/lc0_server">
          ProxyPass "http://127.0.0.1:3719/"
          ProxyPassReverse "http://127.0.0.1:3719/"
    </Location>

</VirtualHost>
```






<!-- Deployment Process for leela-server -->
<!-- ------------------------------------- -->
<!-- Log into the server (marfa), then: -->

<!-- $ cd /var/www/leela-server -->
<!-- $ systemctl stop leela-server -->
<!-- $ git pull origin master -->
<!-- $ git submodule update --init --recursive -->
<!-- $ systemctl start leela-server -->

<!-- The service configuration is in -->

<!-- /etc/systemd/system/leela-server.service: -->

<!-- [Unit] -->
<!-- Description=leela-server -->
<!-- After=network.target -->

<!-- [Service] -->
<!-- User=ahauenst -->
<!-- Restart=on-failure -->
<!-- WorkingDirectory=/var/www/leela-server -->
<!-- ExecStart=/home/ahauenst/miniconda/envs/venv-dlgo/bin/gunicorn -c /var/www/leela-server/gunicorn.conf -b 0.0.0.0:2719 -w 1 leela_server:app -->

<!-- [Install] -->
<!-- WantedBy=multi-user.target -->

<!-- Enable the service with -->

<!-- $ sudo systemctl daemon-reload -->
<!-- $ sudo systemctl enable leela-server -->

<!-- Deployment Process for leela-one-playout (the Web front end) -->
<!-- -------------------------------------------------------------- -->

<!-- The heroku push happens through github. -->
<!-- Log into the server (marfa), then: -->

<!-- $ cd /var/www/leela-server/leela-one-playout -->
<!-- $ git pull origin dev -->
<!-- $ git pull origin master -->
<!-- << Change the server address to prod in static/main.js >> -->
<!-- $ git merge dev -->
<!-- $ git push origin master -->

<!-- Log out of the server. -->
<!-- On your desktop, do -->

<!-- $ heroku logs -t --app leela-one-playout -->

<!-- to see if things are OK. -->

<!-- Point your browser at -->
<!-- https://leela-one-playout.herokuapp.com -->


=== The End ===
