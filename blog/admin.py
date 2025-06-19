from django.contrib import admin
from django.core.mail import send_mass_mail
from django.contrib import messages
from .models import BlogPost, Category, Subscriber, Comment

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at', 'views' )
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ['title', 'content']
    list_filter = ['category', 'created_at']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category',)}

@admin.action(description="Send bulk email to subscribers")
def send_bulk_email(modeladmin, request, queryset):
    emails = [sub.email for sub in Subscriber.objects.all()]
    if not emails:
        messages.warning(request, "No subscribers found.")
        return

    subject = "New from our blog!"
    messages_list = []
    for post in queryset:
        body = f"{post.title}\n\n{post.content[:100]}...\nRead more: https://nashvybzes.site/blog/{post.slug}/"
        messages_list.append((subject, body, 'your@email.com', emails))

    send_mass_mail(messages_list, fail_silently=False)
    messages.success(request, "Emails sent successfully!")

@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'subscribed_at')
    actions = [send_bulk_email]

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('username', 'post', 'parent', 'created_at')
    search_fields = ['username', 'text']
    list_filter = ['created_at', 'post']
