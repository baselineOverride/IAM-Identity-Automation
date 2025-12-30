# IAM Identity Automation - Joiner/Mover/Leaver Pipeline (AWS)

## Overview 

The automation follows a straightforward event-driven pattern: 

CSV File upload -> S3 Bucket -> Lambda -> IAM Operations -> CloudTrail -> CloudWatch Logs -> Metric Filters -> Alarms -> SNS Email

## Key Capabilities

- Automated user provisioning based on CSV input.
- Group assignment and reassignment for role changes.
- Automated deprovisioning including group reassignment and user deletion.
- Full audit trial through CloudTrail log streaming.
- Operational monitoring with CloudWatch metric filters.
- Email alerts for sensitive identity events via SNS.

## Architecture Components

**Amazon S3** - Stores CSV file and triggers the workflow 
**AWS Lambda (Python)** - Parses input and performs IAM operations
**AWS IAM** - Users, groups, and permissions
**AWS CloudTrial** - Captures all IAM API activity 
**CloudWatch Logs** - Stores structured CloudTrial events
**Metric Filters** - Detect specific identity-related actions 
**CloudWatch Alarms** - Notify when monitored events occur
**SNS** - Sends email alerts 

## CSV Format 

```csv
username,position,mode
daniel,dev,add
sarah,security,add
samuel,readonly,add
sarah,readonly,move
samuel,security,remove
daniel,security,move
```
- **username** is name of the user
- **position** maps to IAM groups
- **mode** determines the lifecycle action/operation 

## 1. S3 Trigger Setup

![S3 Trigger Setup](imgs/)
