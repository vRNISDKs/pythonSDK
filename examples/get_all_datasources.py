#
# This script uses an input CSV (example: data_sources.csv)
# To add multiple vRealize Network Insight Data Sources. Modify data_sources.csv to contain your own data sources (vCenters, NSX, switches, firewalls)
# and run this script with the param --data_sources_csv to your CSV.

# Note: -
# DataSourceType in data_sources.csv is taken from swagger_client.models.data_source_type.py
# For reference here are the data source types that can be used in CSV
# CiscoSwitchDataSource, DellSwitchDataSource, AristaSwitchDataSource, BrocadeSwitchDataSource, JuniperSwitchDataSource,
# GDDataSource, VCenterDataSource, NSXVManagerDataSource, UCSManagerDataSource, HPVCManagerDataSource,
# HPOneViewDataSource, PanFirewallDataSource, CheckpointFirewallDataSource, NSXTManagerDataSource, KubernetesDataSource,
# InfobloxManagerDataSource

# Cisco Switch type can be taken from from swagger_client.models.cisco_switch_type.py -
# CATALYST_3000, CATALYST_4500, CATALYST_6500, NEXUS_5K, NEXUS_7K, NEXUS_9K

import swagger_client
import init_api_client
import csv
from swagger_client.rest import ApiException
import swagger_client.models.data_source_type as data_source_type
import json


# DATASOURCES_LIST = ["VCenterDataSource","CiscoSwitchDataSource","NSXVManagerDataSource","NSXTManagerDataSource"]
DATASOURCES_LIST = ["VCenterDataSource"]

def get_api_function_name(datasource_type):
    datasource = {data_source_type.DataSourceType.CISCOSWITCHDATASOURCE: "list_cisco_switches",
                  data_source_type.DataSourceType.DELLSWITCHDATASOURCE: "list_dell_switches",
                  data_source_type.DataSourceType.ARISTASWITCHDATASOURCE: "list_arista_switches",
                  data_source_type.DataSourceType.BROCADESWITCHDATASOURCE: "list_brocade_switches",
                  data_source_type.DataSourceType.JUNIPERSWITCHDATASOURCE: "list_juniper_switches",
                  data_source_type.DataSourceType.VCENTERDATASOURCE: "list_vcenters",
                  data_source_type.DataSourceType.NSXVMANAGERDATASOURCE: "list_nsxv_managers",
                  data_source_type.DataSourceType.UCSMANAGERDATASOURCE: "list_ucs_managers",
                  data_source_type.DataSourceType.HPVCMANAGERDATASOURCE: "list_hpvc_managers",
                  data_source_type.DataSourceType.HPONEVIEWDATASOURCE: "list_hpov_managers",
                  data_source_type.DataSourceType.PANFIREWALLDATASOURCE: "list_panorama_firewalls",
                  data_source_type.DataSourceType.CHECKPOINTFIREWALLDATASOURCE: "list_checkpoint_firewalls",
                  data_source_type.DataSourceType.NSXTMANAGERDATASOURCE: "list_nsxt_managers",
                  data_source_type.DataSourceType.INFOBLOXMANAGERDATASOURCE: "list_infoblox_managers",
                  data_source_type.DataSourceType.POLICYMANAGERDATASOURCE: "list_policy_managers",
                  data_source_type.DataSourceType.KUBERNETESDATASOURCE: 'list_kubernetes_clusters'}

    return datasource[datasource_type]

def main(api_client, args):

    # Create data source API client object
    datasource_api = swagger_client.DataSourcesApi(api_client=api_client)
    for data_source_type in DATASOURCES_LIST:
        data_source_api_name = get_api_function_name(data_source_type)
        list_datasource_api_fn = getattr(datasource_api, data_source_api_name)
        try:
            response = list_datasource_api_fn()
            print("Successfully got list of: {} : Response : {}".format(data_source_type, response))
        except ApiException as e:
            print("Failed getting list of data source type: {} : Error : {} ".format(data_source_type, json.loads(e.body)))

if __name__ == '__main__':
    args = init_api_client.parse_arguments()
    api_client = init_api_client.get_api_client(args)
    main(api_client, args)
