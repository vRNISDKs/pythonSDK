# Python SDK Examples
# Script will get total bytes transferred for a specific IP or group of IPs
# or the scope can be any l2 network, security group, etc.

import init_api_client
import argparse
import swagger_client
import utilities
import logging
import yaml

logger = logging.getLogger("vrni_sdk")


def main(args):
    application_api = swagger_client.ApplicationsApi()

    if args.application_backup_action == 'save':
        all_apps = []
        params = dict(size=10)
        while True:
            apps = application_api.list_applications(**params)
            for i in apps.results:
                app = application_api.get_application(i.entity_id)
                tiers = application_api.list_application_tiers(id=app.entity_id)
                app_to_save = dict(name=app.name, no_of_tiers=len(tiers.results), tiers=tiers.to_dict())
                all_apps.append(app_to_save)
            if not apps.cursor:
                break
            params['cursor'] = apps.cursor

        with open(args.application_backup_csv, 'w') as outfile:
            yaml.dump(all_apps, outfile, default_flow_style=False)

    if args.application_backup_action == 'restore':
        with open(args.application_backup_csv, 'r') as outfile:
            all_apps = yaml.load(outfile)
        print(all_apps)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Run Public APIs on vRNI Platform')
    parser.add_argument('--platform_ip', action='store',
                        help='IP address of vRNI platform. In case of cluster IP address of Platform-1')
    parser.add_argument('--username', action='store', default='admin@local',
                        help='user name for authentication')
    parser.add_argument("--password", action="store",
                        default='admin', help="password for authentication")
    parser.add_argument("--domain_type", action="store",
                        default='LOCAL', help="domain type for authentication")
    parser.add_argument("--data_sources_csv", action="store",
                        default='data_sources.csv', help="Data sources are saved in this csv")
    parser.add_argument("--application_backup_csv", action="store",
                        default='application_backup.yml', help="Applications and tiers are saved in this csv")
    parser.add_argument("--application_backup_action", action="store",
                        default='save', help="Action can be 'save' or 'restore'")

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse_arguments()
    utilities.configure_logging("/tmp")
    api_client = init_api_client.get_api_client(args)
    main(args)
