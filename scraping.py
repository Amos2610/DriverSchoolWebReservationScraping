from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from dotenv import load_dotenv
import os
import linebot.v3.messaging
from linebot.v3.messaging import ApiClient, Configuration, MessagingApi, PushMessageRequest
import pprint
import json

load_dotenv()

# # 環境変数から取得
URL = os.getenv("URL")
USER_ID = os.getenv("USER_ID")
PASSWORD = os.getenv("PASSWORD")
LINE_ACCESS_TOKEN = os.getenv("LINE_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")
LINE_USER_ID2 = os.getenv("LINE_USER_ID2")

class LineMessagingAPI:
    def __init__(self, access_token: str):
        """
        初期化メソッド。アクセストークンを受け取り、LINEのAPIクライアントを設定する。
        """
        self.configuration = Configuration(
            host="https://api.line.me",
            access_token=access_token
        )

    def send_message(self, message: str) -> bool:
        """
        指定したユーザーにメッセージを送信する。
        """
        if not LINE_ACCESS_TOKEN:
            print("LINE_ACCESS_TOKENが設定されていません。")
            return False
        if not LINE_USER_ID:
            print("ユーザーIDが指定されていません。")
            return False
        if not message:
            print("メッセージが指定されていません。")
            return False
        
        # メッセージ構造を作成
        message_dict = {
            "to": LINE_USER_ID,
            "messages": [
                {
                    "type": "text",
                    "text": message
                }
            ]
        }

        # メッセージ送信
        with linebot.v3.messaging.ApiClient(self.configuration) as api_client:
            api_instance = linebot.v3.messaging.MessagingApi(api_client)
            push_message_request = linebot.v3.messaging.PushMessageRequest.from_dict(message_dict)

            try:
                api_response = api_instance.push_message(push_message_request)
                print("The response of MessagingApi->push_message:\n")
                return True
            except Exception as e:
                print("Exception when calling MessagingApi->push_message: %s\n" % e)
                return False


class WebDriverHandler:
    def __init__(self, chrome_driver_path: str):
        # ChromeDriverのパスを指定してブラウザドライバを設定
        service = Service(executable_path=chrome_driver_path)
        self.driver = webdriver.Chrome(service=service)
        
    def open_url(self, url: str):
        """指定されたURLを開く"""
        print("Opening URL: ", url)
        self.driver.get(url)
        
    def switch_to_iframe(self, iframe_id: str):
        """指定されたiframeに切り替え"""
        iframe = self.driver.find_element(By.ID, iframe_id)
        self.driver.switch_to.frame(iframe)
        
    def fill_login_form(self, student_no: str, password: str):
        """ログインフォームに教習生番号とパスワードを入力"""
        student_field = self.driver.find_element(By.ID, "txtKyoushuuseiNO")
        password_field = self.driver.find_element(By.ID, "txtPassword")
        
        student_field.send_keys(student_no)
        password_field.send_keys(password)
        
    def click_button(self, button_id: str):
        """指定されたボタンをクリック"""
        button = self.driver.find_element(By.ID, button_id)
        button.click()
        
    def get_page_source(self):
        """ページのHTMLを取得"""
        return self.driver.page_source
    
    # WebDriverのexecute_scriptメソッドをラップする
    def execute_script(self, script):
        return self.driver.execute_script(script)
    
    def close(self):
        """ブラウザを閉じる"""
        self.driver.quit()
        
class ReservationChecker:
    def __init__(self, driver_handler: WebDriverHandler):
        self.driver_handler = driver_handler
        self.reservation_dict = {
            "available_dates": [],
            "reserved_dates": []
        }
    
    def get_reservation_dates(self) -> dict:
        """予約可能な日付と予約済みの日付を取得"""
        dates = self.driver_handler.driver.find_elements(By.CSS_SELECTOR, ".blocks .lbl")
        flags = self.driver_handler.driver.find_elements(By.CSS_SELECTOR, ".blocks .badge")

        for date, flag in zip(dates, flags):
            date_text = date.text
            flag_text = flag.text

            if flag_text == "×":
                self.reservation_dict["reserved_dates"].append(date_text)
            else:
                self.reservation_dict["available_dates"].append(date_text)
        
        return self.reservation_dict
    
    def print_reservations(self):
        """予約可能日と予約済み日を出力"""
        print("予約済みの日付（×）:")
        for reserved_date in self.reservation_dict["reserved_dates"]:
            print(reserved_date)

        print("\n予約可能な日付:")
        for available_date in self.reservation_dict["available_dates"]:
            print(available_date)
            

def main():
    # WebDriverHandlerとReservationCheckerのインスタンスを作成
    driver_handler = WebDriverHandler(chrome_driver_path='/opt/homebrew/bin/chromedriver')
    reservation_checker = ReservationChecker(driver_handler)
    
    # 最初にアクセスするURL
    driver_handler.open_url(URL)

    # iframeを読み込んで切り替え
    driver_handler.switch_to_iframe("frameMenu")

    # ログイン処理
    driver_handler.fill_login_form(USER_ID, PASSWORD)
    
    # ログインボタンをクリック
    driver_handler.click_button("btnAuthentication")

    # ログイン完了を待機
    WebDriverWait(driver_handler.driver, 10).until(
        EC.presence_of_element_located((By.ID, "btnMenu_Kyoushuuyoyaku"))
    )

    # 予約画面に遷移
    driver_handler.click_button("btnMenu_Kyoushuuyoyaku")

    time.sleep(2)

    # ReservationCheckerを用いて予約情報を取得
    reservation_checker.get_reservation_dates()

    # 次の週に移動
    driver_handler.execute_script("$('#btnNextWeek').click();")

    # 次の週の情報が表示されるまで待機
    WebDriverWait(driver_handler.driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".blocks .lbl"))
    )

    # ReservationCheckerを用いて予約情報を取得
    reservation_dict = reservation_checker.get_reservation_dates()
    reservation_checker.print_reservations() # debug用

    # 予約可能な日があればLINEに通知
    if reservation_dict["available_dates"]:
        message = "予約可能な日があります！\n"
        message += "予約可能な日付: " + ", ".join(reservation_dict["available_dates"])
        line_messaging_api = LineMessagingAPI(LINE_ACCESS_TOKEN)
        response = line_messaging_api.send_message(message)
    
        # 送信結果を確認
        if response:
            print("メッセージ送信に成功しました。")
        else:
            print("メッセージ送信に失敗しました。")
    else:
        print("予約可能な日はありません。")
        line_messaging_api = LineMessagingAPI(LINE_ACCESS_TOKEN)
        response = line_messaging_api.send_message("予約可能な日はありません。")
        if response:
            print("メッセージ送信に成功しました。")
        else:
            print("メッセージ送信に失敗しました。")

    # 任意の時間待って結果を確認
    time.sleep(3)

    # ブラウザを閉じる
    driver_handler.close()

if __name__ == "__main__":
    main()
