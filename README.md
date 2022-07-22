# Kubernetes Validating Webhook

K8s validating webhook written in Python using Flask.

The required label is set through environment variable in the webhook deployment file.

```
env:
- name: LABEL
  value: delete-me
  
- name: VALUE
  value: true
```

# SSL 

Communication between webhook and controller should be protected with SSL. 
To do so, the whole chain should be prepared - CA, cert and key.

For Mac users:
You must install a new, separate version of `openssl` to use `subjectAltName`.

```
brew install openssl
```

and then add to your `.zshrc`:

```
export PATH="/usr/local/opt/openssl@3/bin:$PATH"
```

## Create Certificate Authority

```
openssl req -x509 \
            -sha256 -days 356 \
            -nodes \
            -newkey rsa:2048 \
            -subj "/CN=validate.infra-webhooks.svc/C=US/L=Valhalla" \
            -keyout rootCA.key -out rootCA.crt
```

## Create Self-Signed Certificates using OpenSSL

-  Create the Server Private Key

```
openssl genrsa -out server.key 2048
```

- Create Certificate Signing Request Configuration

```
cat > csr.conf <<EOF
[ req ]
default_bits = 2048
prompt = no
default_md = sha256
req_extensions = req_ext
distinguished_name = dn

[ dn ]
C = US
ST = NC
L = Valhalla
O = Boat 1
OU = Viking Squat 1
CN = validate.infra-webhooks.svc

[ req_ext ]
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = validate.infra-webhooks.svc

EOF
```

- Generate Certificate Signing Request (CSR) Using Server Private Key

```
openssl req -new -key server.key -out server.csr -config csr.conf
```

- Create a external file

```
cat > cert.conf <<EOF

authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = validate.infra-webhooks.svc

EOF
```

- Generate SSL certificate With self signed CA

```
openssl x509 -req \
    -in server.csr \
    -CA rootCA.crt -CAkey rootCA.key \
    -CAcreateserial -out server.crt \
    -days 365 \
    -sha256 -extfile cert.conf
```
