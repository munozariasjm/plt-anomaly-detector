#!/bin/bash
mkdir ./Files/mnt22
mkdir ./Files/mnt21
mkdir ./Files/mnt17
sshfs -o reconnect -o password_stdin -oProxyCommand="ssh -W %h:%p jmunozar@cmsusr.cern.ch"   brildev1:/brildata/22/ ./Files/mnt22 <<< 'lXEx|xe03'
sshfs -o reconnect -o password_stdin -oProxyCommand="ssh -W %h:%p jmunozar@cmsusr.cern.ch"   brildev1:/brildata/21/ ./Files/mnt21 <<< 'lXEx|xe03'
sshfs -o reconnect -o password_stdin -oProxyCommand="ssh -W %h:%p jmunozar@cmsusr.cern.ch"   brildev1:/brildata/17/ ./Files/mnt17 <<< 'lXEx|xe03'