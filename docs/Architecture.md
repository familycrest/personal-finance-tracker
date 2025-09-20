The main application instance is represented by the Django node. It uses the library Boto3 to communicate with the AWS SDK, and in turn integrate with AWS SES (Simple Email Service) and AWS RDS (Relational Database Service).

```mermaid
architecture-beta
    group app(cloud)[Finance Tracker]

    group aws_eb(server)[AWS Elastic Beanstalk] in app
    service django(server)[Django] in aws_eb
    service boto3(internet)[AWS SDK API Boto3] in aws_eb

    service aws_ses(server)[AWS Simple Email Service] in app
    
    group aws_rds(database)[AWS Relational Database Service] in app
    service mariadb(database)[MariaDB] in aws_rds

    django:R -- L:boto3
    boto3:R -- L:aws_ses
    boto3:B -- T:mariadb
```
