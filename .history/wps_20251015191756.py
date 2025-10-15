import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# --- 配置 ---
# !!! 重要: 请将此路径替换为你自己下载的 chromedriver.exe 的实际路径
CHROMEDRIVER_PATH = r'chromedriver.exe' 
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

    # --- 2. 初始化WebDriver ---
    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 设置一个最长等待时间
    wait = WebDriverWait(driver, 10) # 最多等待10秒

    try:
        # --- 3. 打开网页 ---
        print(f"正在打开网页: {URL}")
        driver.get(URL)

        # --- 4. 勾选协议 ---
        print("等待并勾选用户协议...")
        # 等待元素可被点击，然后点击
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
        # 等待输入框可见
        email_input = wait.until(EC.visibility_of_element_located((By.XPATH, EMAIL_INPUT_XPATH)))
        email_input.send_keys("aaa") # 输入邮箱
        print("邮箱输入完成。")

        print("输入密码...")
        password_input = driver.find_element(By.XPATH, PASSWORD_INPUT_XPATH)
        password_input.send_keys("bbb") # 输入密码
        print("密码输入完成。")

        print("\n自动化流程执行完毕！")
        # 脚本执行完毕后，可以根据需要添加登录按钮的点击事件
        # login_button_xpath = '...' # 替换为登录按钮的XPATH
        # login_button = wait.until(EC.element_to_be_clickable((By.XPATH, login_button_xpath)))
        # login_button.click()

        # 为了方便观察，让浏览器保持打开状态20秒
        time.sleep(20)

    except TimeoutException:
        print("错误：等待元素超时，请检查XPath是否正确或网络是否延迟。")
    except NoSuchElementException as e:
        print(f"错误：找不到元素，请检查XPath是否正确: {e}")
    except Exception as e:
        print(f"发生未知错误: {e}")
    finally:
        # --- 8. 关闭浏览器 ---
        print("关闭浏览器。")
        driver.quit()

if __name__ == "__main__":
    main()