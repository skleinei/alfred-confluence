![Alfred Confluence Workflow](https://github.com/skleinei/alfred-confluence/raw/master/assets/banner.png)


# Alfred Confluence Workflow

The Alfred Confluence workflow makes the Confluence Quick search available in the Alfred App.
  
Just hit `⌘ Space` and type `c Employee Records` to search for Confluence page. 


## Getting Started

1. Download Alfred Confluence from the Github releases page.
2. Double click to install Alfred Confluence in Alfred.
3. Configure Alfred Confluence with the following commands
   * `confluence_baseurl` - set the Confluence Base URL, e.g. 
     https://www.example.com/wiki or https://wiki.example.com
   * `confluence_username` - set your Confluence usename
   * `confluence_password` - set your Confluence password (it will be stored 
     securely in your MacOS keychain)
4. Use the `c` command to search your Confluence system. `c my search term`



## Advanced Configuration

If you work with multiple Confluence systems, Alfred Confluence supports this 
with config file.

In order to search multiple Confluence systems:

1. Create the file `~/.alfred-confluence.json` that contains a list of
   configuration for each system to be searchable. The first system will be
   treated as the _default_ system. 
   
   Example:
   
   ```[
     {
       "key": "wkc",
       "prefix": "[wkc] ",
       "baseUrl" : "https://www.k15t.com",
       "username" : "your-username",
       "password" : "your-unencrypted-password"
     },
     {
       "key": "cl",
       "prefix": "[Cloud] ",
       "baseUrl" : "https://k15t.jira.com/wiki",
       "username" : "your-username",
       "password" : "your-unencrypted-password"
     }
   ]
   ```
2. Use the following commands to search in the default
   * `c <search-query>` – search in the default system for pages `<search-query>`
   * `c <key> <search-query>` – search in the system with `<key>` for pages `<search-query>`

Please be aware that this will store you password in clear text on your file system.


# Development

## Building

To build Alfred Confluence just make:

```
$ make all
```

## Releasing

In order to release a new version:

1. Bump the version numbers (semantic version numbering!) in both files:
   * `Info.plist` (at the very end of the file)
   * `alfred-confluence.py` (line ~15)
2. Commit all changes.
3. Create a release on [Github](https://help.github.com/categories/releases/)
   and use the same version number.


# Credits

The Alfred Confluence workflow was build by Stefan Kleineikenscheidt 
([@skleinei](https://twitter.com/skleinei)). 

It was created in Python with the help of 
[Dean Jackson's](https://github.com/deanishe/alfred-workflow) Alfred library. 