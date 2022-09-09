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


def parseArgs():
    parser = argparse.ArgumentParser()
    parser.add_argument("text", metavar='text', nargs='+')
    parser.add_argument("--url", help="Specify the url. E.g. https://k15t.atlassian.net/ or https://k15t.jira.com/ (for really old cloud instances)")
    parser.add_argument("--user", help="Specify the user's email")
    parser.add_argument("--token", help="Specify the authentication token (generate one here: https://id.atlassian.com/manage/api-tokens)")
    parser.add_argument("-o", "--output", default='cli', help="Specify output mode [alfred|cli].")
    parser.add_argument("-s", "--space", nargs="?", default=None, const=None, help="Specify the space key")
    parser.add_argument("-l", "--limit", default=10, help="Specify the max number of results")
    parser.add_argument("-t", "--type", default="page,blogpost", help="Type of content to search for [page,blogpost,attachment] (default: page,blogpost)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Switch on logging")
    
    args = parser.parse_args()
    
    args.textAsString = " ".join(args.text)

    args.url = getAndValidateUrl(args)
    args.user = getAndValidateUser(args)
    args.token = getAndValidateToken(args)

    args.pathPrefix = ""
    args.isDatacenter = True
    if re.search("atlassian.net", args.url) or re.search("jira.com", args.url):
        args.isDatacenter = False
        args.pathPrefix = "/wiki"
    
    return args


def getAndValidateUrl(args):
    url = os.getenv("CA_URL", args.url)
    log(url, args)

    if url == None or len(url) <= 0:
        raise Exception("URL not specified.")

    return url


def getAndValidateUser(args):
    user = os.getenv("CA_USER", args.user)
    log(user, args)

    if user == None or len(user) <= 0:
        raise Exception("User not specified.")

    return user


def getAndValidateToken(args):
    token = os.getenv("CA_TOKEN", args.token)
    log(token, args)

    if token == None or len(token) <= 0:
        raise Exception("Token not specified.")

    return token


def searchConfluence(args):
    response = requests.request(
        "GET",
        args.url + args.pathPrefix + '/rest/api/search',
        headers = {
            "Accept": "application/json",
            "Authorization": createAuth(args)
        },
        params = createSearchQuery(args)
    )

    if response.status_code != 200:
        raise Exception('Response {} ({})'.format(response.status_code, response.text))

    log(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")), args)
    
    return json.loads(response.text)["results"]


def createAuth(args):
    message = args.user + ':' + args.token
    message_bytes = message.encode('utf-8')
    base64_bytes = base64.b64encode(message_bytes)
    authHeader = 'Basic ' + base64_bytes.decode('utf-8')
    log(authHeader, args)
    return authHeader


def createSearchQuery(args):
    log("space: {}".format(args.space), args)
    log("text: {}".format(args.text), args)

    cql = "title ~ \"" + args.textAsString + "\""

    if args.space:
        cql += " AND space = \"" + args.space + "\""

    cql += " AND type IN (" + args.type + ")"

    log('cql: ' + cql, args)

    return {
        'cql': cql,
        'limit': args.limit,
        'expand': 'content.space,content.metadata.properties.emoji_title_published,content.history.lastUpdated'
    }


def createOutput(searchResults, args):
    if args.output == 'alfred':
        alfredItems = convertToAlfredItems(searchResults, args)
        sys.stdout.write(json.dumps({
            "items": alfredItems
        }))
    else:
        textResult = convertToTextResult(searchResults, args)
        sys.stdout.write(textResult)


def convertToAlfredItems(searchResults, args):
    alfredItems = []

    if len(searchResults) < 1:
        alfredItems.append({
            "title": "No search results",
            "subtitle": "Hit <enter> to do a full-text search for '" + args.textAsString + "' in Confluence",
            "arg": args.url + args.pathPrefix + "/search?text=" + urllib.parse.quote(args.textAsString),
            "icon": {
                "path": "./assets/search-for.png"
            },
        })

    for result in searchResults:
        # docs: https://www.alfredapp.com/help/workflows/inputs/script-filter/json/ 
        result = {
            "title": createTitle(result, args),
            "subtitle": createSubtitle(result, args),
            "arg": createUrl(result, args),
            "icon": {
                "path": getIconPath(result, args)
            },
            "mods": getMods(result, args),
            "text": {
                "copy": createUrl(result, args),
                "largetype": createUrl(result, args)
            }
        }
        
        alfredItems.append(result)

    return alfredItems


def createTitle(result, args):
    if "emoji-title-published" in result["content"]["metadata"]["properties"]:
        emoji = chr(ast.literal_eval('0x'+ result["content"]["metadata"]["properties"]["emoji-title-published"]["value"])) + ' '
    else:
        emoji = ''

    return "{1}{2}".format(
        result["content"]["space"]["key"], 
        emoji, 
        result["content"]["title"])


def createSubtitle(result, args):
    return "Last Update: {1} by {2} | Space: {0}".format(
        result["content"]["space"]["name"], 
        result["friendlyLastModified"], 
        result["content"]["history"]["lastUpdated"]["by"]["displayName"])


def createUrl(result, args):
    return args.url + args.pathPrefix + result["url"]


def getIconPath(result, args):
    path = "./assets/content-type-page.png"

    if result["content"]["type"] == "blogpost":
        path = "./assets/content-type-blogpost.png"

    return path

def getMods(result, args):
    mod = {}

    if args.isDatacenter == True:
        if result["content"]["type"] == "blogpost" or result["content"]["type"] == "page":
            mod["cmd"] = {
                "valid": True,
                "arg": args.url + args.pathPrefix + "/pages/editpage.action?pageId=" + result["content"]["id"],
                "subtitle": "Open in editor"
            }
    else:
        if result["content"]["type"] == "blogpost" or result["content"]["type"] == "page":
            mod["cmd"] = {
                "valid": True,
                "arg": args.url + args.pathPrefix + result["content"]["_links"]["editui"],
                "subtitle": "Open in editor"
            }

    return mod


def convertToTextResult(searchResults, args):
    textResult = ""

    if len(searchResults) < 1:
        textResult += "No search results found\n"
        textResult += "    Search Confluence for '" + args.textAsString + "':\n"
        textResult += "    " + args.url + args.pathPrefix + "/search?text=" + urllib.parse.quote(args.textAsString)

    for result in searchResults:
        textResult += "· " + createTitle(result, args) + "\n"
        textResult += "    " + createSubtitle(result, args) + "\n"
        textResult += "    " + createUrl(result, args)

    return textResult


try:
    args = parseArgs()
    searchResults = searchConfluence(args)
    createOutput(searchResults, args)

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
