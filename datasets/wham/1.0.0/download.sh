#!/bin/bash
wget -c https://my-bucket-a8b4b49c25c811ee9a7e8bba05fa24c7.s3.amazonaws.com/wham_noise.zip
unzip wham_noise.zip
mv wham_noise/* .
rm -rf wham_noise/
