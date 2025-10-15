# -*- coding: utf-8 -*-

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- 配置 ---
# 目标网页 URL
URL = "https://account.wps.cn/login?accessid=AK20210823OPGONG&from=v1-web-kdocs-login&logo=kdocs&cb=https%3A%2F%2Faccount.wps.cn%2Fapi%2Fv3%2Fsession%2Fcorrelate%2Fredirect%3Ft%3D1760525356945%26appid%3D375024576%26cb%3Dhttps%253A%252F%252Fwww.kdocs.cn%252FsingleSign4CST%253Fcb%253Dhttps%25253A%25252F%25252Fwww.kdocs.cn%25252Flatest"

# --- XPaths ---
# 目标元素的XPath路径
CHECKBOX_XPATH = '//*[@id="footWrap"]/div[2]/label/span[3]'
OTHER_LOGIN_METHOD_XPATH = '//*[@id="footWrap"]/div[3]/a[4]/span[1]'
ACCOUNT_LOGIN_TAB_XPATH = '//*[@id="account"]'
EMAIL_INPUT_XPATH = '//*[@id="email"]'
PASSWORD_INPUT_XPATH = '//*[@id="password"]'

def main():
    """主函数，执行自动化流程"""
    
    # --- 1. 设置Chrome选项 (无痕模式) ---
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito") # 启用无痕模式
    chrome_options.add_argument("--start-maximized") # 浏览器窗口最大化

    # --- 2. 初始化WebDriver (已修改) ---
    # 不再需要手动指定chromedriver的路径
    # Selenium Manager会自动处理驱动的下载和匹配
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 设置一个最长等待时间，避免因网速慢导致元素找不到而报错
    wait = WebDriverWait(driver, 10) # 最多等待10秒

    try:
        # --- 3. 打开网页 ---
        print(f"正在打开网页: {URL}")
        driver.get(URL)

        # --- 4. 勾选协议 ---
        print("等待并勾选用户协议...")
        # 等待元素变为“可点击”状态，然后执行点击
        checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, CHECKBOX_XPATH)))
        checkbox.click()
        print("用户协议已勾选。")

        # --- 5. 点击“其他方式登录” ---
        print("点击'其他方式登录'...")
        other_login_method = wait.until(EC.element_to_be_clickable((By.XPATH, OTHER_LOGIN_METHOD_XPATH)))
        other_login_method.click()
        print("'其他方式登录'已点击。")

        # --- 6. 点击“账号密码登录”标签页 ---
        print("切换到'账号密码登录'...")
        account_login_tab = wait.until(EC.element_to_be_clickable((By.XPATH, ACCOUNT_LOGIN_TAB_XPATH)))
        account_login_tab.click()
        print("'账号密码登录'已切换。")

        # --- 7. 输入邮箱和密码 ---
        print("输入邮箱地址...")
        # 等待输入框在页面上“可见”，然后输入内容
        email_input = wait.until(EC.visibility_of_element_located((By.XPATH, EMAIL_INPUT_XPATH)))
        email_input.send_keys("aaa") # 输入邮箱
        print("邮箱输入完成。")

        print("输入密码...")
        # 因为上一步已经确保页面加载完成，这里可以直接查找元素
        password_input = driver.find_element(By.XPATH, PASSWORD_INPUT_XPATH)
        password_input.send_keys("bbb") # 输入密码
        print("密码输入完成。")

        print("\n自动化流程执行完毕！")
        # 如果需要自动点击登录，可以在这里添加代码
        # login_button = wait.until(...)
        # login_button.click()

        # 为了方便观察结果，让浏览器保持打开状态20秒
        print("将在20秒后自动关闭浏览器...")
        time.sleep(20)

    except TimeoutException:
        print("错误：等待元素超时。请检查XPath是否正确或网络是否延迟。")
    except NoSuchElementException as e:
        print(f"错误：找不到指定的元素。请检查XPath是否正确: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")
    finally:
        # --- 8. 确保最后关闭浏览器 ---
        print("关闭浏览器。")
        driver.quit()

# 程序入口
if __name__ == "__main__":
    main()