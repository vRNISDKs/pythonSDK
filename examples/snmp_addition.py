# swagger Examples - Adding datasources in bulk
#
# This script uses an input CSV (example: data_sources.csv)
# To add multiple vRealize Network Insight Data Sources. Modify data_sources.csv to contain your own data sources
# (vCenters, NSX, switches, firewalls)
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

import csv
import json
import logging

import swagger_client

from swagger_client.rest import ApiException
import swagger_client.models.data_source_type as data_source_type

import init_api_client
import utilities

logger = logging.getLogger("vrni_sdk")


def get_api_function_name(datasource_type):
    datasource = {data_source_type.DataSourceType.CISCOSWITCHDATASOURCE: {"snmp_config": "update_cisco_switch_snmp_config",
                                                                          "list" : "list_cisco_switches",
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

def get_add_request_body(datasource, proxy_id=None, vcenter_id=None):
    api_request_body = {
        "ip": "{}".format(datasource['IP']),
        "fqdn": "",
        "proxy_id": "{}".format(proxy_id),
        "enabled": True,
        "nickname": datasource["NickName"],
        "notes": "added by public api",
    }
    if datasource['Username']:
        api_request_body["credentials"] = {"username": "{}".format(datasource['Username']),
                               "password": "{}".format(datasource['Password'])}
    if datasource['CSPRefreshToken']:
        api_request_body["csp_refresh_token"] = datasource['CSPRefreshToken']
    if datasource['CentralCliEnabled']:
        api_request_body["central_cli_enabled"] = datasource['CentralCliEnabled']
    if datasource['IPFixEnabled']:
        api_request_body["ipfix_enabled"] = datasource['IPFixEnabled']
    if vcenter_id:
        api_request_body['vcenter_id'] = vcenter_id
    if datasource['SwitchType']:
        api_request_body["switch_type"] = datasource['SwitchType']
    if datasource['IsVMC']:
        api_request_body["is_vmc"] = datasource['IsVMC']
    logger.info("Request body : <{}>".format(api_request_body))
    return api_request_body


def get_snmp_request_body(datasource):
    api_request_body = {
            "snmp_enabled": True,
            "snmp_version": "{}".format(datasource['snmp_version']),
        }

    snmp_config = dict()
    if datasource['snmp_version'] == 'v2c':
        snmp_config = dict(config_snmp_2c=dict(community_string='{}'.format(datasource['snmp_community_string'])))

    elif datasource['snmp_version'] == 'v3':
        snmp_config = dict(config_snmp_3=dict(
            username="{}".format(datasource['snmp_username']),
            authentication_password="{}".format(datasource['snmp_password']),
            context_name="",
            authentication_type="{}".format(datasource['snmp_auth_type']),
            privacy_type="{}".format(datasource['snmp_privacy_type'])
        ))

    api_request_body.update(snmp_config)

    logger.info("Request body : <{}>".format(api_request_body))
    return api_request_body


def get_node_entity_id(api_client, proxy_ip=None):
    infrastructure_api = swagger_client.InfrastructureApi(api_client=api_client)
    node_list = infrastructure_api.list_nodes()
    for entity in node_list.results:
        node = infrastructure_api.get_node(id=entity.id)
        if proxy_ip == node.ip_address:
            return node.id
    return None


def get_vcenter_manager_entity_id(data_source_api, vcenter_ip=None):
    if not vcenter_ip: return None
    data_source_list = data_source_api.list_vcenters()
    for entity in data_source_list.results:
        ds = data_source_api.get_vcenter(id=entity.entity_id)
        if ds.ip == vcenter_ip:
            return entity.entity_id
    return None


proxy_ip_to_id = dict()

def main(api_client, args):

    # Create data source API client object
    data_source_api = swagger_client.DataSourcesApi(api_client=api_client)
    with open("{}".format(args.data_sources_csv), 'rb') as csvFile:
        data_sources = csv.DictReader(csvFile)
        for data_source in data_sources:
            switch_ip = data_source['IP']
            nickname = data_source['NickName']
            data_source_type = data_source['DataSourceType']

            # Get the Proxy ID from Proxy IP
            if data_source['ProxyIP'] not in proxy_ip_to_id:
                proxy_id = get_node_entity_id(api_client, data_source['ProxyIP'])
                if not proxy_id:
                    print("Incorrect Proxy IP {}".format(data_source['ProxyIP']))
                    continue
                proxy_ip_to_id[data_source['ProxyIP']] = proxy_id
            else:
                proxy_id = proxy_ip_to_id[data_source['ProxyIP']]

            # Get vCenter ID for vCenter manager required for adding NSX
            vcenter_id = get_vcenter_manager_entity_id(data_source_api, data_source['ParentvCenter'])
            print("Adding: <{}> <{}>".format(data_source_type, data_source['IP']))
            # Get the Data source add api fn
            data_source_api_name = get_api_function_name(data_source_type)
            list_datasource_api_fn = getattr(data_source_api, data_source_api_name["list"])
            get_datasource_fn = getattr(data_source_api, data_source_api_name["get"])
            try:
                data_source_list = list_datasource_api_fn()
                print("Successfully got list of: {} : Response : {}".format(data_source_type, data_source_list))
                for data_source1 in data_source_list.results:
                    datasource11 = get_datasource_fn(id=data_source1.entity_id)
                    print("Successfully got {} : Response : {}".format(data_source_type, datasource11.fqdn))
                    if data_source['snmp_version']:
                        if datasource11.proxy_id == proxy_id:
                            print("Successfully got {} : Response : {}".format(data_source_type, datasource11))
                            add_snmp_api_fn = getattr(data_source_api, data_source_api_name['snmp_config'])
                            try:
                                response = add_snmp_api_fn(id=datasource11.entity_id, body=get_snmp_request_body(data_source))
                                print("Successfully added: {} {} snmp : Response : {}".format(data_source_type, data_source['IP'],
                                                                                              response))
                            except ApiException as e:
                                print(
                                "Failed adding snmp: {} : Error : {} ".format(data_source['IP'], json.loads(e.body)))

            except ApiException as e:
                print("Failed adding data source: {} : Error : {} ".format(data_source['IP'], json.loads(e.body)))

if __name__ == '__main__':
    args = init_api_client.parse_arguments()
    utilities.configure_logging("/tmp")
    api_client = init_api_client.get_api_client(args)
    main(api_client, args)
