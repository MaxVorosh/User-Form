from flask import Flask
from data import db_session
from data.User import User
from data.Jobs import Jobs
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, BooleanField, DateTimeField
from wtforms.validators import DataRequired
from wtforms.fields.html5 import EmailField
from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_required, logout_user, login_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_session.global_init('db/mars_explorer.db')
    session = db_session.create_session()
    return session.query(User).get(user_id)


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Ваше имя', validators=[DataRequired()])
    surname = StringField('Ваша фамилия', validators=[DataRequired()])
    age = IntegerField('Ваш возраст', validators=[DataRequired()])
    position = StringField('Ваша должность', validators=[DataRequired()])
    speciality = StringField('Ваша проффессия', validators=[DataRequired()])
    address = StringField('Ваш адрес', validators=[DataRequired()])
    submit = SubmitField('Войти')


class LoginForm(FlaskForm):
    email = StringField('Электронная почта астронавта', validators=[DataRequired()])
    password = PasswordField('Пароль астронавта', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class AddJobForm(FlaskForm):
    team_lead = StringField('Id руководителя', validators=[DataRequired()])
    job = StringField('Суть работы', validators=[DataRequired()])
    size = IntegerField('Длительность работы', validators=[DataRequired()])
    collaborators = StringField('Перечислите id астронавтов, выполняющих эту работу через запятую',
                                validators=[DataRequired()])
    start = DateTimeField('Время начала работы', validators=[DataRequired()])
    stop = DateTimeField('Время окончания работы', validators=[DataRequired()])
    finish = BooleanField('Работа завершена?')
    submit = SubmitField('Добавить')


@app.route('/')
def main_page():
    db_session.global_init('db/mars_explorer.db')
    session = db_session.create_session()
    data = session.query(Jobs).all()
    return render_template('main.html', title='Главная страница', data=data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    db_session.global_init('db/mars_explorer.db')
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login_1.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login_1.html', title='Авторизация', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    db_session.global_init('db/mars_explorer.db')
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            age=form.age.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data,
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/addjob', methods=['GET', 'POST'])
@login_required
def addjob():
    db_session.global_init('db/mars_explorer.db')
    form = AddJobForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        job = Jobs(team_leader=form.team_lead.data, job=form.job.data, work_size=form.size.data,
                   collaborators=form.collaborators.data, start_date=form.start.data, end_date=form.stop.data,
                   is_finished=form.finish.data)
        current_user.jobs.append(job)
        session.merge(current_user)
        session.commit()
        return redirect('/')
    return render_template('AddJob.html', title='Добавление работы', form=form)


if __name__ == '__main__':
    app.run()
