from selenium.webdriver.common.by import By

PROVIDER_BUTTON = (By.NAME, "provider")
USERNAME_INPUT = (By.CSS_SELECTOR, "#responsive_page_template_content > div.page_content > div:nth-child(1) > div > div > div > div.newlogindialog_FormContainer_3jLIH > div > form > div:nth-child(1) > input")
PASSWORD_INPUT = (By.CSS_SELECTOR, "#responsive_page_template_content > div.page_content > div:nth-child(1) > div > div > div > div.newlogindialog_FormContainer_3jLIH > div > form > div:nth-child(2) > input")
LOGIN_BUTTON = (By.CLASS_NAME, "newlogindialog_SubmitButton_2QgFE")
SECOND_LOGIN_BUTTON = (By.ID, "imageLogin")