import argparse
import json
import sys
import logging
from base64 import b64encode
from HTMLParser import HTMLParser
from lib.workflow import Workflow, ICON_INFO, web, PasswordNotFound
from os.path import expanduser
from urlparse import urlparse

log = logging

PROP_BASEURL = 'confluence_baseUrl'
PROP_USERNAME = 'confluence_username'
PROP_PASSWORD = 'confluence_password'

VERSION = '1.0.3'


def getConfluenceBaseUrl():
    if wf.settings.get(PROP_BASEURL):
        return wf.settings[PROP_BASEURL].strip('/')
    else:
        wf.add_item(title='No Confluence Base URL set.', 
            subtitle='Type confluence_baseurl <baseUrl> and hit enter.',
            valid=False
            )
        wf.send_feedback()
        return 0


def getConfluenceUsername():
    if wf.settings.get(PROP_USERNAME):
        return wf.settings[PROP_USERNAME]
    else:
        wf.add_item(
            title='No Confluence Username set. Please run confluence_username', 
            subtitle='Type confluence_username <username> and hit enter.',
            valid=False
            )
        wf.send_feedback()
        return 0


def getConfluencePassword():
    try:
        return wf.get_password(PROP_PASSWORD)
    except PasswordNotFound:
        wf.add_item(
            title='No Confluence Password set. Please run confluence_password',
            subtitle='Type confluence_password <password> and hit enter.',
            valid=False
            )
        wf.send_feedback()
        return 0


def checkConfig(config):
    log.info('~~ Checking config..')
    log.info('~~   baseUrl: ' + config['baseUrl'])
    log.info('~~   username: ' + config['username'])
    log.info('~~   password: ' + config['password'])

    r = web.get(config['baseUrl'] + '/rest/api/user/current', headers=dict(Authorization='Basic ' + b64encode(config['username'] + ':' + config['password'])))

    if not ((r.status_code == 200) and (r.json()['type'] == 'known')):
        log.info('~~   Status code: %d', r.status_code)
        log.info('~~   ... Failed.')
        wf.add_item(
            title='Authentication failed.',
            subtitle='CAPTCHA issues? Try to logout and login again in your browser.',
            valid=False
        )
        wf.send_feedback()
        return 0
    else:
        log.info('~~   ... Ok.')


def main(wf):
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseUrl', dest='baseUrl', nargs='?', default=None)
    parser.add_argument('--username', dest='username', nargs='?', default=None)
    parser.add_argument('--password', dest='password', nargs='?', default=None)
    parser.add_argument('query', nargs='?', default=None)
    args = parser.parse_args(wf.args)


    if args.baseUrl:
        wf.settings[PROP_BASEURL] = args.baseUrl
        return 0

    if args.username:
        wf.settings[PROP_USERNAME] = args.username
        return 0

    if args.password:
        wf.save_password(PROP_PASSWORD, args.password)
        return 0  

    try:
        # lookup config for system
        args = wf.args[0].split()
        config = findConfig(args)

        if config.get('isFallback') is None:
            query = ' '.join(args[1:])
        else:
            query = ' '.join(args)
    except:
        query = wf.args[0]
        config = dict(
            baseUrl=getConfluenceBaseUrl(),
            prefix='',
            username=getConfluenceUsername(),
            password=getConfluencePassword()
            )

    checkConfig(config)

    # query Confluence
    r = web.get(config['baseUrl'] + '/rest/quicknav/1/search',
                params=dict(query=query),
                headers=dict(Authorization='Basic ' + b64encode(config['username'] + ':' + config['password'])))

    # throw an error if request failed
    # Workflow will catch this and show it to the user
    r.raise_for_status()

    # Parse the JSON returned by pinboard and extract the posts
    result = r.json()
    contentGroups = result['contentNameMatches']

    # Loop through the returned posts and add an item for each to
    # the list of results for Alfred
    for contentGroup in contentGroups:
        for content in contentGroup:
            # filter results to only contain pages and blog posts (and search site link)
            if content['className'] in ['content-type-page', 'content-type-blogpost', 'search-for']:
                if (content.get('spaceName')):
                    subtitle = content['spaceName']
                else:
                    subtitle = 'Use full Confluence Search'
                    

                wf.add_item(title=htmlParser.unescape(content['name']), 
                    subtitle=config['prefix'] + subtitle,
                    arg=getBaseUrlWithoutPath(config['baseUrl']) + content['href'],
                    valid=True,
                    icon='assets/' + content['className'] + '.png')

    # Send the results to Alfred as XML
    wf.send_feedback()


def findConfig(args):
    homeDir = expanduser('~')
    with open(homeDir + '/.alfred-confluence.json') as configFile:    
        configs = json.load(configFile)

    
    if len(args) > 1:
        for config in configs:
            if args[0].lower() == config['key'].lower():
                return config
    
    # Fallback to first entry
    configs[0]['isFallback'] = True
    configs[0]['baseUrl'] = configs[0]['baseUrl'].strip('/')
    return configs[0]


def getBaseUrlWithoutPath(baseUrl):
    parsedBaseUrl = urlparse(baseUrl)
    baseUrlWithoutPath = parsedBaseUrl.scheme + '://' + parsedBaseUrl.netloc
    return baseUrlWithoutPath.strip('/')


if __name__ == u'__main__':
    wf = Workflow(update_settings={
        'github_slug': 'skleinei/alfred-confluence',
        'version': VERSION
        })
    htmlParser = HTMLParser()
    log = wf.logger

    if wf.update_available:
        # Add a notification to top of Script Filter results
        wf.add_item('New version of the Alfred Confluence workflow available',
                    'Hit enter to to install the update.',
                    autocomplete='workflow:update',
                    icon=ICON_INFO)

    sys.exit(wf.run(main))
