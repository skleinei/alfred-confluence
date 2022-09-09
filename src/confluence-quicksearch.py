import argparse
import ast
import base64
import json
import os
import re
import requests
import sys
import urllib



def log(message, args):
    if args.output != 'alfred':
        if args.verbose:
            print(message)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("text", metavar='text', nargs='+')
    parser.add_argument("--url", help="Specify the url. E.g. https://k15t.atlassian.net/ or https://k15t.jira.com/ (for really old cloud instances)")
    parser.add_argument("--user", help="Specify the user's email")
    parser.add_argument("--token", help="Specify the authentication token (generate one here: https://id.atlassian.com/manage/api-tokens)")
    parser.add_argument("-o", "--output", default='cli', help="Specify output mode [alfred|cli].")
    parser.add_argument("-s", "--space", nargs="*", default=[], help="Specify the space key")
    parser.add_argument("-l", "--limit", nargs="?", default=10, help="Specify the max number of results")
    parser.add_argument("-t", "--type", nargs="*", help="Type of content to search for [page,blogpost,attachment] (default: page,blogpost)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Switch on logging")
    
    args = parser.parse_args()
    
    args.text_as_string = " ".join(args.text)

    args.url = validate_url(args)
    args.user = validate_user(args)
    args.token = validate_token(args)

    args.path_prefix = ""
    args.is_enterprise = True
    if re.search("atlassian.net", args.url) or re.search("jira.com", args.url):
        args.is_enterprise = False
        args.path_prefix = "/wiki"
    
    args.space = validate_space(args)
    args.type = validate_type(args)

    return args


def validate_url(args):
    url = os.getenv("CA_URL", args.url)
    log(url, args)

    if url == None or len(url) <= 0:
        raise Exception("URL not specified.")

    return url


def validate_user(args):
    user = os.getenv("CA_USER", args.user)
    log(user, args)

    if user == None or len(user) <= 0:
        raise Exception("User not specified.")

    return user


def validate_token(args):
    token = os.getenv("CA_TOKEN", args.token)
    log(token, args)

    if token == None or len(token) <= 0:
        raise Exception("Token not specified.")

    return token


def validate_space(args):
    return args.space


def validate_type(args):
    if args.type and len(args.type) and all(type in ['page', 'blogpost', 'attachment'] for type in args.type):
        return args.type
    else:
        default_content_types = []
        if int(os.getenv('CA_CONTENT_TYPE_PAGE', '1')):
            default_content_types.append("page")
        if int(os.getenv('CA_CONTENT_TYPE_BLOGPOST', '1')):
            default_content_types.append("blogpost")
        if int(os.getenv('CA_CONTENT_TYPE_ATTACHMENT', '0')):
            default_content_types.append("attachment")

        return default_content_types


