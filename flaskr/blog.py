from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort
from datetime import timezone, datetime, timedelta
import pytz
from flaskr.auth import login_required
from flaskr.db import get_db



bp = Blueprint("blog", __name__)

@bp.route("/")
def index():
    return render_template("blog/index.html")


@bp.route("/<int:offset>/posts", methods=("GET", "POST"))
@login_required
def posts(offset):
    """Show all the posts, most recent first."""
    # print(offset)
    search = False
    q = request.args.get('q')
    if q:
        search = True
    db = get_db()
    count=len(db.execute("SELECT * FROM post").fetchall())


    posts = db.execute(
        "SELECT p.id, title, body, created, author_id, img_url, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
        " LIMIT 50"
        " OFFSET ?",(offset,)
    ).fetchall()
   
    return render_template("blog/posts.html", posts=posts,count=count)

@bp.route("/<int:id>/<int:dir>/post", methods=("GET", "POST"))
@login_required
def post(id,dir):
    """Show the post details"""
    db = get_db()
    count=len(db.execute("SELECT * FROM post").fetchall())
   
  
    post1 = db.execute(
        "SELECT p.id, title, body, created, img_url, author_id, username"
        " FROM post p JOIN user u ON p.author_id = u.id"
        " WHERE p.id = ? ", 
        (id,),
        ).fetchone()
    
    while post1 is None: #if cant find the post id(maybe it's deleted or out of range)
        if id>count or id<1: #if it is out of range:
            return render_template("blog/nopost.html")
        #if it is deleted, loop until find next one in the direction
        elif dir==2: #2: go back 
            id=id-1
        elif dir==1:#1: go next
            id=id+1
        post1 = db.execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ? ", 
            (id,),
            ).fetchone()    


    # commentcount=len(db.execute("SELECT * FROM post").fetchall())
    
    comments = db.execute(
        "SELECT c.id, c.post_id,c.body, c.created, c.author_id, c.retweet_id,u.username"
        " FROM comments c "
        " LEFT JOIN post p ON c.post_id = p.id"
        " LEFT JOIN user u ON c.author_id = u.id"
        " WHERE c.post_id = ? ORDER BY c.created DESC", 
        (id,),
        ).fetchall()
    
    return render_template("blog/post.html", post=post1,comments=comments)

@bp.route("/<int:id>/<int:user>/comment", methods=("GET", "POST"))
@login_required
def comment(id,user):
    #get current time stamp and convert to new york time
    time=datetime.now(pytz.timezone('America/New_York'))
    """Create a new comment for the current user."""
    if request.method == "POST":
        body = request.form["commentbody"]
        error = None
    if error is not None:
        flash(error)
    if not body:
            error = "context is required."
    else:
        db = get_db()
        db.execute(
            "INSERT INTO comments (post_id, body, author_id,created) VALUES (?, ?, ?,?)",
            (id, body, user,time),
        )
        db.commit()
        
    return  redirect(url_for("blog.post",id=id,dir=0))

@bp.route("/<int:id>/<int:user>/<int:cid>/commentupdate", methods=("GET", "POST"))
@login_required
def commentupdate(id,user,cid):
    #get current time stamp and convert to new york time
    time=datetime.now(pytz.timezone('America/New_York'))
    """update the comment."""
    if request.method == "POST":
        body = request.form["commentbodyup"]
        error = None
    if error is not None:
        flash(error)
    if not body:
            error = "context is required."
    else:
        db = get_db()
        db.execute(
            "UPDATE comments SET body=?, created=? WHERE id=? AND post_id=? ",
            (body,time, cid,id),
        )
        db.commit()
    return  redirect(url_for("blog.post",id=id,dir=0))




@bp.route("/<int:id>/<int:cid>/commentdelete", methods=("POST",))
@login_required
def commentdelete(id,cid):
    """Delete a comment.

    """
   
    db = get_db()
    db.execute("DELETE FROM comments WHERE id = ?", (cid,))
    # print("DELETE FROM comments WHERE id = ?", (cid,))
    db.commit()
    return redirect(url_for("blog.post",id=id,dir=0))

