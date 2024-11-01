#!/bin/bash
api_key=$(openssl rand -base64 32 | tr -d '/+=' | cut -c1-40)
echo "$api_key"
