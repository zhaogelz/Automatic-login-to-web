import json5 
import os 
import subprocess 
import time 
from PIL import Image, ImageFilter, ImageOps 
from selenium import webdriver 
from selenium.webdriver.common.by  import By 
from selenium.webdriver.support.ui  import WebDriverWait 
from selenium.webdriver.support  import expected_conditions as EC 
from selenium.webdriver.chrome.service  import Service 
 
 
def load_config(): 
    """加载配置文件（JSON5格式）""" 
    return json5.load(open('config.json5',  'r', encoding='utf-8')) 
 
 
def optimize_captcha(image_path, output_path, scale_factor=2, bg_ratio=0.5): 
    """优化验证码图片：调整大小、增加清晰度和添加白色背景""" 
    img = Image.open(image_path).convert("RGBA")  
    bg_width = int(img.width  * (1 + bg_ratio)) 
    bg_height = int(img.height  * (1 + bg_ratio)) 
    background = Image.new("RGBA",  (bg_width, bg_height), "white") 
    position = ((bg_width - img.width)  // 2, (bg_height - img.height)  // 2) 
    background.paste(img,  position, img) 
    new_size = (int(bg_width * scale_factor), int(bg_height * scale_factor)) 
    resized_img = background.resize(new_size,  Image.LANCZOS) 
    sharpened_img = resized_img.filter(ImageFilter.SHARPEN)  
    sharpened_img.convert("RGB").save(output_path,  "PNG", quality=95) 
 
 
def recognize_captcha(driver, captcha_element, config): 
    """使用Umi-OCR识别验证码""" 
    captcha_path = 'captcha.png'  
    captcha_element.screenshot(captcha_path)  
    optimized_captcha_path = "optimized_captcha.png"  
    optimize_captcha(captcha_path, optimized_captcha_path) 
    absolute_optimized_captcha_path = os.path.abspath(optimized_captcha_path).replace("\\",  "/") 
    captcha_result_path = os.path.join(os.path.dirname(absolute_optimized_captcha_path),  "captcha_result.txt")  
 
    try: 
        powershell_command = f'powershell -Command "{config["UMIOCR_PATH"]} --path {absolute_optimized_captcha_path} --output {captcha_result_path}"' 
        subprocess.run(powershell_command,  shell=True, capture_output=True, text=True, check=True) 
        with open(captcha_result_path, 'r', encoding='utf-8') as file: 
            return file.read().strip()  
    except Exception as e: 
        print(f"验证码识别异常: {str(e)}") 
        return "" 
 
 
def auto_login(): 
    config = load_config() 
    service = Service(config["DRIVER_PATH"]) 
# 添加防止自动关闭的配置 
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach",  True)  # 关键修改[8]()
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # driver = webdriver.Chrome(service=service) 
    driver.get(config["LOGIN_URL"])  
    wait = WebDriverWait(driver, 10) 
 
    try: 
        username_input = wait.until(EC.presence_of_element_located((By.XPATH,  config["XPATH_USERNAME"]))) 
        password_input = wait.until(EC.presence_of_element_located((By.XPATH,  config["XPATH_PASSWORD"]))) 
        login_btn = wait.until(EC.element_to_be_clickable((By.XPATH,  config["XPATH_LOGIN_BUTTON"]))) 
        username_input.send_keys(config["USERNAME"])  
        password_input.send_keys(config["PASSWORD"])  
 
        # 关键修改：检测验证码配置是否存在 
        has_captcha = True 
        captcha_input = None 
        captcha_img = None 
 
        # 检查是否配置了验证码输入框路径 
        if "XPATH_CAPTCHA_INPUT" in config and config["XPATH_CAPTCHA_INPUT"]: 
            try: 
                captcha_input = wait.until(EC.presence_of_element_located((By.XPATH,  config["XPATH_CAPTCHA_INPUT"]))) 
                captcha_img = wait.until(EC.presence_of_element_located((By.XPATH,  config["XPATH_CAPTCHA_IMAGE"]))) 
            except: 
                has_captcha = False 
        else: 
            has_captcha = False  # 无验证码配置 
 
        if has_captcha: 
            for attempt in range(config["MAX_RETRIES"]): 
                captcha_code = recognize_captcha(driver, captcha_img, config) 
                if captcha_code: 
                    captcha_input.clear()  
                    captcha_input.send_keys(captcha_code)  
                    login_btn.click()  
                    time.sleep(3)  
                    print("✅ 验证码输入成功，尝试登录...") 
                    return driver 
                print(f"⚠️ 验证码识别失败，重试中... (尝试 #{attempt + 1})") 
                captcha_img.click()  
                time.sleep(1)  
            raise Exception("❌ 验证码识别失败超过最大重试次数") 
        else: 
            # 无验证码直接登录 
            login_btn.click()  
            time.sleep(3)  
            print("✅ 无验证码，尝试登录...") 
            return driver 
 
    except Exception as e: 
        driver.save_screenshot("login_error.png")  
        print(f"登录失败: {str(e)}") 
        return None 
    finally: 
        try: 
            subprocess.run("taskkill   /F /IM umi-ocr.exe",  shell=True) 
        except: 
            pass 
 
 
# 执行登录 
if __name__ == "__main__": 
    browser = auto_login() 
    if browser: 
        print("当前URL:", browser.current_url)  
    # 去掉退出浏览器的代码 
    # browser.quit()  
 