from __future__ import print_function
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

import os
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import google.auth

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


def cred():
    SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
    """Shows basic usage of the Drive v3 API.
        Prints the names and ids of the first 10 files the user has access to.
        """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        service = build('drive', 'v3', credentials=cred())

        # Call the Drive v3 API
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
            return
        print('Files:')
        for item in items:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=item.get("name"))

            print(u'{0} ({1})'.format(item['name'], item['id']))
    except HttpError as error:
        # TODO(developer) - Handle errors from drive API.
        print(f'An error occurred: {error}')


async def upload_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    newFile = await update.message.effective_attachment.get_file()
    await newFile.download_to_drive(custom_path='downloaded/'+update.message.effective_attachment.file_name)
    ##+ update.message.effective_attachment.file_name)

    try:
        # create drive api client
        service = build('drive', 'v3', credentials=cred())

        file_metadata = {'name': update.message.document.file_name}
        media = MediaFileUpload("downloaded/" + update.message.document.file_name,
                                mimetype=update.message.document.mime_type, resumable=True)
        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, media_body=media,
                                      fields='id').execute()
        print(F'File ID: {file.get("id")}')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Sussec")
    return file.get('id')


if __name__ == '__main__':
    load_dotenv()
    application = ApplicationBuilder().token(os.getenv('TOKEN')).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('files', list_files))
    application.add_handler(MessageHandler(filters.Document.ALL, upload_files))
    application.run_polling()
