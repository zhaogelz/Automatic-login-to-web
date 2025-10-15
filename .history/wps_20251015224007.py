# -*- coding: utf-8 -*-

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException

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
HOVER_TRIGGER_XPATH = "//button[contains(., '全部类型')]"
TARGET_BUTTON_CSS = ".kdv-button.kdv-button--secondary.kdv-button--large.kdv-popover__reference"


def main():
    """主函数，执行自动化流程"""
    
    # ... (初始化代码不变，此处省略) ...
    download_dir = os.path.join(os.getcwd(), "download")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    print(f"文件将下载到: {download_dir}")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    prefs = {"download.default_directory": download_dir}
    chrome_options.add_experimental_option("prefs", prefs)
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    wait = WebDriverWait(driver, 15)

    try:
        # ... (登录前的代码部分保持不变，这里省略) ...
        print(f"正在打开网页: {URL}")
        driver.get(URL)
        print("等待点击第一个按钮...")
        btn1 = wait.until(EC.element_to_be_clickable((By.XPATH, BTN_1_XPATH)))
        btn1.click(); time.sleep(0.3)
        print("等待点击第二个按钮...")
        btn2 = wait.until(EC.element_to_be_clickable((By.XPATH, BTN_2_XPATH)))
        btn2.click(); time.sleep(0.3)
        print("等待并切换到'账号密码登录'标签页...")
        account_tab = wait.until(EC.element_to_be_clickable((By.XPATH, ACCOUNT_TAB_XPATH)))
        account_tab.click(); time.sleep(0.3)
        print("正在等待并切换到登录表单的 iframe...")
        wait.until(EC.frame_to_be_available_and_switch_to_it(LOGIN_IFRAME_LOCATOR))
        print("等待并点击SVG按钮...")
        svg_button = wait.until(EC.element_to_be_clickable((By.XPATH, SVG_BTN_XPATH)))
        svg_button.click(); time.sleep(0.3)
        print("在 iframe 中输入邮箱地址...")
        email_input = wait.until(EC.visibility_of_element_located((By.XPATH, EMAIL_INPUT_XPATH)))
        email_input.send_keys("15023957739")
        print("在 iframe 中输入密码...")
        password_input = driver.find_element(By.XPATH, PASSWORD_INPUT_XPATH)
        password_input.send_keys("Aa123456")
        time.sleep(3)
        print("等待并点击登录按钮...")
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, LOGIN_BTN_XPATH)))
        login_button.click()
        print("登录按钮已点击。")

        # ==================== 修改后的代码: 登录后操作 ====================
        print("登录成功！等待页面加载并执行后续操作...")
        
        print("从 iframe 切换回主文档...")
        driver.switch_to.default_content()
        
        # 1. 定位触发元素
        print(f"正在定位触发元素 (通过XPath): {HOVER_TRIGGER_XPATH}")
        trigger_element = wait.until(
            EC.presence_of_element_located((By.XPATH, HOVER_TRIGGER_XPATH))
        )
        
        # 2. 模拟鼠标悬停
        print("正在模拟鼠标悬停到 '全部类型' 按钮上...")
        actions = ActionChains(driver)
        actions.move_to_element(trigger_element).perform()

        # 3. 【新策略】悬停后，固定等待300毫秒，给动画启动时间
        print("悬停后固定等待300毫秒...")
        time.sleep(0.3)

        # 4. 【新策略】使用最初可行的 'element_to_be_clickable' 方法来等待并点击
        print(f"尝试使用 'element_to_be_clickable' 定位并点击目标按钮: {TARGET_BUTTON_CSS}")
        target_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, TARGET_BUTTON_CSS))
        )
        target_button.click()
        print("标准点击成功！")
        # ====================================================================

        print("\n自动化流程执行完毕！")
        print("将在30秒后自动关闭浏览器...")
        time.sleep(30)

    except TimeoutException:
        print("错误：等待元素超时。请检查 XPath 或 CSS Selector 是否正确、网页结构是否已改变或网络是否延迟。")
        print("如果错误发生在此处，说明悬停后等待300ms，目标按钮仍未出现或不可点击。")
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