#!/usr/local/bin/bash
snmpwalk -v 2c -c public $1 -Ovq $2
