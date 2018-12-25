# Random Number Bot
Random number bot for reddit that uses random.org, modified to run on AWS Lambda.

The goal of moving this to AWS Lambda was to create a reddit bot that could run for free. This is first foray into AWS Lambda, so if there is anything you see that I could improve on I am 100% open to suggestions. 

## Buliding the Function

The code runs on python 3.6, but will require non standard packages to work. I found this to be the largest difficulty in setting up the project. Details for creating your own deployment package for python can be found [here](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html)

TODO add info...

## Resources
- [PRAW DOCS](https://praw.readthedocs.io/en/latest/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/index.html)
- [RANDOM.ORG API](https://api.random.org/json-rpc/1/) 
