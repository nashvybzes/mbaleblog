from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.utils.timezone import now
from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.db.models import F
from django.contrib import messages
from .forms import NewsletterForm, CommentForm,ContactForm
from .models import BlogPost, Category, Subscriber, Comment

from django.http import HttpResponse

def robots_txt(request):
    content = (
        "User-agent: *\n"
        "Disallow: /admin/\n"
        "Sitemap: https://nashvybzes.site/sitemap.xml\n"
    )
    return HttpResponse(content, content_type="text/plain")



def get_trending_posts(days=7, limit=30):
    recent_period = timezone.now() - timedelta(days=days)
    return BlogPost.objects.filter(published_at__gte=recent_period).order_by('-views')[:limit]

def contact_view(request):
    trending_posts = get_trending_posts()
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully! We will get back to you soon.')
            return redirect('blog:contact')  
    else:
        form = ContactForm()

    return render(request, 'blog/contact.html', {
        'form': form,
        'trending_posts': trending_posts,
    })

def home_view(request):
    most_viewed = BlogPost.objects.order_by('-views')[:30]
    trending_posts = get_trending_posts()


    return render(request, 'blog/home.html', {
        'most_viewed': most_viewed,
        'trending_posts': trending_posts,
    })

def about(request):
    trending_posts = get_trending_posts()
    return render(request, 'blog/about.html',{'trending_posts': trending_posts,})

def blog_list(request):
    trending_posts = get_trending_posts()
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q')
    categories = Category.objects.all()
    posts = BlogPost.objects.all().order_by('-created_at')

    if category_slug:
        posts = posts.filter(category__slug=category_slug)
    if search_query:
        posts = posts.filter(title__icontains=search_query)

    # Pagination: 6 posts per page
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    blog_posts = paginator.get_page(page_number)

    # Sidebar: recent posts
    recent_posts = BlogPost.objects.order_by('-created_at')[:3]

    return render(request, 'blog/list.html', {
        'blog_posts': blog_posts,
        'trending_posts': trending_posts,
        'categories': categories,
        'selected_category': category_slug,
        'search_query': search_query,
        'recent_posts': recent_posts,
    })

def trending_list(request):
    trending_posts = get_trending_posts()
    posts = BlogPost.objects.all().order_by('-views')  
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page')
    blog_posts = paginator.get_page(page_number)

    return render(request, 'blog/trending.html', {
        'trending_posts': trending_posts,
        'blog_posts': blog_posts,
    })

def blog_detail(request, slug):
    trending_posts = get_trending_posts()
    post = get_object_or_404(BlogPost, slug=slug)

    # ✅ Increment views safely using F() expression
    BlogPost.objects.filter(pk=post.pk).update(views=F('views') + 1)
    post.refresh_from_db()  # to get updated views

    # Initialize the comment form and get top-level comments
    comment_form = CommentForm()
    comments = post.comments.filter(parent__isnull=True).order_by('-created_at')

    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            # 🛡️ Honeypot spam protection
            if comment_form.cleaned_data.get('honeypot'):
                return redirect('blog:detail', slug=slug)

            # 🛡️ Rate limit: prevent same user/IP from commenting repeatedly in 10s
            ip = request.META.get('REMOTE_ADDR')
            recent_comments = Comment.objects.filter(
                post=post,
                created_at__gte=now() - timedelta(seconds=10),
                username=comment_form.cleaned_data.get('username')
            )
            if recent_comments.exists():
                comment_form.add_error(None, "You're commenting too quickly. Try again shortly.")
            else:
                new_comment = comment_form.save(commit=False)
                new_comment.post = post

                # Handle replies if parent_id is set
                parent_id = comment_form.cleaned_data.get('parent_id')
                if parent_id:
                    parent_comment = Comment.objects.filter(id=parent_id, post=post).first()
                    if parent_comment:
                        new_comment.parent = parent_comment

                new_comment.save()
                return redirect('blog:detail', slug=slug)

    # Fetch related content
    cover_image_url = request.build_absolute_uri(post.cover_image.url) if post.cover_image else None
    related_posts = BlogPost.objects.filter(category=post.category).exclude(id=post.id)[:4]
    you_may_also_like = BlogPost.objects.exclude(id=post.id).order_by('?')[:4]
    trending_posts = BlogPost.objects.order_by('-views')[:5]

    return render(request, 'blog/detail.html', {
        'post': post,
        'trending_posts': trending_posts,
        'cover_image_url': cover_image_url,
        'comments': comments,
        'comment_form': comment_form,
        'related_posts': related_posts,
        'you_may_also_like': you_may_also_like,
        'trending_posts': trending_posts,
    })
def newsletter_signup(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            form.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))

@require_POST
def ajax_add_comment(request, slug):
    from .models import BlogPost, Comment
    from .forms import CommentForm

    post = get_object_or_404(BlogPost, slug=slug)
    form = CommentForm(request.POST)

    if form.is_valid():
        if form.cleaned_data.get('honeypot'):
            return JsonResponse({'error': 'Spam detected'}, status=400)

        username = form.cleaned_data.get('username')
        recent_comments = Comment.objects.filter(
            post=post,
            created_at__gte=now() - timedelta(seconds=10),
            username=username
        )
        if recent_comments.exists():
            return JsonResponse({'error': 'You’re commenting too quickly. Try again shortly.'}, status=429)

        new_comment = form.save(commit=False)
        new_comment.post = post

        parent_id = form.cleaned_data.get('parent_id')
        if parent_id:
            parent_comment = Comment.objects.filter(id=parent_id, post=post).first()
            if parent_comment:
                new_comment.parent = parent_comment

        new_comment.save()

        return JsonResponse({
            'success': True,
            'username': new_comment.username,
            'text': new_comment.text,
            'created_at': new_comment.created_at.strftime("%b %d, %Y %H:%M"),
            'parent_id': new_comment.parent.id if new_comment.parent else None
        })

    return JsonResponse({'error': 'Invalid form'}, status=400)
