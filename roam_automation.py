from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dictionary import xpath_dict
from generating_sentences import generate_observation

def load_webpage(driver):
    try:
        iframe = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "iframe"))
        )
        driver.switch_to.frame(iframe)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='panelHeader']"))
        )
        print("Page loaded successfully inside iframe!")
    except Exception as e:
        print("Error loading page:", e)

def click_button(driver, xpath):
    driver.find_element(By.XPATH, xpath).click()

def select_from_dropdown(driver, xpath):
    WebDriverWait(driver, 5).until(
        EC.visibility_of_element_located((By.XPATH, xpath))
    ).click()

def write_in_box(driver, xpath, text):
    driver.find_element(By.XPATH, xpath).send_keys(text)

def submit_observation(location, observation, action):
    """Submit a single generated observation/action pair to the ROAM site."""
    try:
        options = webdriver.EdgeOptions()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        driver = webdriver.Edge(options=options)
        driver.get('https://ipassm/NetForms/#/new/ROAM-Online')

        load_webpage(driver)

        click_button(driver, xpath_dict["contractor"])
        click_button(driver, xpath_dict["home_or_office"])
        select_from_dropdown(driver, "//div[text()='Hatch office']")
        click_button(driver, xpath_dict["working_hours"])
        click_button(driver, xpath_dict["office_location"])
        select_from_dropdown(driver, "//div[text()='100 Sylvan Parkway, Amherst']")
        write_in_box(driver, xpath_dict["exact_location"], location.capitalize())
        click_button(driver, xpath_dict["behavior_or_cond"])
        select_from_dropdown(driver, "//div[text()='Behaviour']")
        click_button(driver, xpath_dict["safe_or_risk"])
        select_from_dropdown(driver, "//div[text()='Safe']")
        write_in_box(driver, xpath_dict["describe_obs"], observation)
        write_in_box(driver, xpath_dict["action_taken"], action)
        click_button(driver, xpath_dict["obs_category"])
        select_from_dropdown(driver, "//div[text()='Access Breach']")
        click_button(driver, xpath_dict["obs_type"])
        select_from_dropdown(driver, "//div[text()='VFL- Office Safety Audit Card, Green Card']")

        driver.find_element(By.ID, xpath_dict["save_obs"]).click()
        return True, "Submitted successfully."
    except Exception as e:
        return False, str(e)
    finally:
        driver.quit()

def run_roam(n, progress_callback=None):
    """
    Runs the ROAM automation n times.
    progress_callback: function to update progress bar in GUI.
    """
    for i in range(n):
        try:
            location, observation, action = generate_observation()
            success, message = submit_observation(location, observation, action)
            if success:
                print(f"Observation {i+1} saved!")
            else:
                print(f"Error during iteration {i+1}: {message}")
        except Exception as e:
            print(f"Error during iteration {i+1}: {e}")
        finally:
            if progress_callback:
                progress_callback(i + 1)
