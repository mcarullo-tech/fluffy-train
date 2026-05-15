import random

locations = [
    "open-plan office",
    "conference room",
    "break room",
    "main corridor",
    "reception area",
    "printer area",
    "server room",
    "kitchenette",
    "desk cluster",
    "stairwell landing"
]

hazards = [
    {
        "focus": "a loose electrical cord crossing a busy walkway",
        "actions": [
            "secured the cord with cable protectors and rerouted it away from the main aisle",
            "moved the cord to a safer route and notified facilities to install a permanent cable management solution"
        ]
    },
    {
        "focus": "a fresh spill on the floor near a shared coffee station",
        "actions": [
            "placed a wet-floor sign and arranged for immediate cleanup",
            "cleaned the spill and alerted housekeeping to prevent a slip hazard"
        ]
    },
    {
        "focus": "a stack of boxes blocking the emergency exit path",
        "actions": [
            "cleared the boxes from the exit route and informed the team about safe storage practices",
            "moved the boxes to a secure area and reported the obstruction to facilities"
        ]
    },
    {
        "focus": "a chair with unstable wheels positioned in a high-traffic corridor",
        "actions": [
            "repositioned the chair away from the walkway and checked that it was on a stable surface",
            "moved the chair to a less crowded area and made sure it could not roll into the path of coworkers"
        ]
    },
    {
        "focus": "a desk lamp cord stretched across a shared workstation",
        "actions": [
            "secured the cord under the desk and adjusted the lamp to reduce trip risk",
            "rerouted the cable neatly and advised the occupant to use a cable organizer"
        ]
    },
    {
        "focus": "an unlocked office door that could allow unauthorized access",
        "actions": [
            "closed and locked the door and notified security about the access concern",
            "ensured the door was secured and reminded the team to keep sensitive areas locked"
        ]
    },
    {
        "focus": "an overflowing trash bin creating clutter near the printer area",
        "actions": [
            "emptied the bin and tidied the surrounding area to maintain a clean workspace",
            "removed the waste and scheduled a follow-up with facilities for more frequent pickup"
        ]
    },
    {
        "focus": "a monitor placed at an awkward height that could cause neck strain",
        "actions": [
            "adjusted the monitor height and suggested using a laptop stand for better posture",
            "repositioned the screen and reminded the user about ergonomic setup guidelines"
        ]
    },
    {
        "focus": "a loose shelf item positioned above a workstation that could fall",
        "actions": [
            "secured the item to the shelf and cleared the area below to prevent injury",
            "moved the item to a safer location and checked the shelving for stability"
        ]
    },
    {
        "focus": "a fire extinguisher that was partially blocked by office furniture",
        "actions": [
            "cleared the obstruction and confirmed the extinguisher was fully accessible",
            "moved the furniture and reported the blockage to the safety team for correction"
        ]
    }
]

templates = [
    "I observed {focus} in the {location}.",
    "I noticed {focus} near the {location}.",
    "I identified {focus} beside the {location}."
]

action_templates = [
    "I {action}.",
    "I {action} and notified facilities to prevent a repeat issue.",
    "I {action} and reported it to the office safety team for follow-up."
]


def generate_observation():
    location = random.choice(locations)
    hazard = random.choice(hazards)

    observation = random.choice(templates).format(location=location, focus=hazard["focus"])
    action = random.choice(action_templates).format(action=random.choice(hazard["actions"]))

    return location, observation, action

if __name__ == "__main__":
    _, observation, action = generate_observation()
    print("Observation:", observation)
    print("Action:", action)