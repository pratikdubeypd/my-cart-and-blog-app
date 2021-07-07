from django.shortcuts import render
from django.http import HttpResponse
from .models import Blogpost

# Create your views here.
def index(request):
    blog = Blogpost.objects.all()
    parames={'blog':blog}
    return render(request, 'blog/index.html', parames)

def blogpost(request, blogid):
    blog=Blogpost.objects.all()
    return render(request, 'blog/blogpost.html', {'blog': blog[blogid-1]})

def search(request):
    query = request.GET.get('search')
    if len(query)>70:
        allBlogs = Blogpost.objects.none()
    else:
        allBlogsTitle = Blogpost.objects.filter(title__icontains=query)
        allBlogsHead = Blogpost.objects.filter(head0__icontains=query)
        allBlogsGenre = Blogpost.objects.filter(genre__icontains=query)
        allBlogsContent = Blogpost.objects.filter(chead0__icontains=query)
        allBlogs = allBlogsHead.union(allBlogsTitle, allBlogsGenre, allBlogsContent)
    if allBlogs.count()!=0:
        msg=""
        params={'allBlogs':allBlogs, 'msg':msg}
    else:
        params = {'msg': "Please enter relevant query"}
    return render(request, 'blog/search.html', params)