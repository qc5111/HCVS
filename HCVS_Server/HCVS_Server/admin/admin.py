from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader


from HCVS_Server.admin.authorization import AuthorizationCheck


@AuthorizationCheck
def index(request, user):
    template = loader.get_template('admin/index.html')

    print(user.username)
    return HttpResponse(template.render({"username": user.username}, request))


