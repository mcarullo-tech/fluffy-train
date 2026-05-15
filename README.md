# Project Overview

At my company, one of the performance metrics involves logging weekly safety observations—called **ROAM Observations**. Employees submit these through a simple web form, describing any safety concerns they noticed and the actions taken to address them.

The process was repetitive and time‑consuming, so I built a tool to automate it.

---

## How It’s Made

### Tech Stack: **Python**, **Tkinter**, **Selenium WebDriver**

### How It Works
The program fills out ROAM observations exactly as a human would:

- Loads the ROAM web form using Selenium  
- Generates contextual safety observations for an office environment  
  - Example: “I observed a loose electrical cord crossing a busy walkway in the printer area.”
  - Uses structured hazard templates and plausible office locations to keep entries realistic  
- Generates matching corrective actions that are appropriate for each observation  
- Provides a web interface where the user can start/stop periodic generation  
- Supports demo mode (generate only) and submit mode (post to ROAM)  
- Displays generated observation/action entries and timestamps in the browser

---

## Outcome

My company awards a $20 gift card each quarter to the person who logs the most ROAM observations. I won twice.

Eventually, I was asked to retire the tool for “undermining the safety intent” of the initiative - but it was a fun project and a great exercise in automation, UI design, and creative text generation.
