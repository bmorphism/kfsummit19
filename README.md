# Kubeflow Pipelines on Anthos

This is an example of a pipeline designed for execution on kubeflow depolyed Anthos / GKE on-prem.

The example is liberally adapted from CIFAR-10 sample contributed by nvidia https://github.com/kubeflow/pipelines/tree/master/samples/contrib/nvidia-resnet

## Prerequisites

- kubeflow deployed on Anthos with:

https://github.com/kubeflow/manifests/blob/master/kfdef/kfctl_anthos.yaml

- VMWare standard storage PV / PVC for pipeline artifacts

## How to run

This assumes 'kfsummit' namespace.

0. Create PV / PVC

`kubectl apply -f pv.yaml`
`kubectl apply -f pvc.yaml`

1. Forward istio-ingress

`kubectl port-forward svc/istio-ingressgateway -n gke-system 9080:80`

2. Using kfp SDK, launch the pipeline:

```python
import kfp

c = kfp.Client("127.0.0.1:8082/pipeline", namespace="kfsummit")

c.create_run_from_pipeline_package("resnet_kfsummit.tar.gz", arguments={}, experiment_name="kfsummit")  
```