#!/bin/bash
INSTALL_PATH=~/.mozilla/native-messaging-hosts/
BASE_DIR=$(dirname "$0")

if test -f $INSTALL_PATH/mkb_driver.json; then
	rm $INSTALL_PATH/mkb_driver.json
	echo "Native app manifest uninstalled from $INSTALL_PATH"
fi

if test -d $BASE_DIR/__pycache__; then 
	rm -rf $BASE_DIR/__pycache__
	echo "pycache removed"
fi
if test -d $BASE_DIR/venv; then
	rm -rf $BASE_DIR/venv
	echo "venv removed"
fi

echo "uninstall complete."
