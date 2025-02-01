from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

# 初期設定
is_debug = False  # デバッグモード

# 環境変数から取得
URL = os.getenv("URL")
USER_ID = os.getenv("USER_ID")
PASSWORD = os.getenv("PASSWORD")
# メールアドレス
FROM_EMAIL = os.getenv("FROM_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
if is_debug:
    TO_EMAIL = os.getenv("TO_DEBUG_EMAIL")
else:
    TO_EMAIL = os.getenv("TO_EMAIL")
CC_EMAILS = os.getenv("CC_EMAILS", "").split(",") if os.getenv("CC_EMAILS") else []

print("==================================== 直方自動車学校 予約状況通知システム ====================================")
print("URL: ", URL)
print("USER_ID: ", USER_ID, "PASSWORD: ", PASSWORD)
print("通知方法: メール")
print("FROM_EMAIL: ", FROM_EMAIL, "TO_EMAIL: ", TO_EMAIL)
print("CC_EMAILS: ", CC_EMAILS)
print("============================================================================================================")


class SendEmail:
    def __init__(self):
        self.smtp_server = "smtp.gmail.com"  # SMTPサーバ（Gmail）
        self.smtp_port = 465 # ポート番号 # 587 or 465
        self.sender_email = FROM_EMAIL  # 送信元メールアドレスを設定
        self.sender_password = APP_PASSWORD  # アプリパスワードを設定

    def send_email(self, subject: str, body: str, to_email: str, cc_emails=None) -> bool:
        """
        メールを送信する関数
        Args:
            subject (str): メールの件名
            body (str): メールの本文
            to_email (str): 送信先メールアドレス
            cc_emails (list): CC先のメールアドレス（デフォルトはNone）
        Returns:
            bool: 送信に成功した場合はTrue、失敗した場合はFalse
        """
        cc_emails = cc_emails or []  # None の場合は空リストにする

        # メールの設定
        self.msg = MIMEMultipart()
        self.msg["From"] = self.sender_email
        self.msg["To"] = to_email
        self.msg["Cc"] = ",".join(cc_emails) # CC先のメールアドレスを設定
        self.msg["Subject"] = subject
        self.msg.attach(MIMEText(body, "plain"))

        # 送信先リスト（TO + CC）
        recipients = [to_email] + cc_emails

        try:
            # SMTPサーバに接続
            # server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            # server.starttls()  # セキュアな通信に切り替え
            # SMTP_SSL を使用する（ポート465のとき）
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(self.sender_email, self.sender_password)  # ログイン
                server.sendmail(self.sender_email, recipients, self.msg.as_string())  # メール送信
            # server.quit()
            print("メール送信に成功しました。")
            return True
        except Exception as e:
            print("メール送信に失敗しました:", e)
            return False


class WebDriverHandler:
    def __init__(self, chrome_driver_path: str):
        print("ChromeDriverの初期化中...")
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        # ChromeDriverのパスを指定してブラウザドライバを設定
        service = Service(executable_path=chrome_driver_path)
        self.driver = webdriver.Chrome(service=service)
        
    def open_url(self, url: str):
        """指定されたURLを開く"""
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
        print("ReservationCheckerの初期化中...")
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
        print("\n=============== 予約状況 ===============")
        print("予約済みの日付（×）:")
        for reserved_date in self.reservation_dict["reserved_dates"]:
            print(reserved_date)

        print("\n予約可能な日付:")
        for available_date in self.reservation_dict["available_dates"]:
            print(available_date)
        print("=========================================\n")
            

def main():
    print("\n===== メイン処理を開始します =====")
    # 初期設定
    # 初期設定
    is_debug = False  # デバッグモード
    is_send_email = True # メール送信フラグ
    retry_count = 3 # リトライ回数
    print("リトライ回数: ", retry_count, "回")
    print("メール通知するか: ", is_send_email)    

    # WebDriverHandlerとReservationCheckerのインスタンスを作成
    driver_handler = WebDriverHandler(chrome_driver_path='/opt/homebrew/bin/chromedriver')
    reservation_checker = ReservationChecker(driver_handler)

    attempts = 0 # リトライ回数のカウント
    success = False # 成功フラグ    
    while attempts < retry_count and not success:
        try:
            print(f"\n試行 {attempts + 1}/{retry_count} - URLにアクセスします...")

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

            # 成功したらフラグを立てる
            success = True  # 処理成功
            print("処理が成功しました。")
        except Exception as e:
            attempts += 1
            print(f"エラーが発生しました: {e}")
            if attempts < retry_count:
                print(f"{retry_count - attempts} 回リトライします...")
                # ブラウザを閉じる
                driver_handler.close()
                driver_handler.driver.quit()

                time.sleep(5)  # リトライ間隔（5秒待機）
                # ブラウザを再度開く
                driver_handler = WebDriverHandler(chrome_driver_path='/opt/homebrew/bin/chromedriver')
                print("ChromeDriverを再起動しました。")
            else:
                print("最大リトライ回数に達しました。処理を終了します。")
                print("エラー内容: ", e)

                # メール送信フラグをfalseにする
                is_send_email = False
        finally:
            # ブラウザを閉じる
            driver_handler.close()
    

    if is_send_email is True:
        # 予約可能な日があればメールで通知
        if reservation_dict["available_dates"]:
            message = "予約可能な日があります！\n"
            message += "予約可能な日付: " + ", ".join(reservation_dict["available_dates"])
            message += "\n\n予約はこちらから: \n"
            message += URL
            # メールに送信
            print("メールに送信します。", "to: ", TO_EMAIL, "cc: ", CC_EMAILS)
            send_email = SendEmail()
            response = send_email.send_email("直方自動車学校 予約可能日のお知らせ", message, TO_EMAIL)
            # 送信結果を確認
            if response:
                print("メッセージ送信に成功しました。")
            else:
                print("メッセージ送信に失敗しました。")
        else:
            print("予約可能な日はありません。")
            # メールに送信(debug用)
            message = "予約可能な日はありません。"
            message += "\n\n予約の確認はこちらから: \n"
            message += URL
            if is_debug is True:
                # メールに送信
                print("メールに送信します。", "to: ", TO_EMAIL, "cc: ", CC_EMAILS)
                send_email = SendEmail()
                response = send_email.send_email(
                    subject="直方自動車学校 予約可能日のお知らせ",
                    body=message,
                    to_email=TO_EMAIL,
                    cc_emails=CC_EMAILS
                )
                # 送信結果を確認
                if response:
                    print("メッセージ送信に成功しました。")
                else:
                    print("メッセージ送信に失敗しました。")
    else:
        print("メール通知はOFFです。")

    # 任意の時間待って結果を確認
    time.sleep(3)

    # ブラウザを閉じる
    driver_handler.close()

if __name__ == "__main__":
    main()