@bp.route("/<int:id>/<int:user>/<int:rid>/commentretweet", methods=("GET", "POST"))
@login_required
def commentretweet(id,user,rid):
    #get current time stamp and convert to new york time
    time=datetime.now(pytz.timezone('America/New_York'))
    """Create a new comment for the current user."""
    if request.method == "POST":
        body = request.form["commentboxretweet"]
        error = None
    if error is not None:
        flash(error)
    if not body:
            error = "context is required."
    else:
        db = get_db()
        db.execute(
            "INSERT INTO comments (post_id, body, author_id,created,retweet_id) VALUES (?, ?, ?,?,?)",
            (id, body, user,time,rid),
        )
        db.commit()
     
    return  redirect(url_for("blog.post",id=id,dir=0))




def get_post(id, check_author=True):
    """Get a post and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of post to get
    :param check_author: require the current user to be the author
    :return: the post with author information
    :raise 404: if a post with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    post = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, img_url, author_id, username"
            " FROM post p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if post is None:
        abort(404, f"Post id {id} doesn't exist.")

    if check_author and post["author_id"] != g.user["id"]:
        abort(403)

    return post


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new post for the current user."""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        img_url = request.form["img_url"]
        error = None
         #get current time stamp and convert to new york time
        time=datetime.now(pytz.timezone('America/New_York'))
        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO post (title, body, img_url, author_id,created) VALUES (?, ?, ?, ?,?)",
                (title, body, img_url, g.user["id"],time),
            )
            db.commit()
            return redirect(url_for("blog.posts",id=id,dir=0,offset=0))

    return render_template("blog/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a post if the current user is the author."""
    post = get_post(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        img_url = request.form["img_url"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE post SET title = ?, body = ?, img_url=? WHERE id = ?", (title, body,img_url, id)
            )
            db.commit()
            return redirect(url_for("blog.post",id=id,dir=0))

    return render_template("blog/update.html", post=post)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a post.
    Ensures that the post exists and that the logged in user is the
    author of the post.
    """
    get_post(id)
    db = get_db()
    db.execute("DELETE FROM post WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("blog.posts",offset=0))

# @bp.route("/<int:id>/likes",methods="GET")
# @login_required
# def likepost(id):
#     db=get_db()
#     db.execute("INSERT INTO likes WHERE post_id= ?",(id,))
#     db.commit()
#     return redirect(url_for("blog.posts",offset=0))

@bp.route("/search", methods=("POST","GET"))
@login_required
def search():
    
    """return the result of list of users and posts
    """
    msg={'post':"",'users':""}
    if request.method == "POST":
        body=request.form["searchbody"]
        text = "%"+request.form["searchbody"].lower()+"%"

        error = None
        if error is not None:
            flash(error)
        if not body:
            error = "context is required."
        else:
            db = get_db()
  
            posts = db.execute(
                "SELECT p.id, title, body, created, img_url, author_id, username"
                " FROM post p JOIN user u ON p.author_id = u.id"
                " WHERE title LIKE ? ", 
                (text,),
                ).fetchall()
            users = db.execute(
                "SELECT *"
                " FROM user"
                " WHERE username LIKE ?", 
                (text,),
                ).fetchall()
        
            if len(posts) ==0: #if cant find the post id(maybe it's deleted or out of range)
                msg['posts']="No result from posts"
            if len(users) ==0:
                msg['users']="No result from users"
            return render_template("blog/result.html",posts=posts, users=users,word=body,msg=msg)
    return render_template("blog/search.html")


@bp.route("/<int:id>/profile", methods=("POST","GET"))
@login_required
def profile(id):
    db = get_db()
    msg=""

    user = db.execute(
                "SELECT *"
                " FROM user "
                " WHERE user.id =?", 
                (id,),
                ).fetchone()
    posts=db.execute(
                 "SELECT p.id, title, body, created, img_url, author_id, username"
                " FROM post p JOIN user u ON p.author_id = u.id"
                " WHERE u.id=? ", 
                (id,),
                ).fetchall()
    if len(user)==0:
        msg="no such a user, please try again."
    else:
        return render_template("blog/profile.html",user=user,posts=posts,msg=msg)