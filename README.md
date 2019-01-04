# Random Number Bot
Random number bot for reddit that uses random.org, modified to run on AWS Lambda.

The goal of moving this to AWS Lambda was to create a reddit bot that could run for free. This is first foray into AWS Lambda, so if there is anything you see that I could improve on I am 100% open to suggestions. 

## Building the Function

The code runs on python 3.6, but will require non standard packages to work. I found this to be the largest difficulty in setting up the project. Details for creating your own deployment package for python can be found [here](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html) You will need to create a package with random_number_bot.py as your source and the following packages:
- praw
- rdoclient_py3
  (I think these are the only two, need to verify)


Steps to build the function:
* Create a Function
  * Get to : Lambda -> Functions
  * Click  "Create Function"
  * Select "Author from scratch" 
  * Give your function a name 
  * Select Python 3.6 for your runtime
  * In Role, choose "Create new role from template(s)"
    * In Role name, enter a name for your role
    * Leave the Policy templates field blank
  * Select Create Function
* Configure the Function
  * Add the code to the function under "Function Code"
    * Code entry type should be "upload a zip"
    * Runtime should still be python 3.6
    * Handler should be "random_number_bot.call_the_bot" (fileName.functionName)
    * Upload the zip created above in create a package section
* Configure the rest
  * Under "Basic settings"
    * Memory can be left at the smallest amount (128MB)
    * Timeout is set to 40 seconds
      *Timeout can probably be tweaked, timeout is unfortinatly high because the random.org api has a high timeout
      * I have not done a complete analysis on what the timeout should be
  * Under "Environment variables"
    * Create the following environment variables for the python code:
    
| Variable | Value |
| --- | --- |
| username | The reddit bot accounts username |
| password | The reddit bot accounts password |
| client_id | The reddit bot accounts client_id from [Here](https://www.reddit.com/prefs/apps) |
| client_secret | The reddit bot accounts client_secret from [Here](https://www.reddit.com/prefs/apps) |
| random_org_api_key | [API key from random.org](https://api.random.org/json-rpc/1/) |
| dev_user | Your user account, for debug messages |

   * Set the trigger
      * Under Designer select "CloudWatch Events"
      * Under "Configure triggers" select "Create a new rule"
      * Give the rule a name, I used something like "X_minute_rate"
      * Give the rule a description, I used something like "Run once every X minutes"
      * Select "Schedule expression"
      * Give the rule a Schedule expression, I used something like "rate(X minutes)"
      * Make sure enable is checked and hit "Add"

## Cost of Running

A goal of this project was to keep server cost in the free tier. I used the [AWS Lambda Pricing Calculator](https://s3.amazonaws.com/lambda-tools/pricing-calculator.html] to estimate the cost / verify that I could stay within the free tier. 

At the time of making the guide the free tier is 1M requests per month or 400,000 GB-seconds of compute time per month. The free tier does not expire and "is available to both existing and new AWS customers indefinitely". I would veify this at [their pricing page](https://aws.amazon.com/lambda/pricing/)

Because we used the CloudWatch Event as our trigger the timer can be tweaked to increase performance or decrease runtime. 

Number of Executions (Enter the number of times your Lambda function will be called per month): 
  I set it to 44640 (31 days * 24 hours in a day * 60 minutes in a hour)
  
Allocated Memory (MB)(Enter the allocated memory for your function):
  I set this to 128 MB, this should just be the memory size from your basic settings


Estimated Execution Time (ms) (Enter how long you expect the average execution will take in milliseconds)
  I set this to the timeout x 1000 (40000)
  I did the timeout just to be safe, most of the time it will not execute for the timout amount of time  

Include Free Tier Yes

Hopefully this gives your $0.00 ! 

## Resources
- [PRAW DOCS](https://praw.readthedocs.io/en/latest/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/index.html)
- [Create a Lambda Function with the Console](https://docs.aws.amazon.com/lambda/latest/dg/getting-started-create-function.html)
- [Building Lambda Functions](https://docs.aws.amazon.com/lambda/latest/dg/lambda-app.html)
- [RANDOM.ORG API](https://api.random.org/json-rpc/1/) 
