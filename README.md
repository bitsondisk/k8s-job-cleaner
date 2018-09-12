# Kubernetes Job Cleaner
This is a cleaner program to remove completed, failed, or timed-out jobs from Kubernetes.

By default Kubernetes does not remove jobs until they are manually removed from the system,
even if they are successful. Running large number of jobs can cause API thrashing, and
also persist unnecessary resources.

This cleaner provides a way to clean jobs on command, or automatically through kube-cron,
to save on resources, API utilization, and reduce clutter.

## Usage

From the command line:

```
usage: k8s-job-cleaner.py [-h] [--success-seconds SUCCESS_SECONDS]
                          [--failure-seconds FAILURE_SECONDS]
                          [--all-seconds ALL_SECONDS] [--dry-run]

optional arguments:
  -h, --help            show this help message and exit
  --success-seconds SUCCESS_SECONDS
                        Delete successful jobs older than this many seconds.
                        Default: one hour (3.6 ks)
  --failure-seconds FAILURE_SECONDS
                        Delete failed jobs older than this many seconds.
                        Default: Never
  --all-seconds ALL_SECONDS
                        Delete all jobs older than this many seconds. Default:
                        Never)
  --dry-run             Print out the actions that would be taken, but don't
                        actually delete any jobs.
  --version             Show the current version of k8s-job-cleaner
```

Note that this cleaner also comes packaged with a Dockerfile and example kube-cron configuration,
so that it can be run as a cron job inside of Kubernetes, in any clusters where extra jobs need
to be cleaned.

## Docker Commands

To build the docker container locally:

`make docker`

To push the docker container:

`make push`

To tag that version as latest: (only once tested, as this deploys across clusters)

`make latest`

## Kubernetes Cron Job

To start a Kubernetes cron job to run this cleaner in a given cluster, switch to that cluster, then run:

`kubectl create -f cron-job.yaml`

You can also run in once in Kubernetes as a regular batch job with the example yaml:

`kubectl create -f run-once-as-job.yaml`

## Kubernetes Role-Based Access Control

To run successfully in a cluster, you will need to either run this command to generate an 'admin'
rolebinding for the default service account:

`kubectl create rolebinding -n default edit --serviceaccount default:default --clusterrole=admin`

Or set up a separate service account and autheticate using that, as shown in these articles:

https://kubernetes.io/docs/tasks/configure-pod-container/configure-service-account/

https://kubernetes.io/docs/reference/access-authn-authz/rbac/#default-roles-and-role-bindings
