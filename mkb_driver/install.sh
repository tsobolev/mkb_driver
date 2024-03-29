#!/bin/bash
INSTALL_PATH=~/.mozilla/native-messaging-hosts/

if [ -d venv ]; then
  echo "venv"
  venv/bin/python -m pip install -r requirements.txt
else
  echo "novenv"
  python -m venv venv
  venv/bin/python -m pip install -r requirements.txt
fi

mkdir -p $INSTALL_PATH
cp ./mkb_driver.json $INSTALL_PATH
sed -i "s|PATH_TO_MKB_DRIVER|$PWD|" $INSTALL_PATH/mkb_driver.json
cat $INSTALL_PATH/mkb_driver.json
echo "Native app manifest installed to $INSTALL_PATH"
