import json5  # 新增
from selenium import webdriver
from selenium.webdriver.common.by  import By
from selenium.webdriver.support.ui  import WebDriverWait 
from selenium.webdriver.support  import expected_conditions as EC 
from selenium.common.exceptions  import TimeoutException 
 
# 1. 读取配置文件 
def read_config():
    try:
        with open('config.json5',  'r', encoding='utf-8') as f:
            config = json5.load(f)  # 修改为json5.load
        return config
    except FileNotFoundError:
        print("错误：未找到config.json5 文件")
        exit(1)
    except json.JSONDecodeError:
        print("错误：配置文件格式不正确")
        exit(1)
 
# 2. 自动登录函数 
def auto_login(config):
    # 初始化Chrome浏览器 
    driver = webdriver.Chrome()
    #driver.maximize_window()   # 最大化窗口 
    
    try:
        # 打开登录页面 
        driver.get(config["loginUrl"]) 
        print(f"已访问登录页面: {config['loginUrl']}")
        
        # 使用显式等待确保元素加载完成 
        wait = WebDriverWait(driver, 10)
        
        # 输入用户名
        username_field = wait.until( 
            EC.presence_of_element_located((By.XPATH,  config["usernameXpath"]))
        )
        username_field.send_keys(config["username"]) 
        print("用户名已输入")
        
        # 输入密码 
        password_field = wait.until( 
            EC.presence_of_element_located((By.XPATH,  config["passwordXpath"]))
        )
        password_field.send_keys(config["password"]) 
        print("密码已输入")
        
        # 尝试点击登录按钮
        # 使用多种XPath尝试定位登录按钮
        login_btn_xpath_tries = [
            # 推荐优先方式：不区分大小写的文本匹配
            "//button[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'log in')]",
            "//button[contains(text(), '登录')]",
            "//button[.//text()='Log in' or .//text()='登录']",  # 同时匹配按钮内外文本
            "//form//button[contains(@class, 'btn')]",           # 包含 btn 相关的类
            "//form//button[@type='submit'or @type='button']",                   # 提交类型按钮
            # 兜底方式：使用配置中的原始绝对路径
            config["loginBtnXpath"]
        ]

        login_button_found = False
        for xpath in login_btn_xpath_tries:
            try:
                login_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                print(f"使用以下XPath定位到登录按钮:\n{xpath}")
                login_button.click()
                print("登录按钮已点击")
                login_button_found = True
                break
            except TimeoutException:
                print(f"XPath 未找到或超时:\n{xpath} | 正在尝试下一个...")
        
        if not login_button_found:
            print("❌ 无法点击登录按钮，请手动检查页面源码")
            print("当前页面HTML：\n", driver.page_source)
            exit(1)

        
        # 添加登录成功验证（根据实际需求修改）
        wait.until(EC.url_changes(config["loginUrl"])) 
        print("登录成功！当前URL:", driver.current_url) 
        
        # 保持浏览器打开（实际使用时可以移除）
        input("按Enter键关闭浏览器...")
        
    except TimeoutException:
        print("错误：页面元素加载超时，请检查XPath路径")
    except Exception as e:
        print(f"登录过程中发生错误: {str(e)}")
    finally:
        driver.quit() 
 
# 主程序
if __name__ == "__main__":
    config = read_config()
    print("配置文件读取成功，开始自动登录...")
    auto_login(config)