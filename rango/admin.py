from django.contrib import admin
from rango.models import Category, Page, UserProfile

class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')
    search_fields = ['title']


class PageInline(admin.TabularInline):
    model = Page
    extra = 1

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'views', 'likes')
    search_field = ['name']
    list_filter = ['views']
    inlines = [PageInline]


admin.site.register(Category, CategoryAdmin)
admin.site.register(UserProfile)
#admin.site.register(Page, PageAdmin)


