import json


'''
function to return statefullname
ex: sc -> returns South Carolina
'''
def state_full_name(state_abbr):
    with open('state_abbrevation.json','r') as f:
        state_data=json.load(f)
    state_abbr=state_abbr.lower()
    if state_abbr in state_data:
        return state_data[state_abbr]
    else:
        return None
