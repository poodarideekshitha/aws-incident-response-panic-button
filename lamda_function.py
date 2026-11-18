import json
import os
import boto3
from datetime import datetime

s3 = boto3.client('s3')
sns = boto3.client('sns')
dynamodb = boto3.resource('dynamodb')

BUCKET_NAME = os.environ.get('BUCKET_NAME', 'your-forensics-bucket-name')
SNS_TOPIC_ARN = os.environ.get('SNS_TOPIC_ARN', 'arn:aws:sns:us-east-1:123456789012:IncidentAlert')
TABLE_NAME = os.environ.get('TABLE_NAME', 'IncidentStatusTable')

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Emergency Panic Button - AWS Incident Response</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
    body { background-color: #050505; color: #ffffff; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
    .dashboard-card { background-color: #080808; border: 2px solid #d9383a; border-radius: 28px; width: 100%; max-width: 480px; padding: 40px 32px; text-align: center; box-shadow: 0 0 35px rgba(217, 56, 58, 0.25); }
    .header-title { color: #ef4444; font-size: 28px; font-weight: 800; line-height: 1.25; margin-bottom: 24px; }
    .sub-heading { color: #ffffff; font-size: 24px; font-weight: 700; line-height: 1.3; margin-bottom: 18px; }
    .description { color: #b0b0b0; font-size: 16px; margin-bottom: 36px; }
    .panic-wrapper { display: flex; justify-content: center; margin-bottom: 36px; }
    .panic-btn { width: 170px; height: 170px; border-radius: 50%; background: radial-gradient(circle at 35% 35%, #ef2326, #b91c1c); border: 4px solid #7f1d1d; color: #ffffff; cursor: pointer; display: flex; flex-direction: column; justify-content: center; align-items: center; gap: 10px; box-shadow: 0 10px 30px rgba(220, 38, 38, 0.55); transition: transform 0.15s ease, box-shadow 0.15s ease; }
    .panic-btn:hover { transform: scale(1.04); box-shadow: 0 12px 40px rgba(239, 68, 68, 0.8); }
    .panic-btn:active { transform: scale(0.96); }
    .panic-btn:disabled { opacity: 0.6; cursor: not-allowed; }
    .panic-text { font-size: 22px; font-weight: 800; letter-spacing: 1px; }
    .status-box { background-color: #121212; border: 1px solid #2a2a2a; border-radius: 12px; padding: 14px; font-size: 14px; color: #d4d4d4; margin-bottom: 20px; display: none; word-break: break-word; line-height: 1.5; }
    .footer-note { color: #a3a3a3; font-size: 14px; }
  </style>
</head>
<body>
  <div class="dashboard-card">
    <div class="header-title">🚨 EMERGENCY PANIC<br>BUTTON</div>
    <div class="sub-heading">ACTIVATE INCIDENT<br>RESPONSE</div>
    <p class="description">AWS Cloud-Hosted Incident Response Dashboard</p>
    <div class="panic-wrapper">
      <button id="panicBtn" class="panic-btn" onclick="triggerIncident()">
        <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <polygon points="7.86 2 16.14 2 22 7.86 22 16.14 16.14 22 7.86 22 2 16.14 2 7.86 7.86 2"></polygon>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <span class="panic-text">PANIC</span>
      </button>
    </div>
    <div id="statusBox" class="status-box"></div>
    <div class="footer-note">Hosted on AWS Lambda &bull; Connected to DynamoDB, S3 &amp; SNS</div>
  </div>
  <script>
    async function triggerIncident() {
      const btn = document.getElementById("panicBtn");
      const statusBox = document.getElementById("statusBox");
      btn.disabled = true;
      statusBox.style.display = "block";
      statusBox.style.borderColor = "#eab308";
      statusBox.innerHTML = "⏳ Executing AWS Incident Response Playbook...";
      try {
        const res = await fetch(window.location.href, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            source: "aws.hosted.dashboard",
            detail: { eventName: "EmergencyPanicButtonActivated", sourceIPAddress: "AWS-Console-Admin" }
          })
        });
        const data = await res.json();
        statusBox.style.borderColor = "#22c55e";
        statusBox.innerHTML = `✅ <strong>INCIDENT PLAYBOOK EXECUTED!</strong><br>ID: ${data.incident_id}<br>DynamoDB: ${data.status}<br>Access Control: Active<br>S3 Evidence &amp; SNS Alert Dispatched.`;
      } catch (err) {
        statusBox.style.borderColor = "#ef4444";
        statusBox.innerHTML = "❌ Error triggering playbook: " + err.message;
      } finally {
        btn.disabled = false;
      }
    }
  </script>
</body>
</html>"""

def lambda_handler(event, context):
    http_method = event.get('requestContext', {}).get('http', {}).get('method', 'POST')

    if http_method == 'GET':
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': DASHBOARD_HTML
        }

    if 'body' in event and isinstance(event['body'], str):
        try:
            body_data = json.loads(event['body'])
        except Exception:
            body_data = event
    else:
        body_data = event

    timestamp = datetime.utcnow().strftime('%Y-%m-%d_%H-%M-%S')
    incident_id = f"INC-{timestamp}"
    detail = body_data.get('detail', {})
    event_name = detail.get('eventName', 'EmergencyPanicButtonActivated')
    source_ip = detail.get('sourceIPAddress', 'AWS-Hosted-Dashboard')
    user_arn = detail.get('userIdentity', {}).get('arn', 'SOC-Administrator')

    access_control_action = "WAF & Security Group Lockdown Activated (Simulated)"

    table = dynamodb.Table(TABLE_NAME)
    table.put_item(
        Item={
            'incident_id': incident_id,
            'timestamp': timestamp,
            'status': 'LOCKDOWN_ACTIVE',
            'trigger_event': event_name,
            'access_control': access_control_action,
            'initiated_by': user_arn
        }
    )

    forensic_key = f"forensics/incident_{timestamp}.json"
    forensic_report = {
        "incident_id": incident_id,
        "timestamp_utc": timestamp,
        "status": "LOCKDOWN_ACTIVE",
        "access_control_action": access_control_action,
        "event_name": event_name,
        "source_ip": source_ip,
        "user_arn": user_arn,
        "raw_event": body_data
    }
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=forensic_key,
        Body=json.dumps(forensic_report, indent=2),
        ContentType='application/json'
    )

    subject = f"[SECURITY ALERT] Incident Response Activated: {incident_id}"
    message = (
        f"EMERGENCY INCIDENT RESPONSE PLAYBOOK EXECUTED\n"
        f"--------------------------------------------------\n"
        f"Incident ID    : {incident_id}\n"
        f"Timestamp (UTC): {timestamp}\n"
        f"Trigger Event  : {event_name}\n"
        f"Initiated By   : {user_arn}\n"
        f"Access Control : {access_control_action}\n"
        f"DynamoDB Status: LOCKDOWN_ACTIVE ({TABLE_NAME})\n"
        f"S3 Forensics   : s3://{BUCKET_NAME}/{forensic_key}\n"
    )
    sns.publish(TopicArn=SNS_TOPIC_ARN, Subject=subject, Message=message)

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'message': 'Incident response playbook executed successfully',
            'incident_id': incident_id,
            'status': 'LOCKDOWN_ACTIVE',
            'access_control': access_control_action,
            'evidence_file': f"s3://{BUCKET_NAME}/{forensic_key}"
        })
    }