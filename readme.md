# Sloth

TLDR: **Unless you are brave, don't use this project.**

Sloth is a content management system that serves my two needs:

1. Replace WordPress
    
    WordPress is an awesome piece of software that is good for a lot of users. That's a problem as I wanted to publish posts for which WordPress was not built.

2. Clear my bucket list of technical problems.
    
    This was a success.

## Project structure

There are actively developed parts, for learning parts and parts in limbo.

Actively developed parts:

- **CMSService** is the  main service that powers the blog (Python/Flask)
- **webapp** is a Next.js app that should serve as the new UI, currently in development
  - **webappMockBackend** is a backend for webapp for Cypress (Python/FastAPI)
