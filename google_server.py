import gspread
import google.auth
from google.auth.transport.requests import Request
from google.auth.credentials import Credentials
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime, timezone, timedelta
import calendar
import google.auth


def write_to_sheet(user_id, received_text, send_text, time, time_now,message_id,time1,time2,time3,time4,time5,time6):
    # 使用預設憑證（Cloud Run 自動提供）
    creds, _ = google.auth.default(scopes=[
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    
    client = gspread.authorize(creds)

    # 開啟 Google Sheet（用 Spreadsheet ID）
    spreadsheet = client.open_by_key("1vjNr5OTtzSrCzIc7j8MRJBFpt8iO9IvIyWhVociaPOI")

    # 選擇工作表
    worksheet = spreadsheet.sheet1  # 或指定名稱：spreadsheet.worksheet("Sheet1")
    
    # 寫入資料
    worksheet.append_row([time_now, user_id, received_text, send_text, time,message_id,time1,time2,time3,time4,time5,time6])
def test_write_to_sheet():
    # 設定授權範圍
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # 載入憑證
    creds = ServiceAccountCredentials.from_json_keyfile_name("propane-shell-461501-u9-31c047a0e0a8.json", scope)
    client = gspread.authorize(creds)

    # 開啟 Google Sheet（用標題或 Spreadsheet ID）
    spreadsheet = client.open_by_key("1vjNr5OTtzSrCzIc7j8MRJBFpt8iO9IvIyWhVociaPOI")

    # 選擇工作表
    worksheet = spreadsheet.sheet1  # 或 spreadsheet.worksheet("工作表名稱")

    # 寫入資料（例如 A1）
    worksheet.update(values=[['Hello, World!']], range_name='A1')
    worksheet.append_row(["姓名", "電話", "Email"])  # 一次新增一整列
    worksheet.append_row(["小明", "0988123456", "ming@example.com"])

def get_calendar_events():

    # === 取得預設憑證（Cloud Run / GCE / Colab 都適用）===
    credentials, _ = google.auth.default(scopes=[
        "https://www.googleapis.com/auth/calendar.readonly"
    ])

    # 建立 Calendar API 服務
    service = build('calendar', 'v3', credentials=credentials)

    # === 計算當月的起訖時間（UTC）===
    now = datetime.now()
    year, month = now.year, now.month
    start_of_month = datetime(year, month, 1, tzinfo=timezone.utc)
    _, last_day = calendar.monthrange(year, month)
    end_of_month = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)

    # 轉成 RFC3339 時間格式
    time_min = start_of_month.isoformat()
    time_max = end_of_month.isoformat()

    # === 指定日曆 ID（必須事先授權給 Cloud Run Service Account）===
    calendar_id = '9qt3c06n1h0u0rcuvf6plir5p0j5rkqn@import.calendar.google.com'  # 或使用 gmail.com

    # === 擷取事件 ===
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    all_events = []
    # === 輸出每筆事件為 [標題, 開始時間, 結束時間] ===
    for event in events:
        title = event.get('summary', '（無標題）')
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        all_events.append([title, start, end])
    return(all_events)
    
def test_get_calendar_events():
# === 認證與建立服務 ===
    credentials = service_account.Credentials.from_service_account_file(
        "propane-shell-461501-u9-31c047a0e0a8.json",
        scopes=['https://www.googleapis.com/auth/calendar.readonly']
    )
    service = build('calendar', 'v3', credentials=credentials)

    # === 計算當月起訖時間 ===
    today = datetime.now()
    year, month = today.year, today.month
    start_of_month = datetime(year, month, 1, tzinfo=timezone.utc)
    _, last_day = calendar.monthrange(year, month)
    end_of_month = datetime(year, month, last_day, 23, 59, 59, tzinfo=timezone.utc)

    time_min = start_of_month.isoformat()
    time_max = end_of_month.isoformat()

    # === 日曆 ID（請改為你共用的那個日曆 ID）===
    calendar_id = '9qt3c06n1h0u0rcuvf6plir5p0j5rkqn@import.calendar.google.com'

    # === 擷取當月事件 ===
    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])
    all_events = []
    # === 格式化並輸出每筆事件 ['標題', '開始時間', '結束時間'] ===
    for event in events:
        title = event.get('summary', '（無標題）')
        start_time = event['start'].get('dateTime', event['start'].get('date'))
        end_time = event['end'].get('dateTime', event['end'].get('date'))
        all_events.append([title, start_time, end_time])
    return(all_events)