import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

class GoogleIntegration:
    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        self.redirect_uri = 'http://localhost:4001/google-callback'
        
    def get_auth_url(self):
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": [self.redirect_uri]
                }
            },
            scopes=self.scopes
        )
        flow.redirect_uri = self.redirect_uri
        auth_url, _ = flow.authorization_url(prompt='consent')
        return auth_url, flow
    
    def get_credentials(self, code, flow):
        flow.fetch_token(code=code)
        return flow.credentials
    
    def create_spreadsheet(self, credentials, title, data):
        service = build('sheets', 'v4', credentials=credentials)
        
        # Create spreadsheet
        spreadsheet = {
            'properties': {'title': title}
        }
        spreadsheet = service.spreadsheets().create(body=spreadsheet).execute()
        spreadsheet_id = spreadsheet.get('spreadsheetId')
        
        # Prepare data for sheets based on data type
        if data:
            values = []
            
            # Check if it's email data (has 'stats' key)
            if isinstance(data, list) and len(data) > 0 and 'stats' in data[0]:
                # Email data
                headers = ['Email ID', 'Name', 'Subject', 'Created At', 'Sent', 'Delivered', 'Hard Bounced', 'Soft Bounced', 'Opens', 'Unique Opens', 'Opens Rate', 'Total Clicks', 'Unique Clicks', 'Click Through Rate', 'Unique Click Through Rate', 'Click Open Ratio', 'Opt Outs', 'Opt Out Rate', 'Spam Complaints', 'Spam Complaint Rate', 'Delivery Rate']
                values = [headers]
                
                for item in data:
                    stats = item.get('stats', {})
                    row = [
                        item.get('id', ''),
                        item.get('name', ''),
                        item.get('subject', ''),
                        item.get('createdat', ''),
                        stats.get('sent', 0),
                        stats.get('delivered', 0),
                        stats.get('hardBounced', 0),
                        stats.get('softBounced', 0),
                        stats.get('opens', 0),
                        stats.get('uniqueOpens', 0),
                        stats.get('opensRate', 0),
                        stats.get('totalClicks', 0),
                        stats.get('uniqueClicks', 0),
                        stats.get('clickThroughRate', 0),
                        stats.get('uniqueClickThroughRate', 0),
                        stats.get('clickOpenRatio', 0),
                        stats.get('optOuts', 0),
                        stats.get('optOutRate', 0),
                        stats.get('spamComplaints', 0),
                        stats.get('spamComplaintRate', 0),
                        stats.get('deliveryRate', 0)
                    ]
                    values.append(row)
            
            # Check if it's form data (has 'views' key)
            elif isinstance(data, list) and len(data) > 0 and 'views' in data[0]:
                # Form data
                headers = ['Form ID', 'Form Name', 'Views', 'Unique Views', 'Submissions', 'Unique Submissions', 'Clicks', 'Unique Clicks', 'Conversions', 'Conversion Rate']
                values = [headers]
                
                for item in data:
                    views = item.get('views', 0)
                    submissions = item.get('submissions', 0)
                    conversion_rate = (submissions / views * 100) if views > 0 else 0
                    
                    row = [
                        item.get('id', ''),
                        item.get('name', ''),
                        views,
                        item.get('unique_views', 0),
                        submissions,
                        item.get('unique_submissions', 0),
                        item.get('clicks', 0),
                        item.get('unique_clicks', 0),
                        item.get('conversions', 0),
                        f"{conversion_rate:.2f}%"
                    ]
                    values.append(row)
            
            # Check if it's UTM data (list of dictionaries with UTM fields)
            elif isinstance(data, list) and len(data) > 0 and 'Prospect ID' in data[0]:
                # UTM data - already formatted for export
                if data:
                    headers = list(data[0].keys())
                    values = [headers]
                    
                    for item in data:
                        row = [item.get(header, '') for header in headers]
                        values.append(row)
            
            # Check if it's campaign data (list of dictionaries with Campaign ID)
            elif isinstance(data, list) and len(data) > 0 and 'Campaign ID' in data[0]:
                # Campaign data - already formatted for export
                if data:
                    headers = list(data[0].keys())
                    values = [headers]
                    
                    for item in data:
                        row = [item.get(header, '') for header in headers]
                        values.append(row)
            
            # Generic data export (fallback)
            elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                # Generic dictionary data
                headers = list(data[0].keys())
                values = [headers]
                
                for item in data:
                    row = [item.get(header, '') for header in headers]
                    values.append(row)
            
            # Check if it's prospect health data (has 'total_prospects' key)
            elif isinstance(data, dict) and 'total_prospects' in data:
                # Prospect health data
                headers = ['Metric', 'Count', 'Percentage']
                values = [headers]
                
                total = data['total_prospects']
                values.append(['Total Prospects', total, '100%'])
                values.append(['Duplicates', data['duplicates']['count'], f"{(data['duplicates']['count']/total*100):.1f}%"])
                values.append(['Inactive (90+ days)', data['inactive_prospects']['count'], f"{(data['inactive_prospects']['count']/total*100):.1f}%"])
                values.append(['Missing Fields', data['missing_fields']['count'], f"{(data['missing_fields']['count']/total*100):.1f}%"])
                values.append(['Scoring Issues', data['scoring_issues']['count'], f"{(data['scoring_issues']['count']/total*100):.1f}%"])
                
                grading = data.get('grading_analysis', {})
                if grading:
                    values.append(['', '', ''])  # Empty row
                    values.append(['Grading Analysis', '', ''])
                    values.append(['Grading Coverage', f"{grading.get('grading_coverage', 0):.1f}%", ''])
                    values.append(['Graded Prospects', grading.get('graded_prospects', 0), ''])
                    values.append(['Ungraded Prospects', grading.get('ungraded_prospects', 0), ''])
            
            # Update spreadsheet with data
            if values:
                body = {'values': values}
                service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id,
                    range='A1',
                    valueInputOption='RAW',
                    body=body
                ).execute()
        
        return spreadsheet_id
    
    def export_to_drive(self, credentials, spreadsheet_id, filename):
        from googleapiclient.http import MediaIoBaseUpload
        drive_service = build('drive', 'v3', credentials=credentials)
        
        # Export as PDF
        request = drive_service.files().export_media(
            fileId=spreadsheet_id,
            mimeType='application/pdf'
        )
        
        file_io = io.BytesIO()
        downloader = MediaIoBaseDownload(file_io, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        # Upload PDF to Drive
        file_metadata = {'name': f'{filename}.pdf'}
        file_io.seek(0)
        media = MediaIoBaseUpload(file_io, mimetype='application/pdf')
        
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        return file.get('id')