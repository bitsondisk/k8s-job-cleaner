#!/usr/bin/env python3

import argparse
from datetime import datetime, timezone, timedelta
import os

import kubernetes


__version__ = '0.1.0'


def delete_job(client, job, options, dry_run):
    """ Deletes the specified job, unless dry_run is True """

    if not dry_run:
        return client.delete_namespaced_job(
            job.metadata.name, job.metadata.namespace, options, propagation_policy='Background')


def delete_job_if_expired(client, job, options, dry_run, success_timeout, failure_timeout, all_timeout):
    """ Deletes the given job if is it expired, based on the given timeouts """

    current_time = datetime.now(timezone.utc)
    completion_time = None

    status = job.status
    name = job.metadata.name

    completion_time = status.completion_time
    start_time = status.start_time

    if not start_time:
        start_time = job.metadata.creation_timestamp

    if completion_time:
        since_completed = current_time - completion_time
    else:
        since_completed = None

    if start_time:
        since_started = current_time - start_time
    else:
        since_started = None

    since_ran = since_completed if since_completed else since_started

    if not since_ran:
        print(f'Skipping job {name} as it has no completion_time or start_time')

    succeeded = True if status.succeeded else False
    failed = True if status.failed else False

    action = 'Would delete' if dry_run else 'Deleting'
    how_old = f'({since_ran.total_seconds():.0f} seconds old'
    message = f'{action} job {name} {how_old}'

    if succeeded and success_timeout and since_ran > success_timeout:
        print(f'{message} and succeeded)')
        return delete_job(client, job, options, dry_run)

    if failed and failure_timeout and since_ran > failure_timeout:
        print(f'{message} and failed)')
        return delete_job(client, job, options, dry_run)

    if all_timeout and since_ran > all_timeout:
        print(f'{message} and timed-out)')
        return delete_job(client, job, options, dry_run)

    # Not deleting this job
    return None


def main():
    """ Parses command line arguments, gets the list of jobs, then deletes any that match the given criteria """

    parser = argparse.ArgumentParser()

    parser.add_argument('--success-seconds', type=int, default=3600,
                        help='Delete successful jobs older than this many seconds. Default: one hour (3.6 ks)')
    parser.add_argument('--failure-seconds', type=int, default=None,
                        help='Delete failed jobs older than this many seconds. Default: Never')
    parser.add_argument('--all-seconds', type=int, default=None,
                        help='Delete all jobs older than this many seconds. Default: Never)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Print out the actions that would be taken, but do not actually delete any jobs.')
    parser.add_argument('--version', action='version', help='Show the current version of k8s-job-cleaner',
                        version='%(prog)s {version}'.format(version=__version__))

    args = parser.parse_args()

    success_timeout = timedelta(seconds=args.success_seconds)
    failure_timeout = timedelta(seconds=args.failure_seconds) if args.failure_seconds else None
    all_timeout = timedelta(seconds=args.all_seconds) if args.all_seconds else None
    dry_run = True if args.dry_run else False

    # Load default credentials
    if os.path.exists(os.path.expanduser('~/.kube/config')):
        kubernetes.config.load_kube_config()
    else:
        kubernetes.config.load_incluster_config()

    # Create the Batch API Client
    batch_client = kubernetes.client.BatchV1Api()
    delete_options = kubernetes.client.V1DeleteOptions(propagation_policy='Background')

    print('Checking for jobs')

    jobs = batch_client.list_namespaced_job('default', watch=False)

    j_len = len(jobs.items)

    if j_len == 0:
        print('No jobs found')
        return
    else:
        print(f'Checking {j_len} jobs')

    for j in jobs.items:
        delete_job_if_expired(batch_client, j, delete_options, dry_run, success_timeout, failure_timeout, all_timeout)

    print('Done')


if __name__ == '__main__':
    main()
