# Sloth

TLDR: **Unless you are brave, don't use this project.**

Sloth is a content management system that should serve my two needs:

1. Replace WordPress
    
    WordPress is an awesome piece of software that is good for a lot of users. That's a problem as I wanted to publish posts for which WordPress was not built.
2. Clear my bucket list of technical problems.
    
    This was a success.

## Installation notes

1. project needs protobuf

   To install it on Fedora use `sudo yum install protobuf`.

   For other systems follow [tonic's documentation](https://github.com/hyperium/tonic#getting-started)

## Config

There needs to be set an enviromental variable with path to the configuration file, see `sloth.toml`