# -*- coding: utf-8 -*-

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- 配置 (保持不变) ---
URL = "https://account.wps.cn/login?accessid=AK20210823OPGONG&from=v1-web-kdocs-login&logo=kdocs&cb=https%3A%2F%2Faccount.wps.cn%2Fapi%2Fv3%2Fsession%2Fcorrelate%2Fredirect%3Ft%3D1760525356945%26appid%3D375024576%26cb%3Dhttps%253A%252F%252Fwww.kdocs.cn%252FsingleSign4CST%253Fcb%253Dhttps%25253A%25252F%25252Fwww.kdocs.cn%25252Flatest"

# --- XPaths ---
BTN_1_XPATH = '//*[@id="footWrap"]/div[3]/a[4]/span[1]'
BTN_2_XPATH = '//*[@id="dialog"]/div[2]/div/div[3]/div[2]'
ACCOUNT_TAB_XPATH = '//*[@id="account"]'
SVG_BTN_XPATH = '//*[@id="rectTop"]'  # <-- 新增的SVG按钮XPath
EMAIL_INPUT_XPATH = '//*[@id="email"]'
PASSWORD_INPUT_XPATH = '//*[@id="password"]'
LOGIN_IFRAME_LOCATOR = (By.TAG_NAME, "iframe")


def main():
    """主函数，执行自动化流程"""
    
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    wait = WebDriverWait(driver, 15)

    try:
        print(f"正在打开网页: {URL}")
        driver.get(URL)

        print("等待点击第一个按钮...")
        btn1 = wait.until(EC.element_to_be_clickable((By.XPATH, BTN_1_XPATH)))
        btn1.click()
        print("第一个按钮已点击，延迟1秒...")
        time.sleep(1)

        print("等待点击第二个按钮...")
        btn2 = wait.until(EC.element_to_be_clickable((By.XPATH, BTN_2_XPATH)))
        btn2.click()
        print("第二个按钮已点击，延迟1秒...")
        time.sleep(1)
        
        print("等待并切换到'账号密码登录'标签页...")
        account_tab = wait.until(EC.element_to_be_clickable((By.XPATH, ACCOUNT_TAB_XPATH)))
        account_tab.click()
        print("'账号密码登录'已切换，延迟1秒...")
        time.sleep(1)
        
        print("正在等待并切换到登录表单的 iframe...")
        wait.until(EC.frame_to_be_available_and_switch_to_it(LOGIN_IFRAME_LOCATOR))
        print("已成功切换到 iframe。")
        
        # ==================== 新增代码：点击SVG按钮 ====================
        print("等待并点击SVG按钮...")
        svg_button = wait.until(EC.element_to_be_clickable((By.XPATH, SVG_BTN_XPATH)))
        svg_button.click()
        print("SVG按钮已点击，延迟1秒...")
        time.sleep(1)
        # =============================================================

        print("在 iframe 中输入邮箱地址...")
        email_input = wait.until(EC.visibility_of_element_located((By.XPATH, EMAIL_INPUT_XPATH)))
        email_input.send_keys("aaa")
        print("邮箱输入完成。")

        print("在 iframe 中输入密码...")
        password_input = driver.find_element(By.XPATH, PASSWORD_INPUT_XPATH)
        password_input.send_keys("bbb")
        print("密码输入完成。")

        print("\n自动化流程执行完毕！")
        
        print("将在30秒后自动关闭浏览器...")
        time.sleep(30)

    except TimeoutException:
        print("错误：等待元素超时。请检查XPath或iframe定位器是否正确、网页结构是否已改变或网络是否延迟。")
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