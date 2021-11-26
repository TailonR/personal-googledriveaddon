import sys
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.cloud import datastore
import google.oauth2.credentials
import google_auth_oauthlib.flow
import Backend.datastoreMethods as dataMethods

SCOPES = ['https://www.googleapis.com/auth/gmail.addons.current.action.compose',
          'https://www.googleapis.com/auth/gmail.send', 'https://www.googleapis.com/auth/gmail.compose',
          'https://www.googleapis.com/auth/datastore', 'https://www.googleapis.com/auth/drive.readonly',
          'https://www.googleapis.com/auth/drive.metadata',
          'https://www.googleapis.com/auth/admin.reports.audit.readonly']

REDIRECT_URI = "https://us-central1-driveaddon-activity.cloudfunctions.net/trigger"


def get_authorization_url():
    # Use the client_secret.json file to identify the application requesting
    # authorization. The client ID (from that file) and access scopes are required.
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'Backend/credentials_v2.json',
        scopes=SCOPES)

    # Indicate where the API server will redirect the user after the user completes
    # the authorization flow. The redirect URI is required. The value must exactly
    # match one of the authorized redirect URIs for the OAuth 2.0 client, which you
    # configured in the API Console. If this value doesn't match an authorized URI,
    # you will get a 'redirect_uri_mismatch' error.
    flow.redirect_uri = REDIRECT_URI

    # Generate URL for request to Google's OAuth 2.0 server.
    # Use kwargs to set optional request parameters.
    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')
    return authorization_url


def dev_authenticate():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization.py flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'Backend/credentials_v2.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds


def authenticate():
    creds = None
    client = datastore.Client("driveaddon-activity")
    token = dataMethods.get_most_recent_token(client)
    if token is not None:
        creds = Credentials.from_authorized_user_info(token, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            client = datastore.Client("driveaddon-activity", credentials=creds)
            dataMethods.store_token(client, creds)
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'Backend/credentials_v2.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        client = datastore.Client("driveaddon-activity", credentials=creds)
        dataMethods.store_token(client, creds)

    return creds
