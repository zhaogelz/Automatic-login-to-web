# -*- coding: utf-8 -*-

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
import pyautogui # 导入pyautogui库，为方案二做准备

# --- 配置 (保持不变) ---
URL = "https://account.wps.cn/login?accessid=AK20210823OPGONG&from=v1-web-kdocs-login&logo=kdocs&cb=https%3A%2F%2Faccount.wps.cn%2Fapi%2Fv3%2Fsession%2Fcorrelate%2Fredirect%3Ft%3D1760525356945%26appid%3D375024576%26cb%3Dhttps%253A%252F%252Fwww.kdocs.cn%252FsingleSign4CST%253Fcb%253Dhttps%25253A%25252F%25252Fwww.kdocs.cn%25252Flatest"

# --- XPaths (登录前) ---
BTN_1_XPATH = '//*[@id="footWrap"]/div[3]/a[4]/span[1]'
BTN_2_XPATH = '//*[@id="dialog"]/div[2]/div/div[3]/div[2]'
ACCOUNT_TAB_XPATH = '//*[@id="account"]'
SVG_BTN_XPATH = '//*[@id="rectTop"]'
EMAIL_INPUT_XPATH = '//*[@id="email"]'
PASSWORD_INPUT_XPATH = '//*[@id="password"]'
LOGIN_BTN_XPATH = '//*[@id="login"]'
LOGIN_IFRAME_LOCATOR = (By.TAG_NAME, "iframe")

# --- 登录后操作的 Locators ---
POST_LOGIN_BTN_1_CSS = "label.list-header-checkbox" 
POST_LOGIN_BTN_2_CSS = ".kdv-button.kdv-button--secondary.kdv-button--large.kdv-popover__reference"
HOVER_TARGET_BTN_XPATH = "//button[contains(., '全部类型')]"
DOWNLOAD_OPTION_XPATH = "//div[contains(@class, 'kdv-menu-item__top')]//span[text()='下载']"
CONFIRM_EXPORT_BTN_XPATH = "//button[contains(., '确定导出并继续')]"


def main():
    """主函数，执行自动化流程"""
    
    download_dir = os.path.join(os.getcwd(), "download")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    print(f"文件将自动下载到: {download_dir}")

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # --- 方案一：加强Chrome下载配置 ---
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True,  # 新增配置，直接下载而不是预览
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    wait = WebDriverWait(driver, 15)

    try:
        # ... (前面的登录和点击操作代码保持不变) ...
        print(f"正在打开网页: {URL}")
        driver.get(URL)
        print("等待点击第一个按钮...")
        btn1 = wait.until(EC.element_to_be_clickable((By.XPATH, BTN_1_XPATH)))
        btn1.click()
        time.sleep(0.3)
        print("等待点击第二个按钮...")
        btn2 = wait.until(EC.element_to_be_clickable((By.XPATH, BTN_2_XPATH)))
        btn2.click()
        time.sleep(0.3)
        print("等待并切换到'账号密码登录'标签页...")
        account_tab = wait.until(EC.element_to_be_clickable((By.XPATH, ACCOUNT_TAB_XPATH)))
        account_tab.click()
        time.sleep(0.3)
        print("正在等待并切换到登录表单的 iframe...")
        wait.until(EC.frame_to_be_available_and_switch_to_it(LOGIN_IFRAME_LOCATOR))
        print("已成功切换到 iframe。")
        print("等待并点击SVG按钮...")
        svg_button = wait.until(EC.element_to_be_clickable((By.XPATH, SVG_BTN_XPATH)))
        svg_button.click()
        time.sleep(0.3)
        print("在 iframe 中输入邮箱地址...")
        email_input = wait.until(EC.visibility_of_element_located((By.XPATH, EMAIL_INPUT_XPATH)))
        email_input.send_keys("15023957739")
        print("邮箱输入完成。")
        print("在 iframe 中输入密码...")
        password_input = driver.find_element(By.XPATH, PASSWORD_INPUT_XPATH)
        password_input.send_keys("Aa123456")
        print("密码输入完成。")
        print("输入完毕，等待3秒...")
        time.sleep(3)
        print("等待并点击登录按钮...")
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, LOGIN_BTN_XPATH)))
        login_button.click()
        print("登录按钮已点击。")
        print("登录成功！等待页面加载并执行后续操作...")
        print("从 iframe 切换回主文档...")
        driver.switch_to.default_content()
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, POST_LOGIN_BTN_2_CSS)))
        print("主页面元素已加载。")
        print("模拟鼠标悬停以显示'全选'复选框...")
        hover_target = wait.until(EC.visibility_of_element_located((By.XPATH, HOVER_TARGET_BTN_XPATH)))
        actions = ActionChains(driver)
        actions.move_to_element(hover_target).perform()
        print("鼠标已成功悬停在'全部类型'按钮上。")
        time.sleep(1)
        print("等待并点击'全选'复选框...")
        post_login_btn1 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, POST_LOGIN_BTN_1_CSS)))
        post_login_btn1.click()
        print("'全选'复选框已点击。")
        print("等待并点击'更多操作'按钮...")
        post_login_btn2 = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, POST_LOGIN_BTN_2_CSS)))
        post_login_btn2.click()
        print("'更多操作'按钮已点击，菜单已弹出。")
        print("正在等待'下载'选项出现并点击...")
        download_option = wait.until(EC.element_to_be_clickable((By.XPATH, DOWNLOAD_OPTION_XPATH)))
        download_option.click()
        print("'下载'选项已点击。")
        try:
            confirm_wait = WebDriverWait(driver, 3) 
            print("检查是否存在'确定导出并继续'的确认弹窗...")
            confirm_button = confirm_wait.until(EC.element_to_be_clickable((By.XPATH, CONFIRM_EXPORT_BTN_XPATH)))
            print("确认弹窗已出现，正在点击'确定导出并继续'按钮...")
            confirm_button.click()
            print("'确定导出并继续'按钮已点击。")
        except TimeoutException:
            print("未发现确认弹窗，脚本将继续执行。")
            pass

        print("\n自动化流程执行完毕！文件正在后台自动下载...")
        
        # --- 方案二：如果方案一无效，请取消下面几行代码的注释 ---
        # print("等待'另存为'对话框出现(等待5秒)...")
        # time.sleep(5)
        # print("模拟按下'回车'键确认保存...")
        # pyautogui.press('enter')
        # print("已模拟按下'回车'键。")
        # -----------------------------------------------------

        print("将在60秒后自动关闭浏览器（留出下载时间）...")
        time.sleep(60) # 延长等待时间以确保大文件有时间下载完成

    except TimeoutException:
        print("错误：等待元素超时。请检查 Class Name, XPath 或 CSS Selector 是否正确、网页结构是否已改变或网络是否延迟。")
        driver.save_screenshot('error_screenshot.png')
        print("已保存截图 'error_screenshot.png' 方便调试。")
    except Exception as e:
        print(f"发生未知错误: {e}")
        driver.save_screenshot('error_screenshot.png')
        print("已保存截图 'error_screenshot.png' 方便调试。")
    finally:
        print("关闭浏览器。")
        driver.quit()

if __name__ == "__main__":
    main()