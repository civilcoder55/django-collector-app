<p align="center">
  <img src="screenshots/logo.svg" alt="Logo" width="200" height="100">

  <h3 align="center">Collector App</h3>

  <p align="center">
      Blog and twitter bot to pull tweets chains into blog post to read/save easily
  </p>
</p>

## Screenshots

<img src="screenshots/3FnDyDJ22N.gif">
<img src="screenshots/2020-09-22_204753.png">
<img src="screenshots/2020-09-22_204856.png">
<img src="screenshots/2020-09-22_205014.png">
<img src="screenshots/2020-09-22_204839.png">

## Usage

1. Clone the repo

   ```sh
   git clone https://github.com/civilcoder55/django-collector-app.git
   ```

2. update env file

   ```sh
   cp .env.example .env
   ```

3. run containers

   ```sh
   docker-compose up -d
   ```

4. access website at
   ```sh
   http://127.0.0.1:8000
   ```

## Features

- pulling tweets chains into blog post.
- authentication system.
- twitter oauth for login and linking account.
- two factor authentication with otp.
- comment, like, dislike posts.
- save post as pdf.
- websocket notification on new collected tweets.
