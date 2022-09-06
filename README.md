![Confluence Quicksearch for Alfred](https://github.com/skleinei/alfred-confluence/raw/main/src/assets/banner.png)


# Confluence Quicksearch for Alfred

*Confluence Quicksearch for Alfred* allows you to search, open, and edit Confluence content from 
Alfred. Just hit type `c <search term>` to search for Confluence.


## Getting Started

In order to get started:

1. Download the latest version of *Confluence Quicksearch for Alfred* from the 
   [Github releases page](https://github.com/skleinei/alfred-confluence/releases).
2. Double click the downloaded file to install the workflow in Alfred.
3. In the workflow configuration:
   * **Atlassian URL** - enter the Confluence Base URL, e.g. https://amce.atlassian.net (if you 
     have a really old Atlassian URL it could also be something like https://amce.jira.com)
   * **Email** - enter the email adress of your Atlassian ID account
   * **Token** - enter an API token for Confluence. (Generate it here: 
     https://id.atlassian.com/manage/api-tokens)

To search for Confluence content, open Alfred with `⌘Space` and enter `c <search term>`.



## Advanced Topics

### Searching multiple Confluence systems

If you work with multiple Confluence systems and want to search content, *Confluence Quicksearch 
for Alfred* supports in a straight forward way, bu duplicating the workflow in Alfred.

To search in a second Confluence instance:
1. Right-click the Confluence Quicksearch workflow and **Duplicate**.
1. Click **Configure Workflow** and change the URL in the configuration.

Please note that you have to re-do this, everytime when you install a new version of *Confluence 
Quicksearch for Alfred*, because only the orginial version will be upgraded.


## Troubleshooting

In general, make sure to look at the output of *Confluence Quicksearch for Alfred*. When there is an error it will report `Error in Confluence Quicksearch` along with some details. Try to match that output with the errors mentioned below.

If that doesn't help hit `⌘C` to copy the error message in the clipboard and post a question in the [Discussion Forum](https://www.alfredforum.com/topic/10234-atlassian-confluence-quick-search/).

### Common Errors

<details><summary>HTTPSConnectionPool(host='...</summary>

````
HTTPSConnectionPool(host='amce.atlassian.com', port=443): Max retries exceeded with url: /wiki/rest/api/search?cql=title+~+%22c%22+AND+type+IN+%28page%2Cblogpost%29&limit=10&expand=content.space%2Ccontent.metadata.properties.emoji_title_published%2Ccontent.history.lastUpdated (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x10199e6a0>: Failed to establish a new connection: [Errno 8] nodename nor servname provided, or not known'))
````

If you get an error like that, make sure you have configured the correct URL.

**Tipps:**
- Make sure it is ending with `atlassian.net` (and not `atlassian.com`) or `jira.com`
- Make sure to **not** include `/wiki` at the end of the URL
</details>

<details><summary>Response 404 (...</summary>

````
Response 404 ({"errorMessage": "Site temporarily unavailable"})
````
If you get an error like that, make sure you have configured the correct URL.

**Tipps:**
- Make sure it is ending with `atlassian.net` (and not `atlassian.com`) or `jira.com`
- Make sure to **not** include `/wiki` at the end of the URL
</details>

<details><summary>Response 401 ({"message":"Request rejected because issuer is either not authorized...</summary>

````
Response 401 ({"message":"Request rejected because issuer is either not authorized or not authorized to impersonate","status-code":401})
````

If you get an error like that, make sure you have configured the correct Atlassian API token.
</details>


<details><summary>Response 401 (Basic authentication with passwords is deprecated...</summary>

````
Response 401 (Basic authentication with passwords is deprecated.  For more information, see: https://developer.atlassian.com/cloud/confluence/deprecation-notice-basic-auth/
````

If you get an error like that, make sure you have configured the correct email.
</details>


### Other issues and questions

Please raise any feedback issues and questions here: 
https://www.alfredforum.com/topic/10234-atlassian-confluence-quick-search/


## Releases

### 2.0.0

New major version that now works with macOS 12.3 (Monterey) and up.

**🚨 Breaking Changes:**
* Removed support for Confluence Server/DataCenter
* Bumped requirement to Alfred 5, because it is using the new workflow configuration UI.

**Notable Improvements:**
* Filter by spaces, example: `c search term -s SPACEKEY` (default: search all spaces)
* Filter by content types, example: `c search term -t attachment` (default: page,blogpost)
* Increase results limit, example: `c search term -l 50` (default: 10)
* Use ⌘ as modifier key to directly open page in editor

### 1.0.3

* Fixed issue with authentication Confluence Cloud instances. Authentication
  require tokens now (see above).
* Improved error handling for authentication issues.
* Fixed issue with Confluence on custom ports. Thanks to @wooyeong and @Frogli.
* Trailing slashes in the confluence_baseUrl should no longer be an issue.


## Development

### Building

To build *Confluence Quicksearch for Alfred* just make:

```
$ make all
```

### Releasing

In order to release a new version:

1. Bump the version numbers (semantic version numbering!) in these files:
   * `src/Info.plist` (2 times: at the very end of the file AND line ~110 (for the workflow name))
   * `src/alfred-confluence.py` (line ~15)
2. Commit all changes.
3. Create a release on [Github](https://help.github.com/categories/releases/)
   and use the same version number.


## Credits

The *Confluence Quicksearch for Alfred* workflow was build by Stefan Kleineikenscheidt 
([@skleinei](https://twitter.com/skleinei)). 

Its first version was created in Python with the help of Dean Jackson's
[Alfred library](https://github.com/deanishe/alfred-workflow). 