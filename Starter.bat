call env\Scripts\activate
flask run
timeout /t 2
cmd /c start http://127.0.0.1:5000/
