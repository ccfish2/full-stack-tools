# svc.ns.local
# no public FQDN
./mkcert fullstack.dolphin.local 127.0.0.1
k -n dolphin create secret tls fullstack-tls --cert fullstack.dolphin.local+1.pem --key fullstack.dolphin.local+1-key.pem
curl -v --cacert fullstack.dolphin.local+1.pem  --resolve fullstack.dolphin.local:443:{gateway-external-IP}  https://fullstack.dolphin.local/api/v1/hello -L
