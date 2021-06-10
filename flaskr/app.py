import os

from flask import Flask


"""Create and configure an instance of the Flask application."""
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    # a default secret that should be overridden by instance config
    SECRET_KEY="dev",
    # store the database in the instance folder
    DATABASE=os.path.join(app.instance_path, "flaskr.sqlite"),
)



# register the database commands
from flaskr import db
db.init_app(app)

# apply the blueprints to the app
from flaskr import auth, blog
# from flaskr import chat

app.register_blueprint(auth.bp)
app.register_blueprint(blog.bp)
# app.register_blueprint(chat.bp)


# make url_for('index') == url_for('blog.index')
# in another app, you might define a separate main index here with
# app.route, while giving the blog blueprint a url_prefix, but for
# the tutorial the blog will be the main index
app.add_url_rule("/", endpoint="index")




if __name__ == '__main__':
    app.run(debug=True) 