def search_confluence(args):
    response = requests.request(
        "GET",
        get_base_url(args) + '/rest/api/search',
        headers = {
            "Accept": "application/json",
            "Authorization": create_auth(args)
        },
        params = create_search_query(args)
    )

    if response.status_code != 200:
        raise Exception('Response {} ({})'.format(response.status_code, response.text))

    log(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")), args)
    
    return json.loads(response.text)["results"]


def get_base_url(args):
    return args.url + args.path_prefix


def create_auth(args):
    message = args.user + ':' + args.token
    message_bytes = message.encode('utf-8')
    base64_bytes = base64.b64encode(message_bytes)
    auth_header = 'Basic ' + base64_bytes.decode('utf-8')
    log(auth_header, args)
    return auth_header


def create_search_query(args):
    log('text:   {}'.format(args.text), args)
    log('spaces: {}'.format(args.space), args)
    log('types:  {}'.format(args.type), args)

    cql = 'title ~ "' + args.text_as_string + '"'

    if args.space:
        cql += ' AND space in ("' + '", "'.join(args.space) + '")'

    if args.type:
        cql += ' AND type IN ("' + '", "'.join(args.type) + '")'

    log('cql:    {}'.format(cql), args)

    return {
        'cql': cql,
        'limit': args.limit,
        'expand': 'content.space,content.metadata.properties.emoji_title_published,content.history.lastUpdated'
    }


def create_output(searchResults, args):
    if args.output == 'alfred':
        alfredItems = convert_to_alfred_items(searchResults, args)
        sys.stdout.write(json.dumps({
            "items": alfredItems
        }))
    else:
        textResult = convert_to_text_result(searchResults, args)
        sys.stdout.write(textResult)


def convert_to_alfred_items(search_results, args):
    alfred_items = []

    if len(search_results) < 1:
        alfred_items.append({
            "title": "No search results",
            "subtitle": "Hit <enter> to do a full-text search for '" + args.text_as_string + "' in Confluence",
            "arg": get_base_url(args) + "/search?text=" + urllib.parse.quote(args.text_as_string),
            "icon": {
                "path": "./assets/search-for.png"
            },
        })

    for result in search_results:
        # docs: https://www.alfredapp.com/help/workflows/inputs/script-filter/json/ 
        result = {
            "title": create_title(result, args),
            "subtitle": create_subtitle(result, args),
            "arg": create_url(result, args),
            "icon": {
                "path": get_icon_path(result, args)
            },
            "mods": get_mods(result, args),
            "text": {
                "copy": create_url(result, args),
                "largetype": create_url(result, args)
            }
        }
        
        alfred_items.append(result)

    return alfred_items


def create_title(result, args):
    if "emoji-title-published" in result["content"]["metadata"]["properties"]:
        emoji = chr(ast.literal_eval('0x'+ result["content"]["metadata"]["properties"]["emoji-title-published"]["value"])) + ' '
    else:
        emoji = ''

    return "{1}{2}".format(
        result["content"]["space"]["key"], 
        emoji, 
        result["content"]["title"])


def create_subtitle(result, args):
    return "Last Update: {1} by {2} | Space: {0}".format(
        result["content"]["space"]["name"], 
        result["friendlyLastModified"], 
        result["content"]["history"]["lastUpdated"]["by"]["displayName"])


def create_url(result, args):
    return get_base_url(args) + result["url"]


def get_icon_path(result, args):
    path = "./assets/content-type-page.png"

    if result["content"]["type"] == "blogpost":
        path = "./assets/content-type-blogpost.png"
    if result["content"]["type"] == "attachment":
        path = "./assets/content-type-attachment.png"

    return path

def get_mods(result, args):
    mod = {}

    if args.is_enterprise == True:
        if result["content"]["type"] == "blogpost" or result["content"]["type"] == "page":
            mod["cmd"] = {
                "valid": True,
                "arg": get_base_url(args) + "/pages/editpage.action?pageId=" + result["content"]["id"],
                "subtitle": "Open in editor"
            }
    else:
        if result["content"]["type"] == "blogpost" or result["content"]["type"] == "page":
            mod["cmd"] = {
                "valid": True,
                "arg": get_base_url(args) + result["content"]["_links"]["editui"],
                "subtitle": "Open in editor"
            }

    return mod


def convert_to_text_result(searchResults, args):
    textResult = ""

    if len(searchResults) < 1:
        textResult += "No search results found\n"
        textResult += "    Search Confluence for '" + args.text_as_string + "':\n"
        textResult += "    " + get_base_url(args) + "/search?text=" + urllib.parse.quote(args.text_as_string)

    for result in searchResults:
        textResult += "· " + create_title(result, args) + "\n"
        textResult += "    " + create_subtitle(result, args) + "\n"
        textResult += "    " + create_url(result, args)

    return textResult


try:
    args = parse_args()

    if args.text_as_string == 'gd':
        sys.stdout.write(json.dumps({
            "items": [{
                "title": "Open Confluence Dashboard",
                "subtitle": "Hit <enter> to open global dashboard",
                "arg": get_base_url(args) + '/home'
            }]
        }))
        sys.exit(0)

    elif args.text_as_string == 'c':
        sys.stdout.write(json.dumps({
            "items": [{
                "title": "Create Confluence Page",
                "subtitle": "Hit <enter> to open new draft in editor",
                "arg": get_base_url(args) + '/create-content/page?spaceKey=&parentPageId=&withFallback=true&source=createBlankFabricPage'
            }]
        }))
        sys.exit(0)

    else:
        search_results = search_confluence(args)
        create_output(search_results, args)

except Exception as e:
    sys.stdout.write(json.dumps({
        "items": [{
            "title": "Error in Confluence Quicksearch",
            "subtitle": "Details: " + str(e),
            "valid": False,
            "text": {
                "copy": str(e),
                "largetype": str(e)
            }
        }]
    }))
