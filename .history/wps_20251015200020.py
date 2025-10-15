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
# 按照操作顺序定义所有元素的XPath
BTN_1_XPATH = '//*[@id="footWrap"]/div[3]/a[4]/span[1]'
BTN_2_XPATH = '//*[@id="dialog"]/div[2]/div/div[3]/div[2]'
ACCOUNT_TAB_XPATH = '//*[@id="account"]'
EMAIL_INPUT_XPATH = '//*[@id="email"]'
PASSWORD_INPUT_XPATH = '//*[@id="password"]'

def main():
    """主函数，执行自动化流程"""
    
    # 1. 设置Chrome选项 (无痕模式)
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--incognito")      # 启用无痕模式
    chrome_options.add_argument("--start-maximized")  # 浏览器窗口最大化

    # 2. 初始化WebDriver (Selenium自动管理驱动)
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 设置一个最长等待时间，用于等待页面元素加载
    wait = WebDriverWait(driver, 15) # 最多等待15秒

    try:
        # 3. 打开网页
        print(f"正在打开网页: {URL}")
        driver.get(URL)

        # 4. 执行一系列点击和输入操作
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
        
        print("输入邮箱地址...")
        email_input = wait.until(EC.visibility_of_element_located((By.XPATH, EMAIL_INPUT_XPATH)))
        email_input.send_keys("aaa")
        print("邮箱输入完成。")

        print("输入密码...")
        password_input = driver.find_element(By.XPATH, PASSWORD_INPUT_XPATH)
        password_input.send_keys("bbb")
        print("密码输入完成。")

        print("\n自动化流程执行完毕！")
        
        # 为了方便观察结果，让浏览器保持打开状态
        print("将在30秒后自动关闭浏览器...")
        time.sleep(30)

    except TimeoutException:
        print("错误：等待元素超时。请检查XPath是否正确、网页结构是否已改变或网络是否延迟。")
    except NoSuchElementException as e:
        print(f"错误：找不到指定的元素。请检查XPath是否正确: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")
        # 可以在这里增加截图代码，方便调试
        # driver.save_screenshot('error_screenshot.png')
    finally:
        # 5. 确保最后关闭浏览器
        print("关闭浏览器。")
        driver.quit()

# 程序入口
if __name__ == "__main__":
    main()