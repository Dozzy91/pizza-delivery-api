# This configurtion or for gunicorn to be able to run the app automatically

from api import create_app
from api.config.config import config_dict

app = create_app(config=config_dict['prod'])

if __name__=="__main__":
    app.run()
