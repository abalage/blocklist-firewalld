#!/usr/bin/env python3

from subprocess import Popen, PIPE
import sys
import argparse
import os
import json

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="A script to load specified blocklist with firewalld using ipsets.")

    parser.add_argument("--create",
                        help="Create ipsets", action="store_true")
    parser.add_argument("--flush",
                        help="Flush existing ipsets", action="store_true")
    parser.add_argument("--populate",
                        help="Import list of IPs from files", action="store_true")

    args = parser.parse_args()

    # json parsing
    JSONFILE = 'blocklist.json'
    DOTFILE = '.'+ JSONFILE
    HOME = os.path.expandvars("$HOME")
    ETC = "/etc/blocklist"
    SCRIPT_LOC = os.path.dirname(os.path.abspath(__file__))
    for location in HOME, ETC, SCRIPT_LOC:
        CONFIGFILE = os.path.join(location, JSONFILE)
        if os.path.exists(CONFIGFILE): break
        if location == HOME:
            CONFIGFILE = os.path.join(location, DOTFILE)
            if os.path.exists(CONFIGFILE): break

    with open(CONFIGFILE) as config_file:
        lists = json.load(config_file)
    # end of json parsing

    def runcmd(text, cmd, echo):
        if echo in ['Y', 'Yes', 'yes']:
            print(text)
        stdout = []
        with Popen([cmd],
                   shell=True,
                   stdout=PIPE,
                   bufsize=1,
                   universal_newlines=True
                   ) as process:

            for line in process.stdout:
                if echo in ['Y', 'Yes', 'yes']:
                    print(line, end='')

                line = line.rstrip()
                stdout.append(line)

        return stdout

    def create_ipset():
        for list in lists:
            rc = runcmd("Checking : " + lists[list],
                'firewall-cmd --info-ipset '+lists[list], "no")
            if rc[0] =! '0':
                runcmd("Creating ipset for " + lists[list], "firewall-cmd --permanent --new-ipset=" + lists[list] + " --type=hash:net --option=family=inet --option=hashsize=4096 --option=maxelem=200000", "no")
                runcmd("Setting policy to drop ", "firewall-cmd --permanent --zone=drop --add-source=ipset:"+lists[list], "no")

        runcmd("Reload firewalld for changes to take effect ", "firewall-cmd --reload", "no")

    # https://blog.fpmurphy.com/2018/10/using-the-d-bus-interface-to-firewalld.html
    # https://stackoverflow.com/questions/34402914/control-firewalld-in-centos-via-pythons-dbus-module
    # https://firewalld.org/documentation/man-pages/firewalld.dbus.html
    def flush_ipset():
        for list in lists:
            runcmd("Flushing ipset" + lists[list], "/usr/sbin/ipset flush " + lists[list], "no")

    def populate_ipset():
        import pycurl
        import tempfile
        from pathlib import Path

        for list in lists:
            with tempfile.TemporaryDirectory() as tmpdirname:
                tmpdir = Path(tmpdirname)
                tmpfile = tmpdir / lists[list]
                # Tried pycurl but it always truncated the output.
                runcmd("Downloading "+lists[list],"curl -s -L -o "+str(tmpfile)+" "+list,"no")
                runcmd("Remove IPv6 addresses from: "+str(tmpfile), "sed -i '/\:/d' "+str(tmpfile), "no")
                runcmd("Populating ipset: " + lists[list], "firewall-cmd --ipset=" + lists[list] + " --add-entries-from-file=" + str(tmpfile), "no")

    if (args.flush):
        flush_ipset()
    elif (args.populate):
        populate_ipset()
    elif (args.create):
        create_ipset()
    else:
        create_ipset()
        flush_ipset()
        populate_ipset()

sys.exit(0)
