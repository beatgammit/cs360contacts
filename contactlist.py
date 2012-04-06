import cgi
import datetime


from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util


# providers that we support
providers = {
  'Google'   : 'www.google.com/accounts/o8/id', # shorter alternative: "Gmail.com"
  'Yahoo'    : 'yahoo.com',
  'MySpace'  : 'myspace.com',
  'AOL'      : 'aol.com',
  'MyOpenID' : 'myopenid.com'
# add more here
}

# just use google for this example
provider = providers['Google']

main_template = '''\
<html>
<link rel='stylesheet' type='text/css' href='/css/style.css'>
<body>
  <div class='wrapper'>
    <h1>Contact List Manager</h1>

    <a href='%(login)s'>Log in with your Google Account</a>
    <br />
    <a href='/public/contacts'>Check out some public contacts</a>
  </div>
</body>
</html>''' % {'login' : users.create_login_url(federated_identity=provider)}


contact_page_template = '''\
<html>
<head>
<link rel='stylesheet' type='text/css' href='/css/style.css'>
<script type='text/javascript' src='/js/pakmanaged.js'></script>
</head>
<body>
<div class='wrapper'>
<h1>%(title)s</h1>

<div class='contact-list'>
%(from_db)s
</div>
%(add_contact)s
</div>
</body>
</html>\
'''


add_contact_form = '''\
<button id='show-add-contact-form'>Add Contact</button>
<div class='add-contact-form hidden'>
<div>
<form method='POST' action='/user/contacts'>
<label>Name:</label>
<br />
<input type='text' name='name' size='40'/>
<br />
<label>Email:</label>
<br />
<input type='text' name='email' size='40'/>
<br />
<label>Phone:</label>
<br />
<input type='text' name='phone' size='40'/>
<br />
<label>Details:</label>
<br />
<textarea name='details' rows='5' cols='40'></textarea>
<br />
<label>Private:</label><input type='checkbox' name='private' />
<br />
<input type='submit' />
</form>
</div>
</div>\
'''


contact_template = '''\
<div class='contact' data-id='%(id)d'>
  <div>
    <label class='prop-name'>Name:</label><span class='prop'>%(name)s</span>
  </div>
  <div>
    <label class='prop-name'>Email:</label><span class='prop'>%(email)s</span>
  </div>
  <div>
    <label class='prop-name'>Phone:</label><span class='prop'>%(phone)s</span>
  </div>
  <div>
    <label class='prop-name'>Details:</label><span class='prop'>%(details)s</span>
  </div>
  %(additional)s
</div>\
'''


# our database object
class Contact(db.Model):
  owner = db.UserProperty()
  private = db.BooleanProperty()
  name = db.StringProperty()
  email = db.EmailProperty()
  phone = db.PhoneNumberProperty()
  details = db.StringProperty()


class MainPage(webapp.RequestHandler):
  def get(self):
    user = users.get_current_user()
    if user:
      self.redirect('/user/contacts')
      return

    self.response.out.write(main_template)  


# helper function to template out a list of contacts
def template_contacts(lst, additional):
  out = ""
  for c in lst:
    first = False
    out += contact_template % {'name' : c.name, 'email' : c.email, 'phone' : c.phone, 'details' : c.details, 'id' : c.key().id(), 'additional' : additional}

  return out


class ContactManager(webapp.RequestHandler):
  def get(self, mount):
    user = users.get_current_user()
    if mount == 'public' or user == None:
      # get the public contacts only if they want it or
      # if they're not signed in
      q = db.GqlQuery("SELECT * FROM Contact WHERE private = FALSE ORDER BY name")
      public = q.fetch(10)

      from_db = template_contacts(public, '')

      self.response.out.write(contact_page_template % {'from_db' : from_db, 'add_contact' : '', 'title' : 'Public Contacts- <a href="' + users.create_login_url(federated_identity=provider) + '">login</a>'})
      return


    q = db.GqlQuery("SELECT * FROM Contact WHERE owner = :1 ORDER BY name", user)
    private = q.fetch(10)
    from_db = template_contacts(private, '<button>Delete</button>')

    self.response.out.write(contact_page_template % {'from_db' : from_db, 'add_contact' : add_contact_form, 'title' : 'Contacts- <a href="' + users.create_logout_url('/') + '">logout</a>'})

  def post(self, mount):
    # TODO: do something useful here
    user = users.get_current_user()
    if users.get_current_user():
      c = Contact()

      c.owner = user
      c.private = self.request.get('private') == 'on'
      c.name = self.request.get('name')
      c.email = self.request.get('email')
      c.phone = self.request.get('phone')
      c.details = self.request.get('details')

      c.put()

      self.redirect(self.request.url)
    else:
      self.error(401)

  def delete(self, mount):
    # TODO: do something useful here
    user = users.get_current_user()
    tid = self.request.get('id')
    if user:
      if type(tid) is not int:
        tid = int(tid)

      if type(tid) is int:
        tid = int(tid)
        p = Contact.get_by_id(tid)
        if p:
          p.delete()

        self.response.out.write('Successfully deleted %d' % tid)
      else:
        self.error(400)
        self.response.out.write('id not set or not a valid number: ' + tid)
    else:
      self.error(401)
      self.response.out.write('Invalid credentials')


class LoginHandler(webapp.RequestHandler):
  def get(self):
    self.response.out.write('[<a href="%s">%s</a>]' % (
    users.create_login_url(federated_identity=provider), 'Google'))


application = webapp.WSGIApplication([
  ('/', MainPage),
  ('/(user|public)/contacts', ContactManager),
  ('/login', LoginHandler)
], debug=True)


def main():
  util.run_wsgi_app(application)


if __name__ == '__main__':
  main()
