import os
import time
import json5
import subprocess
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from PIL import Image, ImageFilter

# 加载配置文件
config_path = "config.json5"
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        CONFIG = json5.load(f)
except Exception as e:
    print(f"❌ 配置文件读取失败: {e}")
    exit(-1)

DRIVER_PATH = "chromedriver.exe"
UMIOCR_PATH = "Umi-OCR_Rapid_v2.1.5/umi-ocr.exe"

def optimize_captcha(image_path, output_path):
    """验证码图片增强处理"""
    img = Image.open(image_path).convert("RGBA")
    bg_width = int(img.width * 1.5)
    bg_height = int(img.height * 1.5)
    background = Image.new("RGBA", (bg_width, bg_height), "white")
    pos = ((bg_width - img.width) // 2, (bg_height - img.height) // 2)
    background.paste(img, pos, img)
    background.resize((bg_width * 2, bg_height * 2), Image.LANCZOS).filter(ImageFilter.SHARPEN).save(output_path)

def recognize_captcha(driver, captcha_element):
    """识别验证码"""
    captcha_path = "captcha.png"
    captcha_element.screenshot(captcha_path)
    print("📸 验证码截图已保存")

    optimize_captcha(captcha_path, "optimized_captcha.png")
    print("🖼️ 验证码优化完成")

    abs_captcha = os.path.abspath("optimized_captcha.png").replace("\\", "/")
    result_path = os.path.join(os.path.dirname(abs_captcha), "captcha_result.txt").replace("\\", "/")

    try:
        # OCR 识别验证码
        cmd = f'powershell -Command "{UMIOCR_PATH} --path {abs_captcha} --output {result_path}"'
        subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)

        if os.path.exists(result_path):
            with open(result_path, "r", encoding='utf-8') as f:
                result_text = f.read().strip()
            # 保留所有字母和数字，不限制位数
            captcha_code = ''.join(filter(str.isalnum, result_text))
            print(f"OCR识别结果: {captcha_code}")
            return captcha_code
        return ""
    except Exception as e:
        print(f"⚠️ 验证码识别失败: {e}")
        return ""

def auto_login_with_captcha():
    """使用验证码登录流程"""
    service = Service(DRIVER_PATH)
    driver = webdriver.Chrome(service=service)
    driver.get(CONFIG.get("loginUrl"))
    wait = WebDriverWait(driver, 10)
    print("🔁 使用验证码登录...")

    try:
        username = CONFIG.get("username")
        password = CONFIG.get("password")
        userXpath = CONFIG.get("usernameXpath")
        pwdXpath = CONFIG.get("passwordXpath")
        captchaInputXpath = CONFIG.get("captchaInputXpath")
        captchaImageXpath = CONFIG.get("captchaImageXpath")
        loginBtnXpath = CONFIG.get("loginBtnXpath")

        username_input = wait.until(EC.presence_of_element_located((By.XPATH, userXpath)))
        password_input = wait.until(EC.presence_of_element_located((By.XPATH, pwdXpath)))
        captcha_input = wait.until(EC.presence_of_element_located((By.XPATH, captchaInputXpath)))
        captcha_img = wait.until(EC.presence_of_element_located((By.XPATH, captchaImageXpath)))
        login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, loginBtnXpath)))

        username_input.send_keys(username)
        password_input.send_keys(password)

        for attempt in range(5):
            captcha_code = recognize_captcha(driver, captcha_img)
            if captcha_code:
                captcha_input.clear()
                captcha_input.send_keys(captcha_code)
                login_btn.click()
                time.sleep(3)
                if "PacketRetrieval" in driver.current_url:
                    print("✅ 验证码登录成功！")
                    input("按回车键退出浏览器...")
                    driver.quit()
                    return
            print(f"⚠️ 第 {attempt + 1} 次验证码识别失败，刷新中...")
            captcha_img.click()
            time.sleep(1.5)
        print("❌ 验证码识别失败5次以上，退出")
        driver.quit()

    except Exception as e:
        print(f"❌ 登录异常: {e}")
        driver.save_screenshot("login_error.png")
        driver.quit()

# 主程序运行入口
if __name__ == "__main__":
    use_captcha = CONFIG.get("captchaInputXpath") and CONFIG.get("captchaImageXpath")

    if use_captcha:
        auto_login_with_captcha()
    else:
        print("🔁 配置中无验证码字段，启动 new1.py ...")
        try:
            # 直接调用 new1.py，使用相同配置
            subprocess.run(["myenv\Scripts\python.exe", "new1.py"], check=True)
        except Exception as e:
            print(f"❌ new1.py 执行失败: {e}")