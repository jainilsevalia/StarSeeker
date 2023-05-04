from user.models import State, City
import json

with open('static/data/state_city.json', 'r') as f:
    data = json.load(f)

State.objects.all().delete()
for i in data:
    state = State.objects.create(name=i.strip())
    for j in data[i]:
        city = City.objects.create(state=state,name=j.strip())
