#
# This script write the added datasource in an input CSV (example: data_sources.csv)
# To list multiple vRealize Network Insight Data Sources run this script with the param --data_sources_csv to your CSV.

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


DATASOURCES_LIST = ["VCenterDataSource","CiscoSwitchDataSource","NSXVManagerDataSource","NSXTManagerDataSource",
                   "PolicyManagerDataSource", "PanFirewallDataSource"]

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

def get_vcenter_manager_ip(api_client, datasource_api, datasource):
    # USING search public API to get Vcenter IP address

    # Getting entity id of
    search_api = swagger_client.SearchApi(api_client=api_client)
    if datasource.entity_type == "NSXVManagerDataSource":
        nsx_entity_id = get_nsxv_manager_entity_id(search_api, datasource.ip)

    elif datasource.entity_type == "PolicyManagerDataSource":
        return None
    search_payload = dict(entity_type=swagger_client.EntityType.VCENTERMANAGER,
                                 filter="nsx_manager.entity_id = '{}'".format(nsx_entity_id))
    vcenter = search_api.search_entities(body=search_payload).results[0]
    entities_api = swagger_client.EntitiesApi(api_client=api_client)
    get_entity_by_id_fn = getattr(entities_api, "get_vcenter_manager")
    vcenter = get_entity_by_id_fn(id=vcenter.entity_id)
    return vcenter.ip_address.ip_address

def get_nsxv_manager_entity_id(search_api, nsx_ip):
    search_payload = dict(entity_type=swagger_client.EntityType.NSXVMANAGER,
                                 filter="ip_address.ip_address = '{}'".format(nsx_ip))
    result = search_api.search_entities(body=search_payload).results[0]
    return result.entity_id

def get_nsxt_manager_entity_id(search_api, nsx_ip):
    search_payload = dict(entity_type=swagger_client.EntityType.NSXTMANAGER,
                                 filter="ip_address.ip_address = '{}'".format(nsx_ip))
    result = search_api.search_entities(body=search_payload).results[0]
    return result.entity_id

def get_data(datasource_api, datasource):
    data = {}
    if datasource.entity_type == "NSXVManagerDataSource" or datasource.entity_type == "PolicyManagerDataSource":
        vcenter_ip = get_vcenter_manager_ip(api_client, datasource_api, datasource)
        data["ParentvCenter"] = "{}".format(vcenter_ip)
    data["DataSourceType"] = "{}".format(datasource.entity_type)
    data["IP"] = "{}".format(datasource.ip)
    if hasattr(datasource, "credentials"):
        data["Username"] = "{}".format(datasource.credentials.username)
    data["NickName"] = "{}".format(datasource.nickname)
    if hasattr(datasource ,"SwitchType"):
        data["SwitchType"] = "{}".format(datasource.switch_type)
    if hasattr(datasource ,"ipfix_enabled"):
        data["IPFixEnabled"] = "{}".format(datasource.ipfix_enabled)
    if hasattr(datasource ,"central_cli_enabled"):
        data["CentralCliEnabled"] = "{}".format(datasource.central_cli_enabled)
    return data

def main(api_client, args):

    # Create data source API client object
    datasource_api = swagger_client.DataSourcesApi(api_client=api_client)
    with open("{}".format(args.data_sources_csv), 'w') as csvFile:
        fields = ["DataSourceType","IP","Username","Password","CSPRefreshToken","NickName","CentralCliEnabled",
           "IPFixEnabled","SwitchType","ParentvCenter","IsVMC"]
        writer = csv.DictWriter(csvFile, fieldnames=fields)
        writer.writeheader()
        data =[]
        for data_source_type in DATASOURCES_LIST:
            data_source_api_name = get_api_function_name(data_source_type)
            # Get lis function for datasource
            list_datasource_api_fn = getattr(datasource_api, data_source_api_name["list"])
            get_datasource_fn = getattr(datasource_api, data_source_api_name["get"])
            try:
                data_source_list = list_datasource_api_fn()
                print("Successfully got list of: {} : Response : {}".format(data_source_type, data_source_list))
                for data_source in  data_source_list.results:
                    datasource = get_datasource_fn(id=data_source.entity_id)
                    print("Successfully got {} : Response : {}".format(data_source_type, datasource))
                    data.append(get_data(datasource_api, datasource))
            except ApiException as e:
                print("Failed getting list of data source type: {} : Error : {} ".format(data_source_type, json.loads(e.body)))
        writer.writerows(data)

if __name__ == '__main__':
    args = init_api_client.parse_arguments()
    api_client = init_api_client.get_api_client(args)
    main(api_client, args)
