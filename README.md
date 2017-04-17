# Alfred Confluence Workflow




## Getting Started

1. Download Alfred Confluence from the Github releases page.
2. Install Alfred Confluence in Alfred.
3. Configure Alfred Confluence with the following commands
3. cqs_baseurl - set the Confluence Base Url
3. cqs_username - set your Confluence usename
3. cqs_password - set your Confluence password (it will be stored securely in the MacOS keychain)
4. Then use the following command to search your Confluence system: {{c my search tem}}



# Advanced Configuration

If you work with multiple Confluence systems, you have to create the file {{~/.alfred-confluence.json}} that looks like the following:

''''
[
	{
	    "key": "wkc",
	    "name": "www.k15t.com",
		"baseUrl" : "https://www.k15t.com",
		"username" : "stefan",
		"password" : "your-unencrypted-password"
	},
	{
		"key": "cl",
		"name": "Cloud",
		"baseUrl" : "https://k15t.jira.com/wiki",
		"username" : "stefan",
		"password" : "your-unencrypted-password"
	}
]
''''

Please be aware that this will store you password in clear text on your file system.


# Release History

## 1.0.0

Initial release.
