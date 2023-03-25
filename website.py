# carolina estrada rangel
# cestra31@uic.edu
# I hereby attest that I have adhered to the rules for quizzes and projects as well as UIC’s Academic Integrity standards. Signed: [Carolina Estrada Rangel]

from bs4 import BeautifulSoup
import urllib3

import requests
import json 
import re

def scrape():
  # their name has the hyperlink to their personal information about their schedules. 
  http = urllib3.PoolManager() 
  chi_math_url = "https://mscs.uic.edu/people/faculty/"
  requested = http.request('GET', chi_math_url)
  B = BeautifulSoup(requested.data.decode('utf-8'), "html5lib")
  # print(B.prettify()) 
  
  name_info = B.find_all("span", attrs = { "class": "_name"})
  names_list = []
  for name in name_info: 
    n_info = name.find_all('a')[0]
    new_info = n_info.text.strip()
    more = re.sub("\s+",' ',new_info)
    names_list.append(more)
  # print(names_list)
  

  email_info = B.find_all("span", attrs = { "class": "_email"})
  # found the class through the code from the website to narrow down the emails from professors 
  email_list = []
  for email_ in email_info:
    e_info = email_.find_all('a')[0]
    e = e_info['href']
    email_list.append(e)
  # print(email_list)


  time_info = B.find_all("div", attrs = { "class": "_colB"})
  time_list = []
  # the purpose of this list is to get all the personal websites of the professors to then loop over those websites to find the schedule of their classes.
  for time_ in time_info:
    time_info = time_.find_all('a')[0]
    t = time_info['href']
    time_list.append(t)
  # print(time_list)

  t_list = []
  # this list will get all the times from the professors, having nested lists in a big list.
  
  for web in range(len(time_list)):
    

    http = urllib3.PoolManager() 
    web_url = "{}".format(time_list[web])
    # this is where I start looping from every professors personal page on the UIC website.
    requested = http.request('GET', web_url)
    soup = BeautifulSoup(requested.data.decode('utf-8'), "html5lib")

    t_info = soup.find_all("div", attrs = { "class": "u-rich-text"})
    
    counter = 0
    lst = []
    for times_ in t_info:
      t_info = times_.find_all('li')
      for i in t_info:
        counter += 1
        # the lst will take the times into a list and then that list will be appended into the bigger list for the times.
        s = i.text
        spt = s.split()
        for i in spt:
          if len(i) == 17:
            lst.append(i)
            
    t_list.append(lst)
          
    if counter == 1:
      lst.append("no teaching schedule")
      # this will be added to the list if the professors are not teaching this semester so their time will still have something to index over. 


  new_dict = {"name":names_list,"email":email_list,"schedule":t_list}
  with open('uic.json', 'w') as f: 
    json.dump(new_dict, f, indent = 2)

# scrape()

from flask import Flask, render_template, redirect, url_for,request

app = Flask(__name__)

@app.route('/', methods = ["GET","POST"])
def index():
  
  return render_template('index.html')
    
@app.route('/email', methods = ["GET", "POST"])

def email_ad():
  if request.method == "GET":
    return render_template('email.html')
  if request.method =="POST":
    n_em = request.form['n_email']
    return redirect(url_for('name_email', email_ = n_em))

@app.route('/name_email/<email_>')
def name_email(email_):
  """This function looked at the information from the user that they inputted and start to see if it matches with anything in the json file and used indexing to see if the email matches, the indexes align with all the names, emails and schedules so I would just use the index to get the name of the professor the user wanted.
  """
  with open('uic.json') as r:
    file = json.load(r)
    mail = []
    for i in file['email']:
      if email_ in i: 
        f = file['email'].index(i)
        d = file['name'][f]
        mail.append(d)
    final = '  |  '.join(mail)
    # had this to make it look more neat to give the professors name with more space from other names. 

    return final

@app.route('/time', methods = ["GET", "POST"])

def time_sch():
  if request.method == "GET":
    return render_template('time.html')
  if request.method =="POST":
    n_tim = request.form['n_time']
    return redirect(url_for('name_time', time_ = n_tim))
    # same concept as the email function just have to add one more step because its a nested list.


@app.route('/name_time/<time_>')
def name_time(time_):
  with open('uic.json') as r:
    time_file = json.load(r)
    time_prof = []
    # created a list because if there was more than one professor it would only print out one, so list was needed for me.
    for i in time_file['schedule']:
      for lists in i:
        if time_ in lists: 
          schedule = time_file['schedule'].index(i)
          name_sch = time_file['name'][schedule]
          time_prof.append(name_sch)
    result = [*set(time_prof)]
    # didn't want to have multiple repeats of the same name because of their time so I deleted any duplicates.
    new_p = '  |  '.join(result)
    return new_p

@app.route('/info', methods = ["GET","POST"])

def info():

  if request.method == "GET":
    return render_template('info.html')
  if request.methof == "POST":
    return render_template('info.html')
    # had a bit of trouble with because I can click on the page, but I can't go to other pages afterwards, so it's a bit glitchy there but all the links work it's just a bit weird once clicking on this 'About' section so I would say to click on it first to read and then refresh the page.

  
app.run('0.0.0.0', port = 81)
