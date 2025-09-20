The main application instance is represented by the Django node. It uses the library Boto3 to communicate with the AWS SDK, and in turn integrate with AWS SES (Simple Email Service). Communication with the database is done directly.

```mermaid
architecture-beta
    group app(cloud)[Finance Tracker]

    group aws_ec2(server)[AWS EC2] in app
    service django(server)[Django] in aws_ec2
    service boto3(internet)[AWS SDK API Boto3] in aws_ec2

    service aws_ses(server)[AWS Simple Email Service] in app
    
    group aws_rds(database)[AWS Relational Database Service] in app
    service mariadb(database)[MariaDB] in aws_rds

    django:R -- L:boto3
    django:R -- L:mariadb
    boto3:R -- L:aws_ses
```
