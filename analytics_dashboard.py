#!/usr/bin/env python3
"""
BigQuery Analytics Dashboard for Outreach Campaign Performance
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from utils.bigquery_client import bq_client


def display_dashboard():
    """Display a comprehensive analytics dashboard."""
    print("📊 OUTREACH CAMPAIGN ANALYTICS DASHBOARD")
    print("=" * 60)
    
    if not bq_client.client:
        print("❌ BigQuery client not available")
        return
    
    try:
        # Overall campaign performance
        analytics = bq_client.get_campaign_analytics()
        
        print("📈 OVERALL PERFORMANCE")
        print("-" * 30)
        print(f"Total Leads: {analytics.get('total_leads', 0)}")
        print(f"Initial Emails Sent: {analytics.get('initial_emails_sent', 0)}")
        print(f"Follow-up Emails Sent: {analytics.get('follow_up_emails_sent', 0)}")
        print(f"Replies Received: {analytics.get('replies_received', 0)}")
        print(f"Response Rate: {analytics.get('response_rate_percent', 0):.2f}%")
        
        # Lead status breakdown
        query = f"""
        SELECT 
            status,
            COUNT(*) as count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as percentage
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.leads`
        GROUP BY status
        ORDER BY count DESC
        """
        
        job = bq_client.client.query(query)
        results = list(job.result())
        
        if results:
            print("\n📊 LEAD STATUS BREAKDOWN")
            print("-" * 30)
            for row in results:
                print(f"{row.status}: {row.count} ({row.percentage}%)")
        
        # Email events timeline (last 7 days)
        query = f"""
        SELECT 
            DATE(timestamp) as date,
            event_type,
            COUNT(*) as count
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.email_events`
        WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 7 DAY)
        GROUP BY date, event_type
        ORDER BY date DESC, event_type
        """
        
        job = bq_client.client.query(query)
        results = list(job.result())
        
        if results:
            print("\n📅 EMAIL ACTIVITY (LAST 7 DAYS)")
            print("-" * 40)
            current_date = None
            for row in results:
                if row.date != current_date:
                    current_date = row.date
                    print(f"\n{row.date}:")
                print(f"  {row.event_type}: {row.count}")
        
        # Top performing industries
        query = f"""
        SELECT 
            l.industry,
            COUNT(*) as total_leads,
            COUNT(CASE WHEN e.event_type = 'REPLIED' THEN 1 END) as replies,
            SAFE_DIVIDE(
                COUNT(CASE WHEN e.event_type = 'REPLIED' THEN 1 END),
                COUNT(CASE WHEN e.event_type = 'INITIAL_SENT' THEN 1 END)
            ) * 100 as response_rate
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.leads` l
        LEFT JOIN `{bq_client.project_id}.{bq_client.dataset_id}.email_events` e 
            ON l.email = e.lead_email
        WHERE l.industry IS NOT NULL AND l.industry != ''
        GROUP BY l.industry
        HAVING COUNT(CASE WHEN e.event_type = 'INITIAL_SENT' THEN 1 END) > 0
        ORDER BY response_rate DESC
        LIMIT 10
        """
        
        job = bq_client.client.query(query)
        results = list(job.result())
        
        if results:
            print("\n🏭 INDUSTRY PERFORMANCE")
            print("-" * 40)
            print(f"{'Industry':<15} {'Leads':<8} {'Replies':<8} {'Rate':<8}")
            print("-" * 40)
            for row in results:
                response_rate = row.response_rate or 0
                print(f"{row.industry:<15} {row.total_leads:<8} {row.replies:<8} {response_rate:.1f}%")
        
        print("\n" + "=" * 60)
        print("💡 Tips:")
        print("- Monitor response rates by industry to optimize targeting")
        print("- Track email activity trends to find optimal sending times")
        print("- Follow up with leads that haven't replied within 48-72 hours")
        
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}")


def export_data_to_csv():
    """Export data to CSV files for further analysis."""
    if not bq_client.client:
        print("❌ BigQuery client not available")
        return
    
    try:
        import pandas as pd
        
        # Export leads data
        query = f"""
        SELECT 
            lead_id,
            first_name,
            last_name,
            email,
            company,
            title,
            industry,
            status,
            created_at,
            updated_at
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.leads`
        ORDER BY created_at DESC
        """
        
        df_leads = pd.read_gbq(query, project_id=bq_client.project_id)
        df_leads.to_csv('leads_export.csv', index=False)
        print("✅ Exported leads data to leads_export.csv")
        
        # Export email events
        query = f"""
        SELECT 
            event_id,
            lead_email,
            event_type,
            email_subject,
            timestamp,
            campaign_id
        FROM `{bq_client.project_id}.{bq_client.dataset_id}.email_events`
        ORDER BY timestamp DESC
        """
        
        df_events = pd.read_gbq(query, project_id=bq_client.project_id)
        df_events.to_csv('email_events_export.csv', index=False)
        print("✅ Exported email events to email_events_export.csv")
        
    except ImportError:
        print("⚠️  pandas and pandas-gbq required for CSV export")
        print("Install with: pip install pandas pandas-gbq")
    except Exception as e:
        print(f"❌ Error exporting data: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--export":
        export_data_to_csv()
    else:
        display_dashboard()
