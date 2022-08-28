# Forums by Rainee
#### Video Demo:  <URL HERE>
#### Description:

   My name is Violet (Rainee) and my CS50 Final Project is a website called Forums. As it's name suggests, it's a simple Forum where the user can create a thread,
 reply to other people's thread, and even upload a profile picture. It's designed with html and CSS while using python with the Flask framework for its backend. 

   The user begins on a landing page with the options to register or login if the user has an existing account. As it's backend is Flask, it has sepate routes for each
page. The routes for every other page, besides the landing, register, and login pages, is wrapped by a login_required function which would require the user to be logined in order to access it. If the user is not logined it will redirect the user to the landing page. It detects if the user is logged in or not by cookies which is set when the user goes to the login page and logs in. So as a new user, they should first register an account which will store the newly created account information into SQL database if it passes all the backend validation. Then they can login and gain access to the main parts of the Forum.

   The main part of the Forum includes the main home page which shows all of the threads you and other people have posted. Since it's a small project with few or none 
amount of people actually posting on it, I decided to not include any subthreads to keep it simple. It will be a very general Forum without any specific topics and the
user can post whatever they wish to. So right now, the database has 2 tables, one for the different threads, and another one for the different posts which references the specfic thread it's linked to. I imagine that if I wish to extend the forum to include specific subtopics in the future, one way I can do it is simply extending the pair of database tables of thread and posts and add a pair for each subtopic.

   Since each thread has a specific thread ID within the database, clicking on any specific thread title will take the user to a route with a specific corresponding 
thread ID. It is then passed to the backend which lets Flask handle variable routes. Flask will then render the corresponding thread by passing back all the relevant
information for that thread based on the given ID.

   Creating and replying to specific threads is simply taking the information and passing it to the backend which then stores it into a database. The replies will 
go into the relevant table for replies. And the threads will go into the relevant table for threads.

 Uploading a profile picture is simply storing the url of the image into the database. The image is uploaded to a separate CDN for storage. The project uses Imagekitio
for this.

