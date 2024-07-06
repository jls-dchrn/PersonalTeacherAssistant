# PersonalTeacherAssistant
Machine Intelligence Project


## Server Setup

```pip install django```

```
git clone https://github.com/jls-dchrn/PersonalTeacherAssistant.git
```
make the .env file under ~/PersonalTeacherAssistant/ and write the SECRET_KEY into the file
```
cd ~/PersonalTeacherAssistant/project
python manage.py makemigrations
python manage.py migrate
```
runserver command  
```
python manage.py runserver
```