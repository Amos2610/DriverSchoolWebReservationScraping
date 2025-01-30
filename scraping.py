from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

URL = "https://nogata.obic7.obicnet.ne.jp/EGWWeb30/Api/Access/Navigate?p=MKddJE9aAXfowcf9FKZrqS%2b9VWreLBK2%2f9%2bJjA7QJRPDlOpr5YbtAkS34t0D0Tev"
USER_ID = "2407518"
PASSWORD = "0702"

class WebDriverHandler:
    def __init__(self, chrome_driver_path: str):
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
        self.driver_handler = driver_handler
        self.reservation_dict = {
            "available_dates": [],
            "reserved_dates": []
        }
    
    def get_reservation_dates(self):
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
    reservation_checker.get_reservation_dates()
    reservation_checker.print_reservations()

    # 任意の時間待って結果を確認
    time.sleep(3)

    # ブラウザを閉じる
    driver_handler.close()

if __name__ == "__main__":
    main()
