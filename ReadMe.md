## 1
User management is under accounts where you can registration ,login,
CustomUserProject is the main application I didn't name it properly in the start since I didnt know where the project is heading
alot of the code are a bit junk it may need some cleaning specially script.py another dev did it and i didnt want to change it since in quite simple terms it works
payment is responsable for the user payment but the model is preaty much useless right now you can use it if you need to scale up the payment
we don't have actually websockets due to the timing my solution to get a file checker for the loading scenes
as to run it use sqlite3 to make it faster but the mysql is commented you can remove the comment if you want someother dev used phpmyadmin don't know his reasoning but you can you use whatever
## 2
how to run install the requirement also ffmpeg has some security conf you might need to change since it wont allow video to be edited
I was intending to make a dockerfile but was busy to do it with uni

python3 manage.py migrate
python3 manage.py runserver


the core value of the project is user can upload a video and edited it we make 2 video 1 used for later and second is watermaked 
the user upload are found in folder tmp / userid
this project is bruteforced with plain html css js expect to take a while when you change the front to add stuff
## 3
you need to setup your plan in stripe and fill them out as i did in the setting.py to make the payment works
provide the price,credits to be allowed ....