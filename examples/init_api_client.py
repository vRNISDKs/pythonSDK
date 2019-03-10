import argparse
import swagger_client


def get_api_client(args):
    config = swagger_client.Configuration()
    config.verify_ssl = False

    api_client = swagger_client.ApiClient(host="https://{}/api/ni".format(args.platform_ip))
    user_creds = swagger_client.UserCredential(username=args.username, password=args.password,
                                               domain=dict(domain_type=args.domain_type))

    auth_api = swagger_client.AuthenticationApi(api_client=api_client)

    auth_token = auth_api.create(user_creds)

    config.api_key['Authorization'] = auth_token.token
    config.api_key_prefix['Authorization'] = 'NetworkInsight'
    return api_client

#
# def get_nias_api_client(args):
#     # Setting Up swagger client for public api
#     public_api_url = "{}/ni".format(args.nias_setup_url,)
#     public_api_client = swagger_client.ApiClient(host=public_api_url)
#     config = swagger_client.Configuration()
#     config.verify_ssl = False
#     config.api_key['csp-auth-token'] = cookie.split('csp-auth-token=')[1]
#     config.deployment_type = deployment_type
#
# def get_nias_csp_auth_token(args):
#     authorize_api_url = "{}/api/auth/api-tokens/authorize?refresh_token=2d371c9d405c5c75581d49b0d1912".format(args.nias_setup_url,)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Run Public APIs on vRNI Platform')
    parser.add_argument('--csp_url', action='store', default="https://csp.nd11.vrni-symphony.com/csp/gateway/", help='Provide nias test envirnoment')
    parser.add_argument('--nias_setup_url', action='store', default="https://nd11.main.vrni-symphony.com/ni/api", help='Provide nias test envirnoment')
    parser.add_argument('--refresh_token', action='store', default="2d371c9d405c5c75581d49b0d1912", help='Provide nias test envirnoment')
    parser.add_argument('--platform_ip', action='store',
                        help='IP address of vRNI platform. In case of cluster IP address of Platform-1')
    parser.add_argument('--username', action='store', default='admin@local',
                        help='user name for authentication')
    parser.add_argument("--password", action="store",
                        default='admin', help="password for authentication")
    parser.add_argument("--domain_type", action="store",
                        default='LOCAL', help="domain type for authentication")
    parser.add_argument("--data_sources_csv", action="store",
                        default='data_sources.csv', help="domain type for authentication")
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    get_api_client()
