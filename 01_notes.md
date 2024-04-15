#### Part 1: AWS S3 & Sourcing Datasets
1. Republish [this open dataset](https://download.bls.gov/pub/time.series/pr/) in Amazon S3 and share with us a link.

    [rearc-quest-bucket-roman](https://us-east-1.console.aws.amazon.com/s3/buckets/rearc-quest-bucket-roman)

    [/analyse_data.ipynb](/analyse_data.ipynb) - cmd 3, [/lambda_function.py](/lambda_function.py) - line 41

2. Script this process so the files in the S3 bucket are kept in sync with the source when data on the website is updated, added, or deleted.
    - Don't rely on hard coded names - the script should be able to handle added or removed files.
    - Ensure the script doesn't upload the same file more than once.
    [/analyse_data.ipynb](/analyse_data.ipynb) - cmd 5, [/lambda_function.py](/lambda_function.py) - line 43

#### Part 2: APIs
2. Save the result of this API call as a JSON file in S3.
    (https://rearc-quest-bucket-roman.s3.amazonaws.com/api_response.json)

    [/analyse_data.ipynb](/analyse_data.ipynb) - cmd 4, [/lambda_function.py](/lambda_function.py) - line 42

#### Part 3: Data Analytics
0. Load both the csv file from **Part 1** `pr.data.0.Current` and the json file from **Part 2**
   as dataframes ([Spark](https://spark.apache.org/docs/1.6.1/api/java/org/apache/spark/sql/DataFrame.html),
                  [Pyspark](https://spark.apache.org/docs/latest/api/python/reference/api/pyspark.sql.DataFrame.html),
                  [Pandas](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html),
                  [Koalas](https://koalas.readthedocs.io/en/latest/),
                  etc).

    [/analyse_data.ipynb](/analyse_data.ipynb) - cmd 6 and cmd 7, [/lambda_function.py](/lambda_function.py) - lines 45-59
    
1. Using the dataframe from the population data API (Part 2),
   generate the mean and the standard deviation of the annual US population across the years [2013, 2018] inclusive.

   [/analyse_data.ipynb](/analyse_data.ipynb) - cmd 8, [/lambda_function.py](/lambda_function.py) - lines 61-71

2. Using the dataframe from the time-series (Part 1),
   For every series_id, find the *best year*: the year with the max/largest sum of "value" for all quarters in that year. Generate a report with each series id, the best year for that series, and the summed value for that year.
   For example, if the table had the following values:

   [/analyse_data.ipynb](/analyse_data.ipynb) - cmd 9, [/lambda_function.py](/lambda_function.py) - lines 73-85


3. Using both dataframes from Part 1 and Part 2, generate a report that will provide the `value`
   for `series_id = PRS30006032` and `period = Q01` and the `population` for that given year (if available in the population dataset)

   [/analyse_data.ipynb](/analyse_data.ipynb) - cmd 10, [/lambda_function.py](/lambda_function.py) - lines 87-106

4. Submit your analysis, your queries, and the outcome of the reports as a [.ipynb](https://fileinfo.com/extension/ipynb) file.
    [/analyse_data.ipynb](/analyse_data.ipynb)

#### Part 4: Infrastructure as Code & Data Pipeline with AWS CDK
0. Using [AWS CloudFormation](https://aws.amazon.com/cloudformation/), [AWS CDK](https://aws.amazon.com/cdk/) or [Terraform](https://www.terraform.io/), create a data pipeline that will automate the steps above.
1. The deployment should include a Lambda function that executes
   Part 1 and Part 2 (you can combine both in 1 lambda function).
   
    1.1. The lambda function is based on docker image, described in Dockerfile and pushed to AWS ECR by [push_image.sh](/push_image.sh)
    1.2. [aws-lambda.yaml](/cloud_formation/aws-lambda.yaml) is a CloudFormation template used to deploy the services. 
         The lambda function LambdaFunction will be scheduled to run daily EventsRule.

2. The deployment should include an SQS queue that will be populated every time the JSON file is written to S3. (Hint: [S3 - Notifications](https://docs.aws.amazon.com/AmazonS3/latest/userguide/NotificationHowTo.html))
    2.1. [aws-lambda.yaml](/cloud_formation/aws-lambda.yaml) -> SQSQueue & S3Bucket.NotificationConfiguration
3. For every message on the queue - execute a Lambda function that outputs the reports from Part 3 (just logging the results of the queries would be enough. No .ipynb is required).
    3.1. [aws-lambda.yaml](/cloud_formation/aws-lambda.yaml) - > LambdaEventSourceMapping