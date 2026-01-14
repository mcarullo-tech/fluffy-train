# Project Overview

At my company, one of the performance metrics involves logging weekly safety observations—called **ROAM Observations**. Employees submit these through a simple web form, describing any safety concerns they noticed and the actions taken to address them.

The process was repetitive and time‑consuming, so I built a tool to automate it.

---

## How It’s Made

### Tech Stack
**Python**, **Tkinter**, **Selenium WebDriver**

### How It Works
The program fills out ROAM observations exactly as a human would:

- Loads the ROAM web form using Selenium  
- Generates randomized ad‑lib style safety observations  
  - Example: “I observed a/an *[noun]* *[verb]*‑ing by the *[location]*.”
  - Nouns, verbs, and locations are pulled from predefined lists to create many unique combinations  
- Generates corresponding “actions taken” in the same style  
- Uses a Tkinter GUI where the user selects how many observations to submit  
- Displays progress through a simple progress bar

---

## Outcome

My company awards a $20 gift card each quarter to the person who logs the most ROAM observations. I won twice.

Eventually, I was asked to retire the tool for “undermining the safety intent” of the initiative - but it was a fun project and a great exercise in automation, UI design, and creative text generation.
