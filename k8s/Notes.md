```
 kubectl -n kube-system create sa tiller \
 && kubectl create clusterrolebinding tiller \
 --clusterrole cluster-admin \
--serviceaccount=kube-system:tiller
helm init --skip-refresh --upgrade --service-account tiller
helm repo update # run twice if bad connection
```

>Dashboard
```
helm install stable/kubernetes-dashboard --name kubernetes-dashboard --namespace kube-system --set=ingress.enabled=true,ingress.hosts[0]=test-kube.auvence.co,ingress.path=/dashboard,ingress.hosts=ingress.local,ingress.annotations[0]="kubernetes.io/ingress.class"
helm install stable/kubernetes-dashboard --name kubernetes-dashboard --namespace kube-system --set ingress.enabled=True,ingress.ingress.path=/dashboard,ingress.annotations[0]="kubernetes.io/ingress.class: nginx"

helm install stable/kubernetes-dashboard --name kubernetes-dashboard --namespace kube-system --set=ingress.enabled=true,ingress,ingress.path=/dashboard,ingress.annotations."nginx\.ingress\.kubernetes\.io/secure-backends"="true"

```

>Admin user
```
kubectl apply -f admin-sa.yaml \
&& kubectl apply -f admin-role.yaml
```

>Get Admin token
```
kubectl -n kube-system describe secret $(kubectl -n kube-system get secret | grep admin-user | awk '{print $1}'
```

```
curl http://localhost:8001/api/v1/namespaces/kube-system/services/https:kubernetes-dashboard:/proxy/#!/login
\\\

# Create certs
kubectl create secret generic kubernetes-dashboard-certs --from-file=fregate.crt -n kube-system
helm install stable/docker-registry --name docker-registry --namespace ingress-nginx --set=ingress.enabled=true,ingress.hosts[0]=fregate.local
helm install --name my-release stable/grafana --name gra --namespace ingress-nginx --set=ingress.enabled=true,ingress.hosts[0]=fregate.local
