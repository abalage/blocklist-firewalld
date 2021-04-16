# blocklist-firewalld
Create [ipset](https://ipset.netfilter.org/) lists from blocklists managed by [firewalld](https://firewalld.org/).

## Manual

```
usage: blocklist-firewalld.py [-h] [--create] [--flush] [--populate]

A script to load specified blocklist with firewalld using ipsets.

optional arguments:
  -h, --help  show this help message and exit
  --create    Create ipsets
  --flush     Flush existing ipsets
  --populate  Import list of IPs from files
```

## Configuration

Create a JSON file called blocklist.json in one of the following locations:
 - /etc/blocklist/blocklist.json
 - $HOME/blocklist.json
 - "Right next to the script"

Its format is pretty simple. Key is the URL of the list, the value is the name of the ipset it creates.

```json
    "https://lists.blocklist.de/lists/ssh.txt" : "blocklist-ssh",
    "https://lists.blocklist.de/lists/80.txt" : "blocklist-80",
    "https://lists.blocklist.de/lists/443.txt" : "blocklist-443"
```

You can find further readily available blocklists on the following sites.
 - https://lists.blocklist.de
 - https://www.ipdeny.com/ipblocks/

## Usage

Run the script as a cronjob. The following example runs the script at 3AM every day.

```
0 3 * * * python3 /root/bin/blocklist-firewalld.py
```
