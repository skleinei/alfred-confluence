import argparse
import json
import sys
import logging
from base64 import b64encode
import html
from lib.workflow import Workflow, ICON_INFO, web, PasswordNotFound
from os.path import expanduser
from urllib.parse import urlparse

log = logging

PROP_BASEURL = 'confluence_baseUrl'
PROP_USERNAME = 'confluence_username'
PROP_PASSWORD = 'confluence_password'

VERSION = '1.0.3'


def get_confluence_base_url():
    if wf.settings.get(PROP_BASEURL):
        return wf.settings[PROP_BASEURL].strip('/')
    else:
        wf.add_item(title='No Confluence Base URL set.',
                    subtitle='Type confluence_baseurl <baseUrl> and hit enter.',
                    valid=False
                    )
        wf.send_feedback()
        return 0


def get_confluence_username():
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


def get_confluence_password():
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


def check_config(config):
    log.info('~~ Checking config..')
    log.info('~~   baseUrl: ' + config['baseUrl'])
    log.info('~~   username: ' + config['username'])
    log.info('~~   password: ' + config['password'])

    r = web.get(config['baseUrl'] + '/rest/api/user/current',
                headers=dict(Authorization='Basic ' + str(b64encode(config['username'] + ':' + config['password']))))

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


def main(workflow):
    parser = argparse.ArgumentParser()
    parser.add_argument('--baseUrl', dest='baseUrl', nargs='?', default=None)
    parser.add_argument('--username', dest='username', nargs='?', default=None)
    parser.add_argument('--password', dest='password', nargs='?', default=None)
    parser.add_argument('query', nargs='?', default=None)
    args = parser.parse_args(workflow.args)

    if args.baseUrl:
        workflow.settings[PROP_BASEURL] = args.baseUrl
        return 0

    if args.username:
        workflow.settings[PROP_USERNAME] = args.username
        return 0

    if args.password:
        workflow.save_password(PROP_PASSWORD, args.password)
        return 0

    try:
        # lookup config for system
        args = workflow.args[0].split()
        config = find_config(args)

        if config.get('isFallback') is None:
            query = ' '.join(args[1:])
        else:
            query = ' '.join(args)
    except:
        query = workflow.args[0]
        config = dict(
            baseUrl=get_confluence_base_url(),
            prefix='',
            username=get_confluence_username(),
            password=get_confluence_password()
        )

    check_config(config)

    # query Confluence
    r = web.get(config['baseUrl'] + '/rest/quicknav/1/search',
                params=dict(query=query),
                headers=dict(Authorization='Basic ' + str(b64encode(config['username'] + ':' + config['password']))))

    # throw an error if request failed
    # Workflow will catch this and show it to the user
    r.raise_for_status()

    # Parse the JSON returned by pinboard and extract the posts
    result = r.json()
    content_groups = result['contentNameMatches']

    # Loop through the returned posts and add an item for each to
    # the list of results for Alfred
    for contentGroup in content_groups:
        for content in contentGroup:
            # filter results to only contain pages and blog posts (and search site link)
            if content['className'] in ['content-type-page', 'content-type-blogpost', 'search-for']:
                if content.get('spaceName'):
                    subtitle = content['spaceName']
                else:
                    subtitle = 'Use full Confluence Search'

                workflow.add_item(
                    title=html.unescape(content['name']),
                    subtitle=config['prefix'] + subtitle,
                    arg=get_base_url_without_path(config['baseUrl']) + content['href'],
                    valid=True,
                    icon='assets/' + content['className'] + '.png'
                )

    # Send the results to Alfred as XML
    workflow.send_feedback()


def find_config(args):
    home_dir = expanduser('~')
    with open(home_dir + '/.alfred-confluence.json') as configFile:
        configs = json.load(configFile)

    if len(args) > 1:
        for config in configs:
            if args[0].lower() == config['key'].lower():
                return config

    # Fallback to first entry
    configs[0]['isFallback'] = True
    configs[0]['baseUrl'] = configs[0]['baseUrl'].strip('/')
    return configs[0]


def get_base_url_without_path(base_url):
    parsed_base_url = urlparse(base_url)
    base_url_without_path = parsed_base_url.scheme + '://' + parsed_base_url.netloc
    return base_url_without_path.strip('/')


if __name__ == u'__main__':
    wf = Workflow(update_settings={
        'github_slug': 'skleinei/alfred-confluence',
        'version': VERSION
    })
    log = wf.logger

    if wf.update_available:
        # Add a notification to top of Script Filter results
        wf.add_item('New version of the Alfred Confluence workflow available',
                    'Hit enter to to install the update.',
                    autocomplete='workflow:update',
                    icon=ICON_INFO)

    sys.exit(wf.run(main))
