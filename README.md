# 🚨 AWS Automated Incident Response Panic Button

A 100% serverless cloud security automation project built on AWS that transforms multi-step manual incident response into a single click. Pressing the **PANIC** button on the AWS-hosted web dashboard immediately triggers automated containment, state tracking, forensic evidence logging, and real-time email alerting in under two seconds.

---

## 🏗️ System Architecture

```text
[Emergency Panic Button Web Dashboard]
        (Hosted via AWS Lambda Function URL)
                       │
                       ▼  HTTPS POST Request
  ┌──────────────────────────────────────────────────────┐
  │    AWS Lambda: IncidentPlaybookRemediation (Python)   │
  └──────────────────────────────────────────────────────┘
       │               │               │               │
       ▼               ▼               ▼               ▼
  [Access Control] [DynamoDB]     [Amazon S3]     [Amazon SNS]
  WAF & Security   Logs Incident  Saves JSON      Sends Instant
  Group Lockdown   ID & Status    Forensic Log    Email Alert
  (Simulated)      LOCKDOWN_ACTIVE (forensics/)   [SECURITY ALERT]