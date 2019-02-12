#
# This script uses an input CSV (example: data_sources.csv)
# To add multiple vRealize Network Insight Data Sources. Modify data_sources.csv to contain your own data sources (vCenters, NSX, switches, firewalls)
# and run this script with the param --data_sources_csv to your CSV.

# Note: -
# DataSourceType in DATASOURCES_LIST is taken from swagger_client.models.data_source_type.py
# For reference here are the data source types that can be used in CSV
# CiscoSwitchDataSource, DellSwitchDataSource, AristaSwitchDataSource, BrocadeSwitchDataSource, JuniperSwitchDataSource,
# GDDataSource, VCenterDataSource, NSXVManagerDataSource, UCSManagerDataSource, HPVCManagerDataSource, PolicyManagerDataSource,
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
DATASOURCES_LIST = ["CiscoSwitchDataSource"]

def get_api_function_name(datasource_type):
    datasource = {data_source_type.DataSourceType.CISCOSWITCHDATASOURCE: {"list" : "list_cisco_switches",
                                                                          "get": "get_cisco_switch"},
                  data_source_type.DataSourceType.DELLSWITCHDATASOURCE: {"list": "list_dell_switches",
                                                                         "get": "get_dell_switch"},
                  data_source_type.DataSourceType.ARISTASWITCHDATASOURCE: {"list": "list_arista_switches",
                                                                           "get": "get_arista_switch"},
                  data_source_type.DataSourceType.BROCADESWITCHDATASOURCE: {"list": "list_brocade_switches",
                                                                            "get": "get_brocade_switch"},
                  data_source_type.DataSourceType.JUNIPERSWITCHDATASOURCE: {"list": "list_juniper_switches",
                                                                            "get": "get_juniper_switch"},
                  data_source_type.DataSourceType.VCENTERDATASOURCE: {"list": "list_vcenters",
                                                                      "get": "get_vcenter"},
                  data_source_type.DataSourceType.NSXVMANAGERDATASOURCE: {"list": "list_nsxv_managers",
                                                                          "get": "get_nsxv_manager"},
                  data_source_type.DataSourceType.UCSMANAGERDATASOURCE: {"list": "list_ucs_managers",
                                                                         "get": "get_ucs_manager"},
                  data_source_type.DataSourceType.HPVCMANAGERDATASOURCE: {"list": "list_hpvc_managers",
                                                                          "get": "get_hpvc_manager"},
                  data_source_type.DataSourceType.HPONEVIEWDATASOURCE: {"list": "list_hpov_managers",
                                                                        "get": "get_hpov_manager"},
                  data_source_type.DataSourceType.PANFIREWALLDATASOURCE: {"list": "list_panorama_firewalls",
                                                                          "get": "get_panorama_firewall"},
                  data_source_type.DataSourceType.CHECKPOINTFIREWALLDATASOURCE: {"list": "list_checkpoint_firewalls",
                                                                                 "get": "get_checkpoint_firewall"},
                  data_source_type.DataSourceType.NSXTMANAGERDATASOURCE: {"list": "list_nsxt_managers",
                                                                          "get": "get_nsxt_manager"},
                  data_source_type.DataSourceType.INFOBLOXMANAGERDATASOURCE: {"list": "list_infoblox_managers",
                                                                              "get": "get_infoblox_manager"},
                  data_source_type.DataSourceType.POLICYMANAGERDATASOURCE: {"list": "list_policy_managers",
                                                                            "get": "get_policy_manager"},
                  data_source_type.DataSourceType.KUBERNETESDATASOURCE: {"list": "list_kubernetes_clusters",
                                                                         "get": "get_kubernetes_cluster"}}

    return datasource[datasource_type]

def main(api_client, args):

    # Create data source API client object
    datasource_api = swagger_client.DataSourcesApi(api_client=api_client)
    with open("list_of_datasources.csv", 'w') as csvFile:
        fields = ["DataSourceType","IP","Username","Password","CSPRefreshToken","NickName","CentralCliEnabled",
           "IPFixEnabled","SwitchType","ParentvCenter","IsVMC","ProxyIP"]
        writer = csv.DictWriter(csvFile, fieldnames=fields)
        writer.writeheader()
        data =[]
        for data_source_type in DATASOURCES_LIST:
            data_source_api_name = get_api_function_name(data_source_type)
            list_datasource_api_fn = getattr(datasource_api, data_source_api_name["list"])
            get_datasource_fn = getattr(datasource_api, data_source_api_name["get"])
            try:
                data_source_list = list_datasource_api_fn()
                print("Successfully got list of: {} : Response : {}".format(data_source_type, data_source_list))
                for data_source in  data_source_list.results:
                    ds = get_datasource_fn(id=data_source.entity_id)
                    print("Successfully got {} : Response : {}".format(data_source_type, ds))
                    data.append({"DataSourceType" : "{}".format(ds.entity_type), "IP": "{}".format(ds.ip),"NickName" : "{}".format(ds.nickname)})
            except ApiException as e:
                print("Failed getting list of data source type: {} : Error : {} ".format(data_source_type, json.loads(e.body)))
        writer.writerows(data)

if __name__ == '__main__':
    args = init_api_client.parse_arguments()
    api_client = init_api_client.get_api_client(args)
    main(api_client, args)
