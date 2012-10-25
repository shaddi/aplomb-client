"""
Tasks for client auth:
- Generate initial client UUID
- Send request to get client keys/certs.
- Send generic requests wrapped with client key/cert to server.
- (probably not actually this code) Run a web service to allow user to log in with username/password to begin first-run.
"""

import os
import time
import uuid

import requests
import envoy

import config

conf = config.Config()

def set_uuid():
    if not os.path.exists(conf.uuid_file):
        f = open(conf.uuid_file, "w")
        uuid_ = uuid.uuid4()
        f.write(str(uuid_))
        f.close()

    if not os.path.exists(conf.uuid_html):
        f = open(conf.uuid_html, "w")
        f.write("<html><head><title>Welcome to APLOMB!</title></head><body><center><h1>Welcome to APLOMB!</h1><br /><h2>This client's UUID is %s.</h2></center></body></html>" % conf.uuid)
        f.close()

    return uuid_

def gen_key_and_csr(conf_file=conf.openssl_conf, key_name="aplomb-private.key", csr_name="aplomb-csr.csr"):
    openssl_cmd_str = "openssl req -out %s -new -newkey rsa:2048 -nodes -keyout %s -config %s" % (csr_name, key_name, conf_file)
    r = requests.get("%s/sslconf" % conf.conf_server, params={"uuid": conf.uuid})
    http_status = r.status_code
    if r.status_code == 200:
        f = open(conf_file, "w")
        f.write(r.content)
        f.close()

        r = envoy.run(openssl_cmd_str)
        if r.status_code != 0:
            raise Exception

    return http_status


def get_csr_signed(csr_file):
    if not os.path.exists(csr_file):
        return
    f = open(csr_file, "r")
    csr_data = ""
    for line in f:
        csr_data += line
    f.close()

    r = requests.post("%s/csr" % conf.conf_server, data={"csr_data":csr_data, "uuid": conf.uuid})
    if r.status_code == 200:
        f = open(conf.client_crt, "w")
        f.write(r.content)
        f.close()
    return r.status_code

def main():
    # get uuid
    uuid_ = set_uuid()
    print "This client's ID is: %s" % uuid_

    while True:
        try:
            if gen_key_and_csr() == 200:
                break
            else:
                print "Bad response. Maybe UUID isn't registered?"
        except requests.exceptions.ConnectionError:
            print "Couldn't connect! Retrying..."
        except:
            print "Problem with OpenSSL! Aborting."
        time.sleep(15) # wait 15 seconds

    print "Generated key and CSR!"
    while True:
        try:
            if get_csr_signed("aplomb-csr.csr") == 200:
                break
            else:
                print "Bad response. Retrying..."
        except requests.exceptions.ConnectionError:
            print "Couldn't connect! Retrying..."
        except:
            print "Problem with OpenSSL! Aborting."
        time.sleep(15) # wait 15 seconds

    print "Keys generated!"

if __name__ == "__main__":
    main()
