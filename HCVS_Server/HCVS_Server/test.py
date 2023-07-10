from django.http import HttpResponse

from tools.hash_chain import calcVotes


def test(request):
    calcVotes(1688615100+600)
    return HttpResponse("test")