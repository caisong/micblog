from app import app, db, lm
from flask import (render_template,flash,redirect, session, url_for, request, g)
from flask.ext.login import (login_user, logout_user, current_user, login_required)
from forms import LoginForm
from models import User, ROLE_USER, ROLE_ADMIN

@app.route('/')
@app.route('/index')
def index():
    user = 'Man'
    post = [
            {'author':{'nickname':'John'},
             'body':'Beautiful day in Portland'
            },
            {
                'author':{'nickname':'Susan'},
                'body':'The Avengers movie was so cool!'
            }
            ]
    return render_template('index.html', title = 'Home', user = user, posts = post)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        return redirect('index')

    form = LoginForm()
    if form.validate_on_submit():
        user = User.login_check(request.form.get('user_name'))
        if user:
            login_user(user)
            flash('Your Name:' + request.form.get('user_name'))
            flash('remember_me ?' + str(request.form.get('remember_me')))
            return redirect('/index')
        return render_template('login.html',title = 'Sign In', form = form)

@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/user/<int:user_id>', methods=['POST','GET'])
@login_required
def users(user_id):
    form  = AboutMeForm()
    user = User.query.filter(User.id== user_id).first()
    if not user:
        flash('The user is not exist.')
        redirect('/index')
    blogs = user.posts.all()

    return render_template('user.thml',form = form, user=user, blogs= blogs)

@app.route('/publish/<int:user_id>', methods=['POST', 'GET'])
@login_required
def publish(user_id):
    form = PublishBlogForm()
    posts = post()
    if form.validate_on_submit():
        blog_body = request.form.get('body')
        if not len(strip(blog_body)):
            flash('The content is necessray!')
            return redirect(url_for('publish',user_id=user_id))
        posts.body = blog_body
        posts.timestamp = datatime.datetime.now()
        posts.user_id = user_id

        try:
            db.session.add(posts)
            db.session.commit()
        except:
            flash('Database error!')
            return redirect(url_for('publish',user_id = user_id))
        
        flash('Publish Successful!')
        return redirect(url_for('publish', user_id = user_id))

    return render_template('publish.html',form=form)

@app.route('/user/about-me/<int:user_id>', methods=['POST','GET'])
@login_required
def about_me(user_id):
    user = User.query.filter(User.id == user_id).first()
    if request.method == 'POST':
        content = request.form.get('describe')
        if len(content) and len(content)<=140:
            user.about_me = content
            
            try:
                db.session.add(user)
                db.session.commit()
            except:
                flash('Database error!')
                return redirect(url_for('users', user_id=user_id))
    else:
        flash('Sorry, May be your data have some error.')
    return redirect(url_for('users',user_id=user_id))

@app.route('/user/<int:user_id>', defaults={'page':1}, methods = ['POST','GET'])
@app.route('/user/<int:user_id>/page/<int:page>', methods=['GET','POST'])
@login_required
def users(user_id, page):
    form  = AboutMeForm()
    if user_id != current_user.id:
        flash('Sorry, you can only view your profile!', 'error')
        return redirect('/index')

   #blogs = user.posts.paginate(page, PER_PAGE, Flase).items

    pagination = Post.query.filter_by(user_id = current_user.id).order_by(
            db.desc(Post.timestamp)).paginate(page, PER_PAGE, False)

    return render_template('user.html',form=form,pagination=pagination)

@app.route('/sign_up')
def sign_up():
    return redirect(url_for('/index'))
