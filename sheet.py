import gspread
from oauth2client.service_account import ServiceAccountCredentials

def write_to_sheet(user_id , received_text, send_text, time,time_now):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

    # 載入憑證
    creds = ServiceAccountCredentials.from_json_keyfile_name("propane-shell-461501-u9-31c047a0e0a8.json", scope)
    client = gspread.authorize(creds)

    # 開啟 Google Sheet（用標題或 Spreadsheet ID）
    spreadsheet = client.open_by_key("1vjNr5OTtzSrCzIc7j8MRJBFpt8iO9IvIyWhVociaPOI")

    # 選擇工作表
    worksheet = spreadsheet.sheet1  # 或 spreadsheet.worksheet("工作表名稱")
    worksheet.append_row([time_now,user_id, received_text, send_text, time])

if __name__ == "__main__":
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